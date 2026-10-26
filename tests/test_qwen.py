import json

import pytest

from app.services import qwen


def test_multiturn_request_and_incomplete_response(monkeypatch):
    monkeypatch.setattr(qwen, "load_credentials", lambda: ("test-key", "https://example.test/v1"))
    captured = []
    finish = ["stop"]

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, _):
            return json.dumps(
                {"choices": [{"message": {"content": "模型回答"}, "finish_reason": finish[0]}]}
            ).encode()

    class Opener:
        def open(self, request, timeout):
            captured.append((json.loads(request.data), timeout))
            return Response()

    monkeypatch.setattr(qwen, "build_opener", lambda *_: Opener())
    messages = [
        {"role": "system", "content": "职责"},
        {"role": "user", "content": "第一问"},
        {"role": "assistant", "content": "第一答"},
        {"role": "user", "content": "第二问"},
    ]
    assert qwen.QwenClient().complete(messages) == "模型回答"
    assert captured[0][0]["messages"] == messages
    assert captured[0][1] == 60
    finish[0] = "length"
    with pytest.raises(qwen.QwenError):
        qwen.QwenClient().complete(messages)
    assert len(captured) == 2  # 每个 complete 仅一次 HTTP 请求。
