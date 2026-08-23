# -*- coding: utf-8 -*-
"""四维安全审核 API。

提供同步即时返回的方程式审核端点。
纯算法 < 50ms，不需要异步轮询。
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from chem_skills.chemistry_audit.engine.auditor import audit_equation
from chem_skills.chemistry_audit.engine.parser import ParseError

router = APIRouter(tags=["审核"], prefix="/api/audit")


# ---------------------------------------------------------------------------
# Pydantic response models（符合 CLAUDE.md API 设计规范）
# ---------------------------------------------------------------------------

class BalanceDetail(BaseModel):
    """系数配平详情。"""

    left_elements: dict[str, int] = Field(default_factory=dict)
    right_elements: dict[str, int] = Field(default_factory=dict)


class DimensionResult(BaseModel):
    """单个维度的审核结果。"""

    status: str
    message: str


class BalanceAudit(DimensionResult):
    """维度 1：系数配平审核结果。"""

    detail: BalanceDetail = Field(default_factory=BalanceDetail)


class ConditionAudit(DimensionResult):
    """维度 2：反应条件审核结果。"""

    conditions_found: list[str] = Field(default_factory=list)
    missing_conditions: list[str] = Field(default_factory=list)


class ProductAudit(DimensionResult):
    """维度 3：产物稳定性审核结果。"""

    issues: list[str] = Field(default_factory=list)


class StructureAudit(DimensionResult):
    """维度 4：分子结构审核结果。"""

    issues: list[str] = Field(default_factory=list)


class Audits(BaseModel):
    """四维审核结果汇总。"""

    balance: BalanceAudit
    condition: ConditionAudit
    product: ProductAudit
    structure: StructureAudit


class AuditReportResponse(BaseModel):
    """四维安全审核综合报告（API 响应）。"""

    question_id: str = ""
    equation: str
    audits: Audits
    overall_status: str
    overall_message: str


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.get(
    "/equation",
    summary="审核化学方程式",
    description="对化学方程式执行四维安全审核（系数配平/反应条件/产物稳定性/分子结构），同步即时返回 AuditReport。",
    response_model=AuditReportResponse,
)
async def audit_equation_endpoint(
    eq: str = Query(..., description="待审核的化学方程式，如 2H2 + O2 → 2H2O"),
) -> AuditReportResponse:
    """审核单个化学方程式。

    示例::

        GET /api/audit/equation?eq=2H2+%2B+O2+%E2%86%92+2H2O
    """
    try:
        report = audit_equation(eq)
    except ParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "parse_error", "message": str(e)},
        )

    return AuditReportResponse(**report.to_dict())
