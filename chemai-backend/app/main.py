# -*- coding: utf-8 -*-
"""FastAPI 应用入口。

Phase 2 只挂载 JWT 认证中间件和健康检查，业务路由在后续阶段接入。
"""
from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.auth import DOCS_WHITELIST, WHITELIST_EXACT, JWTAuthMiddleware


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

    return app


app = create_app()
