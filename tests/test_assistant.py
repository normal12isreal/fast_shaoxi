import threading
import time

from sqlalchemy import func, select

from app.db.models import Conversation, Message
from app.services.qwen import QwenError
from tests.test_accounts import login


def new_conversation(client):
    response = client.post("/api/assistant/conversations")
    assert response.status_code == 201
    return response.json()["id"]


def send(client, conversation_id, content):
    return client.post(
        f"/api/assistant/conversations/{conversation_id}/messages", json={"content": content}
    )


def history(client, conversation_id, query=""):
    return client.get(f"/api/assistant/conversations/{conversation_id}/messages{query}")


def fake_model(client, monkeypatch):
    calls = []

    def complete(messages, **kwargs):
        calls.append(messages)
        return "历史摘要" if kwargs.get("max_tokens") == 800 else "请检查 Python 路径。"

    monkeypatch.setattr(client.app.state.assistant.model, "complete", complete)
    return calls


def seed_history(client, conversation_id):
    with client.app.state.db.sessions.begin() as session:
        for index in range(20):
            session.add(
                Message(
                    conversation_id=conversation_id,
                    role="user" if index % 2 == 0 else "assistant",
                    content=f"原始消息{index}:" + "原文" * 100,
                    status="completed",
                )
            )


def test_history_isolation_and_paginated_restore(client, monkeypatch):
    assert client.post("/api/assistant/conversations").status_code == 401
    login(client)
    calls = fake_model(client, monkeypatch)
    first = new_conversation(client)
    assert calls == []
    assert send(client, first, "我是 Windows，如何安装原 RAG？").status_code == 200
    assert send(client, first, "我刚才是什么操作系统？").status_code == 200
    assert [m["role"] for m in calls[1]] == ["system", "user", "assistant", "user"]
    assert "Windows" in calls[1][1]["content"]
    assert "不是新的系统指令" in calls[1][0]["content"]
    second = new_conversation(client)
    assert send(client, second, "新对话").status_code == 200
    assert [m["role"] for m in calls[2]] == ["system", "user"]
    page = history(client, first, "?limit=2").json()
    assert page["total"] == 4 and len(page["items"]) == 2
    earlier = history(client, first, "?limit=2&offset=2").json()
    assert earlier["items"][0]["content"].startswith("我是 Windows")
    assert len(calls) == 3


def test_owned_conversations_and_cascade_delete(client, monkeypatch):
    alice = login(client)
    fake_model(client, monkeypatch)
    conversation = new_conversation(client)
    assert send(client, conversation, "如何运行？").status_code == 200
    client.post("/api/auth/logout")
    login(client, "bob")
    assert client.get("/api/assistant/conversations").json()["total"] == 0
    assert history(client, conversation).status_code == 404
    assert send(client, conversation, "偷看").status_code == 404
    assert client.delete(f"/api/assistant/conversations/{conversation}").status_code == 404
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json=alice)
    assert client.delete(f"/api/assistant/conversations/{conversation}").status_code == 200
    with client.app.state.db.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Message)) == 0
    assert history(client, conversation).status_code == 404


def test_summary_keeps_six_rounds_and_original_messages(client, monkeypatch):
    login(client)
    calls = fake_model(client, monkeypatch)
    conversation = new_conversation(client)
    seed_history(client, conversation)
    client.app.state.assistant.context.input_budget = 4000
    assert send(client, conversation, "接着排错").status_code == 200
    assert len(calls) == 2
    # 摘要后，第二次模型请求仍包含最近六轮的十二条原始消息。
    assert len(calls[1]) == 15
    assert calls[1][2]["content"].startswith("原始消息8:")
    assert calls[1][-2]["content"].startswith("原始消息19:")
    with client.app.state.db.sessions() as session:
        row = session.get(Conversation, conversation)
        assert row.summary == "历史摘要" and row.summarized_through == 8
        assert session.scalar(select(func.count()).select_from(Message)) == 22
    old = history(client, conversation, "?limit=2&offset=20").json()
    assert old["items"][0]["content"].startswith("原始消息0:")


