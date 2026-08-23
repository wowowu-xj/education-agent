# -*- coding: utf-8 -*-
"""维度 1：系数配平审核 — 确定性测试。

HARD RED LINE: 全部测试必须通过。
涵盖文档 26 §9.3 定义的 9 种反应类型。
"""

from __future__ import annotations

import pytest

from chem_skills.chemistry_audit.engine.auditor import audit_equation


# ---------------------------------------------------------------------------
# 化合反应（12 道）
# ---------------------------------------------------------------------------
COMBINATION_TESTS = [
    # (equation, expected_status, description)
    ("2H2 + O2 -> 2H2O", "passed", "氢气燃烧生成水"),
    ("N2 + 3H2 -> 2NH3", "passed", "合成氨"),
    ("2Na + Cl2 -> 2NaCl", "passed", "钠与氯气化合"),
    ("2Mg + O2 -> 2MgO", "passed", "镁燃烧"),
    ("C + O2 -> CO2", "passed", "碳完全燃烧"),
    ("2C + O2 -> 2CO", "passed", "碳不完全燃烧"),
    ("S + O2 -> SO2", "passed", "硫燃烧"),
    ("4P + 5O2 -> 2P2O5", "passed", "磷燃烧"),
    ("2Fe + 3Cl2 -> 2FeCl3", "passed", "铁与氯气"),
    ("CaO + H2O -> Ca(OH)2", "passed", "生石灰与水"),
    ("SO3 + H2O -> H2SO4", "passed", "三氧化硫与水"),
    ("CO2 + H2O -> H2CO3", "passed", "二氧化碳与水"),
]

# ---------------------------------------------------------------------------
# 分解反应（10 道）
# ---------------------------------------------------------------------------
DECOMPOSITION_TESTS = [
    ("2H2O -> 2H2 + O2", "passed", "电解水"),
    ("2KClO3 -> 2KCl + 3O2", "passed", "氯酸钾分解"),
    ("2KMnO4 -> K2MnO4 + MnO2 + O2", "passed", "高锰酸钾分解"),
    ("CaCO3 -> CaO + CO2", "passed", "碳酸钙分解"),
    ("2NaHCO3 -> Na2CO3 + H2O + CO2", "passed", "碳酸氢钠分解"),
    ("2HgO -> 2Hg + O2", "passed", "氧化汞分解"),
    ("2H2O2 -> 2H2O + O2", "passed", "过氧化氢分解"),
    ("NH4HCO3 -> NH3 + H2O + CO2", "passed", "碳酸氢铵分解"),
    ("Cu(OH)2 -> CuO + H2O", "passed", "氢氧化铜分解"),
    ("MgCO3 -> MgO + CO2", "passed", "碳酸镁分解"),
]

# ---------------------------------------------------------------------------
# 置换反应（8 道）
# ---------------------------------------------------------------------------
DISPLACEMENT_TESTS = [
    ("Fe + CuSO4 -> FeSO4 + Cu", "passed", "铁置换铜"),
    ("Zn + H2SO4 -> ZnSO4 + H2", "passed", "锌与稀硫酸"),
    ("Fe + 2HCl -> FeCl2 + H2", "passed", "铁与盐酸"),
    ("2Na + 2H2O -> 2NaOH + H2", "passed", "钠与水"),
    ("Mg + 2HCl -> MgCl2 + H2", "passed", "镁与盐酸"),
    ("Cu + 2AgNO3 -> Cu(NO3)2 + 2Ag", "passed", "铜置换银"),
    ("Zn + CuCl2 -> ZnCl2 + Cu", "passed", "锌置换铜"),
    ("Cl2 + 2KI -> 2KCl + I2", "passed", "氯置换碘"),
]

# ---------------------------------------------------------------------------
# 复分解反应（8 道）
# ---------------------------------------------------------------------------
DOUBLE_DISPLACEMENT_TESTS = [
    ("NaOH + HCl -> NaCl + H2O", "passed", "酸碱中和"),
    ("AgNO3 + NaCl -> AgCl + NaNO3", "passed", "生成氯化银沉淀"),
    ("BaCl2 + Na2SO4 -> BaSO4 + 2NaCl", "passed", "生成硫酸钡沉淀"),
    ("Ca(OH)2 + Na2CO3 -> CaCO3 + 2NaOH", "passed", "生成碳酸钙"),
    ("H2SO4 + 2NaOH -> Na2SO4 + 2H2O", "passed", "硫酸与氢氧化钠"),
    ("HCl + NaHCO3 -> NaCl + H2O + CO2", "passed", "盐酸与碳酸氢钠"),
    ("2HNO3 + Ca(OH)2 -> Ca(NO3)2 + 2H2O", "passed", "硝酸与氢氧化钙"),
    ("Na2CO3 + 2HCl -> 2NaCl + H2O + CO2", "passed", "碳酸钠与盐酸"),
]

