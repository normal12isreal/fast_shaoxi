import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("HANDBOOK_DATABASE_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("COOKIE_SECURE", "false")
    with TestClient(app) as test_client:
        test_client.headers["Origin"] = "http://testserver"
        yield test_client
