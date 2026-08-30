## Context

`GET /api/questions` 当前返回裸数组（`list[QuestionOut]`），无分页；题型/难度/知识点的组合筛选在 `/api/questions/search`（向量检索）上实现，列表接口无等价能力。唯一消费者为 `question-workbench.html` Tab 2。动机见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 列表接口支持分页与组合筛选，契约清晰可测。
- 前端 Tab 2 分页与筛选交互完整（含重置、翻页）。

**Non-Goals:**
- 不做服务端排序开关（沿用现有稳定排序）。
- 不做全文搜索 / 向量检索（属 question-vector-search，本 change 不触碰）。

## Decisions

1. **响应形态：分页对象（破坏性变更）**
   改为 `{"items": [...], "total": int, "page": int, "page_size": int}`。因唯一消费者在同 change 内更新，接受一次破坏性迁移，换取干净契约。
   - 备选：保留裸数组 + 无条件分页参数（向后兼容）—— 但契约含混，弃用。

2. **参数命名与语义**
   `page`（1 起）、`page_size`（默认 20，上限 100）；筛选 `type`、`difficulty`、`knowledge_point` 均为可选、AND 叠加。`page=0` 或负值按 `page=1` 处理，避免 422 噪声。
   - 备选：offset/limit —— 因 UI 天然以「页」为单位，弃用。

3. **筛选复用问题**
   列表接口自行实现组合筛选（type/difficulty/knowledge_point 的 SQL 过滤 + knowledge_point JSON 数组包含在 Python 侧判定），与 search 端点的向量检索解耦。knowledge_point 过滤沿用跨方言的 Python 侧 `in` 判定（同 `vector_search.search`）。

4. **total 语义**
   `total` 为「应用筛选后的总条数」（非全库），供前端渲染总页数。

## Risks / Trade-offs

- [破坏性响应变更] → 同 change 内更新唯一消费者；无其他调用方。
- [knowledge_point JSON 包含在 Python 侧全量过滤，量大时慢] → 先用关键词粗筛候选，后续量大再评估 JSON 列索引 / 反范式，本期不引入。
