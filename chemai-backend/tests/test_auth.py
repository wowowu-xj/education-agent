# -*- coding: utf-8 -*-
"""认证 API 集成测试：登录与刷新端点。

经 TestClient 走完整链路：认证中间件 → 路由 → DB。
种子数据用独立会话（expire_on_commit=False + close），避免与请求会话争用
StaticPool 的单连接。
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.core.enums import ApprovalStatus, TeacherRole
from app.core.jwt import decode_token
from app.core.security import hash_password
from app.main import create_app
from app.models import Account, School, Teacher

INVALID_CREDENTIALS = {
    "error": "invalid_credentials",
    "message": "用户名或密码错误",
}
INVALID_TOKEN = {"error": "invalid_token", "message": "凭证无效或已过期"}


@pytest.fixture()
def client(engine: Engine) -> TestClient:
    """带测试引擎的 FastAPI 应用，get_db 每次请求给一个独立会话。"""
    app = create_app()
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def _seed_account(engine: Engine, username: str, password: str) -> int:
    """种一个带真实 bcrypt 密码的教师账号，返回其 account_id。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    school = School(name="测试中学", region="北京市")
    s.add(school)
    s.flush()
    teacher = Teacher(
        name="张老师",
        phone="13800000001",
        school_id=school.id,
        role=TeacherRole.TEACHER,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    s.add(teacher)
    s.flush()
    account = Account(
        username=username,
        password_hash=hash_password(password),
        teacher_id=teacher.id,
        role="teacher",
    )
    s.add(account)
    s.commit()
    account_id = account.id
    s.close()
    return account_id


def _soft_delete_account(engine: Engine, account_id: int) -> None:
    """软删指定账号。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    account = s.get(Account, account_id)
    account.soft_delete()
    s.commit()
    s.close()


# ---------------------------------------------------------------------------
# 登录端点
# ---------------------------------------------------------------------------


class TestLogin:
    def test_login_success_returns_tokens(
        self, client: TestClient, engine: Engine
    ) -> None:
        """正确凭据返回 200，签发双 token 与用户摘要。"""
        _seed_account(engine, "zhang", "Passw0rd!")

        resp = client.post(
            "/api/auth/login",
            json={"username": "zhang", "password": "Passw0rd!"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["token_type"] == "bearer"
        assert body["user"]["role"] == "teacher"
        assert body["access_token"]
        assert body["refresh_token"]

        access = decode_token(body["access_token"])
        assert access["type"] == "access"
        assert access["role"] == "teacher"
        assert "school_id" in access

    def test_login_wrong_password_401(
        self, client: TestClient, engine: Engine
    ) -> None:
        """密码错误返回 401，与用户名不存在同形。"""
        _seed_account(engine, "zhang", "Passw0rd!")

        resp = client.post(
            "/api/auth/login",
            json={"username": "zhang", "password": "wrong"},
        )

        assert resp.status_code == 401
        assert resp.json() == {"detail": INVALID_CREDENTIALS}

    def test_login_unknown_username_401(self, client: TestClient) -> None:
        """用户名不存在返回 401，响应体与密码错误完全一致（防枚举）。"""
        resp = client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "whatever"},
        )

        assert resp.status_code == 401
        assert resp.json() == {"detail": INVALID_CREDENTIALS}

    def test_login_soft_deleted_account_401(
        self, client: TestClient, engine: Engine
    ) -> None:
        """已软删账号登录返回 401。"""
        account_id = _seed_account(engine, "zhang", "Passw0rd!")
        _soft_delete_account(engine, account_id)

        resp = client.post(
            "/api/auth/login",
            json={"username": "zhang", "password": "Passw0rd!"},
        )

        assert resp.status_code == 401
        assert resp.json() == {"detail": INVALID_CREDENTIALS}


# ---------------------------------------------------------------------------
# 刷新端点
# ---------------------------------------------------------------------------


class TestRefresh:
    def test_refresh_success_returns_new_access_token(
        self, client: TestClient, engine: Engine
    ) -> None:
        """有效 refresh token 换新 access token，payload 保留身份。"""
        _seed_account(engine, "zhang", "Passw0rd!")
        login = client.post(
            "/api/auth/login",
            json={"username": "zhang", "password": "Passw0rd!"},
        ).json()

        resp = client.post(
            "/api/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["token_type"] == "bearer"

        access = decode_token(body["access_token"])
        assert access["type"] == "access"
        assert access["role"] == "teacher"

    def test_refresh_invalid_token_401(self, client: TestClient) -> None:
        """无效 refresh token 返回 401。"""
        resp = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "not-a-valid-jwt"},
        )

        assert resp.status_code == 401
        assert resp.json() == {"detail": INVALID_TOKEN}

    def test_refresh_rejects_access_token(
        self, client: TestClient, engine: Engine
    ) -> None:
        """用 access token 冒充 refresh token 返回 401。"""
        _seed_account(engine, "zhang", "Passw0rd!")
        login = client.post(
            "/api/auth/login",
            json={"username": "zhang", "password": "Passw0rd!"},
        ).json()

        resp = client.post(
            "/api/auth/refresh",
            json={"refresh_token": login["access_token"]},
        )

        assert resp.status_code == 401
        assert resp.json() == {"detail": INVALID_TOKEN}
