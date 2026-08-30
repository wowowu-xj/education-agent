# -*- coding: utf-8 -*-
"""FastAPI 应用入口。

Phase 2 只挂载 JWT 认证中间件和健康检查，业务路由在后续阶段接入。
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.classes import router as classes_router
from app.api.exams import router as exams_router
from app.api.papers import router as papers_router
from app.api.question_sets import router as question_sets_router
from app.api.questions import router as questions_router
from app.core.config import settings
from app.middleware.auth import (
    DOCS_WHITELIST,
    WHITELIST_EXACT,
    WHITELIST_PREFIXES,
    JWTAuthMiddleware,
)

# 前端静态资源目录（Vue 3 CDN 单页，无构建步骤）
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# 静态资源前缀白名单：页面与静态资产无需认证即可加载，业务接口仍强制 JWT。
#   /pages/ 教师端单页（如出题工作台）
#   /css/   本地样式
#   /js/    本地脚本
#   /m/     移动端页面（学生端 / 家长端）
STATIC_WHITELIST_PREFIXES: tuple[str, ...] = ("/pages/", "/css/", "/js/", "/m/")

# 审核接口前缀白名单（临时）：化学方程式安全审核是纯算法、非敏感业务数据，
# 出题工作台在登录端点（Phase 3）落地前无法携带 JWT，故临时放行。
# Phase 3 登录落地后应收回收紧，改由前端携带 access token 调用。
AUDIT_WHITELIST_PREFIXES: tuple[str, ...] = ("/api/audit/",)


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。

    用工厂函数而非模块级单例，便于测试中构造互相隔离的应用。
    """
    # 生产环境不暴露 API 文档：/docs /redoc /openapi.json 全部关闭。
    # 文档会完整列出所有接口、参数结构和枚举取值，是攻击面侦察的现成清单。
    expose_docs = not settings.is_production

    app = FastAPI(
        title=settings.APP_NAME,
        description="智辅化学——AI 驱动的化学教学辅助平台",
        version="0.2.0",
        debug=settings.DEBUG,
        docs_url="/docs" if expose_docs else None,
        redoc_url="/redoc" if expose_docs else None,
        openapi_url="/openapi.json" if expose_docs else None,
    )

    # 中间件注册顺序即「洋葱」由内向外：后注册的更靠外、先执行。
    # 这里先注册 JWT、后注册 CORS，因此实际顺序是 CORS -> JWT -> 路由，
    # 保证跨域响应头在 401 上也能带上，浏览器才能读到错误内容。
    #
    # JWT 认证：三层权限架构的第一层。
    # 文档路径只在暴露文档时并入白名单——生产环境既关闭了路由，
    # 也不在白名单里，避免「关了文档但白名单还留着口子」的漂移。
    app.add_middleware(
        JWTAuthMiddleware,
        exact_whitelist=WHITELIST_EXACT | DOCS_WHITELIST if expose_docs else WHITELIST_EXACT,
        prefix_whitelist=WHITELIST_PREFIXES + STATIC_WHITELIST_PREFIXES + AUDIT_WHITELIST_PREFIXES,
    )

    cors_origins = settings.cors_origins_list
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/health", tags=["系统"], summary="健康检查")
    async def health() -> dict[str, str]:
        """免认证的存活探针。"""
        return {"status": "ok", "app": settings.APP_NAME}

    # 注册业务路由
    app.include_router(auth_router)
    app.include_router(audit_router)
    app.include_router(classes_router)
    app.include_router(questions_router)
    app.include_router(question_sets_router)
    app.include_router(papers_router)
    app.include_router(exams_router)

    # 静态资源挂载：挂载在根路径末尾，仅在无匹配路由时命中前端静态文件。
    # /pages/* /css/* /js/* /m/* 已在中间件白名单中免认证。
    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    return app


app = create_app()
