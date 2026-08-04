"""班级模型（Class）——学生所属的最小组织单元。

文件名末尾加下划线避免与 Python 关键字 class 冲突。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SchoolStage
from app.models.base import Base, BigIntType, SoftDeleteMixin, TimestampMixin, enum_type

if TYPE_CHECKING:
    from app.models.grade import Grade
    from app.models.student import Student
    from app.models.teacher import Teacher
    from app.models.teacher_class_subject import TeacherClassSubject


class Class(Base, TimestampMixin, SoftDeleteMixin):
    """班级——如「高一(3)班」。

    - 关键业务表：软删除
    - 通过任课关系表 TeacherClassSubject 关联多个教师
    """

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="班级名称")

    grade_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("grades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属年级",
    )

    # index=True 是必要的：按班主任查班级是教师端首页的高频查询，
    # 且 ON DELETE SET NULL 在删除教师时要扫这一列。
    homeroom_teacher_id: Mapped[int | None] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="SET NULL"),
        index=True,
        comment="班主任 Teacher.id",
    )

    # 冗余计数字段，design.md:134 明文要求保留。
    # 所有权：**不由 ORM 维护**。学生入班/转班/删除时必须由服务层显式同步。
    # 需要精确人数的场景请直接 COUNT students，不要信任本字段。
    student_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="当前学生人数（冗余，服务层维护）"
    )

    stage: Mapped[SchoolStage | None] = mapped_column(
        enum_type(SchoolStage, length=20), nullable=True, comment="学段 junior/senior"
    )

    subject: Mapped[str] = mapped_column(
        String(20), default="chemistry", nullable=False, comment="学科，固定 chemistry"
    )

    grade: Mapped["Grade"] = relationship(back_populates="classes")

    homeroom_teacher: Mapped["Teacher | None"] = relationship(
        foreign_keys=[homeroom_teacher_id]
    )

    # passive_deletes="all"：删除班级时**不要**把 students.class_id 改写成 NULL。
    # 该列是 NOT NULL + ON DELETE RESTRICT，目的就是"班里还有学生就不许删班"。
    # 若交给 ORM 默认行为，它会先 UPDATE students SET class_id=NULL，
    # 撞上 NOT NULL 报出一条与真实意图无关的错误信息。
    students: Mapped[list["Student"]] = relationship(
        back_populates="class_", passive_deletes="all"
    )

    teacher_assignments: Mapped[list["TeacherClassSubject"]] = relationship(
        back_populates="class_", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Class id={self.id} name={self.name!r} grade_id={self.grade_id}>"
