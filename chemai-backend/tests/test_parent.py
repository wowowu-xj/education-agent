# -*- coding: utf-8 -*-
"""Parent 模型测试：家长独立认证通道。

依据决策 #1：家长不进 Account 表，自带 password_hash，
通过 StudentParentBinding 与学生建立多对多关系。
"""
from __future__ import annotations

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus, ParentRelation
from app.core.security import hash_password, verify_password
from app.models import Account, Class, Parent, Student, StudentParentBinding


@pytest.fixture()
def parent(db: Session) -> Parent:
    """一位测试家长。"""
    obj = Parent(
        name="李妈妈",
        phone="13900000001",
        password_hash=hash_password("Parent@2025"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def student(db: Session, klass: Class) -> Student:
    """一名测试学生。"""
    obj = Student(
        name="李同学",
        student_number="2025010102",
        class_id=klass.id,
        status=ApprovalStatus.APPROVED,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def test_parent_authenticates_independently(parent: Parent) -> None:
    """家长自带密码哈希，可独立校验登录。"""
    assert parent.password_hash != "Parent@2025"
    assert verify_password("Parent@2025", parent.password_hash)
    assert not verify_password("wrong", parent.password_hash)


def test_parent_has_no_account_relationship() -> None:
    """Parent 模型不依赖 Account 表（决策 #1）。"""
    columns = {c.key for c in inspect(Parent).columns}
    relationships = {r.key for r in inspect(Parent).relationships}

    assert "account_id" not in columns
    assert "account" not in relationships
    # 反向确认：Account 只认教师和学生
    account_columns = {c.key for c in inspect(Account).columns}
    assert "parent_id" not in account_columns


def test_parent_phone_is_unique(db: Session, parent: Parent) -> None:
    """手机号唯一（登录标识）。"""
    db.add(
        Parent(
            name="李爸爸",
            phone=parent.phone,
            password_hash=hash_password("Parent@2025"),
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()


def test_parent_binds_to_student(db: Session, parent: Parent, student: Student) -> None:
    """亲子绑定双向关系可用。"""
    binding = StudentParentBinding(
        student_id=student.id,
        parent_id=parent.id,
        relationship_type=ParentRelation.MOTHER.value,
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)

    assert binding.is_active is True
    assert binding.student.name == "李同学"
    assert binding.parent.name == "李妈妈"
    assert binding in parent.student_bindings
    assert binding in student.parent_bindings


def test_one_parent_binds_multiple_students(
    db: Session, parent: Parent, student: Student, klass: Class
) -> None:
    """一位家长可绑定多名学生（多孩家庭）。"""
    second = Student(
        name="李小妹",
        student_number="2025010103",
        class_id=klass.id,
        status=ApprovalStatus.APPROVED,
    )
    db.add(second)
    db.flush()

    db.add_all(
        [
            StudentParentBinding(
                student_id=student.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.MOTHER.value,
            ),
            StudentParentBinding(
                student_id=second.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.MOTHER.value,
            ),
        ]
    )
    db.commit()
    db.refresh(parent)

    assert len(parent.student_bindings) == 2


def test_binding_requires_existing_student(db: Session, parent: Parent) -> None:
    """绑定不存在的学生时外键校验失败。"""
    db.add(
        StudentParentBinding(
            student_id=999999,
            parent_id=parent.id,
            relationship_type=ParentRelation.FATHER.value,
        )
    )
    # SQLite 在带 RETURNING 的 INSERT 中把外键违规报成 OperationalError，
    # MySQL 则报 IntegrityError，因此断言到二者的共同父类 DatabaseError。
    with pytest.raises(DatabaseError):
        db.commit()
