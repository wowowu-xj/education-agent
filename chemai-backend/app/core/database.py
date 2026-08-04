# -*- coding: utf-8 -*-
"""数据库引擎与会话管理。

- 开发环境使用 SQLite，生产环境切 MySQL（改 DATABASE_URL 即可）
- SQLite 需要 check_same_thread=False，否则 FastAPI 多线程访问会报错
- SQLite 默认不强制外键，需通过 PRAGMA 显式开启
"""

from __future__ import annotations

from typing import Any, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# SQLite 单文件库需要放开线程检查；MySQL 不需要
_connect_args: dict[str, Any] = {"check_same_thread": False} if _is_sqlite else {}

engine: Engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)


if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
        """SQLite 默认关闭外键约束，每条连接建立时开启。"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖项：提供请求级数据库会话。

    用法::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "get_db"]
