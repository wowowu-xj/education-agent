# -*- coding: utf-8 -*-
"""作答记录（StudentAnswer）模型 —— 诊断引擎的数据源。

一条作答对应「某学生在某考试中作答某题」，诊断字段（barrier_type /
misconception_category / confidence）在诊断前为空（NULL），诊断后由
三引擎三段式流程写回。
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import BarrierType, MisconceptionCategory
from app.models.base import BigIntType, Base, TimestampMixin, enum_type


class StudentAnswer(Base, TimestampMixin):
    """学生作答记录。

    作答正确与否（is_correct）在录入时即知；诊断三字段只对错误作答有意义，
    正确作答的 barrier_type 保持 NULL，不参与画像聚合。
    """

    __tablename__ = "student_answers"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学生",
    )
    exam_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="考试（即文档的「考试记录」）",
    )
    question_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        comment="题目",
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="是否作答正确"
    )
    student_answer: Mapped[str] = mapped_column(
        Text, nullable=False, comment="学生作答内容"
    )

    # 诊断结果三字段：诊断前为 NULL，诊断后写回。
    barrier_type: Mapped[Optional[BarrierType]] = mapped_column(
        enum_type(BarrierType, length=16), nullable=True, comment="障碍类型"
    )
    misconception_category: Mapped[Optional[MisconceptionCategory]] = mapped_column(
        enum_type(MisconceptionCategory, length=32),
        nullable=True,
        comment="迷思概念类别",
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="诊断置信度（0–1）"
    )

    # 连续对错计数：服务于未来阈值触发，本分支仅维护不消费（design D2 Non-Goals）。
    consecutive_errors: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="连续错误次数"
    )
    consecutive_correct: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="连续正确次数"
    )

    def __repr__(self) -> str:
        return (
            f"<StudentAnswer id={self.id} student={self.student_id}"
            f" exam={self.exam_id} correct={self.is_correct}>"
        )
