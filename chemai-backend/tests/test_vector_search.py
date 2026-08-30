# -*- coding: utf-8 -*-
"""向量检索核心测试（L1/L2）：索引构建、语义召回、两层检索、降级路径。

用 ephemeral ChromaDB 客户端 + 注入的伪 embedding（按关键词打 one-hot），
避免真实 dashscope 调用；降级路径用会抛异常的 client/embed_fn 模拟故障。
"""
from __future__ import annotations

from types import SimpleNamespace

import chromadb
import pytest
from sqlalchemy.orm import Session

from app.core.enums import Difficulty, QuestionType
from app.models import Question, Teacher
from app.services.vector_search import (
    VectorSearchService,
    compose_index_text,
    keyword_candidates,
    md5_vector,
)

DIM = 8


def fake_embed(texts: list[str], dim: int) -> list[list[float]]:
    """伪嵌入：按「氧化/摩尔」关键词打 one-hot，供确定性召回测试。"""
    vecs: list[list[float]] = []
    for t in texts:
        v = [0.0] * dim
        if "氧化" in t:
            v[0] = 1.0
        if "摩尔" in t:
            v[1] = 1.0
        vecs.append(v)
    return vecs


@pytest.fixture()
def chroma_service(tmp_path) -> VectorSearchService:
    """每测试独立的持久化 ChromaDB + 伪 embedding 的服务实例。"""
    return VectorSearchService(
        client=chromadb.PersistentClient(path=str(tmp_path / "chroma")),
        embed_fn=fake_embed,
        dim=DIM,
    )


def _make_question(
    qid: int,
    kps: list[str],
    content: str,
    type_: QuestionType = QuestionType.SINGLE_CHOICE,
    difficulty: Difficulty = Difficulty.MEDIUM,
) -> SimpleNamespace:
    """轻量题目对象（纯属性访问，不落库）。"""
    return SimpleNamespace(
        id=qid,
        knowledge_points=kps,
        content=content,
        type=type_,
        difficulty=difficulty,
        answer="答案",
        source_name=None,
    )


