# -*- coding: utf-8 -*-
"""题目（Question）模型 —— 题库/试卷中的单个结构化题目。"""
from typing import Optional

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Difficulty, QuestionType
from app.models.base import BigIntType, Base, SoftDeleteMixin, TimestampMixin, enum_type


class Question(Base, TimestampMixin, SoftDeleteMixin):
    """题目。

    唯一的结构化题目实体：AI 生成、手动录入、历史真题最终都归一为 Question。
    通过 QuestionSetItem（进题库文件夹）、PaperQuestion（进试卷）被 N:M 共享引用。
    """

    __tablename__ = "questions"

    teacher_id: Mapped[Optional[int]] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        comment="创建者 Teacher.id（可空，AI 生成时无创建者）",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="题干")
    type: Mapped[QuestionType] = mapped_column(
        enum_type(QuestionType), nullable=False, comment="题型（9 种）"
    )
    options: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="选项（JSON 数组，仅选择题）"
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False, comment="标准答案")
    analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="解析")
    knowledge_points: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list, comment="知识点（JSON 数组）"
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        enum_type(Difficulty), nullable=False, comment="难度（4 档）"
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="建议分值")
    source_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="来源名称（如某年高考卷）"
    )
    region: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="来源地区"
    )
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="来源年份")

    def __repr__(self) -> str:
        return f"<Question id={self.id} type={self.type.value}>"
