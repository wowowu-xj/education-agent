# -*- coding: utf-8 -*-
"""教师障碍诊断阈值配置（BarrierConfig）模型。

每个教师最多一条配置（teacher_id 唯一），控制障碍诊断触发阈值；
无历史配置时按 spec 返回默认值（concept=3 / reading=2 / expression=3 /
mastery=3 / auto_sync=false），配置经 upsert 持久化。
"""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BigIntType, Base, TimestampMixin


class BarrierConfig(Base, TimestampMixin):
    """教师诊断阈值配置（upsert，一个教师一条）。"""

    __tablename__ = "barrier_configs"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    teacher_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="教师（唯一）",
    )

    concept_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, comment="概念理解型触发阈值"
    )
    reading_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2, comment="审题障碍型触发阈值"
    )
    expression_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, comment="表述障碍型触发阈值"
    )
    mastery_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, comment="掌握度阈值"
    )
    auto_sync_to_student: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否自动同步到学生画像"
    )

    def __repr__(self) -> str:
        return f"<BarrierConfig id={self.id} teacher={self.teacher_id}>"
