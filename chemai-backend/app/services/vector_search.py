# -*- coding: utf-8 -*-
"""向量检索核心服务。

两层检索：第一层关键词粗筛（知识点重叠 + 精确匹配加权 + 难度排序 Top-20），
第二层 ChromaDB 向量精筛（cosine Top-K，similarity >= 0.6）。
降级策略（Decision 8）：
- ChromaDB 不可用 → 纯关键词匹配，检索仍可用
- embedding 服务不可用 → MD5 伪向量（语义退化为精确）

索引以题目为单位、以考点为粒度：每个 knowledge_point 生成一个向量，
ID 形如 ``<question_id>::kp-n``。
"""
from __future__ import annotations

import hashlib
import re
from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import Difficulty, QuestionType
from app.models import Question

EMBEDDING_MODEL = "text-embedding-v3"
SIMILARITY_THRESHOLD = 0.6
KEYWORD_TOP_N = 20

# 难度排序权重：同关键词得分时 easy 优先。
_DIFFICULTY_RANK: dict[Difficulty, int] = {
    Difficulty.EASY: 0,
    Difficulty.MEDIUM: 1,
    Difficulty.HARD: 2,
    Difficulty.COMPETITION: 3,
}

EmbedFn = Callable[[list[str], int], list[list[float]]]


def md5_vector(text: str, dim: int) -> list[float]:
    """MD5 伪向量：embedding 不可用时语义退化为精确匹配。

    同一文本产生相同向量（cosine=1），不同文本近似正交（cosine≈0）。
    """
    digest = hashlib.md5(text.encode("utf-8")).digest()
    return [((digest[i % len(digest)] / 255.0) * 2.0) - 1.0 for i in range(dim)]


def _dashscope_embed(texts: list[str], dim: int) -> list[list[float]]:
    """调用 dashscope text-embedding-v3，返回 ``list[list[float]]``。"""
    from dashscope import TextEmbedding

    resp = TextEmbedding.call(
        model=EMBEDDING_MODEL,
        input=texts,
        dimension=dim,
        api_key=settings.DASHSCOPE_API_KEY or None,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"embedding 调用失败: {resp.code} {resp.message}")
    return [item["embedding"] for item in resp.output["embeddings"]]


def compose_index_text(question: Question, knowledge_point: str) -> str:
    """嵌入文本：考点 + 题型 + 难度 + 来源 + 题目(前500字) + 答案。"""
    source = question.source_name or ""
    content = (question.content or "")[:500]
    answer = question.answer or ""
    return (
        f"考点:{knowledge_point} 题型:{question.type.value} 难度:{question.difficulty.value} "
        f"来源:{source} 题目:{content} 答案:{answer}"
    )


def _tokenize(query: str) -> list[str]:
    """把查询文本切分为关键词 token（按常见中英文分隔符）。"""
    parts = re.split(r"[,，、;；\s]+", query or "")
    tokens = [p.strip() for p in parts if p.strip()]
    if not tokens:
        stripped = (query or "").strip()
        if stripped:
            tokens = [stripped]
    return tokens


def keyword_candidates(
    questions: list[Question],
    query: str,
    top_n: int = KEYWORD_TOP_N,
) -> list[Question]:
    """第一层：关键词粗筛。

    打分 = 知识点重叠数（查询 token 命中题目考点）+ 精确匹配加权（题干含完整 query）。
    同分按难度 easy→competition 排序，再按 id 稳定。
    """
    tokens = _tokenize(query)
    scored: list[tuple[float, Question]] = []
    for q in questions:
        kps = q.knowledge_points or []
        overlap = sum(1 for kp in kps if any(t and t in kp for t in tokens))
        exact = 1.0 if (query and query in (q.content or "")) else 0.0
        if overlap or exact:
            scored.append((overlap + exact, q))
    scored.sort(key=lambda pair: (-pair[0], _DIFFICULTY_RANK.get(pair[1].difficulty, 9), pair[1].id))
    return [q for _, q in scored[:top_n]]


