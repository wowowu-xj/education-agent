# -*- coding: utf-8 -*-
"""Teacher 模型与角色枚举测试。"""
from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import TEACHER_ROLE_DISPLAY, ApprovalStatus, TeacherRole
from app.models import School, Teacher


def test_teacher_role_enum_values() -> None:
    """四种教师子角色齐全，且取值全为英文。"""
    assert {role.value for role in TeacherRole} == {
        "admin",
        "academic_admin",
        "subject_lead",
        "teacher",
    }


def test_role_display_mapping_is_complete() -> None:
    """每个角色都有中文展示名（决策 #3：枚举存英文，展示层做映射）。"""
    assert set(TEACHER_ROLE_DISPLAY) == set(TeacherRole)
    assert TEACHER_ROLE_DISPLAY[TeacherRole.SUBJECT_LEAD] == "学科组长"


@pytest.mark.parametrize("role", list(TeacherRole))
def test_teacher_role_round_trip(db: Session, school: School, role: TeacherRole) -> None:
    """各角色都能正确落库与读回。"""
    obj = Teacher(
        name=f"教师_{role.value}",
        phone=f"139{list(TeacherRole).index(role):08d}",
        school_id=school.id,
        role=role,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    db.add(obj)
    db.commit()
    db.expire(obj)

    assert obj.role is role


def test_teacher_defaults(db: Session, school: School) -> None:
    """默认为待审批的普通化学教师。"""
    obj = Teacher(name="王老师", phone="13700000001", school_id=school.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    assert obj.role is TeacherRole.TEACHER
    assert obj.status is ApprovalStatus.PENDING
    assert obj.subject == "chemistry"
    assert obj.deleted_at is None


def test_teacher_phone_is_unique(db: Session, teacher: Teacher, school: School) -> None:
    """手机号唯一（登录标识）。"""
    db.add(Teacher(name="李老师", phone=teacher.phone, school_id=school.id))
    with pytest.raises(IntegrityError):
        db.commit()


def test_teacher_belongs_to_school(db: Session, teacher: Teacher) -> None:
    """教师归属学校，双向关系可用。"""
    assert teacher.school.name == "测试中学"
    assert teacher in teacher.school.teachers
