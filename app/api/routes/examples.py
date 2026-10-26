from fastapi import APIRouter

from app.schemas.examples import EchoRequest, EchoResponse

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    """Observe validated JSON input and a typed JSON response."""
    return EchoResponse(message=payload.message, length=len(payload.message))
