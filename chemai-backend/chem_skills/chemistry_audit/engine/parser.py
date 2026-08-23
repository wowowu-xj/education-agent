# -*- coding: utf-8 -*-
"""化学方程式解析器。

将化学方程式字符串解析为结构化的反应物和产物列表。
支持多种分隔符格式和括号嵌套保护。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# 解析相关常量
# ---------------------------------------------------------------------------
# 分隔符优先级：→ > = > ->
_SEPARATORS: list[tuple[str, str]] = [
    (r"\rightarrow", "latex_arrow"),
    ("→", "unicode_arrow"),
    ("->", "ascii_arrow"),
    ("=", "equals"),
]

# 元素符号正则：大写字母开头，可选一个小写字母，后跟数字（可能是下标或电荷）
_ELEMENT_RE = re.compile(r"([A-Z][a-z]?)(\d*)")

# LaTeX 下标（含花括号）：_{12} 格式
_LATEX_SUB_RE = re.compile(r"\{(\d+)\}")

# 括号对映射
_BRACKET_PAIRS: dict[str, str] = {"(": ")", "[": "]", "{": "}"}


@dataclass
class ParsedEquation:
    """解析后的方程式。"""

    reactants: list[str]   # 反应物化合物列表
    products: list[str]    # 产物化合物列表
    separator: str         # 使用的分隔符


@dataclass
class CompoundInfo:
    """单个化合物的解析结果。"""

    coefficient: int       # 系数（默认 1）
    formula: str           # 纯化学式（去除系数后）
    elements: dict[str, int]  # 元素原子计数


@dataclass
class ParseError(Exception):
    """方程式解析错误。"""

    message: str
    equation: str

    def __str__(self) -> str:
        return f"ParseError: {self.message} (equation={self.equation!r})"


def parse_equation(equation: str) -> ParsedEquation:
    """解析化学方程式字符串。

    Args:
        equation: 化学方程式字符串，如 "2H2 + O2 → 2H2O"

    Returns:
        ParsedEquation: 包含反应物列表和产物列表

    Raises:
        ParseError: 无法识别分隔符时抛出
    """
    eq = equation.strip()

    # 按分隔符优先级拆分
    for sep_str, sep_name in _SEPARATORS:
        idx = eq.find(sep_str)
        if idx != -1:
            left = eq[:idx].strip()
            right = eq[idx + len(sep_str):].strip()
            reactants = _split_compounds(left)
            products = _split_compounds(right)
            return ParsedEquation(
                reactants=reactants,
                products=products,
                separator=sep_name,
            )

    raise ParseError(message="找不到有效的方程式分隔符", equation=equation)


def _split_compounds(side: str) -> list[str]:
    """按 + 号拆分化合物，保护括号内的 + 号不被误拆。

    Args:
        side: 反应物侧或产物侧的字符串

    Returns:
        化合物字符串列表
    """
    compounds: list[str] = []
    current: list[str] = []
    depth = 0

    prev = ""
    for ch in side:
        if ch in "([{":
            depth += 1
            current.append(ch)
        elif ch in ")]}":
            depth -= 1
            current.append(ch)
        elif ch == "+" and depth == 0:
            # "+" 是电荷标记（前有数字如 Fe2+，或前有 e 如 e-+）时不拆分
            if prev and (prev.isdigit() or prev == "e"):
                current.append(ch)
            else:
                compounds.append("".join(current).strip())
                current = []
        else:
            current.append(ch)
        prev = ch

    if current:
        compounds.append("".join(current).strip())

    return [c for c in compounds if c]


def strip_coefficient(compound: str) -> tuple[int, str]:
    """从化合物字符串中剥离前导数字作为系数。

    Args:
        compound: 如 "2H2O" 或 "3Fe2(SO4)3"

    Returns:
        (coefficient, formula) 元组
    """
    m = re.match(r"^(\d+)(.+)", compound.strip())
    if m:
        return int(m.group(1)), m.group(2)
    return 1, compound.strip()


def count_elements(compound: str) -> dict[str, int]:
    """统计单个化合物中各元素的原子数。

    处理流程：
    1. 剥离系数
    2. 处理 LaTeX 下标（_{12} → _12 简化形式）
    3. 递归展开括号
    4. 正则匹配元素符号和下标

    Args:
        compound: 如 "2H2O", "Ca(OH)2", "Fe2(SO4)3"

    Returns:
        元素→原子数 的字典
    """
    coef, formula = strip_coefficient(compound)
    # 简化 LaTeX 花括号下标
    formula = _LATEX_SUB_RE.sub(r"\1", formula)
    elements = _count_elements_in_formula(formula)
    # 乘以系数
    for elem in elements:
        elements[elem] *= coef
    return elements


def _count_elements_in_formula(formula: str) -> dict[str, int]:
    """统计纯化学式中的元素原子数（不含系数）。"""
    counts: dict[str, int] = {}
    i = 0
    n = len(formula)

    while i < n:
        ch = formula[i]

        # 处理括号：递归展开
        if ch == "(":
            # 找到匹配的右括号
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if formula[j] == "(":
                    depth += 1
                elif formula[j] == ")":
                    depth -= 1
                j += 1
            inner = formula[i + 1 : j - 1]

            # 括号后面的下标数字
            subscript = 1
            if j < n and formula[j].isdigit():
                k = j
                while k < n and formula[k].isdigit():
                    k += 1
                subscript = int(formula[j:k])
                j = k

            # 递归统计括号内部，乘以括号下标
            inner_counts = _count_elements_in_formula(inner)
            for elem, cnt in inner_counts.items():
                counts[elem] = counts.get(elem, 0) + cnt * subscript

            i = j
            continue

        # 匹配元素符号
        m = _ELEMENT_RE.match(formula, i)
        if m:
            elem = m.group(1)
            num_str = m.group(2)
            # 检查数字后面是否为电荷符号（+, -）
            # Ba2+ → 2 是电荷不是下标 → Ba:1
            # H2O → 2 是下标 → H:2
            next_pos = m.end()
            is_charge = (
                num_str
                and next_pos < n
                and formula[next_pos] in "+-"
            )
            if is_charge:
                num = 1  # 电荷数字不计为原子数
            else:
                num = int(num_str) if num_str else 1
            counts[elem] = counts.get(elem, 0) + num
            i = m.end()
            continue

        # 跳过无关字符（如下划线、空格等）
        i += 1

    return counts


def check_brace_balance(formula: str) -> bool:
    """检查化学式中括号是否匹配。

    Args:
        formula: 化学式字符串

    Returns:
        True 表示括号匹配
    """
    stack: list[str] = []
    for ch in formula:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack:
                return False
            expected = _BRACKET_PAIRS.get(stack.pop(), "")
            if expected != ch:
                return False
    return len(stack) == 0
