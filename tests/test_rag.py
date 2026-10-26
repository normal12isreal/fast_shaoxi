import asyncio
import threading
import time

import pytest

from app.services.execution import BusyError, ExecutionPool


def answer(question):
    return {
        "request_id": "test",
        "question": question,
        "answer": "测试回答 [1]",
        "sources": [
            {
                "label": "[1]",
                "text": "条款",
                "pdf_pages": [12],
                "source_file": "D:/private/book.pdf",
            }
        ],
        "status": "answered",
        "complete": True,
        "elapsed_seconds": 0.1,
        "record_path": "D:/private/key",
    }


def test_public_api_and_validation(client, monkeypatch):
    monkeypatch.setattr(client.app.state.rag, "query", answer)
    response = client.post("/api/rag/ask", json={"question": " 奖学金？ "})
    assert response.status_code == 200
    assert response.json()["question"] == "奖学金？"
    assert "private" not in response.text
    assert "ApiKey" not in client.get("/openapi.json").text
    for value in ("", "  ", "x" * 501, 123, None):
        assert client.post("/api/rag/ask", json={"question": value}).status_code == 422
    assert client.post("/api/rag/ask", json={}).status_code == 422


def test_safe_upstream_failure(client, monkeypatch):
    def fail(_):
        raise ValueError("secret local path")

    monkeypatch.setattr(client.app.state.rag, "query", fail)
    response = client.post("/api/rag/ask", json={"question": "问题"})
    assert response.status_code == 502
    assert "secret" not in response.text


def test_web_citations_are_public_without_internal_paths(client, monkeypatch):
    def web_answer(question):
        result = answer(question)
        result["sources"] = [
            {
                "label": "资料1",
                "kind": "web_search_summary",
                "text": "联网摘要",
                "web_sources": [
                    {
                        "title": "官方资料",
                        "url": "https://www.usx.edu.cn/",
                        "internal_path": "private",
                    }
                ],
            }
        ]
        return result

    monkeypatch.setattr(client.app.state.rag, "query", web_answer)
    response = client.post("/api/rag/ask", json={"question": "问题"})
    assert response.status_code == 200
    assert response.json()["sources"][0]["web_sources"][0]["url"] == "https://www.usx.edu.cn/"
    assert "private" not in response.text


def test_timeout_keeps_real_slot(client, monkeypatch):
    entered, release = threading.Event(), threading.Event()

    def blocked(question):
        entered.set()
        release.wait(3)
        return answer(question)

    service = client.app.state.rag
    service.pool.timeout = 0.03
    monkeypatch.setattr(service, "query", blocked)
    try:
        assert client.post("/api/rag/ask", json={"question": "第一问"}).status_code == 504
        assert entered.is_set()
        response = client.post("/api/rag/ask", json={"question": "第二问"})
        assert response.status_code == 503
        assert response.headers["retry-after"] == "5"
        assert client.get("/health").status_code == 200
    finally:
        release.set()


def test_cancel_keeps_slot():
    async def scenario():
        entered, release = threading.Event(), threading.Event()
        pool = ExecutionPool(timeout=2)
        task = asyncio.create_task(pool.run(lambda: (entered.set(), release.wait(3))))
        while not entered.is_set():
            await asyncio.sleep(0.001)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        try:
            with pytest.raises(BusyError):
                await pool.run(lambda: None)
        finally:
            release.set()
            pool.close()

    asyncio.run(scenario())


def test_question_over_twenty_seconds_keeps_http_responsive(client, monkeypatch):
    def slow(question):
        time.sleep(20.1)
        return answer(question)

    monkeypatch.setattr(client.app.state.rag, "query", slow)
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.post, "/api/rag/ask", json={"question": "慢问题"})
        time.sleep(0.1)
        started = time.monotonic()
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200
        assert time.monotonic() - started < 2
        result = future.result(timeout=25)
        assert result.status_code == 200
