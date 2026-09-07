# -*- coding: utf-8 -*-
"""诊断 LLM 客户端：三级 fallback + 重试 + JSON 鲁棒解析。

对应 design D4：
- 三级模型 fallback：MiMo-V2.5 → qwen-turbo → DeepSeek-V4-Flash
- 每级重试 3 次 + 指数退避
- 解析 / 枚举失败时带「只返回合法枚举 JSON」的 re-prompt 重试一次，
  仍失败才降级下一级 Provider；全部失败抛 :class:`LLMUnavailableError`，
  由编排层降级到规则引擎兜底。

生产路径：:class:`DashScopeDiagnosisClient`（httpx 直连 OpenAI 兼容端点）。
测试路径：注入 `providers` / `transport` / `sleep`，避免真实网络。
"""

from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass
from typing import Callable, Protocol

import httpx

from app.core.config import settings
from app.core.enums import BarrierType, MisconceptionCategory

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class DiagnosisLLMError(Exception):
    """诊断 LLM 客户端基类异常。"""


class LLMUnavailableError(DiagnosisLLMError):
    """所有 Provider 均失败（含修复重试），无法产出诊断。"""


class LLMTransportError(DiagnosisLLMError):
    """单个 Provider 的 HTTP 层失败（超时 / 非 2xx / 网络错误）。"""


class InvalidDiagnosisResponse(DiagnosisLLMError):
    """LLM 返回文本无法解析为合法诊断 JSON。"""


# ---------------------------------------------------------------------------
# 枚举取值集合（用于 JSON 校验）
# ---------------------------------------------------------------------------

_VALID_BARRIERS = frozenset(m.value for m in BarrierType)
_VALID_MISCONCEPTIONS = frozenset(m.value for m in MisconceptionCategory)

# re-prompt 指令：解析 / 枚举失败时追加，要求只返回合法枚举 JSON。
_REPAIR_INSTRUCTION = (
    "只返回一个 JSON 对象，不要输出任何解释、Markdown 或代码围栏。"
    '字段固定为：{"barrier_type": "concept|reading|expression", '
    '"misconception_category": "chemical_equilibrium|redox|mole_calculation|'
    'organic_chemistry|chemical_notation|structure_properties|null", '
    '"confidence": 0 到 1 之间的小数, "reasoning": "诊断依据", '
    '"suggestion": "教学建议"}'
)

# 学习计划的 re-prompt 指令（计划为自由结构，无需枚举校验）。
_PLAN_REPAIR_INSTRUCTION = (
    "只返回一个 JSON 对象，不要输出任何解释、Markdown 或代码围栏。"
    '字段固定为：{"title": "计划标题", "goal": "计划目标", '
    '"items": ["具体学习任务一", "具体学习任务二"], "duration_days": 建议天数整数}'
)


# ---------------------------------------------------------------------------
# JSON 鲁棒解析（纯函数，独立可测）
# ---------------------------------------------------------------------------


def extract_json(text: str) -> str:
    """从 LLM 文本中剥离 markdown 代码围栏并定位 JSON 对象子串。

    Args:
        text: LLM 原始输出（可能带 ```json ... ``` 围栏或前后说明文字）。

    Returns:
        str: 首个 ``{...}`` 对象的原文子串。

    Raises:
        InvalidDiagnosisResponse: 文本为空或不含 JSON 对象。
    """
    if not text:
        raise InvalidDiagnosisResponse("空响应")

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if fence:
        text = fence.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise InvalidDiagnosisResponse("响应中未找到 JSON 对象")
    return text[start : end + 1]


