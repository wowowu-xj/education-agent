# -*- coding: utf-8 -*-
"""诊断覆盖审计日志（DiagnosisOverrideLog）模型。

教师手动覆盖学生障碍画像时 append-only 记录一条：旧画像 + 新画像 + 原因 +
操作教师 + 时间，便于回溯。历史多条而非仅末态（仿 exam_status_transitions）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BigIntType, Base, UTCDateTime, utcnow


class DiagnosisOverrideLog(Base):
    """教师覆盖学生障碍画像的审计日志（append-only）。"""

    __tablename__ = "diagnosis_override_logs"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学生",
    )
    old_profile: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="覆盖前画像"
    )
    new_profile: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="覆盖后画像"
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False, comment="覆盖原因")
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
        comment="覆盖时间（UTC）",
    )

    def __repr__(self) -> str:
        return f"<DiagnosisOverrideLog id={self.id} student={self.student_id}>"
