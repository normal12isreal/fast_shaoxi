"""Compose the application; run with uvicorn app.main:app."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create independent app instances for serving and tests."""
    settings = settings if settings is not None else Settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="A small project for learning HTTP APIs step by step.",
    )

    @application.get("/", tags=["application"])
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "environment": settings.environment,
            "docs": "/docs",
        }

    application.include_router(api_router)
    return application


app = create_app()
