"""账号会话与同源校验；Cookie 是随机令牌，数据库只保存其哈希。"""

import hashlib
import time
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request
from pwdlib import PasswordHash
from sqlalchemy import select

from app.db.models import LoginSession, User
from app.schemas.auth import UserInfo

COOKIE = "handbook_session"
SESSION_SECONDS = 7 * 24 * 60 * 60
passwords = PasswordHash.recommended()
# 无账号时也验证一次哈希，减少用户名存在与否的时间差。
_dummy_hash = passwords.hash("not-a-real-user-password")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def same_origin(request: Request) -> None:
    """浏览器 Cookie 写操作校验 Origin；带会话的脚本调用也应提供 Origin。"""
    origin = request.headers.get("origin")
    if origin is None and COOKIE in request.cookies:
        referer = request.headers.get("referer")
        if not referer:
            raise HTTPException(403, "携带登录 Cookie 的写请求需要同源 Origin。")
        try:
            parts = urlsplit(referer)
        except ValueError:
            raise HTTPException(403, "无效的来源地址。") from None
        origin = f"{parts.scheme}://{parts.netloc}"
    if origin is not None and origin != f"{request.url.scheme}://{request.url.netloc}":
        raise HTTPException(403, "不接受跨站写请求。")


def optional_user(request: Request) -> UserInfo | None:
    token = request.cookies.get(COOKIE)
    if not token or len(token) > 256:
        return None
    with request.app.state.db.sessions() as session:
        user = session.scalar(
            select(User)
            .join(LoginSession)
            .where(
                LoginSession.token_hash == token_hash(token),
                LoginSession.expires_at > int(time.time()),
            )
        )
        return UserInfo.model_validate(user) if user else None


def require_user(request: Request) -> UserInfo:
    user = optional_user(request)
    if user is None:
        raise HTTPException(401, "请先登录。")
    return user


CurrentUser = Annotated[UserInfo, Depends(require_user)]
MaybeUser = Annotated[UserInfo | None, Depends(optional_user)]
