# -*- coding: utf-8 -*-
"""维度 3：产物稳定性审核。

检测产物的化学合理性：
- 不稳定产物自动分解（H₂CO₃ → CO₂↑ + H₂O）— HARD FAIL
- 沉淀生成规则（Ca²⁺ + CO₃²⁻ → CaCO₃↓）— WARNING（建议标注）
- 氧化还原产物与氧化剂强度匹配 — FAIL
"""

from __future__ import annotations

import re

from chem_skills.chemistry_audit.engine.models import ProductResult

# ---------------------------------------------------------------------------
# 不稳定产物 — 触发 status=failed（文档 26 §4.1.1 气体逸出规则）必需
# ---------------------------------------------------------------------------
_UNSTABLE_PRODUCTS: dict[str, str] = {
    "H2CO3": "H₂CO₃ = CO₂↑ + H₂O，不存在游离态碳酸",
    "H2SO3": "H₂SO₃ 不稳定分解为 SO₂↑ + H₂O",
    "NH4OH": "NH₄OH = NH₃↑ + H₂O，不存在游离态",
}

# ---------------------------------------------------------------------------
# 沉淀离子组合（文档 26 §4.1.2）— 触发 status=warning（建议标注）
# ---------------------------------------------------------------------------
_PRECIPITATION_RULES: list[tuple[str, str, str]] = [
    ("Ca2+", "CO3", "CaCO₃↓ 白色沉淀"),
    ("Ba2+", "SO4", "BaSO₄↓ 不溶于酸的白色沉淀"),
    ("Ag+", "Cl-", "AgCl↓ 白色沉淀"),
    ("Fe3+", "OH-", "Fe(OH)₃↓ 红褐色沉淀"),
    ("Cu2+", "OH-", "Cu(OH)₂↓ 蓝色沉淀"),
    ("Al3+", "OH-", "Al(OH)₃↓ 白色胶状沉淀"),
    ("Mg2+", "OH-", "Mg(OH)₂↓ 白色沉淀"),
    ("Pb2+", "SO4", "PbSO₄↓ 白色沉淀"),
]

# ---------------------------------------------------------------------------
# 氧化还原产物合理性（文档 26 §4.1.3）— 触发 status=failed
# ---------------------------------------------------------------------------
_REDOX_RULES: list[tuple[str, str, str, str]] = [
    # (氧化剂特征, 错误产物, 正确产物, 说明)
    ("浓H2SO4", "H2", "SO2", "浓硫酸氧化性来自 S(+6)，被还原为 SO₂"),
    ("浓HNO3", "H2", "NO2", "浓硝酸被还原为 NO₂"),
    ("稀HNO3", "H2", "NO", "稀硝酸被还原为 NO"),
]

# 有机物产物检测
_ORGANIC_PRODUCT_RE = re.compile(r'C\d*H\d*O\d*')
# 碳单质检测（孤立 C，不跟数字）
_CARBON_SINGLETON_RE = re.compile(r'\bC\b(?!\d)')


def check_stability(equation: str, products: list[str]) -> ProductResult:
    """审核产物化学合理性。

    Args:
        equation: 完整方程式字符串（用于氧化还原规则上下文检测）
        products: 产物化合物列表（来自 parser，用于产物级检测）

    Returns:
        ProductResult: 包含产物审核结果
    """
    issues: list[str] = []
    failures: list[str] = []
    warnings: list[str] = []
    all_products_text = " ".join(products)

    # ---- 不稳定产物检测（HARD FAIL） ----
    for unstable, msg in _UNSTABLE_PRODUCTS.items():
        if any(unstable in p for p in products):
            failures.append(msg)

    # ---- 沉淀规则检测（WARNING） ----
    for cation, anion, msg in _PRECIPITATION_RULES:
        # 匹配更灵活：Ca2+ 可匹配产品中的 Ca（分子式），CO3 可匹配 CO3
        # 检查反应物中的离子与产物中的对应物质
        cation_base = cation.rstrip("+").rstrip("0123456789")  # Ca2+ → Ca
        anion_base = anion.rstrip("-").rstrip("0123456789 ")   # CO3 2- → CO3
        has_cation = any(cation_base in p for p in products) or cation in equation
        has_anion = any(anion_base in p for p in products) or anion in equation
        if has_cation and has_anion:
            # 检查产物中是否已有沉淀标注
            if "↓" not in all_products_text and "v" not in all_products_text:
                warnings.append(f"沉淀应标注: {msg}")

    # ---- 有机物检测 ----
    if _ORGANIC_PRODUCT_RE.search(all_products_text):
        warnings.append("该有机物应写分子式或结构简式")

    # ---- 碳单质检测 ----
    if _CARBON_SINGLETON_RE.search(all_products_text):
        warnings.append("碳应标注形态，如 CO₂")

    # ---- 氧化还原产物检测（HARD FAIL） ----
    for oxidizer, wrong_product, correct_product, explanation in _REDOX_RULES:
        if oxidizer in equation and wrong_product in all_products_text:
            failures.append(f"产物应为 {correct_product} 而非 {wrong_product} — {explanation}")

    # ---- 综合判定 ----
    if failures:
        return ProductResult(
            status="failed",
            message="; ".join(failures + warnings) if warnings else "; ".join(failures),
            issues=failures + warnings,
        )

    if warnings:
        return ProductResult(
            status="warning",
            message="; ".join(warnings),
            issues=warnings,
        )

    return ProductResult(
        status="passed",
        message="产物稳定性正常",
    )
