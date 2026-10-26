"""应用装配入口；Uvicorn 通过 app.main:app 找到最下方的 app 对象。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import Settings
from app.pages.routes import router as page_router

APP_DIR = Path(__file__).resolve().parent


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create independent app instances for serving and tests."""
    settings = settings if settings is not None else Settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="A small project for learning HTTP APIs step by step.",
    )
    # 装配时保存配置 → pages/routes.py 从 request.app.state.settings 读取网站名称。
    application.state.settings = settings

    @application.get("/", tags=["application"])
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "environment": settings.environment,
            "docs": "/docs",
        }

    # 注册阶段：API 汇总入口 → api/router.py → api/routes/examples.py 的 echo()。
    application.include_router(api_router)
    # 注册阶段：页面入口 → pages/routes.py；模板页、直接 HTML、下载各有自己的函数。
    application.include_router(page_router)
    # URL /static/<相对路径> → app/static/<相对路径>，不需要为每个文件写路由。
    # 例如 /static/images/user.svg → app/static/images/user.svg。
    # 只公开专用 static 目录，项目配置、源代码和下载资源不挂载到这里。
    application.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    return application


app = create_app()
