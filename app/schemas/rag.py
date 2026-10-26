"""公开 HTTP 契约；只输出允许公开的字段，不暴露内部路径和模型配置。"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class AskRequest(BaseModel):
    question: Question


class Source(BaseModel):
    label: str
    text: str = ""
    pdf_pages: list[int] = Field(default_factory=list)
    kind: str = "handbook"


class AskResult(BaseModel):
    request_id: str
    question: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
    status: str
    complete: bool
    elapsed_seconds: float
    warnings: list[str] = Field(default_factory=list)
