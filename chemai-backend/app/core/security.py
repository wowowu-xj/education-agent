# -*- coding: utf-8 -*-
"""密码哈希工具。

只负责密码的哈希与校验（passlib bcrypt）。

JWT 的签发与解码统一放在 :mod:`app.core.jwt`，此处不再重复实现，
避免出现两套 payload 结构和两套配置项名称。
"""
from __future__ import annotations

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对明文密码做 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否匹配已存储的哈希。"""
    return pwd_context.verify(plain_password, hashed_password)


__all__ = ["hash_password", "verify_password", "pwd_context"]
