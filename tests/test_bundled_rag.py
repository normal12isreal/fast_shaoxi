"""本项目自带完整运行依赖；只加载、校验索引，不调用付费模型。"""

import hashlib
import json
from pathlib import Path

from app.services.knowledge import PROJECT_ROOT, rag_directory
from app.services.rag import import_rag


def test_bundled_assets_match_upstream_snapshot():
    root = PROJECT_ROOT / "rag"
    manifest = json.loads((root / "upstream.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        raw = (root / item["path"]).read_bytes()
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"], item["path"]


def test_default_rag_loads_local_code_and_existing_index(monkeypatch, tmp_path):
    monkeypatch.delenv("RAG_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    assert rag_directory() == PROJECT_ROOT / "rag"
    monkeypatch.setenv("RAG_PROJECT_DIR", "rag")
    assert rag_directory() == PROJECT_ROOT / "rag"
    import_rag()
    import student_handbook_rag

    assert Path(student_handbook_rag.__file__).is_relative_to(rag_directory())
    # 显式传入测试凭据，构造器只读取本地资料，不读取个人密钥或发网络请求。
    client = student_handbook_rag.HandbookRAG(
        rag_directory(),
        api_key="test-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        save_records=False,
    )
    assert client.chunks and len(client.chunks) == len(client.normalized)
    assert client.project_dir == PROJECT_ROOT / "rag"
