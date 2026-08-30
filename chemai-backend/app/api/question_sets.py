# -*- coding: utf-8 -*-
"""题库文件夹 CRUD API。

文件夹软删、is_preset 不可删、question_count 派生；加题/移题走 QuestionSetItem（硬删）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.api.questions import QuestionOut
from app.core.database import get_db
from app.models import Question, QuestionSet, QuestionSetItem, Teacher

router = APIRouter(tags=["题库"], prefix="/api/question-sets")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class QuestionSetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None


class QuestionSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None


class QuestionSetOut(BaseModel):
    id: int
    name: str
    teacher_id: int
    description: Optional[str]
    region: Optional[str]
    year: Optional[int]
    is_preset: bool
    question_count: int
    created_at: datetime
    updated_at: datetime


class AddQuestionRequest(BaseModel):
    question_id: int
    sort_order: int = 0


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _get_owned_set(db: Session, question_set_id: int, teacher_id: int) -> QuestionSet:
    """按 id + 教师归属取题库文件夹（软删过滤），不存在则 404。"""
    obj = db.execute(
        select(QuestionSet).where(
            QuestionSet.id == question_set_id,
            QuestionSet.deleted_at.is_(None),
            QuestionSet.teacher_id == teacher_id,
        )
    ).scalar_one_or_none()
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "题库文件夹不存在"},
        )
    return obj


def _serialize(s: QuestionSet, count: int) -> QuestionSetOut:
    """组装 QuestionSetOut（附派生的题目数）。"""
    return QuestionSetOut(
        id=s.id,
        name=s.name,
        teacher_id=s.teacher_id,
        description=s.description,
        region=s.region,
        year=s.year,
        is_preset=s.is_preset,
        question_count=count,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _count_questions(db: Session, question_set_id: int) -> int:
    """派生：文件夹内未软删题目数（join Question 过滤软删）。"""
    count = db.execute(
        select(func.count())
        .select_from(QuestionSetItem)
        .join(Question, Question.id == QuestionSetItem.question_id)
        .where(
            QuestionSetItem.question_set_id == question_set_id,
            Question.deleted_at.is_(None),
        )
    ).scalar()
    return count or 0


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("", response_model=QuestionSetOut, status_code=status.HTTP_201_CREATED, summary="创建题库文件夹")
def create_question_set(
    payload: QuestionSetCreate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> QuestionSetOut:
    """创建题库文件夹。"""
    obj = QuestionSet(teacher_id=teacher.id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _serialize(obj, 0)


@router.get("", response_model=list[QuestionSetOut], summary="题库文件夹列表")
def list_question_sets(
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[QuestionSetOut]:
    """本教师文件夹列表（附派生题目数）。"""
    sets = db.execute(
        select(QuestionSet)
        .where(QuestionSet.deleted_at.is_(None), QuestionSet.teacher_id == teacher.id)
        .order_by(QuestionSet.id)
    ).scalars().all()

    counts: dict[int, int] = {}
    if sets:
        rows = db.execute(
            select(QuestionSetItem.question_set_id, func.count())
            .join(Question, Question.id == QuestionSetItem.question_id)
            .where(
                QuestionSetItem.question_set_id.in_([s.id for s in sets]),
                Question.deleted_at.is_(None),
            )
            .group_by(QuestionSetItem.question_set_id)
        ).all()
        counts = {row[0]: row[1] for row in rows}

    return [_serialize(s, counts.get(s.id, 0)) for s in sets]


@router.get("/{question_set_id}", response_model=QuestionSetOut, summary="题库文件夹详情")
def get_question_set(
    question_set_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> QuestionSetOut:
    """文件夹详情（附派生题目数）。"""
    obj = _get_owned_set(db, question_set_id, teacher.id)
    return _serialize(obj, _count_questions(db, obj.id))


@router.put("/{question_set_id}", response_model=QuestionSetOut, summary="更新题库文件夹")
def update_question_set(
    question_set_id: int,
    payload: QuestionSetUpdate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> QuestionSetOut:
    """更新文件夹。"""
    obj = _get_owned_set(db, question_set_id, teacher.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return _serialize(obj, _count_questions(db, obj.id))


@router.delete("/{question_set_id}", status_code=status.HTTP_204_NO_CONTENT, summary="软删题库文件夹")
def delete_question_set(
    question_set_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """软删文件夹（is_preset 拒绝）。"""
    obj = _get_owned_set(db, question_set_id, teacher.id)
    if obj.is_preset:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "系统预设题库不可删除"},
        )
    obj.soft_delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{question_set_id}/questions",
    response_model=list[QuestionOut],
    summary="文件夹内题目列表",
)
def list_questions_in_set(
    question_set_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[Question]:
    """列出文件夹内题目（按 sort_order 升序，同序按题目 id 稳定，过滤软删题）。"""
    _get_owned_set(db, question_set_id, teacher.id)
    return db.execute(
        select(Question)
        .join(QuestionSetItem, QuestionSetItem.question_id == Question.id)
        .where(
            QuestionSetItem.question_set_id == question_set_id,
            Question.deleted_at.is_(None),
        )
        .order_by(QuestionSetItem.sort_order, QuestionSetItem.question_id)
    ).scalars().all()


@router.post("/{question_set_id}/questions", status_code=status.HTTP_201_CREATED, summary="文件夹加题")
def add_question_to_set(
    question_set_id: int,
    payload: AddQuestionRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> dict:
    """文件夹加题（重复 409）。"""
    obj = _get_owned_set(db, question_set_id, teacher.id)

    question = db.execute(
        select(Question).where(
            Question.id == payload.question_id,
            Question.deleted_at.is_(None),
            Question.teacher_id == teacher.id,
        )
    ).scalar_one_or_none()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "题目不存在"},
        )

    exists = db.execute(
        select(QuestionSetItem.id).where(
            QuestionSetItem.question_set_id == obj.id,
            QuestionSetItem.question_id == payload.question_id,
        )
    ).first()
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "题目已在该文件夹中"},
        )

    item = QuestionSetItem(
        question_set_id=obj.id, question_id=payload.question_id, sort_order=payload.sort_order
    )
    db.add(item)
    db.commit()
    return {"question_set_id": obj.id, "question_id": payload.question_id}


@router.delete(
    "/{question_set_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="文件夹移题",
)
def remove_question_from_set(
    question_set_id: int,
    question_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """文件夹移题（仅删关联，不删题）。"""
    _get_owned_set(db, question_set_id, teacher.id)

    item = db.execute(
        select(QuestionSetItem).where(
            QuestionSetItem.question_set_id == question_set_id,
            QuestionSetItem.question_id == question_id,
        )
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "题目不在该文件夹中"},
        )

    # 仅删除关联记录，不删除题目本身（共享引用）
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
