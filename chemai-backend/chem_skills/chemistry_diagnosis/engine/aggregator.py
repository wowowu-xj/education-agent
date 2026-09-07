# -*- coding: utf-8 -*-
"""双维度聚合：障碍类型 / 迷思概念独立计数归一化。

对应 design D6。对每个学生的已诊断作答分别按 `barrier_type` 与
`misconception_category` 计数 → 归一化为占比（保留两位小数、和约 1.0）→
补齐缺失类型为 0。主导障碍 `dominant_barrier` = 占比最高类型。

引擎层纯函数，DB 查询由 API 层负责（见 tasks §7）。
"""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from app.core.enums import BarrierType, MisconceptionCategory

BARRIER_KEYS: tuple[str, ...] = tuple(m.value for m in BarrierType)
MISCONCEPTION_KEYS: tuple[str, ...] = tuple(m.value for m in MisconceptionCategory)

# 迷思概念 → 关联知识点（首版映射，后续可调，见 design risks）。
# 用于组装班级查询里的 weak_knowledge_points。
MISCONCEPTION_KNOWLEDGE_POINTS: dict[str, tuple[str, ...]] = {
    "chemical_equilibrium": ("化学平衡", "勒夏特列原理", "平衡常数"),
    "redox": ("氧化还原反应", "氧化剂与还原剂", "电子转移"),
    "mole_calculation": ("物质的量", "摩尔计算", "阿伏加德罗常数"),
    "organic_chemistry": ("有机化学", "官能团", "同分异构"),
    "chemical_notation": ("化学用语", "化学式书写", "方程式配平"),
    "structure_properties": ("物质结构与性质", "化学键", "晶体结构"),
}


def knowledge_points_for(categories: Sequence[str]) -> list[str]:
    """把迷思概念类别映射为关联知识点（去重、保持顺序）。"""
    seen: list[str] = []
    for cat in categories:
        for kp in MISCONCEPTION_KNOWLEDGE_POINTS.get(cat, ()):
            if kp not in seen:
                seen.append(kp)
    return seen


def _value(x) -> str:
    """把枚举成员或字符串统一为存储值字符串。"""
    return x.value if hasattr(x, "value") else x


def normalize_counts(
    counts: dict[str, int],
    all_keys: Sequence[str],
) -> dict[str, float]:
    """计数归一化为占比（保留两位小数、和恰为 1.0），补齐缺失键为 0。

    用「最大余数法」而非 ``round``：精确占比先向下取整到 0.01（basis points），
    再把剩余份额按小数余数降序逐个补 0.01。避免 ``round`` 的银行家舍入与浮点
    误差导致键值和 ≠ 1.0（如三路均摊 1/3 用 ``round`` 得 0.33×3=0.99）。

    Args:
        counts: 类型 → 出现次数。
        all_keys: 全部合法键（用于补齐缺失类型为 0）。

    Returns:
        dict: 每个键的占比（0–1，两位小数，和恰为 1.0）。
    """
    total = sum(counts.values())
    if total <= 0:
        return {k: 0.0 for k in all_keys}

    exact = {k: counts.get(k, 0) / total for k in all_keys}
    # 向下取整到 basis point（0.01），使份额为整数、总和控制为 100。
    basis = {k: int(exact[k] * 100) for k in all_keys}
    slack = 100 - sum(basis.values())
    # 按被舍掉的小数余数降序，把剩余 0.01 逐位补给余数最大的键。
    order = sorted(all_keys, key=lambda k: exact[k] * 100 - basis[k], reverse=True)
    for idx in range(slack):
        basis[order[idx]] += 1
    return {k: basis[k] / 100 for k in all_keys}


def build_barrier_profile(
    types: Sequence[BarrierType],
) -> dict[str, float] | None:
    """按障碍类型计数归一化。

    Args:
        types: 已诊断作答的障碍类型序列。

    Returns:
        dict | None: 三键画像（concept/reading/expression）；空输入返回 None
            （「暂无足够数据」，不生成画像）。
    """
    if not types:
        return None
    counts = Counter(_value(t) for t in types)
    return normalize_counts(counts, BARRIER_KEYS)


def build_misconception_profile(
    categories: Sequence[MisconceptionCategory | str | None],
) -> dict[str, float] | None:
    """按迷思概念类别计数归一化。

    Args:
        categories: 已诊断作答的迷思概念序列（可为 None）。

    Returns:
        dict | None: 六键画像；空输入（含全 None）返回 None。
    """
    valid = [_value(c) for c in categories if c is not None]
    if not valid:
        return None
    counts = Counter(valid)
    return normalize_counts(counts, MISCONCEPTION_KEYS)


def dominant(profile: dict[str, float] | None) -> str | None:
    """返回占比最高的类型键。

    Args:
        profile: 画像字典（见 :func:`build_barrier_profile`）。

    Returns:
        str | None: 主导类型键；空画像返回 None。
    """
    if not profile:
        return None
    return max(profile, key=profile.get)
