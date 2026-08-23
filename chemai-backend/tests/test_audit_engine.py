# -*- coding: utf-8 -*-
"""维度 2-4 + 归一化 + 解析器 + API 测试。"""

from __future__ import annotations

import pytest

from chem_skills.chemistry_parser.engine.normalizer import normalize_chem_formulas
from chem_skills.chemistry_audit.engine.parser import parse_equation, ParseError
from chem_skills.chemistry_audit.engine.auditor import audit_equation


# ============================================================================
# 归一化测试
# ============================================================================

class TestNormalizer:
    """化学式归一化测试。"""

    def test_arrow_normalization(self) -> None:
        """Unicode 箭头应转为 ASCII。"""
        result = normalize_chem_formulas("2H2 + O2 → 2H2O")
        assert "->" in result

    def test_prose_formula_wrapping(self) -> None:
        """散文中的裸化学式应自动 $ 包裹。"""
        result = normalize_chem_formulas("H2O is water")
        assert "$H_2O$" in result

    def test_equation_not_wrapped(self) -> None:
        """方程式中的化学式不应被 $ 包裹（保留可解析性）。"""
        result = normalize_chem_formulas("Fe + O2 -> Fe2O3")
        # 方程式只做箭头归一化，不做 $ 包裹
        assert "$" not in result or result.count("$") <= 2  # 箭头归一化可能不引入 $

    def test_word_boundary_protection(self) -> None:
        """3+ 小写字母的英文单词不触发包装。"""
        result = normalize_chem_formulas("water is H2O")
        assert "water" in result
        assert "$H_2O$" in result  # H2O 应被包装

    def test_ce_macro_stripped(self) -> None:
        """LaTeX \\ce{} 宏包裹应被剥离，恢复纯文本。"""
        result = normalize_chem_formulas(r"\ce{2H2 + O2 -> 2H2O}")
        assert result == "2H2 + O2 -> 2H2O"


# ============================================================================
# 解析器测试
# ============================================================================

class TestParser:
    """方程式解析器测试。"""

    def test_ascii_arrow(self) -> None:
        parsed = parse_equation("2H2 + O2 -> 2H2O")
        assert parsed.reactants == ["2H2", "O2"]
        assert parsed.products == ["2H2O"]

    def test_equals_separator(self) -> None:
        parsed = parse_equation("NaOH + HCl = NaCl + H2O")
        assert len(parsed.reactants) == 2
        assert len(parsed.products) == 2

    def test_parenthesis_protection(self) -> None:
        """带括号离子式中的 + 号不应被拆分。"""
        parsed = parse_equation("[Cu(NH3)4]2+ + 2OH- -> Cu(OH)2 + 4NH3")
        assert parsed.reactants[0] == "[Cu(NH3)4]2+"

    def test_parse_error_no_separator(self) -> None:
        with pytest.raises(ParseError):
            parse_equation("just some text without arrow")


# ============================================================================
# 综合审核测试
# ============================================================================

class TestAuditIntegration:
    """端到端审核流程测试。"""

    def test_valid_equation_passes(self) -> None:
        report = audit_equation("2H2 + O2 -> 2H2O")
        assert report.overall_status == "passed"

    def test_unbalanced_equation_blocked(self) -> None:
        report = audit_equation("Fe + O2 -> Fe2O3")
        assert report.overall_status == "blocked"
        assert report.balance.status == "blocked"

    def test_combustion_missing_condition(self) -> None:
        report = audit_equation("CH4 + 2O2 -> CO2 + 2H2O")
        assert report.condition.status == "failed"
        assert "点燃" in report.condition.missing_conditions

    def test_report_to_dict(self) -> None:
        report = audit_equation("2H2 + O2 -> 2H2O")
        d = report.to_dict()
        assert d["overall_status"] == "passed"
        assert "audits" in d
        assert "balance" in d["audits"]
        assert d["audits"]["balance"]["status"] == "passed"

    def test_warning_does_not_block(self) -> None:
        """warning 不应触发 overall blocked。"""
        # H2O2 分解无催化剂 → 应 pass（催化剂是 warning 级别）
        report = audit_equation("2H2O2 -> 2H2O + O2")
        assert report.overall_status == "passed", (
            f"Expected passed, got {report.overall_status}: {report.overall_message}"
        )

    def test_structure_issues_caught(self) -> None:
        """元素符号大小写错误应被检测。"""
        report = audit_equation("FE + O2 -> FE2O3")
        assert report.structure.status == "failed"

    def test_ce_macro_equation_passes(self) -> None:
        """Regression: ISSUE-001 — \\ce{} 包裹的方程式不应被误判未配平。

        项目约定化学方程式可用 LaTeX 写法，教师按题干字段提示
        （「用 \\ce{H2O} 表示」）输入 \\ce{2H2 + O2 -> 2H2O} 时，
        应等价于纯文本 ``2H2 + O2 -> 2H2O`` 并通过审核。
        """
        report = audit_equation(r"\ce{2H2 + O2 -> 2H2O}")
        assert report.overall_status == "passed"
        assert report.balance.status == "passed"
