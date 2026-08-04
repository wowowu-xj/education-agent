"""Student 模型：学生。

设计要点：
- 归属班级（class_id）
- 6 位绑定码用于家长绑定
- 障碍画像（barrier_profile）用 JSON 存储三维分布
- 累计练习数、最近练习时间
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ApprovalStatus
from app.models.base import (
    Base,
    BigIntType,
    SoftDeleteMixin,
    TimestampMixin,
    UTCDateTime,
    enum_type,
)

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.class_ import Class
    from app.models.student_parent_binding import StudentParentBinding


class Student(Base, TimestampMixin, SoftDeleteMixin):
    """学生。"""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    # 全局唯一（design.md:103 明文规定 student_number VARCHAR(20) UNIQUE）。
    # 注意这不是「校内唯一」：跨校学号撞号会被拒。真出现跨校冲突时
    # 需要改成 (school_id, student_number) 复合唯一，届时 Student 需补 school_id。
    student_number: Mapped[str | None] = mapped_column(
        String(32), unique=True, nullable=True, index=True
    )

    class_id: Mapped[int] = mapped_column(
        BigIntType, ForeignKey("classes.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        enum_type(ApprovalStatus, length=16),
        nullable=False,
        default=ApprovalStatus.APPROVED,
    )

    bind_code: Mapped[str | None] = mapped_column(String(6), unique=True, nullable=True, index=True)

    barrier_profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    barrier_updated_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)

    total_practice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practice_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)

    # cascade + passive_deletes：删除 Student 时由数据库 ON DELETE CASCADE
    # 清理 accounts / student_parent_bindings，避免 ORM 把外键置空
    # （accounts.student_id 置空会违反 XOR CHECK 约束）。
    account: Mapped["Account | None"] = relationship(
        "Account",
        back_populates="student",
        foreign_keys="[Account.student_id]",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    class_: Mapped["Class"] = relationship("Class", back_populates="students")
    parent_bindings: Mapped[list["StudentParentBinding"]] = relationship(
        "StudentParentBinding",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} name={self.name!r} class_id={self.class_id}>"
