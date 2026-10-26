"""网站问答 → 原项目公共 Python 接口；不复写检索算法。"""

import os
import subprocess
import sys
from pathlib import Path

from app.services.execution import ExecutionPool
from app.services.knowledge import PROJECT_ROOT, rag_directory


def import_original() -> None:
    root = rag_directory()
    if not (root / "student_handbook_rag" / "__init__.py").is_file():
        raise ValueError("RAG 项目尚未配置")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def reference_directory() -> Path:
    """配置、索引使用目录引用；原库的相对缓存写入网站自己的运行目录。"""
    root = PROJECT_ROOT / ".runtime" / "rag-view"
    root.mkdir(parents=True, exist_ok=True)
    for name in ("config", "output"):
        target, link = rag_directory() / name, root / name
        if not target.is_dir():
            raise ValueError("RAG 数据不完整")
        if link.exists():
            if link.resolve() != target.resolve():
                raise ValueError("RAG 目录引用与配置不一致，请检查运行说明")
            continue
        if os.name == "nt":
            # Junction 不要求管理员权限；参数只来自已解析的本地目录，不含模型凭据。
            quoted = [str(path).replace("'", "''") for path in (link, target)]
            command = (
                "$ErrorActionPreference='Stop'; New-Item -ItemType Junction "
                f"-Path '{quoted[0]}' -Target '{quoted[1]}' | Out-Null"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            link.symlink_to(target, target_is_directory=True)
    return root


class RAGService:
    def __init__(self):
        self.pool = ExecutionPool()
        self._client = None

    def query(self, question: str) -> dict:
        if self._client is None:
            import_original()
            from scripts.embed_chunks import load_local_credentials
            from student_handbook_rag import HandbookRAG

            key, base_url = load_local_credentials(rag_directory())
            self._client = HandbookRAG(
                reference_directory(), api_key=key, base_url=base_url, save_records=False
            )
        # 不传历史、不覆盖 crag/reflection/allow_web 等原项目默认参数。
        return self._client.ask(question)

    async def ask(self, question: str) -> dict:
        return await self.pool.run(lambda: self.query(question))
