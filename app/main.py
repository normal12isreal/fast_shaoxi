"""应用入口；Uvicorn 通过 app.main:app 找到下面的 app 对象。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.pages.routes import router as page_router

APP_DIR = Path(__file__).resolve().parent
app = FastAPI()


# API 注册：api/router.py → 各主题 JSON 路由。
app.include_router(api_router)
# 页面注册：pages/routes.py → 首页、安装教程、账号页面。
app.include_router(page_router)
# /static/images/user.svg → app/static/images/user.svg；同样适用于 CSS 和 JS。
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
