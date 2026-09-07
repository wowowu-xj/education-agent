# -*- coding: utf-8 -*-
"""置信度融合引擎：2×2 决策表纯函数。

对应 design D9。融合规则引擎与 LLM 信号，产出最终「障碍类型 + 置信度」，
按「规则命中状态 × LLM 置信度」二维决策表决策：

- 规则命中且与 LLM 一致 → 取该类型，``confidence = max(rule_conf, llm_conf)``
  （规则命中是高精确信号，不因 LLM 低置信被拖低）。
- 规则命中但与 LLM 矛盾 → 默认取 LLM 分类，保留规则候选 + ``needs_review``。
- 规则未命中 + LLM 正常（≥0.7）→ 纯 LLM。
- 规则未命中 + LLM 低置信（<0.7）→ 双低，标记「建议人工复核」。
- LLM 失败/非法（``llm=None``）→ 规则兜底，置信度取规则 0.5–0.7，
  迷思概念为空。

迷思概念仅 LLM 产出，规则引擎不参与。
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import BarrierType
from chem_skills.chemistry_diagnosis.engine.rule_engine import RuleResult

# 低置信阈值：低于 0.7 视为「双低」信号。
_LLM_LOW_CONF = 0.7
# 浮点比较容差：0.7 非精确可表示，阈值比较带 ε 吸收二进制表示噪声，
# 避免「恰等于 0.7 却被其浮点下邻判为低置信」的边界翻转（code-review F5）。
_CONF_EPSILON = 1e-9


@dataclass(frozen=True)
class FusionResult:
    """融合后的最终诊断。

    Attributes:
        barrier_type: 最终障碍类型；``None`` 表示规则与 LLM 均无信号
            （极端兜底失败，作答保持未诊断）。
        misconception_category: 迷思概念类别（仅 LLM 产出，可为 ``None``）。
        confidence: 融合置信度（0–1）。
        needs_review: 是否建议人工复核（冲突 / 双低）。
        fallback_reason: 兜底或复核原因（rule_fallback / conflict /
            low_confidence / no_signal）。
        rule_candidate: 与 LLM 矛盾时保留的规则候选类型。
        reasoning: 判定依据（来自 LLM，规则兜底时为空）。
        suggestion: 干预建议（来自 LLM，规则兜底时为空）。
    """

    barrier_type: BarrierType | None
    misconception_category: str | None
    confidence: float
    needs_review: bool = False
    fallback_reason: str | None = None
    rule_candidate: BarrierType | None = None
    reasoning: str = ""
    suggestion: str = ""


def _to_barrier(value: str | BarrierType) -> BarrierType:
    """把 LLM 返回的字符串值或枚举统一为 BarrierType。"""
    return value if isinstance(value, BarrierType) else BarrierType(value)


def fuse(rule: RuleResult, llm: dict | None) -> FusionResult:
    """融合规则与 LLM 结果，输出最终诊断。

    Args:
        rule: 规则引擎预分类结果（:class:`RuleResult`）。
        llm: LLM 解析后的诊断 dict（见
            :func:`chem_skills.chemistry_diagnosis.engine.llm_client.parse_diagnosis_json`），
            或 ``None`` 表示 LLM 失败/非法。

    Returns:
        FusionResult: 最终诊断。
    """
    rule_type = rule.barrier_type

    # LLM 失败 / 非法 → 规则兜底
    if llm is None:
        if rule.is_hit:
            return FusionResult(
                barrier_type=rule_type,
                misconception_category=None,
                confidence=rule.confidence,
                fallback_reason="rule_fallback",
            )
        # 规则与 LLM 均无信号，无法判定
        return FusionResult(
            barrier_type=None,
            misconception_category=None,
            confidence=0.0,
            fallback_reason="no_signal",
        )

    llm_type = _to_barrier(llm["barrier_type"])
    llm_conf = llm["confidence"]
    misconception = llm["misconception_category"]
    reasoning = llm["reasoning"]
    suggestion = llm["suggestion"]

    # 规则命中
    if rule.is_hit:
        if llm_type == rule_type:
            # 双路一致 → 取高置信
            return FusionResult(
                barrier_type=rule_type,
                misconception_category=misconception,
                confidence=max(rule.confidence, llm_conf),
                reasoning=reasoning,
                suggestion=suggestion,
            )
        # 冲突 → 默认 LLM 分类，保留规则候选 + 人工复核
        return FusionResult(
            barrier_type=llm_type,
            misconception_category=misconception,
            confidence=llm_conf,
            needs_review=True,
            fallback_reason="conflict",
            rule_candidate=rule_type,
            reasoning=reasoning,
            suggestion=suggestion,
        )

    # 规则未命中
    if llm_conf >= _LLM_LOW_CONF - _CONF_EPSILON:
        # 纯 LLM
        return FusionResult(
            barrier_type=llm_type,
            misconception_category=misconception,
            confidence=llm_conf,
            reasoning=reasoning,
            suggestion=suggestion,
        )
    # 双低 → 标记复核，不自动采纳
    return FusionResult(
        barrier_type=llm_type,
        misconception_category=misconception,
        confidence=llm_conf,
        needs_review=True,
        fallback_reason="low_confidence",
        reasoning=reasoning,
        suggestion=suggestion,
    )
