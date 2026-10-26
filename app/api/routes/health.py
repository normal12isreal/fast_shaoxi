from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Report process liveness; database readiness is a future concern."""
    return {"status": "ok"}
