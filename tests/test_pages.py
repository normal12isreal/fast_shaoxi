def test_pages_and_knowledge(client):
    for path in ("/", "/guide", "/api-docs", "/login", "/register", "/account"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
    assert "绍兴大学学生手册" in client.get("/").text
    assert "学生手册 RAG" in client.get("/guide").text
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/examples/echo").status_code == 404
    home = client.get("/").text
    assert 'href="/api-docs"' in home and 'href="/docs"' not in home
    assert "curl -X POST" not in home
    tutorial = client.get("/api-docs").text
    assert "http://testserver/api/rag/ask" in tutorial
    assert "Invoke-RestMethod" in tutorial and "urlopen(request, timeout=210)" in tutorial
    specification = client.get("/openapi.json").json()
    assert specification["paths"]["/api/rag/ask"]["post"]["tags"] == ["公开手册问答"]
    assert specification["paths"]["/api/rag/records"]["get"]["tags"] == ["个人记录"]
