from fastapi.testclient import TestClient

from app.main import app
from app.services.qwen import QwenClient
from tests.test_accounts import login
from tests.test_assistant import history, new_conversation, send


def test_restart_keeps_conversation_and_multiturn_context(tmp_path, monkeypatch):
    monkeypatch.setenv("HANDBOOK_DATABASE_PATH", str(tmp_path / "persistent.sqlite3"))
    monkeypatch.setenv("RAG_PROJECT_DIR", str(tmp_path))
    monkeypatch.setenv("COOKIE_SECURE", "false")
    calls = []

    def complete(self, messages, **kwargs):
        calls.append(messages)
        return "重启前的助手回答"

    monkeypatch.setattr(QwenClient, "complete", complete)
    with TestClient(app, headers={"Origin": "http://testserver"}) as client:
        credentials = login(client)
        conversation = new_conversation(client)
        assert send(client, conversation, "重启前的用户问题").status_code == 200
    with TestClient(app, headers={"Origin": "http://testserver"}) as client:
        assert client.post("/api/auth/login", json=credentials).status_code == 200
        assert history(client, conversation).json()["total"] == 2
        assert send(client, conversation, "重启后继续").status_code == 200
    assert calls[-1][1]["content"] == "重启前的用户问题"
    assert calls[-1][2]["content"] == "重启前的助手回答"
