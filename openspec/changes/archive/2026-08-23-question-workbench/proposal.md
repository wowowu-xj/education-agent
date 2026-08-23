## Why

出题工作台是 ChemAI 教师端的内容生产中枢，但前端页面尚不存在（`frontend/` 全为 .gitkeep），且"题型""难度"两个核心词汇在 CONTEXT.md、产品文档 25、原型之间互相矛盾（8 种 vs 5 种 vs 5 种；1-5 级 vs 4 档 vs 3 档）。在写任何前端代码之前，必须先冻结一套单一词汇表，作为前端 chip、后端 enum、LLM prompt 三方的共享契约。

## What Changes

- 冻结题目领域词汇表：题型 9 种枚举、难度 4 档枚举、LLM 输出别名 → 枚举值的映射
- 新增出题工作台前端页面：4 Tab 单页应用，Tab 1 内含三种出题子模式（AI 生成 / 手动录入 / OCR 导入）
- 前端渲染四维安全审核引擎（已实现）的 AuditReport 徽章

## Capabilities

### New Capabilities
- `question-vocabulary`: 题目领域词汇表——题型/难度枚举 + LLM 别名映射，前端、后端、LLM 三方的单一契约
- `question-workbench-frontend`: 出题工作台前端页面——4 Tab 结构、出题子模式、审核徽章渲染

## Impact

- **新增规格**: `specs/question-vocabulary/`、`specs/question-workbench-frontend/`
- **新增前端页面**: `chemai-backend/frontend/pages/question-workbench.html`
- **依赖**: Vue 3 CDN、Tailwind CSS CDN、KaTeX CDN（前端）；四维审核引擎 AuditReport（后端，已实现）
- **不新增后端依赖**：词汇表为纯契约定义，enum 在后续 Question 模型落地时一并实现