# ---------------------------------------------------------------------------
# 氧化还原反应（14 道）
# ---------------------------------------------------------------------------
REDOX_TESTS = [
    ("2Al + Fe2O3 -> Al2O3 + 2Fe", "passed", "铝热反应"),
    ("3Fe + 2O2 -> Fe3O4", "passed", "铁在氧气中燃烧"),
    ("2CuO + C -> 2Cu + CO2", "passed", "碳还原氧化铜"),
    ("Fe2O3 + 3CO -> 2Fe + 3CO2", "passed", "一氧化碳还原氧化铁"),
    ("2KMnO4 + 16HCl -> 2KCl + 2MnCl2 + 5Cl2 + 8H2O", "passed", "高锰酸钾与浓盐酸"),
    ("CuO + H2 -> Cu + H2O", "passed", "氢气还原氧化铜"),
    ("MnO2 + 4HCl -> MnCl2 + Cl2 + 2H2O", "passed", "二氧化锰与浓盐酸"),
    ("2SO2 + O2 -> 2SO3", "passed", "二氧化硫氧化"),
    ("2NO + O2 -> 2NO2", "passed", "一氧化氮氧化"),
    ("4Fe(OH)2 + O2 + 2H2O -> 4Fe(OH)3", "passed", "氢氧化亚铁氧化"),
    ("2H2S + SO2 -> 3S + 2H2O", "passed", "硫化氢与二氧化硫"),
    ("Cl2 + 2NaOH -> NaCl + NaClO + H2O", "passed", "氯气与氢氧化钠歧化"),
    ("3Cu + 8HNO3 -> 3Cu(NO3)2 + 2NO + 4H2O", "passed", "铜与稀硝酸"),
    ("Cu + 4HNO3 -> Cu(NO3)2 + 2NO2 + 2H2O", "passed", "铜与浓硝酸"),
]

# ---------------------------------------------------------------------------
# 有机反应（8 道）
# ---------------------------------------------------------------------------
ORGANIC_TESTS = [
    ("CH4 + 2O2 -> CO2 + 2H2O", "passed", "甲烷完全燃烧"),
    ("C2H5OH + 3O2 -> 2CO2 + 3H2O", "passed", "乙醇燃烧"),
    ("2C2H2 + 5O2 -> 4CO2 + 2H2O", "passed", "乙炔燃烧"),
    ("CH3COOH + C2H5OH -> CH3COOC2H5 + H2O", "passed", "酯化反应"),
    ("C6H12O6 + 6O2 -> 6CO2 + 6H2O", "passed", "葡萄糖氧化"),
    ("2CH3OH + 3O2 -> 2CO2 + 4H2O", "passed", "甲醇燃烧"),
    ("CH2=CH2 + Br2 -> CH2BrCH2Br", "passed", "乙烯与溴加成"),
    ("C6H6 + HNO3 -> C6H5NO2 + H2O", "passed", "苯的硝化"),
]

# ---------------------------------------------------------------------------
# 离子方程式（10 道）
# ---------------------------------------------------------------------------
IONIC_TESTS = [
    ("Ag+ + Cl- -> AgCl", "passed", "银离子与氯离子"),
    ("Ba2+ + SO4 2- -> BaSO4", "passed", "钡离子与硫酸根"),
    ("H+ + OH- -> H2O", "passed", "氢离子与氢氧根"),
    ("Fe3+ + 3OH- -> Fe(OH)3", "passed", "铁离子与氢氧根"),
    ("Ca2+ + CO3 2- -> CaCO3", "passed", "钙离子与碳酸根"),
    ("Cu2+ + 2OH- -> Cu(OH)2", "passed", "铜离子与氢氧根"),
    ("2H+ + CO3 2- -> H2O + CO2", "passed", "氢离子与碳酸根"),
    ("Fe + Cu2+ -> Fe2+ + Cu", "passed", "铁置换铜(离子)"),
    ("Zn + 2H+ -> Zn2+ + H2", "passed", "锌与氢离子"),
    ("Cl2 + 2I- -> 2Cl- + I2", "passed", "氯置换碘(离子)"),
]

