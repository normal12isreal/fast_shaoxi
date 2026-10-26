import time

from sqlalchemy import func, select

from app.db.models import LoginSession, RAGRecord, User
from app.services.auth import COOKIE, token_hash
from tests.test_rag import answer


def login(client, username="alice"):
    credentials = {"username": username, "password": "test-password-123"}
    assert client.post("/api/auth/register", json=credentials).status_code == 201
    assert client.post("/api/auth/login", json=credentials).status_code == 200
    return credentials


def test_auth_hash_session_logout(client):
    credentials = login(client)
    assert client.get("/api/auth/me").json()["username"] == "alice"
    with client.app.state.db.sessions() as session:
        row = session.scalar(select(User))
        assert row.password_hash.startswith("$argon2id$")
        assert row.password_hash != credentials["password"]
        assert session.scalar(select(LoginSession)).token_hash != client.cookies.get(COOKIE)
    assert client.post("/api/auth/register", json=credentials).status_code == 409
    wrong = {**credentials, "password": "wrong-password"}
    assert client.post("/api/auth/login", json=wrong).status_code == 401
    cookie = client.cookies.get(COOKIE)
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    client.cookies.set(COOKIE, cookie)
    assert client.get("/api/auth/me").status_code == 401


def test_cookie_flags_expiry_and_origin(client):
    credentials = login(client)
    response = client.post("/api/auth/login", json=credentials)
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie and "path=/" in cookie
    assert (
        client.post("/api/auth/logout", headers={"Origin": "https://evil.example"}).status_code
        == 403
    )
    del client.headers["Origin"]
    assert client.post("/api/auth/logout").status_code == 403
    with client.app.state.db.sessions.begin() as session:
        row = session.get(LoginSession, token_hash(client.cookies.get(COOKIE)))
        row.expires_at = int(time.time()) - 1
    assert client.get("/api/auth/me").status_code == 401


def test_anonymous_no_history_and_owned_pagination(client, monkeypatch):
    monkeypatch.setattr(client.app.state.rag, "query", answer)
    assert client.post("/api/rag/ask", json={"question": "匿名问题"}).status_code == 200
    with client.app.state.db.sessions() as session:
        assert session.scalar(select(func.count()).select_from(RAGRecord)) == 0
    assert client.get("/api/rag/records").status_code == 401
    login(client)
    for question in ("第一个问题", "第二个问题"):
        assert client.post("/api/rag/ask", json={"question": question}).status_code == 200
    page = client.get("/api/rag/records?limit=1").json()
    assert page["total"] == 2 and len(page["items"]) == 1
    record_id = page["items"][0]["id"]
    detail = client.get(f"/api/rag/records/{record_id}").json()
    assert detail["result"]["question"] == "第二个问题"
    assert "private" not in str(detail)
    assert (
        client.get("/api/rag/records?limit=1&offset=1").json()["items"][0]["question"]
        == "第一个问题"
    )
    client.post("/api/auth/logout")
    login(client, "bob")
    assert client.get("/api/rag/records").json()["total"] == 0
    assert client.get(f"/api/rag/records/{record_id}").status_code == 404


def test_failed_record_is_explicit(client, monkeypatch):
    login(client)

    def fail(_):
        raise RuntimeError("secret")

    monkeypatch.setattr(client.app.state.rag, "query", fail)
    assert client.post("/api/rag/ask", json={"question": "失败问题"}).status_code == 502
    record = client.get("/api/rag/records").json()["items"][0]
    detail = client.get(f"/api/rag/records/{record['id']}").json()
    assert detail["status"] == "failed"
    assert detail["result"] is None
    assert "secret" not in str(detail)


def test_https_cookie_configuration(client, monkeypatch):
    credentials = login(client)
    monkeypatch.setenv("COOKIE_SECURE", "true")
    response = client.post("/api/auth/login", json=credentials)
    assert "; secure" in response.headers["set-cookie"].lower()
