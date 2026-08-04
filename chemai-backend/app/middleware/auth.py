# -*- coding: utf-8 -*-
"""JWT 认证中间件。

依据决策 #6（最小化白名单）与文档 23（JWT 认证）：

- 除白名单外，所有请求必须携带 ``Authorization: Bearer <token>``
- 只接受 access token；refresh token 不能直接访问业务接口
- 校验通过后把身份信息写入 ``scope["state"]``，下游可通过
  ``request.state.user_id`` / ``role`` / ``school_id`` 读取

白名单遵循最小化原则，只放通「拿不到 token 时必须能访问」的入口：

- ``/api/auth/*``       —— 教师/学生登录、注册、刷新 token
- ``/api/parent/login`` —— 家长独立认证通道（家长不走 Account 表）
- ``/health``           —— 健康检查

API 文档路径（``/docs`` ``/redoc`` ``/openapi.json``）**不在**默认白名单里，
由 :func:`app.main.create_app` 按环境决定是否并入——生产环境不暴露文档。

注意：``/api/parent/`` 下除 login 之外的接口**不在**白名单内，
``/api/agent/*`` 也需要认证，与设计文档中「12 个前缀全放通」的早期草稿不同。

实现方式：**纯 ASGI 中间件**，而非 ``BaseHTTPMiddleware``。
原因是 ``BaseHTTPMiddleware`` 会把响应体经由内部队列转发，
使 SSE / StreamingResponse 失去逐块下发的特性（Phase 3 的
``/api/agent/chat/stream`` 依赖流式输出）。纯 ASGI 实现只在请求进入时
做校验，之后把 ``send`` 原样交给下游，响应体零介入。
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.jwt import ACCESS_TOKEN_TYPE, JWTError, decode_token

# 精确匹配的白名单路径（最小集，不含文档）
WHITELIST_EXACT: frozenset[str] = frozenset(
    {
        "/health",
        "/api/parent/login",
    }
)

# 前缀匹配的白名单（必须带结尾斜杠，避免 /api/authxxx 这类绕过）
WHITELIST_PREFIXES: tuple[str, ...] = ("/api/auth/",)

# API 文档路径。仅在非生产环境由 create_app 并入白名单。
DOCS_WHITELIST: frozenset[str] = frozenset(
    {
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/openapi.json",
    }
)


def _unauthorized_messages(detail: str, code: str) -> tuple[Message, Message]:
    """构造统一 401 响应的两条 ASGI 消息。"""
    body = json.dumps({"detail": detail, "code": code}, ensure_ascii=False).encode()
    start: Message = {
        "type": "http.response.start",
        "status": HTTP_401_UNAUTHORIZED,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            (b"www-authenticate", b"Bearer"),
        ],
    }
    return start, {"type": "http.response.body", "body": body}


class JWTAuthMiddleware:
    """全局 JWT 认证中间件（纯 ASGI）。

    三层权限架构的第一层：只负责「你是谁」，不负责「你能干什么」。
    角色校验和数据范围过滤由后续的依赖项完成。
    """

    def __init__(
        self,
        app: ASGIApp,
        exact_whitelist: Iterable[str] | None = None,
        prefix_whitelist: Iterable[str] | None = None,
    ) -> None:
        self.app = app
        self.exact_whitelist = (
            frozenset(exact_whitelist) if exact_whitelist is not None else WHITELIST_EXACT
        )
        self.prefix_whitelist = (
            tuple(prefix_whitelist) if prefix_whitelist is not None else WHITELIST_PREFIXES
        )

    def is_whitelisted(self, path: str) -> bool:
        """判断路径是否免认证。"""
        if path in self.exact_whitelist:
            return True
        return any(path.startswith(prefix) for prefix in self.prefix_whitelist)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 只拦截 HTTP 请求。lifespan 直接放过；
        # websocket 目前没有路由，将来接入时需要在此补上握手期认证。
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        rejection = self._authenticate(scope)
        if rejection is not None:
            start, body = rejection
            await send(start)
            await send(body)
            return

        await self.app(scope, receive, send)

    # ---------- 内部：认证逻辑 ----------

    def _authenticate(self, scope: Scope) -> tuple[Message, Message] | None:
        """校验请求身份。

        通过则把身份写入 ``scope["state"]`` 并返回 ``None``；
        失败则返回待发送的 401 消息对。
        """
        # CORS 预检请求不带 Authorization 头，直接放过。
        # 预检的实际响应由 CORSMiddleware 生成（见 app/main.py）。
        if scope.get("method") == "OPTIONS":
            return None

        if self.is_whitelisted(scope["path"]):
            return None

        auth_header = _get_header(scope, b"authorization")
        if not auth_header:
            return _unauthorized_messages("缺少认证凭证", "missing_token")

        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return _unauthorized_messages("认证方案无效，需使用 Bearer", "invalid_scheme")

        try:
            payload = decode_token(token.strip())
        except JWTError:
            # 签名错误、格式错误、已过期都归到这里，不向外泄露具体原因
            return _unauthorized_messages("凭证无效或已过期", "invalid_token")

        if payload.get("type") != ACCESS_TOKEN_TYPE:
            return _unauthorized_messages("需使用 access token", "wrong_token_type")

        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or not role:
            return _unauthorized_messages("凭证内容不完整", "malformed_payload")

        # 挂载身份信息，供下游权限校验与数据范围过滤使用。
        # scope["state"] 会被 Starlette 的 request.state 按引用包装。
        state: dict[str, Any] = scope.setdefault("state", {})
        state["user_id"] = user_id
        state["role"] = role
        state["school_id"] = payload.get("school_id")
        state["token_payload"] = payload
        return None


def _get_header(scope: Scope, name: bytes) -> str | None:
    """从 ASGI scope 中取出单个请求头（大小写不敏感）。"""
    for key, value in scope.get("headers", ()):
        if key.lower() == name:
            return value.decode("latin-1")
    return None


__all__ = [
    "JWTAuthMiddleware",
    "WHITELIST_EXACT",
    "WHITELIST_PREFIXES",
    "DOCS_WHITELIST",
]
