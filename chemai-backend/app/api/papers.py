# -*- coding: utf-8 -*-
"""组卷与发布 API。

试卷 CRUD（软删、locked 后只读）、组卷加题/移题（draft 可改）、
发布到 N 个班（生成 N 个 Exam，Paper → locked）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.core.enums import ExamStatus, PaperStatus
from app.models import Class, Exam, Grade, Paper, PaperQuestion, Question, Teacher
from app.services.paper_export import render_docx, render_html

router = APIRouter(tags=["组卷"], prefix="/api/papers")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PaperCreate(BaseModel):
    title: str
    duration: Optional[int] = None


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    duration: Optional[int] = None


class PaperOut(BaseModel):
    id: int
    title: str
    teacher_id: int
    duration: Optional[int]
    status: PaperStatus
    question_count: int
    total_score: float
    created_at: datetime
    updated_at: datetime


class AddQuestionRequest(BaseModel):
    question_id: int
    sort_order: int = 0


class PublishRequest(BaseModel):
    class_ids: list[int]
    exam_date: Optional[datetime] = None


class PublishResponse(BaseModel):
    paper_id: int
    status: PaperStatus
    exam_ids: list[int]


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _get_owned_paper(db: Session, paper_id: int, teacher_id: int) -> Paper:
    """按 id + 教师归属取试卷（软删过滤），不存在则 404。"""
    paper = db.execute(
        select(Paper).where(
            Paper.id == paper_id,
            Paper.deleted_at.is_(None),
            Paper.teacher_id == teacher_id,
        )
    ).scalar_one_or_none()
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "试卷不存在"},
        )
    return paper


def _derived(db: Session, paper_id: int) -> tuple[int, float]:
    """派生字段：题目数与总分（由 PaperQuestion 关联题目实时求和）。"""
    count, total = db.execute(
        select(func.count(), func.coalesce(func.sum(Question.score), 0.0))
        .select_from(PaperQuestion)
        .join(Question, Question.id == PaperQuestion.question_id)
        .where(PaperQuestion.paper_id == paper_id, Question.deleted_at.is_(None))
    ).one()
    return count, float(total)


def _serialize(paper: Paper, count: int, total: float) -> PaperOut:
    """组装 PaperOut（附派生的题目数与总分）。"""
    return PaperOut(
        id=paper.id,
        title=paper.title,
        teacher_id=paper.teacher_id,
        duration=paper.duration,
        status=paper.status,
        question_count=count,
        total_score=total,
        created_at=paper.created_at,
        updated_at=paper.updated_at,
    )


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("", response_model=PaperOut, status_code=status.HTTP_201_CREATED, summary="创建试卷")
def create_paper(
    payload: PaperCreate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> PaperOut:
    """创建试卷（draft）。"""
    paper = Paper(teacher_id=teacher.id, **payload.model_dump())
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return _serialize(paper, 0, 0.0)


@router.get("", response_model=list[PaperOut], summary="试卷列表")
def list_papers(
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[PaperOut]:
    """本教师试卷列表（软删过滤，附派生题目数与总分）。"""
    papers = db.execute(
        select(Paper)
        .where(Paper.deleted_at.is_(None), Paper.teacher_id == teacher.id)
        .order_by(Paper.id)
    ).scalars().all()
    return [_serialize(p, *_derived(db, p.id)) for p in papers]


@router.get("/{paper_id}", response_model=PaperOut, summary="试卷详情")
def get_paper(
    paper_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> PaperOut:
    """试卷详情（附派生题目数与总分）。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)
    return _serialize(paper, *_derived(db, paper.id))


@router.put("/{paper_id}", response_model=PaperOut, summary="更新试卷")
def update_paper(
    paper_id: int,
    payload: PaperUpdate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> PaperOut:
    """更新试卷（locked 拒绝）。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)
    if paper.status == PaperStatus.LOCKED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "已发布试卷不可修改"},
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(paper, field, value)
    db.commit()
    db.refresh(paper)
    return _serialize(paper, *_derived(db, paper.id))


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT, summary="软删试卷")
def delete_paper(
    paper_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """软删试卷（被 Exam 引用则 409）。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)

    # 被 Exam 引用（已发布过）则不可删
    exam_ref = db.execute(
        select(Exam.id).where(Exam.paper_id == paper_id).limit(1)
    ).first()
    if exam_ref is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "试卷已发布为考试，不可删除"},
        )

    paper.soft_delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{paper_id}/questions", status_code=status.HTTP_201_CREATED, summary="组卷加题")
