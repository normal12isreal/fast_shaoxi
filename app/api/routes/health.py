from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """进程存活检查；不代表外部模型或数据库业务调用已经就绪。"""
    return {"status": "ok"}
