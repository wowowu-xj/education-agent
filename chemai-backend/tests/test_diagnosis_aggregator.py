# -*- coding: utf-8 -*-
"""双维度聚合测试（L1）。

覆盖 task 6.1：按类型计数归一化、补齐缺失类型为 0、无诊断数据返回空。
"""

from __future__ import annotations

from app.core.enums import BarrierType
from chem_skills.chemistry_diagnosis.engine.aggregator import (
    BARRIER_KEYS,
    MISCONCEPTION_KEYS,
    build_barrier_profile,
    build_misconception_profile,
    dominant,
)


class TestBarrierProfile:
    def test_count_normalize(self) -> None:
        """3 concept + 2 reading + 1 expression → 归一化为 0.5/0.33/0.17。"""
        profile = build_barrier_profile(
            [
                BarrierType.CONCEPT,
                BarrierType.CONCEPT,
                BarrierType.CONCEPT,
                BarrierType.READING,
                BarrierType.READING,
                BarrierType.EXPRESSION,
            ]
        )
        assert profile == {"concept": 0.5, "reading": 0.33, "expression": 0.17}
        assert round(sum(profile.values()), 2) == 1.0

    def test_three_way_split_sums_to_one(self) -> None:
        """三路均摊（1/3）——旧 ``round`` 得 0.33×3=0.99，最大余数法保证和恰为 1.0。"""
        profile = build_barrier_profile(
            [BarrierType.CONCEPT, BarrierType.READING, BarrierType.EXPRESSION]
        )
        assert abs(sum(profile.values()) - 1.0) < 1e-9
        # 剩余 0.01 补给余数最大（并列取首键 concept）者
        assert profile == {"concept": 0.34, "reading": 0.33, "expression": 0.33}

    def test_fill_missing_zero(self) -> None:
        """仅 concept → 缺失类型补齐为 0。"""
        profile = build_barrier_profile([BarrierType.CONCEPT, BarrierType.CONCEPT])
        assert profile["concept"] == 1.0
        assert profile["reading"] == 0.0
        assert profile["expression"] == 0.0

    def test_empty_returns_none(self) -> None:
        assert build_barrier_profile([]) is None

    def test_has_three_keys(self) -> None:
        profile = build_barrier_profile([BarrierType.READING])
        assert tuple(profile.keys()) == BARRIER_KEYS


class TestMisconceptionProfile:
    def test_six_keys_normalize(self) -> None:
        profile = build_misconception_profile(["redox", "redox", "redox"])
        assert tuple(profile.keys()) == MISCONCEPTION_KEYS
        assert profile["redox"] == 1.0
        assert profile["chemical_equilibrium"] == 0.0

    def test_skips_none(self) -> None:
        profile = build_misconception_profile([None, "redox"])
        assert profile["redox"] == 1.0

    def test_all_none_returns_none(self) -> None:
        assert build_misconception_profile([None, None]) is None

    def test_empty_returns_none(self) -> None:
        assert build_misconception_profile([]) is None


class TestDominant:
    def test_dominant_highest(self) -> None:
        profile = build_barrier_profile(
            [BarrierType.CONCEPT, BarrierType.CONCEPT, BarrierType.READING]
        )
        assert dominant(profile) == "concept"

    def test_dominant_empty(self) -> None:
        assert dominant(None) is None
        assert dominant({}) is None
