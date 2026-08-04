# -*- coding: utf-8 -*-
"""
SQLAlchemy Base 基类和通用 Mixin
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, MetaData, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

# 约束命名规范。两个理由：
# 1. Alembic 在 SQLite 上以 batch 模式重建表，删除约束时必须能按名字引用；
#    匿名约束会让迁移在 "constraint must have a name" 上失败。
# 2. 约束名可预测，测试能直接断言是哪条约束被违反。
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# 跨方言的主键/外键类型。
# MySQL / PostgreSQL 使用 BIGINT；SQLite 降级为 INTEGER。
# 原因：SQLite 只把 "INTEGER PRIMARY KEY" 视为 rowid 别名并自增，
# BIGINT PRIMARY KEY 不会自增，插入时报 NOT NULL constraint failed。
BigIntType = BigInteger().with_variant(Integer, "sqlite")


def utcnow() -> datetime:
    """当前 UTC 时间（带时区）。所有时间字段的 Python 侧默认值。"""
    return datetime.now(tz=timezone.utc)


class UTCDateTime(TypeDecorator[datetime]):
    """始终以 UTC 存取的 DateTime。

    存在的必要性：SQLite 不保存时区，写入带时区的时间、读回来是 naive
    datetime，再与一个 aware datetime 相减会直接抛 TypeError。
    MySQL 的 DATETIME 同样不带时区，行为一致。

    本类型在两个方向做归一：
    - 写入：aware 时间换算到 UTC；naive 时间**视为**已经是 UTC。
    - 读出：naive 时间补上 UTC 时区，保证下游拿到的一定是 aware datetime。

    注意「naive 视为 UTC」这个约定——不要把本地时间直接塞进这些字段，
    用 :func:`utcnow` 或显式带时区的时间。
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: Optional[datetime], dialect: Dialect
    ) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(
        self, value: Optional[datetime], dialect: Dialect
    ) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def enum_type(enum_cls: type[Enum], *, length: int = 32) -> SQLEnum:
    """把 Python 枚举映射成带 CHECK 约束的 VARCHAR 列。

    两个关键字参数都不能省：

    - ``values_callable``：SQLAlchemy 默认存枚举**成员名**（``ACADEMIC_ADMIN``），
      而决策 #3/#4 约定库内取值是**成员值**（``academic_admin``）。不传它，
      库里存的就是大写名，与 API 契约、前端约定全部错开。
    - ``create_constraint=True``：``native_enum=False`` 在 SQLAlchemy 1.4+
      默认**不生成** CHECK 约束，列会退化成任意 VARCHAR，
      ``'超级黑客'`` 这种值也能写进去。
    """
    return SQLEnum(
        enum_cls,
        native_enum=False,
        length=length,
        create_constraint=True,
        values_callable=lambda e: [member.value for member in e],
    )


class Base(DeclarativeBase):
    """所有模型的基类"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # 通用主键（所有表自动拥有）
    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)


class TimestampMixin:
    """时间戳字段 Mixin（所有表自动拥有）

    同时给 Python 侧默认值和 ``server_default``：
    - Python 侧（``default`` / ``onupdate``）保证 ORM 写入的一定是 UTC，
      不受数据库会话时区影响（MySQL 的 ``NOW()`` 跟会话时区绑定）。
    - ``server_default`` 兜底裸 SQL、数据修复脚本等绕过 ORM 的写入。
    """

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utcnow,
        server_default=func.now(),
        nullable=False,
        comment="创建时间（UTC）",
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
        comment="更新时间（UTC）",
    )


class SoftDeleteMixin:
    """软删除 Mixin（关键业务表使用）

    已知限制一：查询**不会**自动过滤已删除行。数据访问层必须显式加
    ``.where(Model.deleted_at.is_(None))``。Phase 3 引入 repository 层后
    在那里统一收口。

    已知限制二：软删除与唯一约束共存时，被软删的行仍占用唯一键——
    软删 ``username='zhang'`` 之后无法再建同名账号。彻底解法是部分唯一索引
    （``WHERE deleted_at IS NULL``），但生产库是 MySQL，不支持该特性。
    等真出现「删除后重建同名」的需求，再改成唯一键带 ``deleted_at``
    或改为物理删除 + 归档表。
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime,
        default=None,
        nullable=True,
        comment="软删除时间（NULL 表示未删除）",
    )

    @property
    def is_deleted(self) -> bool:
        """是否已被软删除。"""
        return self.deleted_at is not None

    def soft_delete(self, *, at: Optional[datetime] = None) -> None:
        """标记为已删除。重复调用不覆盖首次删除时间。"""
        if self.deleted_at is None:
            self.deleted_at = at or utcnow()


__all__ = [
    "NAMING_CONVENTION",
    "Base",
    "BigIntType",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UTCDateTime",
    "enum_type",
    "utcnow",
]
