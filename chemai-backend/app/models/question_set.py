# -*- coding: utf-8 -*-
"""题库文件夹（QuestionSet）与文件夹-题目关联（QuestionSetItem）模型。"""
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BigIntType, Base, SoftDeleteMixin, TimestampMixin


class QuestionSet(Base, TimestampMixin, SoftDeleteMixin):
    """题库文件夹。

    扁平结构：文件夹直接装题目，不嵌套。一道题可进多个文件夹（共享引用）。
    """

    __tablename__ = "question_sets"

    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="文件夹名称")
    teacher_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属教师",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="文件夹描述"
    )
    region: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="来源地区"
    )
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="来源年份")
    is_preset: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否系统预设（不可删）"
    )

    def __repr__(self) -> str:
        return f"<QuestionSet id={self.id} name={self.name}>"


class QuestionSetItem(Base, TimestampMixin):
    """文件夹-题目关联（纯关系表，硬删除）。

    (question_set_id, question_id) 唯一，sort_order 决定文件夹内题目顺序。
    """

    __tablename__ = "question_set_items"
    __table_args__ = (
        UniqueConstraint(
            "question_set_id", "question_id", name="uq_question_set_items_set_qid"
        ),
    )

    question_set_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("question_sets.id", ondelete="CASCADE"),
        nullable=False,
        comment="题库文件夹",
    )
    question_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        comment="题目",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="排序序号"
    )

    def __repr__(self) -> str:
        return f"<QuestionSetItem set={self.question_set_id} q={self.question_id}>"
