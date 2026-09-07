# -*- coding: utf-8 -*-
"""规则引擎测试（L1）。

覆盖：
- 接线守护（task 3.2）：JSON 规则基加载后非空且 schema 合法，防止
  barriers.json 退化成死代码（前车之鉴 chemistry_audit/rules/*.json）；
- 关键词预分类（task 3.3）：三组命中对应类型 + 0.5–0.7 保守置信度，
  未命中标 uncertain。
"""

from __future__ import annotations

from app.core.enums import BarrierType
from chem_skills.chemistry_diagnosis.engine.rule_engine import RULES, classify


# ---------------------------------------------------------------------------
# 接线守护（task 3.2）
# ---------------------------------------------------------------------------


class TestRuleWireGuard:
    def test_rules_non_empty(self) -> None:
        """加载后的规则集非空。"""
        assert RULES, "barriers.json 加载后规则集为空"

    def test_rules_schema_valid(self) -> None:
        """键 ∈ 三障碍类型，值为非空字符串列表。"""
        assert set(RULES.keys()) == {"concept", "reading", "expression"}
        for key, keywords in RULES.items():
            assert isinstance(keywords, tuple) and len(keywords) > 0, f"{key} 关键词为空"
            assert all(isinstance(kw, str) and kw for kw in keywords), f"{key} 含非法关键词"


# ---------------------------------------------------------------------------
# 关键词预分类（task 3.3）
# ---------------------------------------------------------------------------


class TestKeywordClassify:
    def test_concept_hit(self) -> None:
        result = classify("这两个概念我分不清")
        assert result.barrier_type == BarrierType.CONCEPT
        assert 0.5 <= result.confidence <= 0.7

    def test_reading_hit(self) -> None:
        result = classify("我审题没看清条件")
        assert result.barrier_type == BarrierType.READING
        assert 0.5 <= result.confidence <= 0.7

    def test_expression_hit(self) -> None:
        result = classify("方程式我写错了")
        assert result.barrier_type == BarrierType.EXPRESSION
        assert 0.5 <= result.confidence <= 0.7

    def test_no_hit_uncertain(self) -> None:
        result = classify("这道题我不会做")
        assert result.barrier_type is None
        assert result.is_hit is False
        assert result.confidence == 0.0

    def test_empty_text_uncertain(self) -> None:
        assert classify("").barrier_type is None

    def test_multiple_hits_raise_confidence(self) -> None:
        """命中多个关键词时置信度随命中数上升（仍 ≤ 0.7）。"""
        single = classify("分不清")
        multi = classify("分不清 混淆 搞混 记混 弄混")
        assert single.barrier_type == BarrierType.CONCEPT
        assert multi.barrier_type == BarrierType.CONCEPT
        assert multi.confidence > single.confidence
        assert multi.confidence <= 0.7

    def test_matched_keywords_recorded(self) -> None:
        result = classify("分不清 混淆")
        assert "分不清" in result.matched_keywords
