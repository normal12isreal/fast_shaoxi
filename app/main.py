"""应用入口；Uvicorn 通过 app.main:app 找到下面的 app 对象。"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.db.core import Database
from app.pages.routes import router as page_router
from app.services.rag import RAGService

APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(application: FastAPI):
    # 生命周期只管理实际资源；不引入配置工厂。原 RAG 首次提问时才加载。
    application.state.db = Database()
    application.state.db.migrate()
    application.state.db.recover_interrupted()
    application.state.rag = RAGService()
    try:
        yield
    finally:
        application.state.rag.pool.close()
        application.state.db.close()


app = FastAPI(lifespan=lifespan)


# API 注册：api/router.py → 各主题 JSON 路由。
app.include_router(api_router)
# 页面注册：pages/routes.py → 首页、安装教程、账号页面。
app.include_router(page_router)
# /static/images/user.svg → app/static/images/user.svg；同样适用于 CSS 和 JS。
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
