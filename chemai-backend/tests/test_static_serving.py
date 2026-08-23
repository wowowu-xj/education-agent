# -*- coding: utf-8 -*-
"""静态资源托管与认证白名单的集成测试。

验证前端静态页面与化学方程式审核接口（临时白名单）免认证可访问，
同时其他业务接口的 JWT 认证不被放宽。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_static_page_served_without_auth() -> None:
    """前端静态页面应免认证可访问。"""
    resp = client.get("/pages/question-workbench.html")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_audit_equation_whitelisted_without_auth() -> None:
    """化学方程式审核接口在临时白名单内，应免认证可访问。"""
    resp = client.get("/api/audit/equation", params={"eq": "2H2 + O2 -> 2H2O"})
    assert resp.status_code == 200
    assert resp.json()["overall_status"] == "passed"


def test_other_api_still_requires_auth() -> None:
    """未放行的业务接口仍应要求认证（中间件在路由前拦截）。"""
    resp = client.get("/api/agent/chat/stream")
    assert resp.status_code == 401
