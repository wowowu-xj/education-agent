# -*- coding: utf-8 -*-
"""题库/试卷/考试数据模型 L1 测试。

锁住数据层的每一条约束：
- 四个新枚举（QuestionType/Difficulty/PaperStatus/ExamStatus）的 CHECK 约束
- 枚举按 .value（小写下划线）入库
- QuestionSetItem / PaperQuestion 的 (set|paper, qid) 唯一约束
- 软删/硬删边界：Question/QuestionSet/Paper 软删，Exam/纯关系表不软删
- total_score / question_count 派生不落库
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import Difficulty, ExamStatus, PaperStatus, QuestionType
from app.models import (
    Exam,
    Paper,
    PaperQuestion,
    Question,
    QuestionSet,
    QuestionSetItem,
    Teacher,
)


def _expect_check_violation(db: Session, sql: str, params: dict[str, object]) -> None:
    """执行一条应该被 CHECK 约束拦住的原生 SQL。"""
    with pytest.raises(IntegrityError):
        db.execute(text(sql), params)
        db.commit()
    db.rollback()


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture()
def question(db: Session, teacher: Teacher) -> Question:
    """一道单项选择题。"""
    obj = Question(
        teacher_id=teacher.id,
        content="下列反应中，属于氧化还原反应的是？",
        type=QuestionType.SINGLE_CHOICE,
        options=["A. NaCl", "B. HCl", "C. 2H2 + O2 → 2H2O", "D. NaOH"],
        answer="C",
        analysis="有化合价变化的是 C",
        knowledge_points=["氧化还原反应"],
        difficulty=Difficulty.MEDIUM,
        score=2.0,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def question_set(db: Session, teacher: Teacher) -> QuestionSet:
    """一个题库文件夹。"""
    obj = QuestionSet(name="氧化还原专题", teacher_id=teacher.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def paper(db: Session, teacher: Teacher) -> Paper:
    """一份草稿试卷。"""
    obj = Paper(title="期中测试", teacher_id=teacher.id, duration=60)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def exam(db: Session, paper: Paper, klass) -> Exam:
    """一个已发布考试实例。"""
    obj = Exam(paper_id=paper.id, class_id=klass.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# --------------------------------------------------------------------------- #
# 枚举 CHECK 约束
# --------------------------------------------------------------------------- #


class TestEnumCheckConstraints:
    def test_question_type_rejects_garbage(self, db: Session, question: Question) -> None:
        _expect_check_violation(
            db, "UPDATE questions SET type = :v WHERE id = :i", {"v": "essay_plus", "i": question.id}
        )

    def test_question_difficulty_rejects_garbage(self, db: Session, question: Question) -> None:
        _expect_check_violation(
            db,
            "UPDATE questions SET difficulty = :v WHERE id = :i",
            {"v": "impossible", "i": question.id},
        )

    def test_paper_status_rejects_garbage(self, db: Session, paper: Paper) -> None:
        _expect_check_violation(
            db, "UPDATE papers SET status = :v WHERE id = :i", {"v": "frozen", "i": paper.id}
        )

    def test_exam_status_rejects_garbage(self, db: Session, exam: Exam) -> None:
        _expect_check_violation(
            db, "UPDATE exams SET status = :v WHERE id = :i", {"v": "done", "i": exam.id}
        )


# --------------------------------------------------------------------------- #
# 枚举入库格式
# --------------------------------------------------------------------------- #


class TestEnumStorageFormat:
    def test_question_enum_stored_as_value(self, db: Session, question: Question) -> None:
        raw = db.execute(
            text("SELECT type, difficulty FROM questions WHERE id = :i"), {"i": question.id}
        ).one()
        assert raw.type == "single_choice"
        assert raw.difficulty == "medium"

    def test_paper_status_defaults_to_draft(self, db: Session, paper: Paper) -> None:
        assert paper.status is PaperStatus.DRAFT
        raw = db.execute(text("SELECT status FROM papers WHERE id = :i"), {"i": paper.id}).one()
        assert raw.status == "draft"

    def test_exam_status_defaults_to_published(self, db: Session, exam: Exam) -> None:
        assert exam.status is ExamStatus.PUBLISHED
        raw = db.execute(text("SELECT status FROM exams WHERE id = :i"), {"i": exam.id}).one()
        assert raw.status == "published"

    def test_enum_round_trips_to_member(self, db: Session, question: Question) -> None:
        question_id = question.id
        db.expunge_all()
        loaded = db.get(Question, question_id)
        assert loaded is not None
        assert loaded.type is QuestionType.SINGLE_CHOICE
        assert loaded.difficulty is Difficulty.MEDIUM


# --------------------------------------------------------------------------- #
# 关系表唯一约束
# --------------------------------------------------------------------------- #


class TestUniqueConstraints:
    def test_question_set_item_duplicate_rejected(
        self, db: Session, question_set: QuestionSet, question: Question
    ) -> None:
        db.add(QuestionSetItem(question_set_id=question_set.id, question_id=question.id))
        db.commit()

        with pytest.raises(IntegrityError):
            db.add(QuestionSetItem(question_set_id=question_set.id, question_id=question.id))
            db.commit()
        db.rollback()

    def test_paper_question_duplicate_rejected(
        self, db: Session, paper: Paper, question: Question
    ) -> None:
        db.add(PaperQuestion(paper_id=paper.id, question_id=question.id))
        db.commit()

        with pytest.raises(IntegrityError):
            db.add(PaperQuestion(paper_id=paper.id, question_id=question.id))
            db.commit()
        db.rollback()


# --------------------------------------------------------------------------- #
# 软删/硬删边界
# --------------------------------------------------------------------------- #


class TestDeleteSemantics:
    def test_core_entities_have_soft_delete(self) -> None:
        for model in (Question, QuestionSet, Paper):
            assert "deleted_at" in model.__table__.columns, model.__name__

    def test_exam_and_junctions_have_no_soft_delete(self) -> None:
        for model in (Exam, QuestionSetItem, PaperQuestion):
            assert "deleted_at" not in model.__table__.columns, model.__name__

    def test_question_soft_delete_sets_deleted_at(self, db: Session, question: Question) -> None:
        question.soft_delete()
        db.commit()
        raw = db.execute(
            text("SELECT deleted_at FROM questions WHERE id = :i"), {"i": question.id}
        ).scalar()
        assert raw is not None

    def test_paper_question_fk_restrict_blocks_question_delete(
        self, db: Session, paper: Paper, question: Question
    ) -> None:
        db.add(PaperQuestion(paper_id=paper.id, question_id=question.id))
        db.commit()

        # 物理删除被 paper_questions RESTRICT 拦截（Question 本应软删）
        with pytest.raises(IntegrityError):
            db.delete(question)
            db.commit()
        db.rollback()


# --------------------------------------------------------------------------- #
# 派生字段不落库
# --------------------------------------------------------------------------- #


class TestDerivedFields:
    def test_total_score_and_question_count_not_stored(self) -> None:
        assert "total_score" not in Paper.__table__.columns
        assert "question_count" not in QuestionSet.__table__.columns

    def test_total_score_derived_by_query(
        self, db: Session, teacher: Teacher, paper: Paper, question: Question
    ) -> None:
        q2 = Question(
            teacher_id=teacher.id,
            content="第二题",
            type=QuestionType.TRUE_FALSE,
            answer="对",
            knowledge_points=["摩尔计算"],
            difficulty=Difficulty.EASY,
            score=3.0,
        )
        db.add(q2)
        db.flush()
        db.add(PaperQuestion(paper_id=paper.id, question_id=question.id, sort_order=1))
        db.add(PaperQuestion(paper_id=paper.id, question_id=q2.id, sort_order=2))
        db.commit()

        total = db.execute(
            select(func.coalesce(func.sum(Question.score), 0.0))
            .join(PaperQuestion, PaperQuestion.question_id == Question.id)
            .where(PaperQuestion.paper_id == paper.id)
        ).scalar()
        count = db.execute(
            select(func.count()).select_from(PaperQuestion).where(PaperQuestion.paper_id == paper.id)
        ).scalar()

        assert total == 5.0
        assert count == 2
