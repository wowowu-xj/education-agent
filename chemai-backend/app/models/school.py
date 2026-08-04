"""学校模型（School）——组织架构的顶层实体。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.grade import Grade
    from app.models.teacher import Teacher


class School(Base, TimestampMixin, SoftDeleteMixin):
    """学校——组织架构顶层。

    数据隔离的最外层边界：同一学校的教师只能看到本校数据。
    """

    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="学校名称")
    region: Mapped[str | None] = mapped_column(String(100), comment="所在地区")
    address: Mapped[str | None] = mapped_column(String(500), comment="详细地址")
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    current_semester: Mapped[str | None] = mapped_column(
        String(50), comment="当前学期，如 2025-秋"
    )

    # passive_deletes=True：删除学校时把级联交给数据库的 ON DELETE CASCADE。
    # 不加这个参数，ORM 会先把 grades 全量加载再逐条 DELETE，
    # 且沿 Grade → Class 继续级联，最后把 students.class_id 置 NULL，
    # 撞在 NOT NULL 上报出与真实原因无关的错误。
    # 交给数据库后，students → classes 的 RESTRICT 会正常拦住删除。
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="school",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # passive_deletes="all"：teachers.school_id 是 NOT NULL + ON DELETE RESTRICT。
    # ORM 默认行为是删除父行前把子行外键置 NULL，那会先撞 NOT NULL，
    # 掩盖"这所学校还有教师，不允许删除"这个真正的约束。
    teachers: Mapped[list["Teacher"]] = relationship(
        back_populates="school",
        passive_deletes="all",
    )

    def __repr__(self) -> str:
        return f"<School id={self.id} name={self.name!r}>"