# ---------------------------------------------------------------------------
# 电极反应（6 道）
# ---------------------------------------------------------------------------
ELECTRODE_TESTS = [
    ("2H+ + 2e- -> H2", "passed", "阴极析氢"),
    ("Cu2+ + 2e- -> Cu", "passed", "阴极析铜"),
    ("2Cl- -> Cl2 + 2e-", "passed", "阳极析氯"),
    ("4OH- -> O2 + 2H2O + 4e-", "passed", "阳极析氧(碱)"),
    ("2H2O -> O2 + 4H+ + 4e-", "passed", "阳极析氧(酸)"),
    ("Fe3+ + e- -> Fe2+", "passed", "铁离子还原"),
]

# ---------------------------------------------------------------------------
# 工业流程反应（10 道）
# ---------------------------------------------------------------------------
INDUSTRIAL_TESTS = [
    ("2NaCl + 2H2O -> 2NaOH + H2 + Cl2", "passed", "氯碱工业"),
    ("CaCO3 + SiO2 -> CaSiO3 + CO2", "passed", "制玻璃"),
    ("Fe2O3 + 3CO -> 2Fe + 3CO2", "passed", "高炉炼铁"),
    ("4FeS2 + 11O2 -> 2Fe2O3 + 8SO2", "passed", "黄铁矿焙烧"),
    ("2SO2 + O2 -> 2SO3", "passed", "接触法制硫酸"),
    ("NH3 + CO2 + H2O -> NH4HCO3", "passed", "氨与二氧化碳"),
    ("SiO2 + 2C -> Si + 2CO", "passed", "制粗硅"),
    ("Al2O3 + 3H2 -> 2Al + 3H2O", "passed", "氢气还原氧化铝"),
    ("TiCl4 + 2Mg -> Ti + 2MgCl2", "passed", "镁热还原四氯化钛"),
    ("Ca3(PO4)2 + 3H2SO4 -> 3CaSO4 + 2H3PO4", "passed", "制磷酸"),
]

# ---------------------------------------------------------------------------
# 未配平 — 应该被拦截
# ---------------------------------------------------------------------------
UNBALANCED_TESTS = [
    ("Fe + O2 -> Fe2O3", "blocked", "铁生锈（未配平）"),
    ("H2 + O2 -> H2O", "blocked", "氢气燃烧（未配平）"),
    ("Na + H2O -> NaOH + H2", "blocked", "钠与水（未配平）"),
    ("KClO3 -> KCl + O2", "blocked", "氯酸钾分解（未配平）"),
    ("Al + O2 -> Al2O3", "blocked", "铝燃烧（未配平）"),
    ("N2 + H2 -> NH3", "blocked", "合成氨（未配平）"),
    ("Cu + O2 -> CuO", "blocked", "铜氧化（未配平）"),
    ("Fe + Cl2 -> FeCl3", "blocked", "铁与氯气（未配平）"),
]

# 合并所有通过测试
_ALL_PASSED = (
    COMBINATION_TESTS
    + DECOMPOSITION_TESTS
    + DISPLACEMENT_TESTS
    + DOUBLE_DISPLACEMENT_TESTS
    + REDOX_TESTS
    + ORGANIC_TESTS
    + IONIC_TESTS
    + ELECTRODE_TESTS
    + INDUSTRIAL_TESTS
)

# 全部 86 道配平测试 = 76 道通过 + 8 道未配平拦截 + 2（文档 26 示例 3-4）

@pytest.mark.parametrize("equation,expected,description", _ALL_PASSED)
def test_balance_passed(equation: str, expected: str, description: str) -> None:
    """配平正确的方程式应返回 passed。"""
    report = audit_equation(equation)
    assert report.balance.status == expected, (
        f"{description}: 期望 {expected}, 实际 {report.balance.status} — {report.balance.message}"
    )


@pytest.mark.parametrize("equation,expected,description", UNBALANCED_TESTS)
def test_balance_blocked(equation: str, expected: str, description: str) -> None:
    """未配平的方程式应被拦截。"""
    report = audit_equation(equation)
    assert report.balance.status == expected, (
        f"{description}: 期望 {expected}, 实际 {report.balance.status}"
    )


def test_deterministic_count() -> None:
    """验证确定性测试数量达标。

    文档 26 目标：86 道确定性配平测试全部通过。
    实际：86 道通过 + 8 道未配平拦截 = 94 道总方程测试。
    """
    passed = len(_ALL_PASSED)
    total = passed + len(UNBALANCED_TESTS)
    assert passed >= 86, f"配平通过测试 {passed} 道，目标 ≥ 86"
    assert total >= 94, f"总测试 {total} 道，目标 ≥ 94"
