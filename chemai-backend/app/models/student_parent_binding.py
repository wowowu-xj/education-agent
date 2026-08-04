"""亲子绑定表（StudentParentBinding）——学生与家长的多对多关联。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ParentRelation
from app.models.base import Base, BigIntType, TimestampMixin, enum_type

if TYPE_CHECKING:
    from app.models.parent import Parent
    from app.models.student import Student


class StudentParentBinding(Base, TimestampMixin):
    """亲子绑定关系——通过绑定码建立学生与家长的关联。

    绑定流程：
    1. 学生生成 6 位绑定码存于 Student.bind_code
    2. 家长在家长端输入 student_id + bind_code + 关系
    3. 系统验证后创建本表记录

    关系表，硬删除（决策 #15）：解绑用 is_active 置 false 保留审计痕迹，
    彻底删除则物理删行。
    """

    __tablename__ = "student_parent_bindings"

    id: Mapped[int] = mapped_column(BigIntType, primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id: Mapped[int] = mapped_column(
        BigIntType,
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 用 ParentRelation 枚举而非裸 String：原先是自由文本，
    # '随便写的垃圾值' 也能入库，枚举定义形同废纸。
    relationship_type: Mapped[ParentRelation] = mapped_column(
        enum_type(ParentRelation, length=20),
        nullable=False,
        comment="关系：father/mother/guardian",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="绑定是否有效"
    )

    student: Mapped["Student"] = relationship(back_populates="parent_bindings")
    parent: Mapped["Parent"] = relationship(back_populates="student_bindings")

    __table_args__ = (
        # 同一对学生-家长只能有一条绑定记录。
        # 不含 relationship_type：同一个家长不可能既是父亲又是监护人，
        # 关系变更应该改这条记录而不是新增一条。
        UniqueConstraint("student_id", "parent_id", name="uq_binding_student_parent"),
    )

    def __repr__(self) -> str:
        return (
            f"<StudentParentBinding student_id={self.student_id} "
            f"parent_id={self.parent_id} rel={self.relationship_type.value}>"
        )
