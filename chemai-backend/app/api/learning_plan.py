# -*- coding: utf-8 -*-
"""学习计划 API。

覆盖 diagnosis-learning-plan spec：生成（带 24h 缓存）、获取、应用
（写 ``students.current_plan``）、发送家长（写 ``parent_notifications``）、
删除（未应用计划）。数据隔离：教师仅见任课班级学生（TeacherClassSubject）。
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.models import (
    ParentNotification,
    Student,
    StudentAnswer,
    StudentParentBinding,
    Teacher,
    TeacherClassSubject,
)
from chem_skills.chemistry_diagnosis.engine.aggregator import knowledge_points_for
from chem_skills.chemistry_diagnosis.engine.learning_plan import LearningPlanGenerator
from chem_skills.chemistry_diagnosis.engine.llm_client import (
    _PLAN_REPAIR_INSTRUCTION,
    DashScopeDiagnosisClient,
    parse_plan_json,
)

router = APIRouter(tags=["学习计划"], prefix="/api/learning-plans")

# ---------------------------------------------------------------------------
# 学习计划生成器注入缝（测试经 dependency_overrides 注入 FakeLLM）
# ---------------------------------------------------------------------------

_generator: LearningPlanGenerator | None = None


def get_plan_generator() -> LearningPlanGenerator:
    """返回进程级学习计划生成器单例（惰性构建）。"""
    global _generator
    if _generator is None:
        _generator = LearningPlanGenerator(
            DashScopeDiagnosisClient(
                parse=parse_plan_json,
                repair_instruction=_PLAN_REPAIR_INSTRUCTION,
            )
        )
    return _generator


# ---------------------------------------------------------------------------
# Pydantic 模型
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    """生成学习计划请求。"""

    student_id: int


class SendToParentResponse(BaseModel):
    """发送家长响应。"""

    student_id: int
    sent_to: list[int]
    count: int


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------


def _teacher_teaches_class(db: Session, teacher_id: int, class_id: int) -> bool:
    """教师是否任课该班级。"""
    return (
        db.execute(
            select(TeacherClassSubject.id).where(
                TeacherClassSubject.teacher_id == teacher_id,
                TeacherClassSubject.class_id == class_id,
            ).limit(1)
        ).scalar_one_or_none()
        is not None
    )


def _get_owned_student(db: Session, student_id: int, teacher_id: int) -> Student:
    """按 id 取学生并校验教师任课其班级，否则 404/403。"""
    student = db.execute(
        select(Student).where(Student.id == student_id, Student.deleted_at.is_(None))
    ).scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "学生不存在"},
        )
    if not _teacher_teaches_class(db, teacher_id, student.class_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "无权操作该学生"},
        )
    return student


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("/generate", summary="生成学习计划")
def generate_plan(
    payload: GenerateRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    generator: LearningPlanGenerator = Depends(get_plan_generator),
) -> dict:
    """基于学生诊断结果生成学习计划（24h 缓存，命中不重复调用 LLM）。"""
    student = _get_owned_student(db, payload.student_id, teacher.id)

    answers = db.execute(
        select(StudentAnswer).where(
            StudentAnswer.student_id == student.id,
            StudentAnswer.is_correct == False,  # noqa: E712
            StudentAnswer.barrier_type.isnot(None),
        )
    ).scalars().all()

    barrier_types = sorted({a.barrier_type for a in answers}, key=lambda b: b.value)
    misconceptions = [
        a.misconception_category.value
        for a in answers
        if a.misconception_category is not None
    ]

    return generator.generate(
        student_id=student.id,
        student_name=student.name,
        barrier_types=barrier_types,
        weak_knowledge_points=knowledge_points_for(misconceptions),
    )


@router.get("/{student_id}", summary="获取学习计划")
def get_plan(
    student_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    generator: LearningPlanGenerator = Depends(get_plan_generator),
) -> dict:
    """返回学生当前计划：优先已应用 current_plan，其次生成缓存。"""
    student = _get_owned_student(db, student_id, teacher.id)
    plan = student.current_plan or generator.peek(student_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "该学生尚无学习计划"},
        )
    return plan


@router.post("/{student_id}/apply", summary="应用学习计划")
def apply_plan(
    student_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    generator: LearningPlanGenerator = Depends(get_plan_generator),
) -> dict:
    """把最近生成（缓存）的计划写入 students.current_plan，学生端可见。"""
    student = _get_owned_student(db, student_id, teacher.id)
    plan = generator.peek(student_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "尚未生成学习计划，请先调用 generate"},
        )

    student.current_plan = plan
    generator.invalidate(student_id)  # 计划已应用，刷新生成缓存
    db.commit()
    return plan


@router.post("/{student_id}/send-to-parent", response_model=SendToParentResponse, summary="发送家长")
def send_to_parent(
    student_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    generator: LearningPlanGenerator = Depends(get_plan_generator),
) -> SendToParentResponse:
    """把学生计划推送给绑定家长，写入 parent_notifications。"""
    student = _get_owned_student(db, student_id, teacher.id)
    plan = student.current_plan or generator.peek(student_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": "该学生尚无学习计划"},
        )

    bindings = db.execute(
        select(StudentParentBinding).where(
            StudentParentBinding.student_id == student_id,
            StudentParentBinding.is_active == True,  # noqa: E712
        )
    ).scalars().all()
    if not bindings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "no_parent", "message": "该学生没有绑定的家长"},
        )

    content = json.dumps(plan, ensure_ascii=False)
    for b in bindings:
        db.add(
            ParentNotification(
                student_id=student_id,
                parent_id=b.parent_id,
                type="learning_plan",
                content=content,
            )
        )
    db.commit()

    return SendToParentResponse(
        student_id=student_id,
        sent_to=[b.parent_id for b in bindings],
        count=len(bindings),
    )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除未应用计划")
def delete_plan(
    student_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    generator: LearningPlanGenerator = Depends(get_plan_generator),
) -> Response:
    """删除未应用（生成缓存中的）学习计划；幂等。"""
    _get_owned_student(db, student_id, teacher.id)
    generator.invalidate(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
