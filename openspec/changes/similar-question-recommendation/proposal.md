## Why

`/api/questions/search` 现返回相似题但不带相似度分数，前端无法展示「有多相似」；且无「排除自身」能力，教师对某题找相似时会返回该题本身。需要补相似度展示 + 排除自身，并落地前端推荐 UI。

## What Changes

- `/api/questions/search` 响应中每道题附带 `similarity` 分数（0~1，按相似度降序）。
- `/api/questions/search` 新增 `exclude_question_id` 参数，命中时从结果排除该题（自身）。
- 前端提供「相似题推荐」入口，展示每道题的相似度（百分比 / 进度条），并默认排除当前题。
- 降级路径（MD5 伪向量）下相似度语义退化为精确匹配，响应需区分真实 / 降级相似度，前端据此弱化相似度展示。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `question-vector-search`: 语义召回 API 增加相似度返回与排除自身参数。
- `question-workbench-frontend`: 相似题推荐 UI + 相似度展示 + 排除自身。

## Impact

- 后端：`app/services/vector_search.py`（`search` 返回相似度、`exclude_question_id`）、`app/api/questions.py`（search 端点透传与响应模型）。
- 前端：`chemai-backend/frontend/pages/question-workbench.html`。
- 测试：`tests/test_vector_search.py`（相似度降序 / 排除自身 / 降级语义）。
