# -*- coding: utf-8 -*-
"""障碍诊断引擎。

三引擎三阶段诊断（见 design D2）：
规则引擎（关键词预分类，保守置信度）→ LLM（深度诊断）→
置信度融合（2×2 决策表）。识别「障碍类型」与「迷思概念」两个正交维度。
"""

from chem_skills.chemistry_diagnosis.engine.llm_client import (
    DashScopeDiagnosisClient,
    DiagnosisLLMClient,
    InvalidDiagnosisResponse,
    LLMTransportError,
    LLMUnavailableError,
    parse_diagnosis_json,
    parse_plan_json,
)

__all__ = [
    "DiagnosisLLMClient",
    "DashScopeDiagnosisClient",
    "InvalidDiagnosisResponse",
    "LLMTransportError",
    "LLMUnavailableError",
    "parse_diagnosis_json",
    "parse_plan_json",
]
