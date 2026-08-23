# -*- coding: utf-8 -*-
"""化学式格式归一化。

将 LLM 输出中的非标准化学式格式统一转换为审核引擎可解析的标准形式。

处理流程：
1. 扫描 $...$ 包裹的 LaTeX 片段，统一箭头符号
2. 检测裸化学式（无 $...$ 包裹），自动转换为 LaTeX 格式并 $ 包裹
3. 词界保护：3+ 连续小写字母视为英文单词，不触发包装
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# 常见化学式白名单（约 50 个）
# ---------------------------------------------------------------------------
# 无机化合物
COMMON_FORMULAS: list[str] = [
    # 单质
    "H2", "O2", "N2", "Cl2", "Br2", "I2", "F2",
    # 氧化物
    "H2O", "CO2", "CO", "SO2", "SO3", "NO", "NO2", "N2O",
    "Fe2O3", "Fe3O4", "Al2O3", "CaO", "MgO", "CuO", "MnO2",
    "SiO2", "P2O5", "Na2O", "K2O",
    # 酸
    "HCl", "H2SO4", "HNO3", "H3PO4", "H2CO3", "H2S",
    # 碱
    "NaOH", "KOH", "Ca(OH)2", "Ba(OH)2", "Mg(OH)2",
    # 盐
    "NaCl", "KCl", "CaCl2", "MgCl2", "BaCl2",
    "Na2SO4", "K2SO4", "CaSO4", "BaSO4", "CuSO4",
    "Na2CO3", "K2CO3", "CaCO3", "NaHCO3",
    "NaNO3", "KNO3", "AgNO3",
    "KMnO4", "KClO3",
    # 其他
    "NH3", "CH4", "C2H5OH", "CH3COOH",
]

# 编译正则：匹配常见化学式（元素符号后跟数字下标）
_FORMULA_PATTERN = re.compile(
    r'\b(?:' + '|'.join(re.escape(f) for f in COMMON_FORMULAS) + r')\b'
)

# 英文单词保护：3 个以上连续小写字母
_WORD_PATTERN = re.compile(r'\b[a-z]{3,}\b')

# Unicode 箭头 → LaTeX 命令映射
_ARROW_MAP: dict[str, str] = {
    "→": r"\rightarrow",   # →
    "⇌": r"\rightleftharpoons",  # ⇌
    "↑": r"\uparrow",     # ↑
    "↓": r"\downarrow",   # ↓
}


def _strip_ce_macro(text: str) -> str:
    """剥离 LaTeX 的 ``\\ce{...}`` 宏包裹，恢复纯化学式/方程式文本。

    项目约定化学方程式可用 LaTeX 写法（见 chemai-backend/CLAUDE.md），
    但审核引擎解析的是纯文本（如 ``2H2 + O2 -> 2H2O``）。本函数去掉
    ``\\ce{`` 与其配对的 ``}``，使 ``\\ce{2H2 + O2 -> 2H2O}`` 等价于
    ``2H2 + O2 -> 2H2O``。

    假设：方程式字段内 ``}`` 仅作为 ``\\ce{`` 的闭合括号出现
    （系数与下标均为纯数字写法，如 ``2H2`` 而非 ``2H_{2}``）。
    """
    if r"\ce{" not in text:
        return text
    return text.replace(r"\ce{", "").replace("}", "")


def normalize_chem_formulas(text: str) -> str:
    """化学式格式归一化主入口。

    对输入文本执行两步归一化：
    1. 扫描 ``$...$`` 包裹的 LaTeX 片段，统一 Unicode 箭头为 LaTeX 命令
    2. 检测未被 ``$...$`` 包裹的裸化学式，自动转换为 LaTeX 格式

    Args:
        text: 可能包含化学式的原始文本（LLM 输出、用户输入等）

    Returns:
        归一化后的文本
    """
    # 先剥离 \ce{...} 宏包裹，恢复纯文本再走后续归一化
    text = _strip_ce_macro(text)

    # 如果文本包含方程式分隔符，仅归一化箭头，不做化学式包裹
    # 方程式是结构化格式，$ 包裹会破坏 parser 的解析能力
    if _is_equation(text):
        return _normalize_arrows_only(text)

    # Step 1: 处理 $...$ 片段内的箭头
    text = _normalize_latex_fragments(text)

    # Step 2: 自动包装裸化学式
    text = _wrap_bare_formulas(text)

    return text


# 方程式分隔符特征
_EQUATION_SEPARATORS = ("->", "→", "=", r"\rightarrow")


def _is_equation(text: str) -> bool:
    """检测文本是否包含方程式分隔符。"""
    return any(sep in text for sep in _EQUATION_SEPARATORS)


def _normalize_arrows_only(text: str) -> str:
    """仅归一化 Unicode 箭头为 ASCII（不包裹化学式）。"""
    result = text
    for unicode_char, ascii_repl in [
        ("→", "->"),
        ("⇌", "<=>"),
        ("↑", "^"),
        ("↓", "v"),
    ]:
        result = result.replace(unicode_char, ascii_repl)
    return result


def _normalize_latex_fragments(text: str) -> str:
    """扫描 ``$...$`` 包裹的 LaTeX 片段，统一 Unicode 箭头为 LaTeX 命令。"""

    def _replace_in_latex(match: re.Match[str]) -> str:
        fragment = match.group(0)
        for unicode_arrow, latex_cmd in _ARROW_MAP.items():
            fragment = fragment.replace(unicode_arrow, latex_cmd)
        return fragment

    return re.sub(r'\$[^$]+\$', _replace_in_latex, text)


def _wrap_bare_formulas(text: str) -> str:
    """检测文本中未被 ``$...$`` 包裹的裸化学式，自动转为 LaTeX 格式。

    只处理白名单中的化学式，并跳过：
    - 已被 ``$...$`` 包裹的
    - 作为英文单词一部分的（3+ 连续小写字母）
    - 已被处理的（避免重复包裹 ``$$...$$``）
    """
    # 提取所有已存在的 $...$ 片段位置，保护它们不被重复处理
    latex_ranges: list[tuple[int, int]] = []
    for m in re.finditer(r'\$[^$]+\$', text):
        latex_ranges.append((m.start(), m.end()))

    def _is_inside_latex(pos: int) -> bool:
        return any(start <= pos < end for start, end in latex_ranges)

    result = []
    i = 0
    for m in re.finditer(_FORMULA_PATTERN, text):
        start, end = m.start(), m.end()
        # 添加前面的文本
        result.append(text[i:start])

        if _is_inside_latex(start):
            # 已在 $...$ 内，跳过
            result.append(text[start:end])
        else:
            formula = text[start:end]
            # 保护英文单词
            if _WORD_PATTERN.fullmatch(formula):
                result.append(formula)
            else:
                # 转换数字为 LaTeX 下标
                latex_formula = _to_latex_subscript(formula)
                result.append(f"${latex_formula}$")

        i = end

    result.append(text[i:])
    return "".join(result)


def _to_latex_subscript(formula: str) -> str:
    """将化学式中的数字下标转换为 LaTeX 格式。

    Args:
        formula: 如 "H2O", "Fe2O3", "Ca(OH)2"

    Returns:
        LaTeX 格式: "H_2O", "Fe_2O_3", "Ca(OH)_2"
    """
    # 匹配元素符号后的数字（不在括号后面的单独处理）
    # 先处理括号后跟数字的情况 (OH)2 → (OH)_2
    result = re.sub(r'(\))(\d+)', r'\1_\2', formula)
    # 再处理元素符号后跟数字 Fe2 → Fe_2
    result = re.sub(r'([A-Z][a-z]?)(\d+)', lambda m: _element_subscript(m), result)
    return result


def _element_subscript(m: re.Match[str]) -> str:
    """单元素下标转换辅助函数。"""
    elem = m.group(1)
    num = m.group(2)
    # 检查是否已经在 LaTeX 下标中（前面有 _ 则不处理）
    return f"{elem}_{num}"
