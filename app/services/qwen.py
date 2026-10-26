"""千问多轮 HTTP 客户端；单次调用、不重试、不复用原 RAG 的固定单轮客户端。"""

import json
import os
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.services.knowledge import rag_directory
from app.services.rag import import_rag


class QwenError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_credentials() -> tuple[str, str]:
    import_rag()
    from scripts.embed_chunks import load_local_credentials

    return load_local_credentials(rag_directory())


class QwenClient:
    def __init__(self):
        self.model = os.environ.get("ASSISTANT_MODEL", "qwen3.7-plus")

    def complete(self, messages: list[dict[str, str]], *, max_tokens: int = 1800) -> str:
        try:
            # 仅共用凭据读取和官方地址校验；消息结构由安装助手自己构建。
            key, base_url = load_credentials()
            if not key or any(character.isspace() for character in key):
                raise ValueError("Missing key")
            body = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "enable_thinking": False,
                "temperature": 0.2,
                "max_completion_tokens": max_tokens,
            }
            request = Request(
                base_url + "/chat/completions",
                method="POST",
                data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
            )
            with build_opener(NoRedirect()).open(request, timeout=60) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("Overlong response")
            data = json.loads(raw)
            choice = data["choices"][0]
            text = choice["message"]["content"]
            if choice["finish_reason"] != "stop" or not isinstance(text, str) or not text.strip():
                raise ValueError("Incomplete response")
            return text.strip()
        except Exception:
            # 上游响应和异常可能包含私有信息，统一转换为安全的失败提示。
            raise QwenError("千问调用未完成，请检查配置或稍后重试。") from None
