# -*- coding: utf-8 -*-
"""JWT 工具函数测试。"""
from __future__ import annotations

import pytest

from app.core.jwt import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_access_token_payload_structure() -> None:
    """access token 携带完整身份信息。"""
    payload = decode_token(create_access_token(user_id=1, role="teacher", school_id=2))

    assert payload["user_id"] == 1
    assert payload["role"] == "teacher"
    assert payload["school_id"] == 2
    assert payload["type"] == ACCESS_TOKEN_TYPE
    assert payload["exp"] > payload["iat"]


def test_refresh_token_is_typed_differently() -> None:
    """refresh token 的 type 与 access 区分，且有效期更长。"""
    access = decode_token(create_access_token(user_id=1, role="teacher", school_id=2))
    refresh = decode_token(create_refresh_token(user_id=1, role="teacher", school_id=2))

    assert refresh["type"] == REFRESH_TOKEN_TYPE
    assert refresh["exp"] > access["exp"]


def test_school_id_defaults_to_none() -> None:
    """家长无学校归属，school_id 为 None。"""
    payload = decode_token(create_access_token(user_id=3, role="parent"))
    assert payload["school_id"] is None


def test_decode_rejects_tampered_token() -> None:
    """篡改后的 token 无法通过签名校验。"""
    token = create_access_token(user_id=1, role="teacher", school_id=1)
    header, body, signature = token.split(".")
    tampered = f"{header}.{body}x.{signature}"

    with pytest.raises(JWTError):
        decode_token(tampered)
