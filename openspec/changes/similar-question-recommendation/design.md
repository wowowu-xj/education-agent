## Context

`/api/questions/search` 当前返回相似题（`list[Question]`）但不带相似度分数，`VectorSearchService.search` 在内部用 similarity 做阈值过滤与去重后即丢弃；无「排除自身」参数。动机见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 召回结果附带相似度分数（降序）与降级标注。
- 支持排除指定题目（自身）。

**Non-Goals:**
- 不改两层检索算法与阈值（0.6）本身。
- 不做「相似题 + 变体生成」等下游能力。

## Decisions

1. **返回结构：命中项携带相似度与降级标志**
   服务层 `search` 改为返回命中项序列，每项含 `question`、`similarity`、`degraded`。API 响应模型新增 `similarity: float` 与 `degraded: bool`，与题目字段平铺。真实嵌入路径 similarity 来自 `1 - cosine_distance`；keyword 降级路径 similarity 由关键词得分归一化（精确匹配 = 1.0），`degraded=true`。
   - 备选：仅在真实嵌入时返回 similarity，降级时省略 —— 但前端需统一字段，弃用。

2. **排除自身：`exclude_question_id` 参数**
   在服务层候选池与最终结果中过滤该 id；API 透传。实现为「结果阶段过滤」，不改索引。
   - 备选：向量查询 `where` 排除 —— 需在 where 里排除单个 id，语义等价但更绕，弃用。

3. **降级标注的来源**
   复用现有 `_real_embeddings_ok` 标志：MD5 伪向量或纯关键词路径时 `degraded=true`。前端据此把「百分比」切换为「精确匹配」标签。

## Risks / Trade-offs

- [降级路径相似度无语义，可能误导] → `degraded` 标志驱动前端弱化展示（spec「降级弱化」）。
- [相似度暴露到响应可能被误读为「正确率」] → 前端文案明确为「相似度」，不混用。
