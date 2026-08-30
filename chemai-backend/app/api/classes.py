# -*- coding: utf-8 -*-
"""班级列表 API。

教师端按任课关系（TeacherClassSubject）返回任教班级，供发布试卷选班、考试状态解析。
沿用 organization-hierarchy「数据范围隔离」语义：普通教师仅见任教班级。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.models import Class, Teacher, TeacherClassSubject

router = APIRouter(tags=["班级"], prefix="/api/classes")


class ClassOut(BaseModel):
    """班级响应模型（仅 id 与名称，供前端展示与提交 class_ids）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


@router.get("", response_model=list[ClassOut], summary="班级列表")
def list_classes(
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[Class]:
    """本教师任教班级列表（经 TeacherClassSubject 过滤，软删过滤）。"""
    return db.execute(
        select(Class)
        .join(TeacherClassSubject, TeacherClassSubject.class_id == Class.id)
        .where(
            TeacherClassSubject.teacher_id == teacher.id,
            Class.deleted_at.is_(None),
        )
        .order_by(Class.id)
    ).scalars().all()
