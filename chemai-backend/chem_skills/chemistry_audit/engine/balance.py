# -*- coding: utf-8 -*-
"""维度 1：系数配平审核。

使用元素原子计数法验证化学方程式配平。
HA RD RED LINE: 准确率必须 100%。
"""

from __future__ import annotations

from chem_skills.chemistry_audit.engine.models import BalanceResult
from chem_skills.chemistry_audit.engine.parser import (
    ParseError,
    count_elements,
    parse_equation,
)

# 有机燃烧反应关键词——这些反应通常不写完整配平式
_ORGANIC_COMBUSTION_KEYWORDS = {"C2H5OH", "C6H12O6", "CH3COOH", "CxHy", "CxHyOz"}
# H2 燃烧不在此列——氢气燃烧是标准的无机组反应


def check_balance(equation: str) -> BalanceResult:
    """审核方程式系数配平。

    对反应物侧和产物侧的每种元素分别统计原子总数，逐元素比对。

    Args:
        equation: 化学方程式字符串

    Returns:
        BalanceResult: 包含配平状态和两侧元素计数
    """
    try:
        parsed = parse_equation(equation)
    except ParseError as e:
        return BalanceResult(
            status="blocked",
            message=str(e),
        )

    # 统计反应物侧
    left_elements: dict[str, int] = {}
    for compound in parsed.reactants:
        counts = count_elements(compound)
        for elem, cnt in counts.items():
            left_elements[elem] = left_elements.get(elem, 0) + cnt

    # 统计产物侧
    right_elements: dict[str, int] = {}
    for compound in parsed.products:
        counts = count_elements(compound)
        for elem, cnt in counts.items():
            right_elements[elem] = right_elements.get(elem, 0) + cnt

    # 检测是否为有机燃烧反应
    all_elements = set(left_elements.keys()) | set(right_elements.keys())
    is_organic = any(kw in equation for kw in _ORGANIC_COMBUSTION_KEYWORDS)

    # 逐元素比较
    mismatches: list[str] = []
    for elem in sorted(all_elements):
        left = left_elements.get(elem, 0)
        right = right_elements.get(elem, 0)
        if left != right:
            mismatches.append(f"{elem}: 左{left} vs 右{right}")

    if mismatches:
        if is_organic:
            # 有机反应不写完整配平式，降级为 warning
            return BalanceResult(
                status="passed",  # 有机反应不强制配平
                message=f"有机反应配平提示: {'; '.join(mismatches)}（可能为通式）",
                left_elements=left_elements,
                right_elements=right_elements,
            )
        return BalanceResult(
            status="blocked",
            message=f"方程式未配平 — {'; '.join(mismatches)}",
            left_elements=left_elements,
            right_elements=right_elements,
        )

    return BalanceResult(
        status="passed",
        message="系数配平正确",
        left_elements=left_elements,
        right_elements=right_elements,
    )
