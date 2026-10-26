from pydantic import BaseModel, ConfigDict

from app.schemas.rag import AskResult


class RecordItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question: str
    status: str
    created_at: str


class RecordDetail(RecordItem):
    result: AskResult | None
    error: str | None


class RecordPage(BaseModel):
    items: list[RecordItem]
    total: int
    limit: int
    offset: int
