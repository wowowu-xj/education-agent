# -*- coding: utf-8 -*-
"""考试（Exam）模型 —— 一份 Paper 发布到某班后的按班实例。"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ExamStatus
from app.models.base import (
    BigIntType,
    Base,
    TimestampMixin,
    UTCDateTime,
    enum_type,
    utcnow,
)


class Exam(Base, TimestampMixin):
    """考试（按班实例）。

    一份 Paper 发布到某个班级后形成，生命周期按班独立。不物理删除（走 cancelled）。
    """

    __tablename__ = "exams"

    paper_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("papers.id", ondelete="RESTRICT"),
        nullable=False,
        comment="试卷（共享引用）",
    )
    class_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        comment="班级",
    )
    exam_date: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True, comment="考试时间"
    )
    status: Mapped[ExamStatus] = mapped_column(
        enum_type(ExamStatus),
        nullable=False,
        default=ExamStatus.PUBLISHED,
        comment="状态（6 态）",
    )

    def __repr__(self) -> str:
        return (
            f"<Exam id={self.id} paper={self.paper_id}"
            f" class={self.class_id} status={self.status.value}>"
        )


class ExamStatusTransition(Base):
    """考试状态迁移审计日志（append-only）。

    每次教师侧状态迁移追加一条，记录 from/to 状态、操作教师与时间，
    便于追溯；历史多条而非仅末态，故不落 Exam 列。
    """

    __tablename__ = "exam_status_transitions"

    exam_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        comment="考试",
    )
    from_status: Mapped[ExamStatus] = mapped_column(
        enum_type(ExamStatus), nullable=False, comment="迁移前状态"
    )
    to_status: Mapped[ExamStatus] = mapped_column(
        enum_type(ExamStatus), nullable=False, comment="迁移后状态"
    )
    operator_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
        comment="操作教师",
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utcnow,
        server_default=func.now(),
        nullable=False,
        comment="迁移时间（UTC）",
    )

    def __repr__(self) -> str:
        return (
            f"<ExamStatusTransition id={self.id} exam={self.exam_id}"
            f" {self.from_status.value}->{self.to_status.value}>"
        )
