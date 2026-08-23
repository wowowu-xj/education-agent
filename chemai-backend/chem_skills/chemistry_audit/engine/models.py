# -*- coding: utf-8 -*-
"""四维安全审核数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# 各维度状态字面量
# ---------------------------------------------------------------------------
BalanceStatus = Literal["passed", "blocked"]
ConditionStatus = Literal["passed", "warning", "failed"]
ProductStatus = Literal["passed", "warning", "failed"]
StructureStatus = Literal["passed", "failed"]
OverallStatus = Literal["passed", "blocked"]


@dataclass
class BalanceResult:
    """维度 1：系数配平审核结果。"""

    status: BalanceStatus
    message: str
    left_elements: dict[str, int] = field(default_factory=dict)
    right_elements: dict[str, int] = field(default_factory=dict)


@dataclass
class ConditionResult:
    """维度 2：反应条件审核结果。"""

    status: ConditionStatus
    message: str
    conditions_found: list[str] = field(default_factory=list)
    missing_conditions: list[str] = field(default_factory=list)


@dataclass
class ProductResult:
    """维度 3：产物稳定性审核结果。"""

    status: ProductStatus
    message: str
    issues: list[str] = field(default_factory=list)


@dataclass
class StructureResult:
    """维度 4：分子结构审核结果。"""

    status: StructureStatus
    message: str
    issues: list[str] = field(default_factory=list)


@dataclass
class AuditReport:
    """四维安全审核综合报告。

    与文档 26 §6.1 定义的 JSON 结构一致。
    """

    equation: str
    question_id: str = ""
    balance: BalanceResult = field(default_factory=lambda: BalanceResult(
        status="passed", message="",
    ))
    condition: ConditionResult = field(default_factory=lambda: ConditionResult(
        status="passed", message="",
    ))
    product: ProductResult = field(default_factory=lambda: ProductResult(
        status="passed", message="",
    ))
    structure: StructureResult = field(default_factory=lambda: StructureResult(
        status="passed", message="",
    ))

    @property
    def overall_status(self) -> OverallStatus:
        """综合判定：任一维度 blocked 则整体 blocked。"""
        if self.balance.status == "blocked":
            return "blocked"
        if self.condition.status == "failed":
            return "blocked"
        if self.product.status == "failed":
            return "blocked"
        if self.structure.status == "failed":
            return "blocked"
        return "passed"

    @property
    def overall_message(self) -> str:
        """综合判定描述。"""
        status = self.overall_status
        if status == "passed":
            parts = ["四维审核通过"]
            warnings: list[str] = []
            if self.condition.status == "warning":
                warnings.append(f"条件审核警告: {self.condition.message}")
            if self.product.status == "warning":
                warnings.append(f"产物审核警告: {self.product.message}")
            if warnings:
                parts.append("; ".join(warnings))
            return ". ".join(parts)
        else:
            failures: list[str] = []
            if self.balance.status == "blocked":
                failures.append(f"系数配平: {self.balance.message}")
            if self.condition.status == "failed":
                failures.append(f"反应条件: {self.condition.message}")
            if self.product.status == "failed":
                failures.append(f"产物稳定性: {self.product.message}")
            if self.structure.status == "failed":
                failures.append(f"分子结构: {self.structure.message}")
            return "审核拦截 — " + "; ".join(failures)

    def to_dict(self) -> dict:
        """转为 JSON 兼容的字典（与文档 26 §6.1 格式一致）。"""
        return {
            "question_id": self.question_id,
            "equation": self.equation,
            "audits": {
                "balance": {
                    "status": self.balance.status,
                    "message": self.balance.message,
                    "detail": {
                        "left_elements": self.balance.left_elements,
                        "right_elements": self.balance.right_elements,
                    },
                },
                "condition": {
                    "status": self.condition.status,
                    "message": self.condition.message,
                    "conditions_found": self.condition.conditions_found,
                    "missing_conditions": self.condition.missing_conditions,
                },
                "product": {
                    "status": self.product.status,
                    "message": self.product.message,
                    "issues": self.product.issues,
                },
                "structure": {
                    "status": self.structure.status,
                    "message": self.structure.message,
                    "issues": self.structure.issues,
                },
            },
            "overall_status": self.overall_status,
            "overall_message": self.overall_message,
        }