def _persist_question(
    db: Session,
    teacher: Teacher,
    kps: list[str],
    content: str,
    type_: QuestionType = QuestionType.SINGLE_CHOICE,
    difficulty: Difficulty = Difficulty.MEDIUM,
) -> Question:
    """落库一道题并刷新 id。"""
    q = Question(
        teacher_id=teacher.id,
        content=content,
        type=type_,
        answer="答案",
        knowledge_points=kps,
        difficulty=difficulty,
        score=2.0,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


# ---------------------------------------------------------------------------
# 纯函数
# ---------------------------------------------------------------------------


class TestPureFunctions:
    def test_md5_vector_deterministic_and_dim(self) -> None:
        v1 = md5_vector("氧化还原反应", DIM)
        v2 = md5_vector("氧化还原反应", DIM)
        v3 = md5_vector("摩尔计算", DIM)
        assert len(v1) == DIM
        assert v1 == v2
        assert v1 != v3

    def test_compose_index_text_fields(self) -> None:
        q = _make_question(1, ["氧化还原反应"], "下列关于氧化还原反应的说法正确的是")
        text = compose_index_text(q, "氧化还原反应")
        assert "考点:氧化还原反应" in text
        assert "题型:single_choice" in text
        assert "难度:medium" in text
        assert "下列关于氧化还原反应" in text
        assert "答案:答案" in text

    def test_compose_index_text_truncates_content_500(self) -> None:
        long_content = "C" * 600
        q = _make_question(1, ["氧化"], long_content)
        text = compose_index_text(q, "氧化")
        assert long_content[:500] in text
        assert "C" * 600 not in text

    def test_keyword_candidates_ranks_difficulty_on_tie(self) -> None:
        q_easy = _make_question(2, ["氧化还原反应"], "乙题", difficulty=Difficulty.EASY)
        q_hard = _make_question(1, ["氧化还原反应"], "甲题", difficulty=Difficulty.HARD)
        q_unrelated = _make_question(3, ["摩尔计算"], "丙题")
        # 同分（仅知识点重叠）时 easy 优先；无关题目不进入候选
        result = keyword_candidates([q_hard, q_unrelated, q_easy], "氧化还原反应")
        assert [q.id for q in result] == [q_easy.id, q_hard.id]

    def test_keyword_candidates_exact_match_weight(self) -> None:
        q_overlap_only = _make_question(1, ["氧化还原反应"], "甲题", difficulty=Difficulty.EASY)
        q_exact = _make_question(2, ["氧化还原反应"], "关于氧化还原反应的详解", difficulty=Difficulty.HARD)
        # 题干含完整 query 加权更高，即使难度更难也靠前
        result = keyword_candidates([q_overlap_only, q_exact], "氧化还原反应")
        assert [q.id for q in result] == [q_exact.id, q_overlap_only.id]


# ---------------------------------------------------------------------------
# 索引构建
# ---------------------------------------------------------------------------


class TestIndex:
    def test_index_question_builds_per_kp_vectors(self, chroma_service: VectorSearchService) -> None:
        q = _make_question(42, ["氧化还原反应", "摩尔计算"], "题目内容")
        chroma_service.index_question(q)

        got = chroma_service.collection.get(
            ids=["42::kp-0", "42::kp-1"], include=["metadatas"]
        )
        assert got["ids"] == ["42::kp-0", "42::kp-1"]
        assert [m["question_id"] for m in got["metadatas"]] == [42, 42]
        assert [m["kp"] for m in got["metadatas"]] == ["氧化还原反应", "摩尔计算"]

    def test_index_question_without_kp_skips(self, chroma_service: VectorSearchService) -> None:
        q = _make_question(43, [], "无考点题目")
        chroma_service.index_question(q)
        assert chroma_service.collection.count() == 0

    def test_remove_question(self, chroma_service: VectorSearchService) -> None:
        q = _make_question(44, ["氧化还原反应"], "题目")
        chroma_service.index_question(q)
        assert chroma_service.collection.count() == 1
        chroma_service.remove_question(44)
        assert chroma_service.collection.count() == 0

    def test_reindex_question_removes_stale_vectors(self, chroma_service: VectorSearchService) -> None:
        q = _make_question(55, ["氧化还原反应", "摩尔计算"], "题目")
        chroma_service.index_question(q)
        assert chroma_service.collection.count() == 2

        # 知识点缩减 → 旧向量被清除
        q.knowledge_points = ["氧化还原反应"]
        chroma_service.reindex_question(q)
        got = chroma_service.collection.get(include=["metadatas"])
        assert sorted(got["ids"]) == ["55::kp-0"]
        assert [m["kp"] for m in got["metadatas"]] == ["氧化还原反应"]

        # 知识点清空 → 全部向量移除
        q.knowledge_points = []
        chroma_service.reindex_question(q)
        assert chroma_service.collection.count() == 0


# ---------------------------------------------------------------------------
# 语义召回（两层检索）
# ---------------------------------------------------------------------------


class TestSearch:
    def test_semantic_recall(self, db: Session, teacher: Teacher, chroma_service: VectorSearchService) -> None:
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法正确的是")
        q2 = _persist_question(
            db, teacher, ["摩尔计算"], "计算某物质的摩尔质量", type_=QuestionType.CALCULATION, difficulty=Difficulty.HARD
        )
        chroma_service.index_question(q1)
        chroma_service.index_question(q2)

        result = chroma_service.search(db, "氧化还原反应", teacher.id, top_k=5)
        assert [q.id for q in result] == [q1.id]

    def test_vector_recall_without_keyword_hits(
        self, db: Session, teacher: Teacher, chroma_service: VectorSearchService
    ) -> None:
        # 查询词「氧化剂」不在考点也不在题干，关键词层无候选 → 全量向量检索兜住
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法正确的是")
        chroma_service.index_question(q1)

        result = chroma_service.search(db, "氧化剂", teacher.id, top_k=5)
        assert [q.id for q in result] == [q1.id]

    def test_threshold_filters_low_similarity(
        self, db: Session, teacher: Teacher, chroma_service: VectorSearchService
    ) -> None:
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "氧化还原反应题目")
        chroma_service.index_question(q1)

        # 查询词不命中任何关键词 → 无向量命中 → 空结果
        result = chroma_service.search(db, "有机化学", teacher.id, top_k=5)
        assert result == []

    def test_knowledge_point_filter_narrows_pool(
        self, db: Session, teacher: Teacher, chroma_service: VectorSearchService
    ) -> None:
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法")
        q2 = _persist_question(
            db, teacher, ["氧化还原反应", "摩尔计算"], "判断下列说法是否正确"
        )
        chroma_service.index_question(q1)
        chroma_service.index_question(q2)

        # 不过滤：两道都命中「氧化还原反应」
        result = chroma_service.search(db, "氧化还原反应", teacher.id, top_k=5)
        assert {q.id for q in result} == {q1.id, q2.id}

        # knowledge_point 过滤到「摩尔计算」→ 仅 q2
        result = chroma_service.search(
            db, "氧化还原反应", teacher.id, top_k=5, knowledge_point="摩尔计算"
        )
        assert [q.id for q in result] == [q2.id]

    def test_search_deduplicates_multi_kp_question(
        self, db: Session, teacher: Teacher, chroma_service: VectorSearchService
    ) -> None:
        # 一道题两个知识点，题干同时含「氧化」与「摩尔」→ 两个向量都过阈值，
        # 去重后同一题只应返回一次。
        q = _persist_question(
            db, teacher, ["氧化还原反应", "摩尔计算"], "关于氧化还原与摩尔计算的综合题"
        )
        chroma_service.index_question(q)

        result = chroma_service.search(db, "氧化还原反应", teacher.id, top_k=5)
        assert [x.id for x in result] == [q.id]

    def test_search_fills_top_k_distinct_after_dedup(
        self, db: Session, teacher: Teacher, tmp_path
    ) -> None:
        # 多考点题的向量占据相似度前列时，去重后仍应凑满 top_k 道不同题，
        # 而非被重复向量挤占掉名额。
        def fill_embed(texts: list[str], dim: int) -> list[list[float]]:
            vecs: list[list[float]] = []
            for t in texts:
                if "综合" in t:
                    v = [1.0] + [0.0] * (dim - 1)   # 与查询同向 → sim 1.0
                elif "基础" in t:
                    v = [0.8, 0.6] + [0.0] * (dim - 2)   # sim 0.8
                elif "进阶" in t:
                    v = [0.7, 0.7] + [0.0] * (dim - 2)   # sim ≈0.707
                else:
                    v = [1.0] + [0.0] * (dim - 1)   # 查询向量
                vecs.append(v)
            return vecs

        service = VectorSearchService(
            client=chromadb.PersistentClient(path=str(tmp_path / "chroma")),
            embed_fn=fill_embed,
            dim=DIM,
        )
        q_big = _persist_question(db, teacher, ["氧化还原反应", "摩尔计算"], "综合题：氧化还原")
        q_a = _persist_question(db, teacher, ["氧化还原反应"], "基础题：氧化还原")
        q_b = _persist_question(db, teacher, ["氧化还原反应"], "进阶题：氧化还原")
        service.index_question(q_big)
        service.index_question(q_a)
        service.index_question(q_b)

        result = service.search(db, "氧化还原反应", teacher.id, top_k=2)
        ids = [x.id for x in result]
        assert len(ids) == 2
        assert len(set(ids)) == 2  # 去重后仍是 2 道不同题（而非被 q_big 挤成 1 道）
        assert q_big.id in ids  # 最高相似度的多考点题未被丢弃

    def test_healthy_no_threshold_does_not_fallback_to_keyword(
        self, db: Session, teacher: Teacher, tmp_path
    ) -> None:
        # 关键词命中但向量相似度 < 0.6：ChromaDB 健康时不得降级为关键词结果
        def dissimilar_embed(texts: list[str], dim: int) -> list[list[float]]:
            out: list[list[float]] = []
            for t in texts:
                if t == "氧化还原反应":
                    out.append([1.0] + [0.0] * (dim - 1))
                else:
                    out.append([0.0, 1.0] + [0.0] * (dim - 2))
            return out

        service = VectorSearchService(
            client=chromadb.PersistentClient(path=str(tmp_path / "chroma")),
            embed_fn=dissimilar_embed,
            dim=DIM,
        )
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法")
        service.index_question(q1)

        result = service.search(db, "氧化还原反应", teacher.id, top_k=5)
        assert result == []