def add_question_to_paper(
    paper_id: int,
    payload: AddQuestionRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> dict:
    """组卷加题（draft 可改，重复 409）。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)
    if paper.status == PaperStatus.LOCKED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "已发布试卷不可加题"},
        )

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
        select(PaperQuestion.id).where(
            PaperQuestion.paper_id == paper_id,
            PaperQuestion.question_id == payload.question_id,
        )
    ).first()
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "题目已在试卷中"},
        )

    db.add(
        PaperQuestion(paper_id=paper_id, question_id=payload.question_id, sort_order=payload.sort_order)
    )
    db.commit()
    return {"paper_id": paper_id, "question_id": payload.question_id}


@router.delete(
    "/{paper_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="组卷移题",
)
def remove_question_from_paper(
    paper_id: int,
    question_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """组卷移题（draft 可改）。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)
    if paper.status == PaperStatus.LOCKED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "已发布试卷不可移题"},
        )

    item = db.execute(
        select(PaperQuestion).where(
            PaperQuestion.paper_id == paper_id,
            PaperQuestion.question_id == question_id,
        )
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "题目不在试卷中"},
        )

    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{paper_id}/publish", response_model=PublishResponse, summary="发布到 N 个班")
def publish_paper(
    paper_id: int,
    payload: PublishRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> PublishResponse:
    """发布到 N 个班：校验目标班级、生成 N 个 Exam、Paper → locked。"""
    paper = _get_owned_paper(db, paper_id, teacher.id)
    if paper.status == PaperStatus.LOCKED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "试卷已发布，不可重复发布"},
        )

    count = db.execute(
        select(func.count()).select_from(PaperQuestion).where(PaperQuestion.paper_id == paper_id)
    ).scalar()
    if not count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "试卷至少需要 1 道题才能发布"},
        )

    # 校验班级存在且属于本教师学校（数据隔离）
    class_ids = list(dict.fromkeys(payload.class_ids))  # 去重，保持顺序
    if not class_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "validation", "message": "至少指定一个班级"},
        )
    rows = db.execute(
        select(Class.id, Grade.school_id)
        .join(Grade, Grade.id == Class.grade_id)
        .where(Class.id.in_(class_ids))
    ).all()
    found = {row[0]: row[1] for row in rows}
    if len(found) != len(class_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "部分班级不存在"},
        )
    if any(school_id != teacher.school_id for school_id in found.values()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "不能向其他学校的班级发布"},
        )

    exam_ids: list[int] = []
    for cid in class_ids:
        exam = Exam(
            paper_id=paper.id,
            class_id=cid,
            exam_date=payload.exam_date,
            status=ExamStatus.PUBLISHED,
        )
        db.add(exam)
        db.flush()
        exam_ids.append(exam.id)

    paper.status = PaperStatus.LOCKED
    db.commit()
    return PublishResponse(paper_id=paper.id, status=paper.status, exam_ids=exam_ids)


@router.get("/{paper_id}/export", summary="导出试卷")
def export_paper(
    paper_id: int,
    format: str = Query("html", pattern="^(html|docx)$"),
    include_answer: bool = Query(True),
    include_analysis: bool = Query(True),
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> Response:
    """导出任意状态 Paper（draft 预览 / locked 正式导出）。

    format=html 返回打印友好 HTML；format=docx 返回 Word 文档附件。
    """
    paper = _get_owned_paper(db, paper_id, teacher.id)
    questions = db.execute(
        select(Question)
        .join(PaperQuestion, PaperQuestion.question_id == Question.id)
        .where(PaperQuestion.paper_id == paper_id, Question.deleted_at.is_(None))
        .order_by(PaperQuestion.sort_order, PaperQuestion.id)
    ).scalars().all()

    if format == "html":
        return HTMLResponse(
            content=render_html(
                paper.title, paper.duration, questions, include_answer, include_analysis
            )
        )
    return Response(
        content=render_docx(
            paper.title, paper.duration, questions, include_answer, include_analysis
        ),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="paper_{paper_id}.docx"'},
    )
