"""任课关系表（TeacherClassSubject）——教师与班级的多对多关联。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntType, TimestampMixin

if TYPE_CHECKING:
    from app.models.class_ import Class
    from app.models.teacher import Teacher


class TeacherClassSubject(Base, TimestampMixin):
    """任课关系——一个教师可以在多个班级任课，一个班级可以有多位任课教师。

    唯一约束落在 (teacher_id, class_id, subject) 上：同一教师在同一班级
    教同一门课，只应有一条记录。没有这条约束时重复插入会静默成功，
    再按班级统计任课教师就会出现重复行。
    """

    __tablename__ = "teacher_class_subjects"

    __table_args__ = (
        UniqueConstraint("teacher_id", "class_id", "subject"),
    )

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    teacher_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    class_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(50), default="chemistry", nullable=False, comment="学科（默认化学）"
    )

    is_head_teacher: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否为该班班主任"
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="class_subjects")
    class_: Mapped["Class"] = relationship(back_populates="teacher_assignments")

    def __repr__(self) -> str:
        head = " (班主任)" if self.is_head_teacher else ""
        return f"<TeacherClassSubject teacher_id={self.teacher_id} class_id={self.class_id}{head}>"