# ---------------------------------------------------------------------------
# 降级路径
# ---------------------------------------------------------------------------


class TestDegradation:
    def test_chroma_unavailable_falls_back_to_keyword(self, db: Session, teacher: Teacher) -> None:
        class BrokenClient:
            def get_or_create_collection(self, *args: object, **kwargs: object) -> None:
                raise RuntimeError("chroma down")

        service = VectorSearchService(client=BrokenClient(), embed_fn=fake_embed, dim=DIM)
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法")
        result = service.search(db, "氧化还原反应", teacher.id, top_k=5)
        assert [q.id for q in result] == [q1.id]

    def test_embed_failure_uses_md5_exact_match(self, db: Session, teacher: Teacher, tmp_path) -> None:
        def broken_embed(texts: list[str], dim: int) -> list[list[float]]:
            raise RuntimeError("embed down")

        service = VectorSearchService(
            client=chromadb.PersistentClient(path=str(tmp_path / "chroma")),
            embed_fn=broken_embed,
            dim=DIM,
        )
        q1 = _persist_question(db, teacher, ["氧化还原反应"], "下列关于氧化还原反应的说法")
        service.index_question(q1)  # 不应抛异常（MD5 兜底）
        assert service.collection.count() == 1

        # 语义退化为精确匹配：查询与索引文本完全一致时 MD5 向量相同 → 命中
        index_text = compose_index_text(q1, "氧化还原反应")
        result = service.search(db, index_text, teacher.id, top_k=5)
        assert [q.id for q in result] == [q1.id]

    def test_index_failure_does_not_raise(self) -> None:
        class BrokenClient:
            def get_or_create_collection(self, *args: object, **kwargs: object) -> None:
                raise RuntimeError("chroma down")

        service = VectorSearchService(client=BrokenClient(), embed_fn=fake_embed, dim=DIM)
        q = _make_question(1, ["氧化还原反应"], "题目")
        service.index_question(q)  # 不应抛异常
