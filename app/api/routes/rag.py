"""公开单次问答：网页和外部调用走同一个入口。"""

from fastapi import APIRouter, HTTPException, Request

from app.schemas.rag import AskRequest, AskResult
from app.services.execution import BusyError

router = APIRouter(prefix="/api/rag", tags=["公开手册问答"])


@router.post(
    "/ask",
    response_model=AskResult,
    responses={
        422: {"description": "问题须为 1–500 字符"},
        502: {"description": "RAG 或上游模型调用失败"},
        503: {"description": "RAG 忙碌；稍后重试"},
        504: {"description": "等待超过 180 秒"},
    },
)
async def ask(body: AskRequest, request: Request) -> AskResult:
    """公开接口，无需登录或密钥。只发送 question，等待一次完整 JSON 响应。

    通常约 20 秒；调用端请设置 210 秒超时。不会自动重发整次问答。
    """
    try:
        # /api/rag/ask → RAGService → 工作线程 → 原 HandbookRAG.ask()。
        raw = await request.app.state.rag.ask(body.question)
        return AskResult.model_validate(raw)
    except BusyError:
        raise HTTPException(
            503, "问答服务正在处理其他问题，请稍后重试。", headers={"Retry-After": "5"}
        ) from None
    except TimeoutError:
        raise HTTPException(504, "问答等待超时；后台调用可能仍在结束，请稍后重试。") from None
    except Exception:
        # 不把上游异常、密钥、本地路径直接返回给调用者。
        raise HTTPException(502, "问答暂未完成，请检查服务配置或稍后重试。") from None
