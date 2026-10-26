from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class NewMessage(BaseModel):
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=6000)]


class ConversationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationPage(BaseModel):
    items: list[ConversationItem]
    total: int
    limit: int
    offset: int


class MessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    status: str
    error: str | None
    created_at: str


class MessagePage(BaseModel):
    items: list[MessageItem]
    total: int
    limit: int
    offset: int
    busy: bool


class AssistantReply(BaseModel):
    user_message: MessageItem
    assistant_message: MessageItem
