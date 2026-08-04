# -*- coding: utf-8 -*-
"""JWT 认证中间件测试。

覆盖决策 #6（最小化白名单）的核心断言：
- 白名单内的入口免认证
- 其余路径（含 /api/parent/ 下的非 login 接口、/api/agent/*）一律要求 access token
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from app.core.config import settings
from app.core.jwt import create_access_token, create_refresh_token
from app.middleware.auth import JWTAuthMiddleware


@pytest.fixture()
def client() -> TestClient:
    """带认证中间件的测试应用。

    路由覆盖白名单内外两类路径，用于验证放通与拦截。
    """
    app = FastAPI()
    app.add_middleware(JWTAuthMiddleware)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/auth/login")
    async def teacher_login() -> dict[str, str]:
        return {"scope": "auth"}

    @app.post("/api/parent/login")
    async def parent_login() -> dict[str, str]:
        return {"scope": "parent-login"}

    @app.get("/api/parent/report")
    async def parent_report() -> dict[str, str]:
        return {"scope": "parent-report"}

    @app.get("/api/agent/chat/stream")
    async def agent_stream() -> dict[str, str]:
        return {"scope": "agent"}

    @app.get("/api/authxxx/bypass")
    async def prefix_bypass() -> dict[str, str]:
        return {"scope": "bypass"}

    @app.get("/api/protected")
    async def protected(request: Request) -> dict[str, object]:
        """回显中间件挂载到 request.state 的身份信息。"""
        return {
            "user_id": request.state.user_id,
            "role": request.state.role,
            "school_id": request.state.school_id,
        }

    return TestClient(app)


def _expired_access_token() -> str:
    """手工构造一个已过期的 access token。"""
    issued = datetime.now(tz=timezone.utc) - timedelta(hours=48)
    payload = {
        "user_id": 1,
        "role": "teacher",
        "school_id": 1,
        "type": "access",
        "iat": int(issued.timestamp()),
        "exp": int((issued + timedelta(hours=1)).timestamp()),
    }
    return jose_jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# ---------- 白名单放通 ----------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/health"),
        ("post", "/api/auth/login"),
        ("post", "/api/parent/login"),
    ],
)
def test_whitelisted_paths_need_no_token(
    client: TestClient, method: str, path: str
) -> None:
    """白名单内的入口在无 token 时也能访问。"""
    response = getattr(client, method)(path)
    assert response.status_code == 200


# ---------- 非白名单拦截 ----------


@pytest.mark.parametrize(
    "path",
    [
        "/api/protected",
        # 决策 #6：家长只有 login 免认证，其他家长接口需要 token
        "/api/parent/report",
        # 与设计文档早期草稿不同：agent 接口不在白名单
        "/api/agent/chat/stream",
        # 前缀白名单带结尾斜杠，/api/authxxx 不能绕过
        "/api/authxxx/bypass",
    ],
)
def test_protected_paths_reject_missing_token(client: TestClient, path: str) -> None:
    """非白名单路径缺少 token 时返回 401。"""
    response = client.get(path)
    assert response.status_code == 401
    assert response.json()["code"] == "missing_token"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_reject_non_bearer_scheme(client: TestClient) -> None:
    """非 Bearer 认证方案被拒绝。"""
    response = client.get(
        "/api/protected", headers={"Authorization": "Basic dXNlcjpwYXNz"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_scheme"


def test_reject_empty_bearer_token(client: TestClient) -> None:
    """Bearer 后没有 token 时被拒绝。"""
    response = client.get("/api/protected", headers={"Authorization": "Bearer   "})
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_scheme"


def test_reject_malformed_token(client: TestClient) -> None:
    """无法解析的 token 被拒绝。"""
    response = client.get(
        "/api/protected", headers={"Authorization": "Bearer not-a-real-jwt"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_reject_token_signed_with_wrong_secret(client: TestClient) -> None:
    """用错误密钥签发的 token 被拒绝。"""
    forged = jose_jwt.encode(
        {"user_id": 1, "role": "admin", "type": "access", "exp": 9999999999},
        "wrong-secret",
        algorithm=settings.JWT_ALGORITHM,
    )
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_reject_expired_token(client: TestClient) -> None:
    """过期 token 被拒绝。"""
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {_expired_access_token()}"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_reject_refresh_token_on_business_api(client: TestClient) -> None:
    """refresh token 不能直接访问业务接口。"""
    token = create_refresh_token(user_id=7, role="teacher", school_id=1)
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["code"] == "wrong_token_type"


def test_reject_payload_without_identity(client: TestClient) -> None:
    """payload 缺少 user_id/role 时被拒绝。"""
    token = jose_jwt.encode(
        {"type": "access", "exp": 9999999999},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["code"] == "malformed_payload"


# ---------- 校验通过 ----------


def test_valid_token_passes_and_attaches_identity(client: TestClient) -> None:
    """有效 access token 放行，并把身份挂到 request.state。"""
    token = create_access_token(user_id=42, role="teacher", school_id=9)
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"user_id": 42, "role": "teacher", "school_id": 9}


def test_parent_token_has_null_school_id(client: TestClient) -> None:
    """家长 token 不含学校归属，school_id 为 None。"""
    token = create_access_token(user_id=5, role="parent")
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"user_id": 5, "role": "parent", "school_id": None}


def test_bearer_scheme_is_case_insensitive(client: TestClient) -> None:
    """认证方案大小写不敏感。"""
    token = create_access_token(user_id=1, role="admin", school_id=1)
    response = client.get("/api/protected", headers={"Authorization": f"bearer {token}"})
    assert response.status_code == 200


def test_options_preflight_bypasses_auth(client: TestClient) -> None:
    """CORS 预检请求不带 token 也能通过中间件。

    断言要点：
    1. 状态码不是 401——中间件没有拦截。
    2. 响应头里没有 ``WWW-Authenticate``——这是中间件 401 响应专属的头，
       缺失说明响应来自 app 路由层（405/200），而不是中间件短路。
    3. 响应体里没有 ``code`` 字段——中间件错误响应固定携带 code；
       405/200 来自 Starlette 路由层，不含此字段。
    4. 同路径的 GET 请求（无 token）应当被 401 拦截——反向证明中间件仍在运行，
       OPTIONS 得到豁免不等于整个认证链被绕过。
    """
    options_resp = client.options("/api/protected")

    # 中间件不得拒绝预检
    assert options_resp.status_code != 401
    assert "www-authenticate" not in options_resp.headers  # 仅出现在中间件 401 响应里
    assert "code" not in options_resp.json()               # 仅出现在中间件错误体里

    # 同路径 GET 无 token → 401，证明中间件仍然工作（豁免只针对 OPTIONS）
    get_resp = client.get("/api/protected")
    assert get_resp.status_code == 401
    assert get_resp.json()["code"] == "missing_token"
