# -*- coding: utf-8 -*-
"""考试教师侧状态机 API。

考试列表（按班/状态过滤）、取消（published/in_progress → cancelled）、
finalize（grading → completed）；非法迁移返回 409。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.core.enums import ExamStatus
from app.models import Exam, ExamStatusTransition, Paper, Teacher

router = APIRouter(tags=["考试"], prefix="/api/exams")


class ExamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paper_id: int
    class_id: int
    exam_date: Optional[datetime]
    status: ExamStatus
    created_at: datetime
    updated_at: datetime


def _get_owned_exam(db: Session, exam_id: int, teacher_id: int) -> Exam:
    """按 id + 教师归属取考试（经 Paper 隔离），不存在则 404。"""
    exam = db.execute(
        select(Exam)
        .join(Paper, Paper.id == Exam.paper_id)
        .where(
            Exam.id == exam_id,
            Paper.teacher_id == teacher_id,
            Paper.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "考试不存在"},
        )
    return exam


def _transition(db: Session, exam: Exam, to_status: ExamStatus, operator_id: int) -> Exam:
    """记录迁移审计并推进状态。

    from_status 取自推进前的 exam.status，追加一条 audit 行后提交，
    保证「每次迁移留痕」且 from/to 与时间戳一致。
    """
    db.add(
        ExamStatusTransition(
            exam_id=exam.id,
            from_status=exam.status,
            to_status=to_status,
            operator_id=operator_id,
        )
    )
    exam.status = to_status
    db.commit()
    db.refresh(exam)
    return exam


@router.get("", response_model=list[ExamOut], summary="考试列表")
def list_exams(
    class_id: Optional[int] = None,
    status_filter: Optional[ExamStatus] = None,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[Exam]:
    """本教师考试列表（按班/状态过滤）。"""
    stmt = (
        select(Exam)
        .join(Paper, Paper.id == Exam.paper_id)
        .where(Paper.teacher_id == teacher.id, Paper.deleted_at.is_(None))
    )
    if class_id is not None:
        stmt = stmt.where(Exam.class_id == class_id)
    if status_filter is not None:
        stmt = stmt.where(Exam.status == status_filter)
    return db.execute(stmt.order_by(Exam.id)).scalars().all()


@router.post("/{exam_id}/cancel", response_model=ExamOut, summary="取消考试")
def cancel_exam(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Exam:
    """取消考试（published/in_progress → cancelled）。"""
    exam = _get_owned_exam(db, exam_id, teacher.id)
    if exam.status not in (ExamStatus.PUBLISHED, ExamStatus.IN_PROGRESS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "仅 published/in_progress 状态可取消"},
        )
    return _transition(db, exam, ExamStatus.CANCELLED, teacher.id)


@router.post("/{exam_id}/start", response_model=ExamOut, summary="开考")
def start_exam(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Exam:
    """开考（published → in_progress）。"""
    exam = _get_owned_exam(db, exam_id, teacher.id)
    if exam.status != ExamStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "仅 published 状态可开考"},
        )
    return _transition(db, exam, ExamStatus.IN_PROGRESS, teacher.id)


@router.post("/{exam_id}/collect", response_model=ExamOut, summary="收卷")
def collect_exam(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Exam:
    """收卷进入阅卷（in_progress → grading）。"""
    exam = _get_owned_exam(db, exam_id, teacher.id)
    if exam.status != ExamStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "仅 in_progress 状态可收卷"},
        )
    return _transition(db, exam, ExamStatus.GRADING, teacher.id)


@router.post("/{exam_id}/finalize", response_model=ExamOut, summary="批阅完成")
def finalize_exam(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Exam:
    """批阅完成（grading → completed）。"""
    exam = _get_owned_exam(db, exam_id, teacher.id)
    if exam.status != ExamStatus.GRADING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "仅 grading 状态可 finalize"},
        )
    return _transition(db, exam, ExamStatus.COMPLETED, teacher.id)


@router.post("/{exam_id}/archive", response_model=ExamOut, summary="归档")
def archive_exam(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Exam:
    """归档（completed → archived）。archived 为终态，不再提供反向迁移。"""
    exam = _get_owned_exam(db, exam_id, teacher.id)
    if exam.status != ExamStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "仅 completed 状态可归档"},
        )
    return _transition(db, exam, ExamStatus.ARCHIVED, teacher.id)
