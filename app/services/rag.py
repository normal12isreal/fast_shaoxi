"""网站问答 → 原项目公共 Python 接口；不复写检索算法。"""

import sys

from app.services.execution import ExecutionPool
from app.services.knowledge import rag_directory


def import_rag() -> None:
    root = rag_directory()
    if not (root / "student_handbook_rag" / "__init__.py").is_file():
        raise ValueError("RAG 项目尚未配置")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


class RAGService:
    def __init__(self):
        self.pool = ExecutionPool()
        self._client = None

    def query(self, question: str) -> dict:
        if self._client is None:
            import_rag()
            from scripts.embed_chunks import load_local_credentials
            from student_handbook_rag import HandbookRAG

            key, base_url = load_local_credentials(rag_directory())
            self._client = HandbookRAG(
                rag_directory(), api_key=key, base_url=base_url, save_records=False
            )
        # 不传历史、不覆盖 crag/reflection/allow_web 等原项目默认参数。
        return self._client.ask(question)

    async def ask(self, question: str) -> dict:
        return await self.pool.run(lambda: self.query(question))
