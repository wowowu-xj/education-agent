"""Account 模型：统一登录凭证表。

设计要点：
- Parent 不使用此表（走独立认证通道）
- teacher_id 和 student_id 双可空外键，CHECK constraint 保证恰有一个非空
- teacher_id / student_id 各自唯一：一个教师或学生**最多一个**账号
- username 全局唯一
- password_hash 使用 passlib bcrypt
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ACCOUNT_ROLE_VALUES
from app.models.base import Base, BigIntType, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.teacher import Teacher

_ROLE_VALUES_SQL = ", ".join(f"'{value}'" for value in ACCOUNT_ROLE_VALUES)


class Account(Base, TimestampMixin, SoftDeleteMixin):
    """登录账户。

    每条 Account 记录对应一个 Teacher 或一个 Student（互斥）。
    Parent 独立走 /api/parent/login，不进入此表。
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    # 双可空外键：teacher_id 和 student_id 恰有一个非空。
    # unique=True 是「一人一账号」的唯一保障——Teacher.account / Student.account
    # 声明了 uselist=False，但那只是 ORM 侧的期望；没有唯一约束时数据库允许写入
    # 两条指向同一教师的 Account，随后加载关系只会拿到 SAWarning 和其中任意一条。
    # 可空列上的唯一约束允许多个 NULL（SQLite / MySQL / PostgreSQL 均如此），
    # 所以不影响「学生账号的 teacher_id 全为 NULL」。
    teacher_id: Mapped[int | None] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
        index=True,
    )
    student_id: Mapped[int | None] = mapped_column(
        BigIntType,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
        index=True,
    )

    # 缓存角色（避免登录时 JOIN Teacher 表）。
    # teacher_id 非空时与 Teacher.role 一致，由 app.models.events 的
    # before_flush 监听器在 Teacher.role 变更时自动同步；
    # student_id 非空时固定为 "student"。
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    teacher: Mapped["Teacher | None"] = relationship(
        "Teacher", back_populates="account", foreign_keys=[teacher_id]
    )
    student: Mapped["Student | None"] = relationship(
        "Student", back_populates="account", foreign_keys=[student_id]
    )

    __table_args__ = (
        CheckConstraint(
            "(teacher_id IS NULL) != (student_id IS NULL)",
            name="teacher_xor_student",
        ),
        CheckConstraint(f"role IN ({_ROLE_VALUES_SQL})", name="role_allowed"),
    )

    def __repr__(self) -> str:
        return f"<Account id={self.id} username={self.username!r} role={self.role}>"
