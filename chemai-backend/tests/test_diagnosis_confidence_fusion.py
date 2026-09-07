# -*- coding: utf-8 -*-
"""置信度融合引擎测试（L1）。

覆盖 task 4.1：双路一致取高置信、冲突双候选 + needs_review、双低标记复核、
LLM 失败规则兜底（迷思概念为空）。
"""

from __future__ import annotations

import math

from app.core.enums import BarrierType
from chem_skills.chemistry_diagnosis.engine.confidence_fusion import fuse
from chem_skills.chemistry_diagnosis.engine.rule_engine import RuleResult


def _rule(barrier: BarrierType | None, confidence: float = 0.5) -> RuleResult:
    return RuleResult(
        barrier_type=barrier,
        confidence=confidence if barrier else 0.0,
        matched_keywords=("k",) if barrier else (),
    )


def _llm(barrier: str, confidence: float, misconception: str | None = "redox") -> dict:
    return {
        "barrier_type": barrier,
        "misconception_category": misconception,
        "confidence": confidence,
        "reasoning": "依据",
        "suggestion": "建议",
    }


class TestConfidenceFusion:
    def test_consistent_takes_max_confidence(self) -> None:
        """双路一致 → 取规则与 LLM 置信度较高者。"""
        result = fuse(
            _rule(BarrierType.CONCEPT, 0.6),
            _llm("concept", 0.9),
        )
        assert result.barrier_type == BarrierType.CONCEPT
        assert result.confidence == 0.9
        assert result.needs_review is False
        assert result.fallback_reason is None

    def test_consistent_not_dragged_by_llm_low_conf(self) -> None:
        """规则高精确信号不因 LLM 低置信被拖低。"""
        result = fuse(
            _rule(BarrierType.CONCEPT, 0.7),
            _llm("concept", 0.6),
        )
        assert result.confidence == 0.7

    def test_conflict_dual_candidate(self) -> None:
        """规则与 LLM 矛盾 → 默认 LLM 分类 + 保留规则候选 + needs_review。"""
        result = fuse(
            _rule(BarrierType.CONCEPT, 0.6),
            _llm("reading", 0.8),
        )
        assert result.barrier_type == BarrierType.READING
        assert result.rule_candidate == BarrierType.CONCEPT
        assert result.needs_review is True
        assert result.fallback_reason == "conflict"
        assert result.misconception_category == "redox"

    def test_pure_llm_no_review(self) -> None:
        """规则未命中 + LLM 高置信 → 纯 LLM，不复核。"""
        result = fuse(
            _rule(None),
            _llm("reading", 0.85),
        )
        assert result.barrier_type == BarrierType.READING
        assert result.needs_review is False
        assert result.rule_candidate is None

    def test_boundary_confidence_tolerates_float_noise(self) -> None:
        """0.7 的浮点下邻仍判为正常置信（ε 吸收表示噪声），不误判低置信。"""
        just_below = math.nextafter(0.7, 0.0)
        assert just_below < 0.7
        result = fuse(_rule(None), _llm("concept", just_below))
        assert result.needs_review is False

    def test_double_low_review(self) -> None:
        """规则未命中 + LLM 低置信 → 双低标记复核。"""
        result = fuse(
            _rule(None),
            _llm("expression", 0.5),
        )
        assert result.barrier_type == BarrierType.EXPRESSION
        assert result.needs_review is True
        assert result.fallback_reason == "low_confidence"

    def test_llm_failure_rule_fallback(self) -> None:
        """LLM 失败 → 规则兜底，迷思概念为空。"""
        result = fuse(_rule(BarrierType.CONCEPT, 0.6), None)
        assert result.barrier_type == BarrierType.CONCEPT
        assert result.confidence == 0.6
        assert result.misconception_category is None
        assert result.fallback_reason == "rule_fallback"
        assert result.needs_review is False

    def test_both_fail_no_signal(self) -> None:
        """规则与 LLM 均失败 → 无法判定。"""
        result = fuse(_rule(None), None)
        assert result.barrier_type is None
        assert result.fallback_reason == "no_signal"
