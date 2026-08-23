## Why

ChemAI 教师端缺少统一的出题工作台入口和 AI 生成题目的质量审核机制。教师需要在一个页面内完成手动命题、AI 辅助生成、OCR 导入三件事，而系统需要一个结构化的四维审核流程来保证 AI 生成题目的质量——当前的审核概念仅停留在文档定义层面，尚未落地为 API 和状态机。

## What Changes

- 新增出题工作台前端页面，使用 Vue 3 CDN + Tailwind CSS + KaTeX 化学公式渲染，三个 Tab 分别对应手动命题、AI 辅助生成、OCR 导入
- 新增四维审核 FastAPI 后端 API：提交审核、轮询审核结果、查看审核详情
- 新增审核工作流状态机，定义 pending → reviewing → passed/rejected 的状态转换规则
- 新增 pytest 测试覆盖审核 API 和状态机的核心路径

## Capabilities

### New Capabilities
- `question-workbench`: 出题工作台前端页面，Vue 3 CDN 组件化 Tab 切换（手动命题/AI生成/OCR导入），Tailwind CSS 响应式布局，KaTeX 化学公式实时渲染
- `four-dimension-review`: 四维审核 FastAPI 后端，包含审核提交、状态机流转、结果查询的完整 REST API

### Modified Capabilities
<!-- 无现有 spec 需要修改 -->

## Impact

- **新增前端页面**: `chemai-backend/frontend/pages/question-workbench.html`
- **新增前端脚本**: `chemai-backend/frontend/js/question-workbench/`
- **新增 API 路由**: `chemai-backend/app/api/review.py`
- **新增审核状态机**: `chemai-backend/app/services/review_state_machine.py`
- **新增数据模型**: `chemai-backend/app/models/review.py`
- **新增测试**: `chemai-backend/tests/test_review_api.py`、`chemai-backend/tests/test_review_state_machine.py`
- **依赖**: Vue 3 CDN、Tailwind CSS CDN、KaTeX CDN（前端）；FastAPI、SQLAlchemy、pytest（后端，已有）
