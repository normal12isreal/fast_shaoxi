from fastapi import APIRouter

from app.api.routes import examples, health

api_router = APIRouter()
api_router.include_router(health.router)
# main.py 注册 api_router 后，POST /examples/echo 就会交给 examples.echo()。
api_router.include_router(examples.router)
