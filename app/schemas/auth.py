from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class Credentials(BaseModel):
    username: Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_]{3,32}$")]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
