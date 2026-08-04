# -*- coding: utf-8 -*-
"""
JWT 编码/解码工具

依据决策 #10（passlib）和文档 23（JWT 认证）：
- 算法：HS256
- Access Token：24 小时
- Refresh Token：7 天
- Payload：user_id / role / school_id（家长为 None）/ type / iat / exp
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _build_payload(
    user_id: int,
    role: str,
    school_id: int | None,
    token_type: str,
    expires_in: timedelta,
) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    return {
        "user_id": user_id,
        "role": role,
        "school_id": school_id,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_in).timestamp()),
    }


def create_access_token(
    user_id: int, role: str, school_id: int | None = None
) -> str:
    """签发 access token（24 小时有效）。"""
    payload = _build_payload(
        user_id=user_id,
        role=role,
        school_id=school_id,
        token_type=ACCESS_TOKEN_TYPE,
        expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: int, role: str, school_id: int | None = None
) -> str:
    """签发 refresh token（7 天有效）。"""
    payload = _build_payload(
        user_id=user_id,
        role=role,
        school_id=school_id,
        token_type=REFRESH_TOKEN_TYPE,
        expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """解码并验证 JWT。

    Raises:
        JWTError: token 无效或过期。
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


__all__ = [
    "ACCESS_TOKEN_TYPE",
    "REFRESH_TOKEN_TYPE",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "JWTError",
]
