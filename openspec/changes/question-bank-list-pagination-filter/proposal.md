## Why

教师题库随使用增长，`GET /api/questions` 当前一次性返回全部题目，列表页加载与渲染随题目数线性恶化；且列表接口不支持分页与组合筛选，教师无法按「题型 + 难度 + 知识点」叠加定位题目。

## What Changes

- `GET /api/questions` 新增分页参数 `page`、`page_size`，响应改为分页结构（`items` + `total` + `page` + `page_size`）。**BREAKING**：响应由裸数组变为分页对象，唯一消费者为 `question-workbench.html`，本 change 同步更新。
- `GET /api/questions` 新增组合筛选参数 `type`、`difficulty`、`knowledge_point`，多条件叠加为 AND 语义，可独立于分页使用。
- 前端 Tab 2「题库管理」题目列表接入分页控件与组合筛选（题型 / 难度 / 知识点下拉，可多选叠加）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `question-bank`: 题目列表端点新增分页契约，并明确组合筛选（type/difficulty/knowledge_point 叠加）语义。
- `question-workbench-frontend`: Tab 2 题库列表新增分页控件与组合筛选 UI。

## Impact

- 后端：`app/api/questions.py`（列表端点参数与分页响应）、Pydantic 分页模型。
- 前端：`chemai-backend/frontend/pages/question-workbench.html`（Tab 2 列表区）。
- 测试：`tests/test_question_bank_api.py`（分页 / 组合筛选 / 边界用例）。
