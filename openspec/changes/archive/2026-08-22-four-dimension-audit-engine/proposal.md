## Why

ChemAI 所有产生化学方程式的路径（AI 出题、对话辅导、方程式配平、实验模拟）当前缺乏一道系统性的安全校验门。一个配平错误的方程式输出给学生，意味着系统在传播错误的化学知识——这是教学产品的底线问题。文档 26 定义的化学方程式安全审核引擎是这个问题的确定性解决方案：纯算法 < 50ms，系数配平准确率 100%，无 LLM 不确定性。

## What Changes

- 新增 `chem_skills/chemistry_parser/` 化学式归一化模块：统一 LaTeX 箭头、自动包裹裸化学式
- 新增 `chem_skills/chemistry_audit/` 四维安全审核引擎：系数配平、反应条件、产物稳定性、分子结构
- 新增 `app/api/audit.py` 审核 REST API：`GET /api/audit/equation` 同步即时返回 AuditReport
- 新增审核相关 pytest 测试：86 道确定性配平测试 + 条件/产物/结构规则覆盖测试

## Capabilities

### New Capabilities
- `chemical-formula-normalization`: 化学式格式归一化——LLM 输出的非标准化学式（Unicode 箭头、裸化学式）到审核引擎可解析标准形式的转换管道
- `equation-parser`: 化学方程式解析——按分隔符拆分反应物/产物、处理括号嵌套、剥离系数、正则匹配元素符号与下标
- `four-dimension-safety-audit`: 四维安全审核引擎——系数配平（元素原子计数法，HARD RED LINE 100%）、反应条件（14 条件关键词规则库）、产物稳定性（气体逸出/沉淀/氧化还原规则）、分子结构（LaTeX/括号/电荷校验），输出结构化 AuditReport

### Modified Capabilities
<!-- 无现有 spec 需要修改 -->

## Impact

- **新增模块**: `chem_skills/chemistry_parser/engine/`（归一化）
- **新增模块**: `chem_skills/chemistry_audit/`（审核引擎 + 规则 JSON）
- **新增 API**: `app/api/audit.py`（`GET /api/audit/equation?eq=...`）
- **新增测试**: `tests/test_balance.py`（86 道）、`tests/test_conditions.py`、`tests/test_stability.py`、`tests/test_structure.py`、`tests/test_parser.py`
- **更新领域模型**: `chemai-backend/CONTEXT.md`（已完成）
- **无新外部依赖**: 审核引擎为纯 Python 算法，不依赖 LLM API
