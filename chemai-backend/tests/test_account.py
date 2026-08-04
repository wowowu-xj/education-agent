# -*- coding: utf-8 -*-
"""Account 模型测试：账户归属互斥不变量。

核心约束：``teacher_id`` 与 ``student_id`` 恰有一个非空（CHECK constraint）。
"""
from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus
from app.core.security import hash_password, verify_password
from app.models import Account, Class, Student, Teacher


@pytest.fixture()
def student(db: Session, klass: Class) -> Student:
    """一名测试学生。"""
    obj = Student(
        name="李同学",
        student_number="2025010101",
        class_id=klass.id,
        status=ApprovalStatus.APPROVED,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def test_account_bound_to_teacher(db: Session, teacher: Teacher) -> None:
    """绑定教师的账户可以正常创建。"""
    account = Account(
        username="teacher_zhang",
        password_hash=hash_password("Passw0rd!"),
        teacher_id=teacher.id,
        role="teacher",
    )
    db.add(account)
    db.commit()

    assert account.id is not None
    assert account.student_id is None
    assert account.teacher.name == "张老师"


def test_account_bound_to_student(db: Session, student: Student) -> None:
    """绑定学生的账户可以正常创建。"""
    account = Account(
        username="student_li",
        password_hash=hash_password("Passw0rd!"),
        student_id=student.id,
        role="student",
    )
    db.add(account)
    db.commit()

    assert account.id is not None
    assert account.teacher_id is None
    assert account.student.name == "李同学"


def test_account_rejects_both_owners(
    db: Session, teacher: Teacher, student: Student
) -> None:
    """teacher_id 与 student_id 同时非空时违反 CHECK 约束。"""
    db.add(
        Account(
            username="both_owners",
            password_hash=hash_password("Passw0rd!"),
            teacher_id=teacher.id,
            student_id=student.id,
            role="teacher",
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()


def test_account_rejects_no_owner(db: Session) -> None:
    """teacher_id 与 student_id 同时为空时违反 CHECK 约束。"""
    db.add(
        Account(
            username="orphan",
            password_hash=hash_password("Passw0rd!"),
            role="teacher",
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()


def test_username_is_unique(db: Session, teacher: Teacher, student: Student) -> None:
    """username 全局唯一。"""
    db.add(
        Account(
            username="dup_name",
            password_hash=hash_password("Passw0rd!"),
            teacher_id=teacher.id,
            role="teacher",
        )
    )
    db.commit()

    db.add(
        Account(
            username="dup_name",
            password_hash=hash_password("Passw0rd!"),
            student_id=student.id,
            role="student",
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()


def test_password_hash_is_not_plaintext(db: Session, teacher: Teacher) -> None:
    """存储的是哈希值，且能被校验通过。"""
    raw = "ChemAI@2025"
    account = Account(
        username="hash_check",
        password_hash=hash_password(raw),
        teacher_id=teacher.id,
        role="teacher",
    )
    db.add(account)
    db.commit()

    assert account.password_hash != raw
    assert verify_password(raw, account.password_hash)
    assert not verify_password("wrong-password", account.password_hash)


def test_soft_delete_defaults_to_none(db: Session, teacher: Teacher) -> None:
    """新建账户未被软删除。"""
    account = Account(
        username="soft_delete_check",
        password_hash=hash_password("Passw0rd!"),
        teacher_id=teacher.id,
        role="teacher",
    )
    db.add(account)
    db.commit()

    assert account.deleted_at is None
    assert account.created_at is not None
