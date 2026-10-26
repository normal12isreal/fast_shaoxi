"""安装助手的对话状态：短事务保存原文，模型调用在线程中独立执行。"""

import asyncio
import threading
from uuid import uuid4

from sqlalchemy import select

from app.db.models import Conversation, Message, timestamp
from app.schemas.assistant import AssistantReply, MessageItem
from app.services.assistant_context import ContextBuilder, ContextError
from app.services.execution import BusyError, ExecutionPool
from app.services.qwen import QwenClient, QwenError


class ConversationMissing(Exception):
    pass


class ConversationBusy(Exception):
    pass


def owned_conversation(session, conversation_id: str, user_id: int) -> Conversation:
    conversation = session.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
    )
    if conversation is None:
        raise ConversationMissing
    return conversation


class AssistantService:
    def __init__(self, database):
        self.database = database
        self.model = QwenClient()
        self.context = ContextBuilder(self.model)
        self.pool = ExecutionPool(workers=2)
        self._active: set[str] = set()
        self._lock = threading.Lock()

    def active(self, conversation_id: str) -> bool:
        with self._lock:
            return conversation_id in self._active

    def _reserve(self, conversation_id: str) -> None:
        with self._lock:
            if conversation_id in self._active:
                raise ConversationBusy
            self._active.add(conversation_id)

    def _release(self, conversation_id: str) -> None:
        with self._lock:
            self._active.discard(conversation_id)

    def delete(self, conversation_id: str, user_id: int) -> None:
        self._reserve(conversation_id)
        try:
            with self.database.sessions.begin() as session:
                conversation = owned_conversation(session, conversation_id, user_id)
                session.delete(conversation)  # SQLite 外键级联删除消息。
        finally:
            self._release(conversation_id)

    def _fail(self, message_id: int, error: str) -> None:
        with self.database.sessions.begin() as session:
            message = session.get(Message, message_id)
            if message and message.status == "pending":
                message.status, message.error = "failed", error

    def _answer(self, conversation_id: str, user_id: int, message_id: int) -> AssistantReply:
        try:
            with self.database.sessions() as session:
                conversation = owned_conversation(session, conversation_id, user_id)
                current = session.get(Message, message_id)
                question = current.content
                history = [
                    MessageItem.model_validate(row)
                    for row in session.scalars(
                        select(Message)
                        .where(
                            Message.conversation_id == conversation_id,
                            Message.status == "completed",
                        )
                        .order_by(Message.id)
                    ).all()
                ]
                summary, through = conversation.summary, conversation.summarized_through
            # 数据库会话到这里已关闭；下面的压缩和问答都不持有事务。
            messages, summary, through = self.context.build(summary, through, history, question)
            with self.database.sessions() as session:
                if session.get(Message, message_id).status != "pending":
                    raise QwenError("请求已结束，未继续调用模型。")
            answer = self.model.complete(messages)
            with self.database.sessions.begin() as session:
                current = session.get(Message, message_id)
                if current.status != "pending":
                    raise QwenError("请求已结束，迟到的模型结果未写成成功回答。")
                conversation = owned_conversation(session, conversation_id, user_id)
                conversation.summary, conversation.summarized_through = summary, through
                conversation.updated_at = timestamp()
                current.status = "completed"
                assistant = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    status="completed",
                )
                session.add(assistant)
                session.flush()
                return AssistantReply(
                    user_message=MessageItem.model_validate(current),
                    assistant_message=MessageItem.model_validate(assistant),
                )
        finally:
            # 即使 HTTP 已超时，直到真实线程结束才允许此对话处理下一条消息。
            self._release(conversation_id)

    async def send(self, conversation_id: str, user_id: int, content: str) -> AssistantReply:
        with self.database.sessions() as session:
            owned_conversation(session, conversation_id, user_id)
        self._reserve(conversation_id)
        try:
            with self.database.sessions.begin() as session:
                conversation = owned_conversation(session, conversation_id, user_id)
                conversation.title = (
                    content[:60] if conversation.title == "新对话" else conversation.title
                )
                conversation.updated_at = timestamp()
                message = Message(
                    conversation_id=conversation_id, role="user", content=content, status="pending"
                )
                session.add(message)
                session.flush()
                message_id = message.id
        except BaseException:
            self._release(conversation_id)
            raise
        try:
            return await self.pool.run(lambda: self._answer(conversation_id, user_id, message_id))
        except BusyError:
            self._release(conversation_id)  # 尚未提交线程，没有模型调用。
            self._fail(message_id, "助手服务忙碌，请稍后重试。")
            raise
        except TimeoutError:
            self._fail(message_id, "等待超时，原消息已保存；后台调用可能仍在结束。")
            raise
        except asyncio.CancelledError:
            self._fail(message_id, "请求中断，原消息已保存。")
            raise
        except (ContextError, QwenError) as error:
            self._fail(message_id, str(error))
            raise
        except Exception:
            self._fail(message_id, "助手调用失败，原消息已保存。")
            raise QwenError("助手调用失败，请稍后重试。") from None

    def create(self, user_id: int) -> Conversation:
        with self.database.sessions.begin() as session:
            conversation = Conversation(id=uuid4().hex, user_id=user_id)
            session.add(conversation)
            session.flush()
            return conversation
