import pytest


def test_root_returns_json(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "你好，FastAPI",
        "demo": "/demo",
        "docs": "/docs",
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_echo_preserves_unicode(client):
    response = client.post("/examples/echo", json={"message": "你好，FastAPI"})
    assert response.status_code == 200
    assert response.json() == {"message": "你好，FastAPI", "length": 10}


@pytest.mark.parametrize(
    "payload",
    [{}, {"message": ""}, {"message": "x" * 201}, {"message": 123}, {"message": "hi", "x": 1}],
)
def test_echo_rejects_invalid_input(client, payload):
    assert client.post("/examples/echo", json=payload).status_code == 422


def test_openapi_describes_the_example(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "post" in schema["paths"]["/examples/echo"]
