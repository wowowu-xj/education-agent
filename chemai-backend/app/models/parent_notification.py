# -*- coding: utf-8 -*-
"""家长通知（ParentNotification）模型。

教师将学习计划等推送给学生绑定家长时写入；家长端消息列表据此展示，
read_at 标记已读。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BigIntType, Base, UTCDateTime, utcnow


class ParentNotification(Base, ):
    """家长通知记录。"""

    __tablename__ = "parent_notifications"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学生",
    )
    parent_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="家长",
    )
    type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="通知类型（如 learning_plan）"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="通知内容"
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utcnow,
        server_default=func.now(),
        nullable=False,
        comment="发送时间（UTC）",
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True, comment="已读时间（NULL 表示未读）"
    )

    def __repr__(self) -> str:
        return f"<ParentNotification id={self.id} student={self.student_id} parent={self.parent_id}>"
