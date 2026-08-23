# -*- coding: utf-8 -*-
"""四维安全审核引擎主入口。

串联整个审核管道：
归一化 → 解析 → 四维审核 → AuditReport
"""

from __future__ import annotations

from chem_skills.chemistry_audit.engine.models import (
    AuditReport,
    ProductResult,
)
from chem_skills.chemistry_audit.engine.balance import check_balance
from chem_skills.chemistry_audit.engine.conditions import check_conditions
from chem_skills.chemistry_audit.engine.stability import check_stability
from chem_skills.chemistry_audit.engine.structure import check_structure
from chem_skills.chemistry_audit.engine.parser import parse_equation, ParseError
from chem_skills.chemistry_parser.engine.normalizer import normalize_chem_formulas


class AuditEngine:
    """四维安全审核引擎。

    单例模式——引擎无状态、无 IO，纯计算函数。
    所有产生化学方程式的路径都必须经过本引擎校验。

    使用方式::

        engine = AuditEngine()
        report = engine.audit("2H2 + O2 → 2H2O")
        if report.overall_status == "passed":
            print("安全!")
    """

    def audit(
        self,
        equation: str,
        *,
        question_id: str = "",
    ) -> AuditReport:
        """对化学方程式执行四维安全审核。

        管道：归一化 → 解析 → 四维审核 → AuditReport

        Args:
            equation: 待审核的化学方程式字符串
            question_id: 关联的题目 ID（可选）

        Returns:
            AuditReport: 包含四维度审核结果的完整报告
        """
        # Step 0: 归一化 —— 统一箭头符号、处理裸化学式格式
        normalized = normalize_chem_formulas(equation)

        # 保留原始方程式在报告中，使用归一化版本做审核
        report = AuditReport(equation=equation, question_id=question_id)

        # Step 1: 维度 1 — 系数配平
        report.balance = check_balance(normalized)

        # Step 2: 维度 2 — 反应条件
        report.condition = check_conditions(normalized)

        # Step 3: 维度 3 — 产物稳定性（需要先解析出产物列表）
        try:
            parsed = parse_equation(normalized)
            report.product = check_stability(normalized, parsed.products)
        except ParseError:
            report.product = ProductResult(
                status="warning",
                message="无法解析方程式，跳过产物审核",
            )

        # Step 4: 维度 4 — 分子结构
        report.structure = check_structure(normalized)

        return report


# 全局单例
_engine = AuditEngine()


def audit_equation(
    equation: str,
    *,
    question_id: str = "",
) -> AuditReport:
    """审核化学方程式的全局快捷函数。

    Args:
        equation: 化学方程式字符串
        question_id: 关联题目 ID（可选）

    Returns:
        AuditReport: 四维度审核报告
    """
    return _engine.audit(equation, question_id=question_id)
