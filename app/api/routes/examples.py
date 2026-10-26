from fastapi import APIRouter

from app.schemas.examples import EchoRequest, EchoResponse

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    """Observe validated JSON input and a typed JSON response."""
    # static/app.js 的 fetch → 本函数；EchoRequest 先校验 JSON，失败自动返回 422。
    # 返回 EchoResponse → FastAPI 序列化为 JSON → app.js 更新页面中的结果区域。
    return EchoResponse(message=payload.message, length=len(payload.message))
