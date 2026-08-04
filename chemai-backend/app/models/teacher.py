"""Teacher 模型：教师及子角色。

设计要点：
- role 字段用 TeacherRole 枚举（admin/academic_admin/subject_lead/teacher）
- status 字段用 ApprovalStatus 枚举（pending/approved/rejected）
- 归属学校（school_id）
- 与 Class 通过 TeacherClassSubject 多对多
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ApprovalStatus, TeacherRole
from app.models.base import (
    Base,
    BigIntType,
    SoftDeleteMixin,
    TimestampMixin,
    enum_type,
)

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.school import School
    from app.models.teacher_class_subject import TeacherClassSubject


class Teacher(Base, TimestampMixin, SoftDeleteMixin):
    """教师（含 admin/教务管理员/学科组长/普通教师四种子角色）。"""

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    school_id: Mapped[int] = mapped_column(
        BigIntType, ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    role: Mapped[TeacherRole] = mapped_column(
        enum_type(TeacherRole), nullable=False, default=TeacherRole.TEACHER
    )
    status: Mapped[ApprovalStatus] = mapped_column(
        enum_type(ApprovalStatus, length=16),
        nullable=False,
        default=ApprovalStatus.PENDING,
    )

    subject: Mapped[str] = mapped_column(String(32), nullable=False, default="chemistry")

    # passive_deletes=True：删除 Teacher 时交给数据库的 ON DELETE CASCADE 清理
    # accounts 行，而不是由 ORM 先加载再逐行 UPDATE 外键为 NULL。
    # 后者会把 accounts.teacher_id 置空，直接撞上 XOR CHECK 约束。
    account: Mapped["Account | None"] = relationship(
        "Account",
        back_populates="teacher",
        foreign_keys="[Account.teacher_id]",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    school: Mapped["School"] = relationship("School", back_populates="teachers")
    class_subjects: Mapped[list["TeacherClassSubject"]] = relationship(
        "TeacherClassSubject",
        back_populates="teacher",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Teacher id={self.id} name={self.name!r} role={self.role.value}>"