def _lenient_json_loads(raw: str) -> dict:
    """宽松解析 JSON 对象：标准失败后容忍尾逗号再试。"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            raise InvalidDiagnosisResponse(f"JSON 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise InvalidDiagnosisResponse("JSON 顶层不是对象")
    return data


def parse_diagnosis_json(text: str) -> dict:
    """把 LLM 文本解析并校验为诊断结果字典。

    Args:
        text: LLM 原始输出。

    Returns:
        dict: 键 ``barrier_type``（必填）、``misconception_category``（可空）、
        ``confidence``（float，缺省 0.5 并裁剪到 [0, 1]）、``reasoning``、
        ``suggestion``。

    Raises:
        InvalidDiagnosisResponse: 无 JSON / 解析失败 / 枚举非法。
    """
    raw = extract_json(text)
    data = _lenient_json_loads(raw)

    barrier = data.get("barrier_type")
    if barrier not in _VALID_BARRIERS:
        raise InvalidDiagnosisResponse(f"非法 barrier_type: {barrier!r}")

    misconception = data.get("misconception_category")
    if misconception is not None and misconception not in _VALID_MISCONCEPTIONS:
        raise InvalidDiagnosisResponse(
            f"非法 misconception_category: {misconception!r}"
        )

    try:
        confidence = float(data.get("confidence", 0.5))
    except (TypeError, ValueError) as exc:
        raise InvalidDiagnosisResponse("confidence 非法") from exc
    if not math.isfinite(confidence):
        # NaN / ±Inf：Python json.loads 默认接受 NaN/Infinity 字面量，
        # 而 min/max 对 NaN 语义不可靠，会静默裁剪成 1.0（满置信自动采纳）。
        # 此处显式拒绝，交由修复重试 / 规则兜底处理（code-review F3）。
        raise InvalidDiagnosisResponse(f"confidence 非有限数值: {confidence!r}")
    confidence = max(0.0, min(1.0, confidence))

    return {
        "barrier_type": barrier,
        "misconception_category": misconception,
        "confidence": confidence,
        "reasoning": str(data.get("reasoning", "")),
        "suggestion": str(data.get("suggestion", "")),
    }


def parse_plan_json(text: str) -> dict:
    """把 LLM 文本解析为学习计划字典（自由结构，不做枚举校验）。

    学习计划与诊断不同：计划内容由标题/目标/任务列表组成，无受控枚举，
    因此这里只做「剥离围栏 + 宽松解析 + 顶层是对象」三道鲁棒处理，
    其余字段原样透传（缺省字段在生成层补齐）。

    Args:
        text: LLM 原始输出。

    Returns:
        dict: 学习计划 JSON。

    Raises:
        InvalidDiagnosisResponse: 无 JSON / 解析失败。
    """
    return _lenient_json_loads(extract_json(text))


# ---------------------------------------------------------------------------
# Protocol 与 Provider
# ---------------------------------------------------------------------------


class DiagnosisLLMClient(Protocol):
    """诊断 LLM 客户端注入缝。

    diagnosis.py 通过构造注入本 Protocol 的实现；单测传 FakeLLM，
    生产传 :class:`DashScopeDiagnosisClient`。
    """

    def chat(self, messages: list[dict[str, str]]) -> dict:
        """发送对话消息，返回解析并校验后的诊断结果。

        Args:
            messages: OpenAI 兼容格式的 messages 列表。

        Returns:
            dict: 见 :func:`parse_diagnosis_json` 的返回值。

        Raises:
            LLMUnavailableError: 所有 Provider 失败。
        """
        ...


@dataclass(frozen=True)
class Provider:
    """一个可回退的 LLM Provider（模型 + 端点 + 密钥）。"""

    name: str
    model: str
    base_url: str
    api_key: str


# transport 注入缝：给定 Provider 与消息，返回原始文本；失败抛 LLMTransportError。
Transport = Callable[[Provider, list[dict[str, str]]], str]


# ---------------------------------------------------------------------------
# 真实客户端
# ---------------------------------------------------------------------------


class DashScopeDiagnosisClient:
    """真实对话客户端：三级 fallback + 重试 + 鲁棒解析。

    ``providers`` / ``transport`` / ``sleep`` 为测试注入缝；生产环境
    用默认值（从 settings 构建 Provider 链，httpx 直连，time.sleep 退避）。
    """

    MAX_RETRIES = 3

    def __init__(
        self,
        *,
        providers: list[Provider] | None = None,
        transport: Transport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        parse: Callable[[str], dict] = parse_diagnosis_json,
        repair_instruction: str = _REPAIR_INSTRUCTION,
    ) -> None:
        self._providers = providers if providers is not None else self._build_providers()
        self._transport = transport or self._http_transport
        self._sleep = sleep
        self._parse = parse
        self._repair_instruction = repair_instruction

    @staticmethod
    def _build_providers() -> list[Provider]:
        """从 settings 构建三级 fallback Provider 链（跳过缺密钥的）。"""
        candidates = (
            (
                "mimo",
                settings.LLM_MODEL_PRIMARY,
                settings.LLM_DASHSCOPE_BASE_URL,
                settings.DASHSCOPE_API_KEY,
            ),
            (
                "qwen",
                settings.LLM_MODEL_SECONDARY,
                settings.LLM_DASHSCOPE_BASE_URL,
                settings.DASHSCOPE_API_KEY,
            ),
            (
                "deepseek",
                settings.LLM_MODEL_TERTIARY,
                settings.LLM_DEEPSEEK_BASE_URL,
                settings.DEEPSEEK_API_KEY,
            ),
        )
        providers: list[Provider] = []
        for name, model, base_url, api_key in candidates:
            if api_key:
                providers.append(
                    Provider(name=name, model=model, base_url=base_url, api_key=api_key)
                )
        return providers

    def chat(self, messages: list[dict[str, str]]) -> dict:
        """发送诊断对话并解析结果，按三级顺序回退。

        Raises:
            LLMUnavailableError: 所有 Provider 重试耗尽仍失败。
        """
        if not self._providers:
            raise LLMUnavailableError("未配置任何 LLM Provider（缺少 API Key）")

        messages = list(messages)
        repaired = False
        last_error: Exception | None = None

        for provider in self._providers:
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    text = self._transport(provider, messages)
                except LLMTransportError as exc:
                    last_error = exc
                else:
                    try:
                        return self._parse(text)
                    except InvalidDiagnosisResponse as exc:
                        last_error = exc
                        if not repaired:
                            # 修复重试一次：带「只返回合法 JSON」指令立即重试，不占退避
                            repaired = True
                            messages = messages + [
                                {"role": "user", "content": self._repair_instruction}
                            ]
                            continue
                # 未成功：指数退避后进入下一次尝试
                if attempt < self.MAX_RETRIES:
                    self._sleep(2 ** (attempt - 1))

        raise LLMUnavailableError(f"所有 Provider 均失败: {last_error}")

    def _http_transport(self, provider: Provider, messages: list[dict[str, str]]) -> str:
        """httpx 直连 OpenAI 兼容端点，返回消息正文。"""
        url = f"{provider.base_url.rstrip('/')}/chat/completions"
        try:
            resp = httpx.post(
                url,
                headers={"Authorization": f"Bearer {provider.api_key}"},
                json={"model": provider.model, "messages": messages},
                timeout=30.0,
            )
        except httpx.HTTPError as exc:
            raise LLMTransportError(f"{provider.name} 请求失败: {exc}") from exc

        if resp.status_code != 200:
            raise LLMTransportError(
                f"{provider.name} HTTP {resp.status_code}: {resp.text[:200]}"
            )

        try:
            content = resp.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise InvalidDiagnosisResponse(
                f"{provider.name} 响应结构异常"
            ) from exc
        return content