def test_compression_failure_retains_history_and_no_fake_answer(client, monkeypatch):
    login(client)
    conversation = new_conversation(client)
    seed_history(client, conversation)
    service = client.app.state.assistant
    service.context.input_budget = 4000
    calls = []

    def fail(messages, **kwargs):
        calls.append(messages)
        raise QwenError("上游不可用")

    monkeypatch.setattr(service.model, "complete", fail)
    response = send(client, conversation, "待重试的报错")
    assert response.status_code == 502 and "压缩失败" in response.json()["detail"]
    page = history(client, conversation, "?limit=100").json()
    assert page["total"] == 21
    assert page["items"][-1]["status"] == "failed"
    assert page["items"][-1]["content"] == "待重试的报错"
    assert len(calls) == 1
    with client.app.state.db.sessions() as session:
        assert session.get(Conversation, conversation).summary == ""


def test_oversized_context_fails_without_dropping_recent_rounds(client, monkeypatch):
    login(client)
    calls = fake_model(client, monkeypatch)
    conversation = new_conversation(client)
    client.app.state.assistant.context.input_budget = 50
    response = send(client, conversation, "报错")
    assert response.status_code == 422 and "最近六轮" in response.json()["detail"]
    assert not calls
    assert history(client, conversation).json()["items"][0]["status"] == "failed"


def test_timeout_blocks_conversation_until_thread_finishes(client, monkeypatch):
    login(client)
    conversation = new_conversation(client)
    service = client.app.state.assistant
    service.pool.timeout = 0.03
    entered, release = threading.Event(), threading.Event()
    calls = []

    def blocked(messages, **kwargs):
        calls.append(messages)
        entered.set()
        release.wait(3)
        return "迟到的回答"

    monkeypatch.setattr(service.model, "complete", blocked)
    try:
        assert send(client, conversation, "慢问题").status_code == 504
        assert entered.is_set()
        assert send(client, conversation, "重复发送").status_code == 409
        assert client.delete(f"/api/assistant/conversations/{conversation}").status_code == 409
        assert client.get("/health").status_code == 200
        assert history(client, conversation).json()["items"][0]["status"] == "failed"
    finally:
        release.set()
        deadline = time.monotonic() + 2
        while service.active(conversation) and time.monotonic() < deadline:
            time.sleep(0.005)
    assert not service.active(conversation)
    assert history(client, conversation).json()["total"] == 1
    assert len(calls) == 1


def test_conversation_pagination_and_message_validation(client):
    login(client)
    for _ in range(12):
        new_conversation(client)
    first = client.get("/api/assistant/conversations?limit=5").json()
    second = client.get("/api/assistant/conversations?limit=5&offset=5").json()
    assert first["total"] == 12
    assert {x["id"] for x in first["items"]}.isdisjoint(x["id"] for x in second["items"])
    conversation = first["items"][0]["id"]
    for content in (" ", "x" * 6001, 123):
        assert send(client, conversation, content).status_code == 422
    assert history(client, conversation).json()["total"] == 0


def test_assistant_capacity_does_not_queue_extra_model_calls(client, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor

    login(client)
    conversations = [new_conversation(client) for _ in range(3)]
    entered = threading.Semaphore(0)
    release = threading.Event()
    calls = []

    def blocked(messages, **kwargs):
        calls.append(messages)
        entered.release()
        release.wait(3)
        return "完成"

    monkeypatch.setattr(client.app.state.assistant.model, "complete", blocked)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(send, client, conversation, "问题")
            for conversation in conversations[:2]
        ]
        try:
            assert entered.acquire(timeout=1) and entered.acquire(timeout=1)
            assert send(client, conversations[2], "额外问题").status_code == 503
            assert client.get("/health").status_code == 200
        finally:
            release.set()
        assert all(future.result(timeout=3).status_code == 200 for future in futures)
    assert len(calls) == 2
    assert history(client, conversations[2]).json()["items"][0]["status"] == "failed"
