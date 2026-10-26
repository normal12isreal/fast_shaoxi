from fastapi import APIRouter

from app.api.routes import auth, health, rag

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(rag.router)
api_router.include_router(auth.router)
