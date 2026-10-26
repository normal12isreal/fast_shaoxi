"""网页和安装助手共用同一份公开资料；不遍历项目或读取私有运行目录。"""

import os
from pathlib import Path
from urllib.parse import urljoin

from markdown_it import MarkdownIt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "https://github.com/normal12isreal/shaoxing_university_handbook_rag"
PUBLIC_FILES = ("README.md", "config/dashscope.example.json")


def rag_directory() -> Path:
    return Path(
        os.environ.get("RAG_PROJECT_DIR", PROJECT_ROOT.parent / "student-handbook-rag")
    ).resolve()


def public_sources() -> list[dict[str, str]]:
    sources = []
    for name in PUBLIC_FILES:
        path = rag_directory() / name
        if path.is_file():
            sources.append({"name": name, "text": path.read_text(encoding="utf-8")})
    supplement = PROJECT_ROOT / "knowledge" / "installation.md"
    sources.append({"name": "installation.md", "text": supplement.read_text(encoding="utf-8")})
    return sources


def render_markdown(text: str) -> str:
    # 禁止 Markdown 原始 HTML；相对链接指向原 GitHub，避免落到网站自己的未知路径。
    renderer = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = renderer.parse(text)

    def rewrite(items):
        for token in items:
            attribute = "href" if token.type == "link_open" else "src"
            value = token.attrGet(attribute)
            if value and not value.startswith(("https://", "http://", "#", "mailto:")):
                token.attrSet(attribute, urljoin(REPOSITORY + "/blob/main/", value))
            if token.children:
                rewrite(token.children)

    rewrite(tokens)
    return renderer.renderer.render(tokens, renderer.options, {})


def page_knowledge() -> dict:
    sources = public_sources()
    readme = next((source["text"] for source in sources if source["name"] == "README.md"), "")
    guide = (
        readme.split("## 项目实现", 1)[0]
        if readme
        else "原 RAG 目录未配置，请设置 RAG_PROJECT_DIR。"
    )
    return {
        "readme_html": render_markdown(readme or guide),
        "guide_html": render_markdown(guide),
        "supplement_html": render_markdown(sources[-1]["text"]),
        "sources": [source["name"] for source in sources],
        "repository": REPOSITORY,
    }
