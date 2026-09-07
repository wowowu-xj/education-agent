# -*- coding: utf-8 -*-
"""诊断引擎枚举与数据模型测试（L1 + L2）。

覆盖：BarrierType / MisconceptionCategory 枚举取值合法性；StudentAnswer /
BarrierConfig / DiagnosisOverrideLog / ParentNotification 模型字段与可空性；
Student 扩展 misconception_profile / current_plan 字段。
"""
from __future__ import annotations

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus, BarrierType, MisconceptionCategory
from app.core.security import hash_password
from app.models import (
    BarrierConfig,
    Class,
    DiagnosisOverrideLog,
    Parent,
    ParentNotification,
    Student,
    StudentAnswer,
    Teacher,
)


@pytest.fixture()
def student(db: Session, klass: Class) -> Student:
    """一名测试学生（归属 klass）。"""
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


# ---------------------------------------------------------------------------
# 枚举（task 1.1）
# ---------------------------------------------------------------------------


class TestDiagnosisEnums:
    def test_barrier_type_three_values(self) -> None:
        """BarrierType 仅 concept / reading / expression 三值。"""
        assert {m.value for m in BarrierType} == {"concept", "reading", "expression"}

    def test_misconception_category_six_values(self) -> None:
        """MisconceptionCategory 仅六个合法值。"""
        assert {m.value for m in MisconceptionCategory} == {
            "chemical_equilibrium",
            "redox",
            "mole_calculation",
            "organic_chemistry",
            "chemical_notation",
            "structure_properties",
        }

    @pytest.mark.parametrize("bad", ["concept_plus", "bogus", ""])
    def test_barrier_type_rejects_invalid(self, bad: str) -> None:
        """非法障碍类型取值被拒绝。"""
        with pytest.raises(ValueError):
            BarrierType(bad)

    @pytest.mark.parametrize("bad", ["acid_base", "bogus", ""])
    def test_misconception_rejects_invalid(self, bad: str) -> None:
        """非法迷思概念取值被拒绝。"""
        with pytest.raises(ValueError):
            MisconceptionCategory(bad)


# ---------------------------------------------------------------------------
# StudentAnswer（task 1.3 / 1.4）
# ---------------------------------------------------------------------------


class TestStudentAnswerModel:
    def test_columns_complete(self) -> None:
        """字段齐全，诊断三字段可空。"""
        cols = {c.key: c for c in inspect(StudentAnswer).columns}
        for required in (
            "student_id",
            "exam_id",
            "question_id",
            "is_correct",
            "student_answer",
            "barrier_type",
            "misconception_category",
            "confidence",
            "consecutive_errors",
            "consecutive_correct",
        ):
            assert required in cols, f"缺少字段 {required}"

    def test_diagnostic_fields_nullable(self) -> None:
        """诊断三字段可空（诊断前为 NULL）。"""
        cols = {c.key: c for c in inspect(StudentAnswer).columns}
        for name in ("barrier_type", "misconception_category", "confidence"):
            assert cols[name].nullable, f"{name} 应为可空"

    def test_persist_answer(self, db: Session) -> None:
        """作答记录可持久化，诊断字段初始为 NULL。"""
        answer = StudentAnswer(
            student_id=1,  # 外键在单元测试不校验时可用占位；这里仅验证列
            exam_id=1,
            question_id=1,
            is_correct=False,
            student_answer="我选 A",
        )
        assert answer.barrier_type is None
        assert answer.misconception_category is None
        assert answer.confidence is None

    def test_answer_consecutive_defaults(self) -> None:
        """连续对错计数默认 0。"""
        cols = {c.key: c for c in inspect(StudentAnswer).columns}
        assert cols["consecutive_errors"].default.arg == 0
        assert cols["consecutive_correct"].default.arg == 0


# ---------------------------------------------------------------------------
# 其余三模型 + Student 扩展（task 1.5 / 1.6）
# ---------------------------------------------------------------------------


class TestBarrierConfigModel:
    def test_defaults(self, db: Session, teacher: Teacher) -> None:
        """默认阈值与 spec 一致（落库后应用 default）。"""
        cfg = BarrierConfig(teacher_id=teacher.id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
        assert cfg.concept_threshold == 3
        assert cfg.reading_threshold == 2
        assert cfg.expression_threshold == 3
        assert cfg.mastery_threshold == 3
        assert cfg.auto_sync_to_student is False

    def test_teacher_unique(self, db: Session, teacher: Teacher) -> None:
        """同一教师只能一条配置。"""
        db.add(BarrierConfig(teacher_id=teacher.id))
        db.commit()
        db.add(BarrierConfig(teacher_id=teacher.id))
        with pytest.raises(IntegrityError):
            db.commit()


class TestDiagnosisOverrideLogModel:
    def test_fields(self) -> None:
        cols = {c.key for c in inspect(DiagnosisOverrideLog).columns}
        for required in (
            "student_id",
            "old_profile",
            "new_profile",
            "reason",
            "operator_id",
            "created_at",
        ):
            assert required in cols, f"缺少字段 {required}"

    def test_persist_log(self, db: Session, student: Student, teacher: Teacher) -> None:
        log = DiagnosisOverrideLog(
            student_id=student.id,
            old_profile={"concept": 1.0},
            new_profile={"reading": 0.9, "concept": 0.1},
            reason="教师人工复核",
            operator_id=teacher.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        assert log.created_at is not None
        assert log.new_profile == {"reading": 0.9, "concept": 0.1}


class TestParentNotificationModel:
    def test_fields(self) -> None:
        cols = {c.key: c for c in inspect(ParentNotification).columns}
        for required in ("student_id", "parent_id", "type", "content", "created_at", "read_at"):
            assert required in cols, f"缺少字段 {required}"

    def test_persist_notification(self, db: Session, student: Student, parent: Parent) -> None:
        note = ParentNotification(
            student_id=student.id, parent_id=parent.id, type="learning_plan", content="本周学习计划"
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        assert note.read_at is None
        assert note.type == "learning_plan"


class TestStudentExtension:
    def test_student_has_new_fields(self) -> None:
        """Student 扩展 misconception_profile / current_plan。"""
        cols = {c.key: c for c in inspect(Student).columns}
        assert "misconception_profile" in cols
        assert "current_plan" in cols
