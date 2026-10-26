"""问答记录的短事务；匿名请求完全不创建记录。"""

from uuid import uuid4

from app.db.models import RAGRecord


def begin_record(database, user, question: str) -> str | None:
    if user is None:
        return None
    record_id = uuid4().hex
    with database.sessions.begin() as session:
        session.add(
            RAGRecord(id=record_id, user_id=user.id, question=question, status="processing")
        )
    return record_id


def finish_record(database, record_id: str | None, *, result=None, status="failed", error=None):
    if record_id is None:
        return
    with database.sessions.begin() as session:
        record = session.get(RAGRecord, record_id)
        if record:
            record.status = result.status if result else status
            record.result = result.model_dump() if result else None
            record.error = error
