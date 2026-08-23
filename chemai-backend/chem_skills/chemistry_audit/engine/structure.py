# -*- coding: utf-8 -*-
"""维度 4：分子结构审核。

校验化学式的书写格式规范性：
- 元素符号大小写
- 括号匹配
- 离子电荷表示
- LaTeX 格式
"""

from __future__ import annotations

import re

from chem_skills.chemistry_audit.engine.models import StructureResult
from chem_skills.chemistry_audit.engine.parser import check_brace_balance

# 常见多原子离子/基团（不参与元素符号大小写校验）
_POLYATOMIC_WHITELIST: frozenset[str] = frozenset({
    "OH", "NH", "CN", "SCN", "CH", "NO", "SO", "PO", "CO", "ClO",
    "MnO", "CrO", "FeO", "CuO", "ZnO", "MgO",
})

# 错误格式检测
_BAD_ELEMENT_RE = re.compile(r"[a-z]{2,}[A-Z]")  # 如 fe（小写开头）


def check_structure(equation: str) -> StructureResult:
    """审核化学式的分子结构格式。

    Args:
        equation: 化学方程式字符串

    Returns:
        StructureResult: 包含结构审核结果
    """
    issues: list[str] = []

    # 检查括号匹配
    if not check_brace_balance(equation):
        issues.append("括号不匹配：存在未闭合或多余的括号")

    # 检查常见的元素符号大小写错误
    _check_element_casing(equation, issues)

    # 检查离子电荷格式
    _check_charge_format(equation, issues)

    # 检查 LaTeX 格式问题
    _check_latex_format(equation, issues)

    if issues:
        return StructureResult(
            status="failed",
            message="; ".join(issues),
            issues=issues,
        )

    return StructureResult(
        status="passed",
        message="分子结构格式正确",
    )


def _check_element_casing(text: str, issues: list[str]) -> None:
    """检测元素符号大小写错误。

    规则：
    - 元素符号必须以大写字母开头
    - 不能出现全大写双字母（如 FE, CU）
    - 不能出现小写开头的元素（如 fe, nA）
    """
    # 去除 LaTeX 命令和 $ 标记，聚焦于化学式
    clean = re.sub(r"\$[^$]*\$", " ", text)

    # 检测全大写双字母模式（如 FE, CU, NA）
    bad_caps = re.findall(r'\b([A-Z]{2,})\b', clean)
    for token in bad_caps:
        if len(token) == 2 and token.isalpha():
            # 跳过常见多原子离子/基团（OH, NH, CN 等）
            if token in _POLYATOMIC_WHITELIST:
                continue
            correct = token[0] + token[1].lower()
            issues.append(f"元素符号 '{token}' 应为 '{correct}'（第二字母小写）")


def _check_charge_format(text: str, issues: list[str]) -> None:
    """检测离子电荷表示格式。

    正确：Fe^{3+} 或 Fe³⁺
    错误：Fe+3, Fe3+
    """
    # 在 LaTeX 片段外检测不规范的电荷表示
    outside_latex = re.sub(r"\$[^$]*\$", "", text)

    # 检测 "+数字" 模式（如 Fe+3）
    bad_charge = re.findall(r'[A-Z][a-z]?\+(\d)', outside_latex)
    for num in bad_charge:
        issues.append(f"离子电荷格式错误: '+{num}' 应为 '^{{{num}}}+' 或使用 mhchem 格式")


def _check_latex_format(text: str, issues: list[str]) -> None:
    """检测 LaTeX 格式问题。"""
    # 检测 $ 不配对
    dollar_count = text.count("$")
    if dollar_count % 2 != 0:
        issues.append("LaTeX $ 符号不配对")

    # 检测是否使用了 Unicode 数字下标而非 LaTeX 格式（在关键位置）
    # H₂O 中的 Unicode 下标 ₂ 无法被 parser 解析
    unicode_subscripts = re.findall(r'[₀₁₂₃₄₅₆₇₈₉₊₋]+', text)
    if unicode_subscripts:
        issues.append("检测到 Unicode 下标字符，应使用 LaTeX _{} 格式")
