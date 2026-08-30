# -*- coding: utf-8 -*-
"""考试（Exam）模型 —— 一份 Paper 发布到某班后的按班实例。"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ExamStatus
from app.models.base import (
    BigIntType,
    Base,
    TimestampMixin,
    UTCDateTime,
    enum_type,
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
