"""年级模型（Grade）——学校 → 年级 → 班级的中间层。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BigIntType, TimestampMixin

if TYPE_CHECKING:
    from app.models.class_ import Class
    from app.models.school import School


class Grade(Base, TimestampMixin):
    """年级——初一/初二/初三/高一/高二/高三。

    注意：本表**没有**软删除，而 School / Class 有。
    理由是年级只是纯结构层，不承载业务数据也不是登录主体，
    删除学校时随数据库 CASCADE 一起清掉即可。
    如果将来需要"归档某一届"，再补 SoftDeleteMixin。
    """

    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="年级名称，如 高一")

    school_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属学校",
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(20), comment="所属学年，如 2024-2025"
    )

    school: Mapped["School"] = relationship(back_populates="grades")

    # 同 School.grades：级联交给数据库，让 students 的 RESTRICT 能正常生效。
    classes: Mapped[list["Class"]] = relationship(
        back_populates="grade",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Grade id={self.id} name={self.name!r} school_id={self.school_id}>"
