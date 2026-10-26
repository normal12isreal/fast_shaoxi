import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.qwen import QwenClient
from app.services.rag import RAGService


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("HANDBOOK_DATABASE_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("COOKIE_SECURE", "false")
    public_project = tmp_path / "rag"
    public_project.mkdir()
    (public_project / "README.md").write_text(
        "# 绍兴大学学生手册 RAG\n公开安装资料。", encoding="utf-8"
    )
    monkeypatch.setenv("RAG_PROJECT_DIR", str(public_project))

    def unexpected_call(*args, **kwargs):
        raise AssertionError("自动测试禁止真实模型调用")

    monkeypatch.setattr(RAGService, "query", unexpected_call)
    monkeypatch.setattr(QwenClient, "complete", unexpected_call)
    with TestClient(app) as test_client:
        test_client.headers["Origin"] = "http://testserver"
        yield test_client
