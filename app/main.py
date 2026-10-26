"""应用入口；Uvicorn 通过 app.main:app 找到下面的 app 对象。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.pages.routes import router as page_router

APP_DIR = Path(__file__).resolve().parent
app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    # GET / → 本函数 → 返回 JSON；这些地址是提示文字，不会自动跳转。
    return {"message": "你好，FastAPI", "demo": "/demo", "docs": "/docs"}


# API 注册：api/router.py → api/routes/examples.py 的 echo() 等函数。
app.include_router(api_router)
# 页面注册：pages/routes.py → 模板、直接 HTML、文件下载三个示例。
app.include_router(page_router)
# /static/images/user.svg → app/static/images/user.svg；同样适用于 CSS 和 JS。
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
