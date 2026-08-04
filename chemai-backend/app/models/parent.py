"""Parent 模型：家长（独立认证）。

设计要点：
- 不使用 Account 表，直接存 password_hash
- 通过 StudentParentBinding 与学生多对多关联
- /api/parent/login 直接查此表
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntType, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.student_parent_binding import StudentParentBinding


class Parent(Base, TimestampMixin, SoftDeleteMixin):
    """家长（独立认证通道）。

    带 ``SoftDeleteMixin``：家长是独立登录主体，与 Teacher / Student 同级，
    删除后必须保留审计痕迹（谁在什么时候查看过哪个孩子的学情）。
    之前漏掉软删除，导致"注销家长账号"只能物理删除、连带丢失绑定历史。
    """

    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)

    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    # 绑定关系脱离家长没有意义：删家长即删绑定。
    # FK 已是 ON DELETE CASCADE，passive_deletes 让数据库直接删，
    # 避免 ORM 先把子行加载进内存再逐条 DELETE。
    student_bindings: Mapped[list["StudentParentBinding"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Parent id={self.id} name={self.name!r} phone={self.phone}>"
