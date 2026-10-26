"""验证不同响应类型、资源边界和模板传值；不调用网络模型。"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_template_renders_configuration_and_route_urls(client):
    response = client.get("/demo")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Test Learning Lab" in response.text
    assert "{{ app_name }}" not in response.text
    assert 'data-endpoint="/examples/echo"' in response.text
    assert 'src="/static/images/user.svg"' in response.text


def test_template_escapes_configuration(client):
    settings = client.app.state.settings.model_copy(update={"app_name": "<script>bad()</script>"})
    with TestClient(create_app(settings)) as other_client:
        html = other_client.get("/demo").text
    assert "<script>bad()</script>" not in html
    assert "&lt;script&gt;bad()&lt;/script&gt;" in html


def test_static_mapping_is_independent_of_working_directory(client, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("user.svg", "assistant.svg"):
        response = client.get(f"/static/images/{name}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")
        assert "<svg" in response.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/images/missing.svg").status_code == 404
    assert client.get("/static/main.py").status_code == 404


def test_direct_html_and_file_download(client):
    response = client.get("/demo/html")
    assert response.headers["content-type"].startswith("text/html")
    assert "这是 HTMLResponse" in response.text
    response = client.get("/demo/download")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert 'attachment; filename="request-map.txt"' == response.headers["content-disposition"]
    expected = Path(__file__).resolve().parents[1] / "app/resources/request-map.txt"
    assert response.content == expected.read_bytes()
