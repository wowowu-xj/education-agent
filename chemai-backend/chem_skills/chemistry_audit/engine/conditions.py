# -*- coding: utf-8 -*-
"""维度 2：反应条件审核。

基于 14 类条件关键词规则库和反应类型-条件映射表，
检测化学方程式的反应条件标注完整性。
"""

from __future__ import annotations

from chem_skills.chemistry_audit.engine.models import ConditionResult

# ---------------------------------------------------------------------------
# 14 类条件关键词
# ---------------------------------------------------------------------------
CONDITION_KEYWORDS: dict[str, list[str]] = {
    "点燃": ["点燃"],
    "加热": ["加热", "△", r"\triangle"],
    "高温": ["高温"],
    "催化剂": ["催化剂", "MnO2催化", "Cu催化", "Fe催化", "MnO_2"],
    "通电": ["通电", "电解"],
    "光照": ["光照", "光"],
    "加压": ["加压", "高压"],
    "一定条件": ["一定条件"],
    "浓": ["浓", "浓硫酸", "浓硝酸", "浓盐酸"],
    "稀": ["稀", "稀硫酸", "稀硝酸", "稀盐酸"],
    "过量": ["过量"],
    "足量": ["足量"],
    "适量": ["适量"],
    "高温高压": ["高温高压"],
}

# ---------------------------------------------------------------------------
# 反应类型-条件映射表（文档 26 §3.2）
# ---------------------------------------------------------------------------
# (触发物质列表, 应标注条件, 判定级别: failed/warning)
REACTION_CONDITION_RULES: list[tuple[list[str], str, str]] = [
    # 燃烧反应 → 必须标注"点燃"
    (["CH4", "C2H5OH", "C6H12O6", "S", "P", "Fe"], "点燃", "failed"),
    # 催化分解 → 建议标注催化剂
    (["H2O2", "KClO3", "KMnO4"], "催化剂", "warning"),
    # 电解反应 → 必须标注通电/电解
    ([], "通电", "failed"),  # 由关键词"电解"触发
    # 工业合成氨 → 必须标注高温高压 + 催化剂
    (["N2"], "高温高压", "failed"),  # 仅当含 N2 + H2 且产物为 NH3
    # 浓硫酸反应
    (["浓H2SO4", "浓硫酸"], "浓", "failed"),
    # 稀酸反应
    (["稀H2SO4", "稀硫酸", "稀HCl", "稀盐酸"], "稀", "warning"),
    # 热分解
    (["CaCO3", "NaHCO3"], "加热", "failed"),
    # 酯化反应（需检测醇+酸模式）
    (["浓H2SO4"], "加热", "failed"),
    # 光化学反应
    (["HClO", "AgCl", "AgBr"], "光照", "failed"),
]

# 矛盾条件组合
_CONTRADICTION_PAIRS: list[tuple[str, str]] = [
    ("浓", "稀"),
    ("过量", "适量"),
    ("点燃", "通电"),
    ("高温", "加热"),
]


def _get_reactant_side(equation: str) -> str:
    """提取方程式左侧（反应物部分）。"""
    for sep in ("->", "→", "=", r"\rightarrow"):
        idx = equation.find(sep)
        if idx != -1:
            return equation[:idx]
    return equation


def check_conditions(equation: str) -> ConditionResult:
    """审核方程式的反应条件标注。

    Args:
        equation: 化学方程式字符串

    Returns:
        ConditionResult: 包含条件审核结果
    """
    conditions_found: list[str] = []
    missing_conditions: list[str] = []

    # Step 1: 关键词扫描
    for cond_name, keywords in CONDITION_KEYWORDS.items():
        for kw in keywords:
            if kw in equation:
                conditions_found.append(cond_name)
                break

    # Step 2: 反应类型-条件映射检查
    # 先提取反应物侧（分隔符前面的部分），用于物质检测
    reactant_side = _get_reactant_side(equation)
    suggested_conditions: list[str] = []  # warning 级别

    for triggers, required_cond, severity in REACTION_CONDITION_RULES:
        is_triggered = False
        if triggers:
            # 仅在反应物侧检测触发物质（产物中出现不触发）
            is_triggered = any(t in reactant_side for t in triggers)
        else:
            # 通配规则：如"电解"关键词触发
            is_triggered = required_cond in conditions_found

        if is_triggered and required_cond not in conditions_found:
            if severity == "failed":
                missing_conditions.append(required_cond)
            elif severity == "warning":
                suggested_conditions.append(required_cond)

    # Step 3: 燃烧反应特殊检测（仅在反应物侧检测燃烧物种 + O2）
    combustion_species = ["CH4", "C2H5OH", "C6H12O6", "S", "P", "Fe"]
    has_combustion = any(sp in reactant_side for sp in combustion_species)
    has_oxygen_reactant = "O2" in reactant_side
    if has_combustion and has_oxygen_reactant and "点燃" not in conditions_found:
        missing_conditions.append("点燃")

    # Step 4: 矛盾条件检测
    found_contradictions: list[str] = []
    for a, b in _CONTRADICTION_PAIRS:
        if a in conditions_found and b in conditions_found:
            found_contradictions.append(f"{a}+{b}同时出现")

    # 去重
    missing_conditions = list(dict.fromkeys(missing_conditions))
    suggested_conditions = list(dict.fromkeys(suggested_conditions))

    # Step 5: 综合判定
    if found_contradictions:
        return ConditionResult(
            status="failed",
            message=f"矛盾条件: {', '.join(found_contradictions)}",
            conditions_found=conditions_found,
            missing_conditions=missing_conditions + suggested_conditions,
        )

    if missing_conditions:
        return ConditionResult(
            status="failed",
            message=f"缺少必要条件: {', '.join(missing_conditions)}",
            conditions_found=conditions_found,
            missing_conditions=missing_conditions + suggested_conditions,
        )

    if suggested_conditions:
        return ConditionResult(
            status="warning",
            message=f"建议标注条件: {', '.join(suggested_conditions)}",
            conditions_found=conditions_found,
            missing_conditions=suggested_conditions,
        )

    if not conditions_found:
        return ConditionResult(
            status="passed",
            message="未检测到需要标注的反应条件",
            conditions_found=conditions_found,
            missing_conditions=[],
        )

    return ConditionResult(
        status="passed",
        message=f"条件标注完整: {', '.join(conditions_found)}",
        conditions_found=conditions_found,
        missing_conditions=[],
    )
