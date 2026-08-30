# -*- coding: utf-8 -*-
"""重建向量索引：把未删除题目用当前 embedding 重新入库。

用途：embedding 从「降级（MD5 伪向量）」切到「真实（dashscope）」、
或更换模型 / 维度后，旧向量与新查询向量不在同一语义空间，检索会空命中，
需重建索引。

用法（在 chemai-backend 目录下执行）::

    ./venv/bin/python scripts/reindex_questions.py

幂等：按 question_id::kp-N 幂等 upsert，重复执行只是用同语义向量覆盖。
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

# 让脚本能在任意子目录下被直接执行时仍 import 到 app 包（项目根目录）。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Question
from app.services.vector_search import vector_search


def reindex() -> None:
    """重建全部未删除题目的向量。"""
    with SessionLocal() as db:
        questions = db.execute(
            select(Question).where(Question.deleted_at.is_(None))
        ).scalars().all()

        for q in questions:
            # upsert：同 id 覆盖旧向量，故 MD5 伪向量会被真实向量顶替。
            vector_search.index_question(q)

        # _real_embeddings_ok 反映最近一次 embed() 是否走了真实嵌入（False=MD5 降级）。
        real = vector_search._real_embeddings_ok is True
        mode = "真实 embedding（text-embedding-v3）" if real else "MD5 伪向量（降级）"
        print(f"✓ 已重建 {len(questions)} 道题目的向量，嵌入方式：{mode}")


if __name__ == "__main__":
    reindex()
