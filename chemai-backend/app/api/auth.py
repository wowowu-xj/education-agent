# -*- coding: utf-8 -*-
"""认证 API：登录与刷新端点。

登录鉴权 Account（教师/学生共用）后签发 access + refresh token；
刷新端点用 refresh token 换新 access token。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import verify_password
from app.models import Account

router = APIRouter(tags=["认证"], prefix="/api/auth")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """登录请求体（用户名 + 明文密码）。"""

    username: str
    password: str


class UserBrief(BaseModel):
    """登录响应中的用户摘要。"""

    id: int
    role: str


class LoginResponse(BaseModel):
    """登录成功响应：双 token + 用户摘要。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief


class RefreshRequest(BaseModel):
    """刷新请求体。"""

    refresh_token: str


class RefreshResponse(BaseModel):
    """刷新成功响应。"""

    access_token: str
    token_type: str = "bearer"


def _resolve_school_id(account: Account) -> int | None:
    """从账号的角色归属解析 school_id，写入 token payload。

    教师经 ``account.teacher.school_id``；学生链路（Class→Grade→School）
    本期不覆盖，返回 None。学生端登录落地时在此扩展。
    """
    teacher = account.teacher
    return teacher.school_id if teacher is not None else None


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse, summary="登录")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """账号登录，签发 access（24h）与 refresh（7d）token。

    账号不存在、密码错误、已软删均返回同形 401，避免用户枚举。
    """
    account = db.execute(
        select(Account).where(
            Account.username == payload.username,
            Account.deleted_at.is_(None),
        )
    ).scalar_one_or_none()

    if account is None or not verify_password(payload.password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "message": "用户名或密码错误"},
        )

    school_id = _resolve_school_id(account)
    return LoginResponse(
        access_token=create_access_token(account.id, account.role, school_id),
        refresh_token=create_refresh_token(account.id, account.role, school_id),
        user=UserBrief(id=account.id, role=account.role),
    )


@router.post("/refresh", response_model=RefreshResponse, summary="刷新 token")
def refresh(payload: RefreshRequest) -> RefreshResponse:
    """用 refresh token 换新 access token。

    仅接受 ``type="refresh"`` 的 token；access token 冒充、无效或过期均 401。
    """
    try:
        data = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token", "message": "凭证无效或已过期"},
        )

    if data.get("type") != "refresh" or not data.get("user_id") or not data.get("role"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token", "message": "凭证无效或已过期"},
        )

    return RefreshResponse(
        access_token=create_access_token(
            data["user_id"], data["role"], data.get("school_id")
        ),
        token_type="bearer",
    )
