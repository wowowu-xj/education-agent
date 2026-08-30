# -*- coding: utf-8 -*-
"""题目 CRUD API。

题库管理：创建/列表/详情/更新/软删题目，按教师数据隔离。
被 locked Paper 引用的题目删除返回 409。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.core.enums import Difficulty, PaperStatus, QuestionType
from app.models import Paper, PaperQuestion, Question, Teacher
from app.services.vector_search import vector_search

router = APIRouter(tags=["题库"], prefix="/api/questions")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class QuestionCreate(BaseModel):
    """创建题目请求体（手动录入，9 题型 / 4 难度全开放）。"""

    content: str
    type: QuestionType
    options: Optional[list[str]] = None
    answer: str
    analysis: Optional[str] = None
    knowledge_points: list[str] = Field(default_factory=list)
    difficulty: Difficulty
    score: float = 0.0
    source_name: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None


class QuestionUpdate(BaseModel):
    """更新题目请求体（仅提交需要修改的字段）。"""

    content: Optional[str] = None
    type: Optional[QuestionType] = None
    options: Optional[list[str]] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    knowledge_points: Optional[list[str]] = None
    difficulty: Optional[Difficulty] = None
    score: Optional[float] = None
    source_name: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None


class QuestionOut(BaseModel):
    """题目响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: Optional[int]
    content: str
    type: QuestionType
    options: Optional[list]
    answer: str
    analysis: Optional[str]
    knowledge_points: list
    difficulty: Difficulty
    score: float
    source_name: Optional[str]
    region: Optional[str]
    year: Optional[int]
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    """语义召回请求体。"""

    query: str
    top_k: int = 5
    type: Optional[QuestionType] = None
    difficulty: Optional[Difficulty] = None
    knowledge_point: Optional[str] = None


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _get_owned_question(db: Session, question_id: int, teacher_id: int) -> Question:
    """按 id + 教师归属取题目（软删过滤），不存在则 404。"""
    question = db.execute(
        select(Question).where(
            Question.id == question_id,
            Question.deleted_at.is_(None),
            Question.teacher_id == teacher_id,
        )
    ).scalar_one_or_none()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "题目不存在"},
        )
    return question


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("", response_model=QuestionOut, status_code=status.HTTP_201_CREATED, summary="创建题目")
def create_question(
    payload: QuestionCreate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Question:
    """手动录入题目（teacher_id 记录创建者）。"""
    question = Question(teacher_id=teacher.id, **payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    vector_search.index_question(question)
    return question


@router.get("", response_model=list[QuestionOut], summary="题目列表（结构化过滤）")
def list_questions(
    type: Optional[QuestionType] = None,
    difficulty: Optional[Difficulty] = None,
    knowledge_point: Optional[str] = None,
    source_name: Optional[str] = None,
    region: Optional[str] = None,
    year: Optional[int] = None,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[Question]:
    """按题型/难度/来源地区/年份结构化过滤，仅返回本教师题目。

    knowledge_point 过滤在 Python 侧完成：JSON 数组包含判定跨 SQLite/MySQL
    方言无统一原生实现，教师个人题库量级下 Python 过滤足够快且行为确定。
    """
    stmt = select(Question).where(
        Question.deleted_at.is_(None), Question.teacher_id == teacher.id
    )
    if type is not None:
        stmt = stmt.where(Question.type == type)
    if difficulty is not None:
        stmt = stmt.where(Question.difficulty == difficulty)
    if source_name is not None:
        stmt = stmt.where(Question.source_name == source_name)
    if region is not None:
        stmt = stmt.where(Question.region == region)
    if year is not None:
        stmt = stmt.where(Question.year == year)

    questions = db.execute(stmt.order_by(Question.id)).scalars().all()
    if knowledge_point is not None:
        questions = [q for q in questions if knowledge_point in (q.knowledge_points or [])]
    return questions


@router.post("/search", response_model=list[QuestionOut], summary="语义召回题目")
def search_questions(
    payload: SearchRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[Question]:
    """两层检索：关键词粗筛 → 向量精筛，返回相似题目（教师数据隔离）。"""
    return vector_search.search(
        db,
        payload.query,
        teacher.id,
        top_k=payload.top_k,
        type=payload.type,
        difficulty=payload.difficulty,
        knowledge_point=payload.knowledge_point,
    )


@router.get("/{question_id}", response_model=QuestionOut, summary="题目详情")
def get_question(
    question_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Question:
    """题目详情。"""
    return _get_owned_question(db, question_id, teacher.id)


@router.put("/{question_id}", response_model=QuestionOut, summary="更新题目")
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Question:
    """更新题目并重索引向量。"""
    question = _get_owned_question(db, question_id, teacher.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    vector_search.reindex_question(question)
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="软删题目")
def delete_question(
    question_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """软删题目（被 locked 试卷引用则 409）。"""
    question = _get_owned_question(db, question_id, teacher.id)

    # 被 locked Paper 引用时不可删（已发布考试的完整性）
    locked_ref = db.execute(
        select(PaperQuestion.id)
        .join(Paper, Paper.id == PaperQuestion.paper_id)
        .where(
            PaperQuestion.question_id == question_id,
            Paper.status == PaperStatus.LOCKED,
            Paper.deleted_at.is_(None),
        )
        .limit(1)
    ).first()
    if locked_ref is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "题目被已发布试卷引用，不可删除"},
        )

    question.soft_delete()
    db.commit()
    vector_search.remove_question(question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