class VectorSearchService:
    """ChromaDB 索引 + 两层检索。"""

    COLLECTION_NAME = "questions"

    def __init__(
        self,
        client: object | None = None,
        embed_fn: Optional[EmbedFn] = None,
        dim: int | None = None,
    ) -> None:
        self._client = client
        self._embed_fn = embed_fn or _dashscope_embed
        self.dim = dim or settings.EMBEDDING_DIMENSION
        self._collection: object | None = None

    @property
    def client(self) -> object:
        if self._client is None:
            import chromadb

            self._client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        return self._client

    @property
    def collection(self) -> object:
        if self._collection is None:
            self._collection = self._ensure_collection()
        return self._collection

    @property
    def available(self) -> bool:
        """ChromaDB 是否可用（供降级判断）。"""
        try:
            self.collection
            return True
        except Exception:
            return False

    def _ensure_collection(self) -> object:
        coll = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine", "dimension": str(self.dim)},
        )
        existing_dim = (coll.metadata or {}).get("dimension")
        if existing_dim and existing_dim != str(self.dim):
            # 维度不匹配 → 清空并重建索引。
            self.client.delete_collection(self.COLLECTION_NAME)
            coll = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine", "dimension": str(self.dim)},
            )
        return coll

    def embed(self, texts: list[str]) -> list[list[float]]:
        """嵌入一组文本，embedding 失败时降级为 MD5 伪向量。"""
        try:
            return self._embed_fn(texts, self.dim)
        except Exception:
            return [md5_vector(t, self.dim) for t in texts]

    def index_question(self, question: Question) -> None:
        """为题目每个考点建一个向量（best-effort，失败不阻塞 CRUD 主链路）。"""
        try:
            kps = question.knowledge_points or []
            if not kps:
                return
            ids = [f"{question.id}::kp-{n}" for n in range(len(kps))]
            texts = [compose_index_text(question, kp) for kp in kps]
            embeddings = self.embed(texts)
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=[{"question_id": question.id, "kp": kp} for kp in kps],
            )
        except Exception:
            return

    def remove_question(self, question_id: int) -> None:
        """删除题目在索引中的全部向量。"""
        try:
            self.collection.delete(where={"question_id": question_id})
        except Exception:
            return

    def reindex_question(self, question: Question) -> None:
        """更新后重索引：先清旧向量再按当前考点重建，避免知识点缩减后残留。"""
        self.remove_question(question.id)
        self.index_question(question)

    def search(
        self,
        db: Session,
        query: str,
        teacher_id: int,
        top_k: int = 5,
        type: QuestionType | None = None,
        difficulty: Difficulty | None = None,
        knowledge_point: str | None = None,
    ) -> list[Question]:
        """两层检索：关键词粗筛 → 向量精筛；降级保证可用。"""
        stmt = select(Question).where(
            Question.deleted_at.is_(None),
            Question.teacher_id == teacher_id,
        )
        if type is not None:
            stmt = stmt.where(Question.type == type)
        if difficulty is not None:
            stmt = stmt.where(Question.difficulty == difficulty)
        pool = list(db.execute(stmt).scalars().all())
        # 知识点结构化过滤：JSON 数组包含判定在 Python 侧完成（跨方言无统一原生实现）。
        if knowledge_point is not None:
            pool = [q for q in pool if knowledge_point in (q.knowledge_points or [])]

        kw = keyword_candidates(pool, query, top_n=KEYWORD_TOP_N)
        kw_ids = [q.id for q in kw]

        # ChromaDB 不可用 → 纯关键词降级（Decision 8）。
        if not self.available:
            return kw[:top_k]

        # ChromaDB 可用但无 ≥0.6 命中：返回空，不降级为关键词（阈值是硬约束）。
        # 候选向量总数：一题多考点会产多向量，需请求足够条数，去重后仍凑满 top_k 道不同题。
        total_vecs = sum(len(q.knowledge_points or []) for q in kw)
        hits = self._vector_search(query, kw_ids, top_k, total_vecs)
        by_id = {q.id: q for q in pool}
        return [by_id[qid] for qid in hits if qid in by_id]

    def _vector_search(
        self,
        query: str,
        candidate_ids: list[int],
        top_k: int,
        total_vecs: int = 0,
    ) -> list[int]:
        """第二层：向量精筛，返回去重后的命中题目 id（最多 top_k 个，similarity >= 阈值）。"""
        if not self.available:
            return []
        try:
            query_vec = self.embed([query])[0]
            where = {"question_id": {"$in": candidate_ids}} if candidate_ids else None
            # 有候选时请求全部候选向量，去重后仍能凑满 top_k 道不同题；
            # 无候选（关键词未命中）时回退为 top_k，走全量向量兜底。
            n_results = max(top_k, total_vecs) if candidate_ids else top_k
            res = self.collection.query(
                query_embeddings=[query_vec],
                n_results=n_results,
                where=where,
                include=["metadatas", "distances"],
            )
            metadatas = (res.get("metadatas") or [[]])[0] or []
            distances = (res.get("distances") or [[]])[0] or []
            result: list[int] = []
            seen: set[int] = set()
            for i, meta in enumerate(metadatas):
                dist = distances[i] if i < len(distances) else 1.0
                sim = 1.0 - dist  # cosine 空间 distance = 1 - cosine
                if sim >= SIMILARITY_THRESHOLD:
                    qid = int(meta["question_id"])
                    # 一题多考点 → 多个向量可能同时命中，按题目去重（保留首个即最高相似度）。
                    if qid not in seen:
                        seen.add(qid)
                        result.append(qid)
                        if len(result) >= top_k:
                            break
            return result
        except Exception:
            return []


# 模块级单例：API 层直接使用。
vector_search = VectorSearchService()
