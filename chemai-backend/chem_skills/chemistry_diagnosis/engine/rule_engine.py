# -*- coding: utf-8 -*-
"""规则引擎：关键词预分类（JSON 规则基驱动）。

对应 design D3 / D10：
- 关键词存 `chemistry_diagnosis/rules/barriers.json`，import 时加载一次，
  作为唯一真相源——新增规则 = 加一条 JSON 条目，零代码改动。
- 命中给 0.5–0.7 保守置信度，未命中标 uncertain（barrier_type=None）。
- 前车之鉴：`chemistry_audit/rules/*.json` 因无接线已退化为死代码，本模块
  由 tests/test_diagnosis_rule_engine.py 的接线守护测试约束，防止同样漂移。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.enums import BarrierType

_RULES_PATH = Path(__file__).resolve().parent.parent / "rules" / "barriers.json"

# 命中置信度：单关键词 0.5，每多命中一个 +0.05，封顶 0.7。
_BASE_CONF = 0.5
_CONF_STEP = 0.05
_CONF_MAX = 0.7

# 并列（命中数相同）时按 concept → reading → expression 的优先级取高者。
_PRIORITY: dict[BarrierType, int] = {
    BarrierType.CONCEPT: 2,
    BarrierType.READING: 1,
    BarrierType.EXPRESSION: 0,
}


def load_rules() -> dict[str, tuple[str, ...]]:
    """从 barriers.json 加载三组关键词（import 时调用一次）。"""
    with open(_RULES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {key: tuple(values) for key, values in data.items()}


# 模块加载时解析一次的规则真相源（供 classify 与接线守护测试使用）。
RULES: dict[str, tuple[str, ...]] = load_rules()


@dataclass(frozen=True)
class RuleResult:
    """规则引擎预分类结果。

    Attributes:
        barrier_type: 命中的障碍类型；``None`` 表示 uncertain（未命中）。
        confidence: 命中 0.5–0.7 的保守置信度；未命中为 0.0。
        matched_keywords: 命中的关键词（可能多个）。
    """

    barrier_type: BarrierType | None
    confidence: float
    matched_keywords: tuple[str, ...]

    @property
    def is_hit(self) -> bool:
        """是否命中（未命中为 uncertain）。"""
        return self.barrier_type is not None


def classify(text: str) -> RuleResult:
    """对作答文本做关键词预分类。

    对每个障碍类型统计命中关键词数，取命中最多者为结果；并列时按
    concept → reading → expression 优先级取高者。零命中返回 uncertain。

    Args:
        text: 学生作答文本（可含题干上下文）。

    Returns:
        RuleResult: 预分类结果，命中与否见 :attr:`RuleResult.is_hit`。
    """
    if not text:
        return RuleResult(barrier_type=None, confidence=0.0, matched_keywords=())

    hits: dict[BarrierType, list[str]] = {}
    for name, keywords in RULES.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            hits[BarrierType(name)] = matched

    if not hits:
        return RuleResult(barrier_type=None, confidence=0.0, matched_keywords=())

    # 取命中数最多的类型；并列时按 _PRIORITY 取高者。
    barrier_type, matched = max(
        hits.items(), key=lambda item: (len(item[1]), _PRIORITY[item[0]])
    )
    # round 到两位小数：0.5 + 0.05*n 的浮点累加会引入 1e-16 级噪声
    # （如 0.5+0.05*2=0.6000000000000001），归一后更干净（code-review N2）。
    confidence = min(_CONF_MAX, round(_BASE_CONF + _CONF_STEP * (len(matched) - 1), 2))
    return RuleResult(
        barrier_type=barrier_type,
        confidence=confidence,
        matched_keywords=tuple(matched),
    )
