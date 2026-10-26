"""读取顺序：main.py 注册本 router → URL 选中下方函数 → 返回相应响应。"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.knowledge import page_knowledge

APP_DIR = Path(__file__).resolve().parents[1]
# 这里只指定模板目录；创建 Templates 对象时不会把 HTML 发给浏览器。
templates = Jinja2Templates(directory=APP_DIR / "templates")
router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    # GET / → 原 RAG README → index.html；提问通过独立的 JSON API 发送。
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=page_knowledge(),
    )


@router.get("/guide", response_class=HTMLResponse)
def guide(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="guide.html", context=page_knowledge())


@router.get("/login", response_class=HTMLResponse)
@router.get("/register", response_class=HTMLResponse)
def authentication(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"register": request.url.path == "/register"},
    )


@router.get("/account", response_class=HTMLResponse)
def account(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="account.html")
