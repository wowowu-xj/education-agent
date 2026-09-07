# -*- coding: utf-8 -*-
"""诊断 LLM 客户端测试（L1）。

覆盖：
- JSON 鲁棒解析：围栏剥离 / 尾逗号宽松解析 / 枚举校验 / 置信度裁剪；
- 三级 fallback 顺序 + 每级重试 3 次 + 指数退避（task 2.2）；
- 非法枚举一次 re-prompt 后仍失败降级（task 2.3）。
"""

from __future__ import annotations

import pytest

from chem_skills.chemistry_diagnosis.engine.llm_client import (
    DashScopeDiagnosisClient,
    InvalidDiagnosisResponse,
    LLMTransportError,
    LLMUnavailableError,
    Provider,
    extract_json,
    parse_diagnosis_json,
)


# ---------------------------------------------------------------------------
# JSON 鲁棒解析（task 2.3 纯函数部分）
# ---------------------------------------------------------------------------


class TestParseDiagnosisJson:
    def test_strips_code_fence(self) -> None:
        text = '```json\n{"barrier_type": "concept", "confidence": 0.9}\n```'
        result = parse_diagnosis_json(text)
        assert result["barrier_type"] == "concept"
        assert result["confidence"] == 0.9

    def test_tolerates_trailing_comma(self) -> None:
        result = parse_diagnosis_json('{"barrier_type": "reading", "confidence": 0.7,}')
        assert result["barrier_type"] == "reading"

    def test_extracts_embedded_json(self) -> None:
        text = "诊断结果如下：\n{\"barrier_type\": \"expression\"}\n谢谢。"
        assert parse_diagnosis_json(text)["barrier_type"] == "expression"

    def test_extract_json_strips_fence(self) -> None:
        assert extract_json('```json\n{"a": 1}\n```') == '{"a": 1}'

    def test_defaults_misconception_and_confidence(self) -> None:
        result = parse_diagnosis_json('{"barrier_type": "concept"}')
        assert result["misconception_category"] is None
        assert result["confidence"] == 0.5

    def test_clamps_confidence(self) -> None:
        assert parse_diagnosis_json('{"barrier_type": "concept", "confidence": 9}')["confidence"] == 1.0
        assert parse_diagnosis_json('{"barrier_type": "concept", "confidence": -1}')["confidence"] == 0.0

    def test_rejects_nonfinite_confidence(self) -> None:
        # Python json.loads 默认接受 NaN/Infinity 字面量；若不拦截，
        # min/max 会把 NaN 静默裁剪成 1.0（满置信自动采纳）。应显式拒绝。
        for bad in ("NaN", "Infinity", "-Infinity"):
            with pytest.raises(InvalidDiagnosisResponse):
                parse_diagnosis_json(
                    f'{{"barrier_type": "concept", "confidence": {bad}}}'
                )

    def test_rejects_invalid_barrier(self) -> None:
        with pytest.raises(InvalidDiagnosisResponse):
            parse_diagnosis_json('{"barrier_type": "bogus"}')

    def test_rejects_invalid_misconception(self) -> None:
        with pytest.raises(InvalidDiagnosisResponse):
            parse_diagnosis_json(
                '{"barrier_type": "concept", "misconception_category": "acid_base"}'
            )

    def test_rejects_no_json(self) -> None:
        with pytest.raises(InvalidDiagnosisResponse):
            parse_diagnosis_json("这是一段没有 JSON 的文本")


# ---------------------------------------------------------------------------
# 三级 fallback + 重试 + 退避（task 2.2）
# ---------------------------------------------------------------------------


class TestFallbackAndRetry:
    @staticmethod
    def _make_client(transport, sleeps: list[float]) -> DashScopeDiagnosisClient:
        providers = [
            Provider("mimo", "mimo-model", "http://mimo", "k1"),
            Provider("qwen", "qwen-model", "http://qwen", "k2"),
            Provider("deepseek", "deepseek-model", "http://deepseek", "k3"),
        ]
        return DashScopeDiagnosisClient(
            providers=providers, transport=transport, sleep=sleeps.append
        )

    def test_fallback_order_and_retry(self) -> None:
        calls: list[str] = []
        sleeps: list[float] = []

        def transport(provider: Provider, messages) -> str:
            calls.append(provider.name)
            if provider.name == "deepseek":
                return '{"barrier_type": "concept", "confidence": 0.85}'
            raise LLMTransportError(f"{provider.name} down")

        client = self._make_client(transport, sleeps)
        result = client.chat([{"role": "user", "content": "q"}])

        assert result["barrier_type"] == "concept"
        # MiMo 失败 3 次 → qwen 失败 3 次 → DeepSeek 成功 1 次
        assert calls == ["mimo", "mimo", "mimo", "qwen", "qwen", "qwen", "deepseek"]
        # 每级失败 Provider 在 1→2、2→3 次之间退避 1s / 2s
        assert sleeps == [1, 2, 1, 2]

    def test_all_providers_fail_raises_unavailable(self) -> None:
        def transport(provider: Provider, messages) -> str:
            raise LLMTransportError("down")

        sleeps: list[float] = []
        client = self._make_client(transport, sleeps)
        with pytest.raises(LLMUnavailableError):
            client.chat([{"role": "user", "content": "q"}])
        assert len(sleeps) == 6  # 3 级 × 每级 2 次退避


# ---------------------------------------------------------------------------
# 非法枚举一次 re-prompt 后降级（task 2.3 集成部分）
# ---------------------------------------------------------------------------


class TestRepairReprompt:
    def test_invalid_enum_reprompts_once_then_succeeds(self) -> None:
        calls: list[list[dict[str, str]]] = []

        def transport(provider: Provider, messages) -> str:
            calls.append(messages)
            if len(calls) == 1:
                return '{"barrier_type": "wrong_type"}'
            return '{"barrier_type": "reading", "confidence": 0.7}'

        client = DashScopeDiagnosisClient(
            providers=[Provider("mimo", "m", "http://x", "k")],
            transport=transport,
            sleep=lambda _: None,
        )
        result = client.chat([{"role": "user", "content": "q"}])

        assert result["barrier_type"] == "reading"
        assert len(calls) == 2
        # 第二次调用携带「只返回合法 JSON」修复指令
        assert "只返回" in calls[1][-1]["content"]

    def test_still_invalid_after_repair_raises(self) -> None:
        def transport(provider: Provider, messages) -> str:
            return '{"barrier_type": "wrong_type"}'

        client = DashScopeDiagnosisClient(
            providers=[Provider("mimo", "m", "http://x", "k")],
            transport=transport,
            sleep=lambda _: None,
        )
        with pytest.raises(LLMUnavailableError):
            client.chat([{"role": "user", "content": "q"}])

    def test_empty_providers_raises(self) -> None:
        client = DashScopeDiagnosisClient(
            providers=[],
            transport=lambda p, m: "",
            sleep=lambda _: None,
        )
        with pytest.raises(LLMUnavailableError):
            client.chat([{"role": "user", "content": "q"}])
