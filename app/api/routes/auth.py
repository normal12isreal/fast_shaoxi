import os
import secrets
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.db.models import LoginSession, User
from app.schemas.auth import Credentials, UserInfo
from app.services.auth import (
    COOKIE,
    SESSION_SECONDS,
    CurrentUser,
    _dummy_hash,
    passwords,
    same_origin,
    token_hash,
)

router = APIRouter(prefix="/api/auth", tags=["账号"])


@router.post(
    "/register", response_model=UserInfo, status_code=201, dependencies=[Depends(same_origin)]
)
def register(body: Credentials, request: Request):
    # 密码只以 Argon2 哈希入库；用户名统一小写，避免大小写重复账号。
    hashed = passwords.hash(body.password)
    with request.app.state.db.sessions.begin() as session:
        user = User(username=body.username.lower(), password_hash=hashed)
        session.add(user)
        try:
            session.flush()
        except IntegrityError:
            raise HTTPException(409, "用户名已存在。") from None
        return UserInfo.model_validate(user)


@router.post("/login", response_model=UserInfo, dependencies=[Depends(same_origin)])
def login(body: Credentials, request: Request, response: Response):
    with request.app.state.db.sessions() as session:
        user = session.scalar(select(User).where(User.username == body.username.lower()))
        valid = passwords.verify(body.password, user.password_hash if user else _dummy_hash)
        if user is None or not valid:
            raise HTTPException(401, "用户名或密码不正确。")
        result = UserInfo.model_validate(user)
    token, now = secrets.token_urlsafe(32), int(time.time())
    with request.app.state.db.sessions.begin() as session:
        session.execute(delete(LoginSession).where(LoginSession.expires_at <= now))
        # 登录轮换当前浏览器会话，旧令牌不再可用。
        old = request.cookies.get(COOKIE)
        if old:
            session.execute(delete(LoginSession).where(LoginSession.token_hash == token_hash(old)))
        session.add(
            LoginSession(
                token_hash=token_hash(token), user_id=result.id, expires_at=now + SESSION_SECONDS
            )
        )
    response.set_cookie(
        COOKIE,
        token,
        max_age=SESSION_SECONDS,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    )
    response.headers["Cache-Control"] = "no-store"
    return result


@router.post("/logout", dependencies=[Depends(same_origin)])
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with request.app.state.db.sessions.begin() as session:
            session.execute(
                delete(LoginSession).where(LoginSession.token_hash == token_hash(token))
            )
    response.delete_cookie(COOKIE)
    return {"message": "已退出。"}


@router.get("/me", response_model=UserInfo)
def me(response: Response, user: CurrentUser):
    response.headers["Cache-Control"] = "no-store"
    return user
