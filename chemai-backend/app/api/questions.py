# -*- coding: utf-8 -*-
"""题目 CRUD API。

题库管理：创建/列表/详情/更新/软删题目，按教师数据隔离。
被 locked Paper 引用的题目删除返回 409。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.core.enums import Difficulty, PaperStatus, QuestionType
from app.models import Paper, PaperQuestion, Question, QuestionSetItem, Teacher
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


class QuestionPage(BaseModel):
    """题目列表分页响应（items + 分页元数据）。"""

    items: list[QuestionOut]
    total: int
    page: int
    page_size: int


class SearchRequest(BaseModel):
    """语义召回请求体。"""

    query: str
    top_k: int = 5
    type: Optional[QuestionType] = None
    difficulty: Optional[Difficulty] = None
    knowledge_point: Optional[str] = None
    exclude_question_id: Optional[int] = None


class QuestionSearchHit(QuestionOut):
    """语义召回命中：题目字段平铺 + 相似度 + 降级标志。"""

    similarity: float
    degraded: bool


class QuestionBatchRequest(BaseModel):
    """批量导入请求体（原始题目对象数组，逐题校验）。"""

    items: list[dict]


class QuestionBatchPreviewItem(BaseModel):
    """批量导入预览的逐题结果。"""

    index: int
    valid: bool
    question: Optional[QuestionCreate] = None
    errors: list[str] = Field(default_factory=list)


class QuestionBatchPreviewOut(BaseModel):
    """批量导入预览响应。"""

    items: list[QuestionBatchPreviewItem]
    valid_count: int
    invalid_count: int


class QuestionBatchCommitResult(BaseModel):
    """批量导入确认的逐题结果。"""

    index: int
    status: str  # created | failed
    question_id: Optional[int] = None
    reason: Optional[str] = None


class QuestionBatchCommitOut(BaseModel):
    """批量导入确认响应。"""

    success_count: int
    failed_count: int
    results: list[QuestionBatchCommitResult]


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


def _format_validation_errors(exc: ValidationError) -> list[str]:
    """将 Pydantic 校验错误展平为「字段: 原因」的可读字符串列表。"""
    return [
        f"{'.'.join(str(p) for p in err.get('loc', ()))}: {err.get('msg', '')}"
        for err in exc.errors()
    ]


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


@router.post("/batch/preview", response_model=QuestionBatchPreviewOut, summary="批量导入预览")
def batch_preview(
    payload: QuestionBatchRequest,
    teacher: Teacher = Depends(get_current_teacher),
) -> QuestionBatchPreviewOut:
    """逐题解析并校验批量导入内容，不落库，返回可导入题数与错误明细。

    `teacher` 仅作鉴权门，预览校验与归属无关。
    """
    items: list[QuestionBatchPreviewItem] = []
    valid_count = 0
    invalid_count = 0
    for index, raw in enumerate(payload.items):
        try:
            question = QuestionCreate.model_validate(raw)
        except ValidationError as exc:
            invalid_count += 1
            items.append(
                QuestionBatchPreviewItem(
                    index=index, valid=False, errors=_format_validation_errors(exc)
                )
            )
        else:
            valid_count += 1
            items.append(QuestionBatchPreviewItem(index=index, valid=True, question=question))
    return QuestionBatchPreviewOut(
        items=items, valid_count=valid_count, invalid_count=invalid_count
    )


@router.post("/batch/commit", response_model=QuestionBatchCommitOut, summary="批量导入确认")
def batch_commit(
    payload: QuestionBatchRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> QuestionBatchCommitOut:
    """重校验后逐题写入通过项并建向量索引，返回成功/失败统计与逐题原因。

    逐题独立提交：单题失败捕获后计入「失败」并继续，不整体回滚。
    """
    results: list[QuestionBatchCommitResult] = []
    success_count = 0
    failed_count = 0
    for index, raw in enumerate(payload.items):
        try:
            question_data = QuestionCreate.model_validate(raw)
        except ValidationError as exc:
            failed_count += 1
            results.append(
                QuestionBatchCommitResult(
                    index=index, status="failed", reason=_format_validation_errors(exc)[0]
                )
            )
            continue
        try:
            question = Question(teacher_id=teacher.id, **question_data.model_dump())
            db.add(question)
            db.commit()
            db.refresh(question)
            vector_search.index_question(question)
        except Exception as exc:  # noqa: BLE001 - 逐题失败不阻断整体
            db.rollback()
            failed_count += 1
            results.append(
                QuestionBatchCommitResult(index=index, status="failed", reason=str(exc))
            )
            continue
        success_count += 1
        results.append(
            QuestionBatchCommitResult(index=index, status="created", question_id=question.id)
        )
    return QuestionBatchCommitOut(
        success_count=success_count, failed_count=failed_count, results=results
    )


@router.get("", response_model=QuestionPage, summary="题目列表（分页 + 结构化过滤）")
def list_questions(
    type: Optional[QuestionType] = None,
    difficulty: Optional[Difficulty] = None,
    knowledge_point: Optional[str] = None,
    source_name: Optional[str] = None,
    region: Optional[str] = None,
    year: Optional[int] = None,
    exclude_question_set_id: Optional[int] = None,
    exclude_paper_id: Optional[int] = None,
    question_set_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> QuestionPage:
    """按题型/难度/来源地区/年份结构化过滤 + 分页，仅返回本教师题目。

    可选 exclude_question_set_id / exclude_paper_id 用于「加入题目 / 组卷」选择器：
    排除已在该文件夹/试卷内的题目（NOT EXISTS），跨文件夹/试卷互斥、不互相影响。
    可选 question_set_id 用于限定选题范围为某文件夹内的题目。

    组合筛选为 AND 语义。knowledge_point 过滤在 Python 侧完成：JSON 数组
    包含判定跨 SQLite/MySQL 方言无统一原生实现，教师个人题库量级下 Python
    过滤足够快且行为确定，故分页也在过滤后切片。
    """
    # 越界参数钳制而非 422：page ≤ 0 视作第 1 页，page_size 上限 100。
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

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
    if exclude_question_set_id is not None:
        # 加题选择器：排除已在该文件夹内的题目，避免用户重复勾选。
        # NOT EXISTS 只作用于本教师题目（外层已限 teacher_id），跨文件夹不互斥。
        stmt = stmt.where(
            ~exists().where(
                QuestionSetItem.question_set_id == exclude_question_set_id,
                QuestionSetItem.question_id == Question.id,
            )
        )
    if exclude_paper_id is not None:
        # 组卷选择器：排除已在该试卷内的题目，避免重复加题。
        stmt = stmt.where(
            ~exists().where(
                PaperQuestion.paper_id == exclude_paper_id,
                PaperQuestion.question_id == Question.id,
            )
        )
    if question_set_id is not None:
        # 文件夹过滤：仅保留该文件夹内的题目（可选选题范围）。
        stmt = stmt.where(
            exists().where(
                QuestionSetItem.question_set_id == question_set_id,
                QuestionSetItem.question_id == Question.id,
            )
        )

    questions = db.execute(stmt.order_by(Question.id)).scalars().all()
    if knowledge_point is not None:
        questions = [q for q in questions if knowledge_point in (q.knowledge_points or [])]

    total = len(questions)
    start = (page - 1) * page_size
    return QuestionPage(
        items=questions[start : start + page_size],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/search", response_model=list[QuestionSearchHit], summary="语义召回题目")
def search_questions(
    payload: SearchRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[QuestionSearchHit]:
    """两层检索：关键词粗筛 → 向量精筛，返回相似题目 + 相似度 + 降级标注（教师数据隔离）。"""
    hits = vector_search.search(
        db,
        payload.query,
        teacher.id,
        top_k=payload.top_k,
        type=payload.type,
        difficulty=payload.difficulty,
        knowledge_point=payload.knowledge_point,
        exclude_question_id=payload.exclude_question_id,
    )
    result: list[QuestionSearchHit] = []
    for hit in hits:
        data = QuestionOut.model_validate(hit.question).model_dump()
        data["similarity"] = hit.similarity
        data["degraded"] = hit.degraded
        result.append(QuestionSearchHit(**data))
    return result


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
