# -*- coding: utf-8 -*-
"""pytest 公共 fixture。

测试库使用 SQLite 内存库：
- ``StaticPool`` 保证所有连接共享同一个内存库
- 显式打开 ``PRAGMA foreign_keys``，否则 SQLite 默认不校验外键
"""
from __future__ import annotations

from typing import Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.enums import ApprovalStatus, TeacherRole
from app.models import Base, Class, Grade, School, Teacher


@pytest.fixture()
def engine() -> Iterator[Engine]:
    """每个测试一个独立的内存库。"""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(eng, "connect")
    def _enable_foreign_keys(dbapi_conn, _connection_record) -> None:  # noqa: ANN001
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db(engine: Engine) -> Iterator[Session]:
    """数据库会话。"""
    with Session(engine) as session:
        yield session


@pytest.fixture()
def school(db: Session) -> School:
    """一所测试学校。"""
    obj = School(name="测试中学", region="北京市海淀区", current_semester="2025-秋")
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def klass(db: Session, school: School) -> Class:
    """一个测试班级（连带年级）。"""
    grade = Grade(name="高一", school_id=school.id, academic_year="2025-2026")
    db.add(grade)
    db.flush()

    obj = Class(name="高一（1）班", grade_id=grade.id, subject="chemistry")
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def teacher(db: Session, school: School) -> Teacher:
    """一位普通化学教师。"""
    obj = Teacher(
        name="张老师",
        phone="13800000001",
        school_id=school.id,
        role=TeacherRole.TEACHER,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
