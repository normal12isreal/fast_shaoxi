"""公开单次问答：网页和外部调用走同一个入口。"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select

from app.db.models import RAGRecord
from app.schemas.rag import AskRequest, AskResult
from app.schemas.records import RecordDetail, RecordItem, RecordPage
from app.services.auth import CurrentUser, MaybeUser, same_origin
from app.services.execution import BusyError
from app.services.records import begin_record, finish_record

router = APIRouter(prefix="/api/rag")


@router.post(
    "/ask",
    tags=["公开手册问答"],
    summary="公开单次手册问答",
    dependencies=[Depends(same_origin)],
    response_model=AskResult,
    responses={
        422: {"description": "问题须为 1–500 字符"},
        502: {"description": "RAG 或上游模型调用失败"},
        503: {"description": "RAG 忙碌；稍后重试"},
        504: {"description": "等待超过 180 秒"},
    },
)
async def ask(body: AskRequest, request: Request, user: MaybeUser) -> AskResult:
    """公开接口，无需登录或密钥。只发送 question，等待一次完整 JSON 响应。

    通常约 20 秒；调用端请设置 210 秒超时。不会自动重发整次问答。

    外部调用示例（不携带 Cookie）：
    ```bash
    curl --max-time 210 http://127.0.0.1:8000/api/rag/ask \
      -H 'Content-Type: application/json' \
      -d '{"question":"申请国家奖学金需要满足哪些条件？"}'
    ```
    """
    database = request.app.state.db
    record_id = begin_record(database, user, body.question)
    try:
        # /api/rag/ask → RAGService → 工作线程 → 原 HandbookRAG.ask()。
        raw = await request.app.state.rag.ask(body.question)
        result = AskResult.model_validate(raw)
        finish_record(database, record_id, result=result)
        return result
    except BusyError:
        finish_record(database, record_id, status="busy", error="服务忙碌，请稍后重试。")
        raise HTTPException(
            503, "问答服务正在处理其他问题，请稍后重试。", headers={"Retry-After": "5"}
        ) from None
    except TimeoutError:
        finish_record(database, record_id, status="timeout", error="等待超时。")
        raise HTTPException(504, "问答等待超时；后台调用可能仍在结束，请稍后重试。") from None
    except asyncio.CancelledError:
        finish_record(database, record_id, status="interrupted", error="请求已中断。")
        raise
    except Exception:
        finish_record(database, record_id, error="问答调用失败。")
        # 不把上游异常、密钥、本地路径直接返回给调用者。
        raise HTTPException(502, "问答暂未完成，请检查服务配置或稍后重试。") from None


@router.get("/records", response_model=RecordPage, tags=["个人记录"])
def records(
    request: Request,
    response: Response,
    user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    response.headers["Cache-Control"] = "no-store"
    with request.app.state.db.sessions() as session:
        owned = RAGRecord.user_id == user.id
        total = session.scalar(select(func.count()).select_from(RAGRecord).where(owned))
        rows = session.scalars(
            select(RAGRecord)
            .where(owned)
            .order_by(RAGRecord.created_at.desc(), RAGRecord.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return RecordPage(
            items=[RecordItem.model_validate(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )


@router.get("/records/{record_id}", response_model=RecordDetail, tags=["个人记录"])
def record(record_id: str, request: Request, response: Response, user: CurrentUser):
    response.headers["Cache-Control"] = "no-store"
    with request.app.state.db.sessions() as session:
        row = session.scalar(
            select(RAGRecord).where(RAGRecord.id == record_id, RAGRecord.user_id == user.id)
        )
        if row is None:
            raise HTTPException(404, "记录不存在。")
        return RecordDetail.model_validate(row)
