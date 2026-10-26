"""登录后的安装助手接口；所有对话操作都校验所属用户。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select

from app.db.models import Conversation, Message
from app.schemas.assistant import (
    AssistantReply,
    ConversationItem,
    ConversationPage,
    MessageItem,
    MessagePage,
    NewMessage,
)
from app.services.assistant import ConversationBusy, ConversationMissing, owned_conversation
from app.services.assistant_context import ContextError
from app.services.auth import CurrentUser, same_origin
from app.services.execution import BusyError
from app.services.qwen import QwenError


def private_response(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


router = APIRouter(
    prefix="/api/assistant/conversations",
    tags=["RAG 安装助手"],
    dependencies=[Depends(private_response)],
)


def check_owned(session, conversation_id: str, user_id: int):
    try:
        return owned_conversation(session, conversation_id, user_id)
    except ConversationMissing:
        raise HTTPException(404, "对话不存在。") from None


@router.post(
    "", response_model=ConversationItem, status_code=201, dependencies=[Depends(same_origin)]
)
def create(request: Request, user: CurrentUser):
    return request.app.state.assistant.create(user.id)


@router.get("", response_model=ConversationPage)
def conversations(
    request: Request,
    user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    with request.app.state.db.sessions() as session:
        owned = Conversation.user_id == user.id
        total = session.scalar(select(func.count()).select_from(Conversation).where(owned))
        rows = session.scalars(
            select(Conversation)
            .where(owned)
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return ConversationPage(
            items=[ConversationItem.model_validate(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )


@router.get("/{conversation_id}/messages", response_model=MessagePage)
def messages(
    conversation_id: str,
    request: Request,
    user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """从最新消息向前分页，每页内部按先后顺序展示；不调用模型。"""
    with request.app.state.db.sessions() as session:
        check_owned(session, conversation_id, user.id)
        owned = Message.conversation_id == conversation_id
        total = session.scalar(select(func.count()).select_from(Message).where(owned))
        rows = session.scalars(
            select(Message).where(owned).order_by(Message.id.desc()).offset(offset).limit(limit)
        ).all()
        return MessagePage(
            items=[MessageItem.model_validate(row) for row in reversed(rows)],
            total=total,
            limit=limit,
            offset=offset,
            busy=request.app.state.assistant.active(conversation_id),
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=AssistantReply,
    dependencies=[Depends(same_origin)],
    responses={
        409: {"description": "同一对话正在处理消息"},
        422: {"description": "输入为空、过长或上下文超预算"},
        502: {"description": "千问调用或压缩失败，原消息保留"},
        503: {"description": "助手服务繁忙"},
        504: {"description": "等待超时，原消息保留"},
    },
)
async def send(conversation_id: str, body: NewMessage, request: Request, user: CurrentUser):
    # static/assistant.js → 本接口 → AssistantService → 上下文组织 → QwenClient。
    try:
        return await request.app.state.assistant.send(conversation_id, user.id, body.content)
    except ConversationMissing:
        raise HTTPException(404, "对话不存在。") from None
    except ConversationBusy:
        raise HTTPException(409, "这段对话仍在处理上一条消息，请稍后再试。") from None
    except BusyError:
        raise HTTPException(
            503, "助手服务繁忙，请稍后重试。", headers={"Retry-After": "5"}
        ) from None
    except ContextError as error:
        raise HTTPException(422, str(error)) from None
    except TimeoutError:
        raise HTTPException(504, "助手等待超时，原消息已保存；后台调用可能仍在结束。") from None
    except QwenError as error:
        raise HTTPException(502, str(error)) from None


@router.delete("/{conversation_id}", dependencies=[Depends(same_origin)])
def remove(conversation_id: str, request: Request, user: CurrentUser):
    with request.app.state.db.sessions() as session:
        check_owned(session, conversation_id, user.id)
    try:
        request.app.state.assistant.delete(conversation_id, user.id)
    except ConversationMissing:
        raise HTTPException(404, "对话不存在。") from None
    except ConversationBusy:
        raise HTTPException(409, "对话仍在处理消息，请结束后再删除。") from None
    return {"message": "对话及消息已删除。"}
