def test_pages_and_knowledge(client):
    for path in ("/", "/guide", "/login", "/register", "/account"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    assert "绍兴大学学生手册" in client.get("/").text
    assert "学生手册 RAG" in client.get("/guide").text
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/examples/echo").status_code == 404
