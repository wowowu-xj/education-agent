# -*- coding: utf-8 -*-
"""试卷（Paper）与试卷-题目关联（PaperQuestion）模型。"""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PaperStatus
from app.models.base import BigIntType, Base, SoftDeleteMixin, TimestampMixin, enum_type


class Paper(Base, TimestampMixin, SoftDeleteMixin):
    """试卷（内容实体）。

    教师组好的考试卷，含有序题目列表，可发布到多个班级。
    draft（可编辑）→ locked（已发布，只读）。total_score 由题目分值求和派生，不落库。
    """

    __tablename__ = "papers"

    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="试卷标题")
    teacher_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属教师",
    )
    duration: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="考试时长（分钟）"
    )
    status: Mapped[PaperStatus] = mapped_column(
        enum_type(PaperStatus),
        nullable=False,
        default=PaperStatus.DRAFT,
        comment="状态 draft/locked",
    )

    def __repr__(self) -> str:
        return f"<Paper id={self.id} title={self.title} status={self.status.value}>"


class PaperQuestion(Base, TimestampMixin):
    """试卷-题目关联（纯关系表，硬删除）。

    (paper_id, question_id) 唯一，sort_order 决定试卷内题目顺序。
    """

    __tablename__ = "paper_questions"
    __table_args__ = (
        UniqueConstraint("paper_id", "question_id", name="uq_paper_questions_paper_qid"),
    )

    paper_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        comment="试卷",
    )
    question_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        comment="题目",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="排序序号"
    )

    def __repr__(self) -> str:
        return f"<PaperQuestion paper={self.paper_id} q={self.question_id}>"
