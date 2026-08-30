# -*- coding: utf-8 -*-
"""开发种子账号脚本。

把 dev 库里的教师账号重置为已知凭据，供浏览器手动验证登录流程：

    username: teacher
    password: Chemai@1234

用法（需在 chemai-backend 目录下执行，让 ``sqlite:///./chemai.db`` 指向 dev 库）::

    ./venv/bin/python scripts/seed_dev_account.py

幂等：重复执行只是把密码重置回同一值，不会重复创建账号。
若 dev 库尚无教师账号（全新库），则自动补建 School + Teacher + Account 最小链条。
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

# 让脚本能在任意子目录下被直接执行时仍 import 到 app 包（项目根目录）。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.enums import ApprovalStatus, TeacherRole
from app.core.security import hash_password
from app.models import Account, School, Teacher

DEV_USERNAME = "teacher"
DEV_PASSWORD = "Chemai@1234"


def _create_teacher_account(db: Session) -> Account:
    """无教师账号时，补建 School + Teacher + Account 最小链条。"""
    school = db.execute(select(School)).scalars().first()
    if school is None:
        school = School(name="开发学校", region="北京市")
        db.add(school)
        db.flush()

    teacher = Teacher(
        name="开发教师",
        phone="13800000000",
        school_id=school.id,
        role=TeacherRole.TEACHER,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    db.add(teacher)
    db.flush()

    account = Account(
        username=DEV_USERNAME,
        password_hash=hash_password(DEV_PASSWORD),
        teacher_id=teacher.id,
        role=TeacherRole.TEACHER.value,
    )
    db.add(account)
    db.flush()
    return account


def seed() -> None:
    """重置（或新建）开发教师账号为已知凭据。"""
    with SessionLocal() as db:
        account = db.execute(
            select(Account).where(
                Account.teacher_id.is_not(None),
                Account.deleted_at.is_(None),
            )
        ).scalars().first()

        if account is None:
            account = _create_teacher_account(db)

        account.username = DEV_USERNAME
        account.password_hash = hash_password(DEV_PASSWORD)
        db.commit()

        print(f"✓ 开发账号就绪：username={account.username!r} password={DEV_PASSWORD!r}")
        print("  登录入口：POST /api/auth/login（前端 /pages/login.html）")


if __name__ == "__main__":
    seed()
