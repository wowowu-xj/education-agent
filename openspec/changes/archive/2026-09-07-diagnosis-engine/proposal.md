## Why

ChemAI 的核心价值主张是「从"知道谁错了"进化到"知道为什么错"」，但当前诊断能力只落地了一个空壳——`Student.barrier_profile` JSON 字段存在，作答记录（`StudentAnswer`）、诊断逻辑、LLM 调用、聚合画像全部缺失。同时 CLAUDE.md 明确要求诊断必须**同时输出两个正交维度**（障碍类型 + 迷思概念类别），而 27 号设计文档只覆盖了障碍类型，第二个维度在代码与文档中均未实现。本 change 落地诊断引擎的后端核心，使「错误作答 → 双维度障碍诊断 → 学生画像 → 教师干预」链路首次走通。

## What Changes

- 新增 `StudentAnswer` 作答记录模型，以及 `BarrierType`（concept/reading/expression）、`MisconceptionCategory`（化学平衡/氧化还原/摩尔计算/有机化学/化学用语/物构知识）两个枚举。
- 新增障碍诊断引擎（`chem_skills/chemistry_diagnosis/engine/`），三引擎三段式：规则引擎（关键词预分类，0.5–0.7 保守置信度）→ LLM 深度分析（语义判定，0–1 置信度 + 依据）→ 置信度融合引擎（LLM 主判 + 规则佐证/兜底，融合输出最终 `barrier_type` + `misconception_category` + `confidence` + `reasoning` + `suggestion` 五字段）。
- 新增三级置信度体系：≥0.8 自动采纳、0.7–0.8 采纳并标记、<0.7 建议人工复核；`confidence` 本次直接落库（相较 27 号文档「未来迭代」项，提前偿还，保证中低置信度判定可追溯）。
- 新增聚合逻辑：从已诊断作答聚合学生障碍画像（`barrier_profile`）与迷思概念分布（`misconception_profile`），补充缺失类型为 0。
- 新增教师覆盖机制（`PUT /override/{student_id}`）与教师阈值配置 `BarrierConfig`。
- 新增诊断查询端点：单次考试聚合、班级统计、知识点维度、学生诊断历史。
- 新增学习计划生成子系统：LLM 生成计划、应用、推送家长、24h 内存缓存。
- 新增三级 LLM fallback 客户端（MiMo-V2.5 → 通义千问 qwen-turbo → DeepSeek-V4-Flash，每级 3 次重试 + 指数退避）。

## Capabilities

### New Capabilities

- `diagnosis-engine`: 双维度障碍诊断核心——作答记录模型、障碍类型与迷思概念分类、规则引擎 + LLM 诊断、置信度分级、聚合画像、教师覆盖、班级/知识点/历史聚合查询、教师阈值配置。
- `diagnosis-learning-plan`: 基于诊断结果的学习计划生成、生命周期（预览/应用/发送家长/删除）、持久化与家长推送。

### Modified Capabilities

（无）

## Impact

- 后端数据模型：`app/models/` 新增 `student_answer.py`、`barrier_config.py`、学习计划与家长通知相关模型；`Student` 扩展 `misconception_profile` 字段；`app/core/enums.py` 新增 `BarrierType`、`MisconceptionCategory` 枚举。
- 诊断引擎：`chem_skills/chemistry_diagnosis/engine/`（rule_engine / llm_client / confidence_fusion / diagnosis / aggregator）。
- API：`app/api/diagnosis.py`（诊断端点 + 学习计划端点）。
- 数据库迁移：Alembic 新增迁移。
- 依赖：新增 LLM HTTP 客户端（对接通义千问 DashScope / DeepSeek，多 provider 回退）。
- 测试：`tests/` 新增诊断与学习计划测试（TDD，seed 数据驱动，不依赖 OCR/作答采集链路）。
- 范围外（后续分支）：前端诊断页面、Agent 工具集成、OCR 作答采集、实时诊断。
