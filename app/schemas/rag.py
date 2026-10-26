"""公开 HTTP 契约；只输出允许公开的字段，不暴露内部路径和模型配置。"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class AskRequest(BaseModel):
    question: Question = Field(examples=["申请国家奖学金需要满足哪些条件？"])


class WebSource(BaseModel):
    title: str
    url: Annotated[str, StringConstraints(pattern=r"^https?://")]


class Source(BaseModel):
    label: str
    text: str = ""
    pdf_pages: list[int] = Field(default_factory=list)
    kind: str = "handbook"
    web_sources: list[WebSource] = Field(default_factory=list)


class AskResult(BaseModel):
    request_id: str
    question: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
    status: str = Field(
        description="answered、needs_clarification、abstained、incomplete、"
        "unverified 或 partial_answer；证据不足也是正常结果。"
    )
    complete: bool = Field(
        description="是否完整生成；不代表证据一定充分，请结合 status 和引用核对。"
    )
    elapsed_seconds: float
    warnings: list[str] = Field(default_factory=list)
