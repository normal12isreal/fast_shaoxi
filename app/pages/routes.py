"""读取顺序：main.py 注册本 router → URL 选中下方函数 → 返回相应响应。"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).resolve().parents[1]
# 这里只指定模板目录；创建 Templates 对象时不会把 HTML 发给浏览器。
templates = Jinja2Templates(directory=APP_DIR / "templates")
router = APIRouter(prefix="/demo", tags=["response demos"])


@router.get("", response_class=HTMLResponse)
def demo_page(request: Request) -> HTMLResponse:
    # GET /demo → 本函数 → templates/index.html；context 是 Python 传给模板的数据。
    # Jinja2 将 {{ app_name }} 等表达式填成实际文本，浏览器收到的是渲染后的 HTML。
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": request.app.state.settings.app_name},
    )


@router.get("/html", response_class=HTMLResponse)
def plain_html() -> HTMLResponse:
    # GET /demo/html → 本函数 → 直接返回 HTML 字符串，不读取任何模板文件。
    # HTMLResponse 设置 text/html；若普通返回一个 str，默认会成为 JSON 字符串。
    return HTMLResponse(
        "<!doctype html><html lang='zh-CN'><meta charset='utf-8'>"
        "<title>直接 HTML 响应</title><h1>这是 HTMLResponse</h1>"
        "<p>这段 HTML 来自 app/pages/routes.py 的 plain_html()，没有经过模板。</p>"
        "<p><a href='/demo'>返回演示页</a></p></html>"
    )


@router.get("/download", response_class=FileResponse)
def download_map() -> FileResponse:
    # GET /demo/download → 本函数 → 读取 app/resources/request-map.txt。
    # filename 让响应成为带文件名的附件；文件路径固定，不接受任意磁盘路径输入。
    return FileResponse(
        path=APP_DIR / "resources" / "request-map.txt",
        media_type="text/plain; charset=utf-8",
        filename="request-map.txt",
    )
