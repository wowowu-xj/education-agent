# -*- coding: utf-8 -*-
"""API 依赖项：从请求态解析当前教师身份。"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Account, Teacher


def get_current_teacher(
    request: Request,
    db: Session = Depends(get_db),
) -> Teacher:
    """解析当前请求对应的教师，作为数据隔离的锚点。

    认证中间件把 Account.id 写入 ``request.state.user_id``；
    这里经 ``Account.teacher_id`` 反查 Teacher。所有题库/试卷/考试的
    读写都以返回的 ``teacher.id`` 过滤，保证教师只能操作自己的数据。
    """
    account_id = request.state.user_id
    teacher = db.execute(
        select(Teacher)
        .join(Account, Account.teacher_id == Teacher.id)
        .where(Account.id == account_id, Teacher.deleted_at.is_(None))
    ).scalar_one_or_none()

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "当前账号不是有效教师身份"},
        )
    return teacher


__all__ = ["get_current_teacher"]
