"""SQLAlchemy 模型层——集中导入所有模型，确保 Base.metadata 完整。

Alembic autogenerate 依赖 Base.metadata 感知所有表，因此必须在此模块统一 import。
"""

from app.models.account import Account
from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.class_ import Class
from app.models.grade import Grade
from app.models.parent import Parent
from app.models.school import School
from app.models.student import Student
from app.models.student_parent_binding import StudentParentBinding
from app.models.teacher import Teacher
from app.models.teacher_class_subject import TeacherClassSubject

from app.models import events as _events  # noqa: F401 — 注册 before_flush 监听器

_events.register_events()

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "Account",
    "Teacher",
    "Student",
    "Parent",
    "School",
    "Grade",
    "Class",
    "TeacherClassSubject",
    "StudentParentBinding",
]
