# -*- coding: utf-8 -*-
"""化学式格式归一化模块。

将 LLM 输出中的非标准化学式格式统一转换为审核引擎可解析的标准形式。
"""

from chem_skills.chemistry_parser.engine.normalizer import normalize_chem_formulas

__all__ = ["normalize_chem_formulas"]
