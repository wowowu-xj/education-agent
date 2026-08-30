## Context

题库现有题目逐题录入路径（手动录入 / AI 生成），无批量入口。题目数据模型、`question-vocabulary` 取值域、四维安全审核引擎均已就绪，可复用。动机见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 一个无状态的两阶段导入（预览 / 确认），不引入服务端会话态。
- 部分成功语义：通过者写入、未通过者跳过并逐题说明。

**Non-Goals:**
- 不做 Excel / Word 二进制解析（首期只接受结构化输入）。
- 不做后台异步导入任务（数据量在同步可承受范围）。

## Decisions

1. **输入格式：结构化 JSON 题目数组**
   前端将教师粘贴/上传的模板文本解析为 `QuestionImportIn[]`（与 `QuestionCreate` 字段一致，`type`/`difficulty` 引用 vocabulary）。首期不做 Excel 二进制，模板解析在前端完成。
   - 备选：服务端解析 CSV/TSV —— 增加服务端解析与编码处理复杂度，弃用。

2. **两阶段无状态 API**
   `POST /api/questions/batch/preview`（解析 + 校验 + 审核，逐题返回，不落库）与 `POST /api/questions/batch/commit`（重校验后写入通过项 + 建向量索引，返回统计）。无服务端预览 token：commit 端重校验，避免 TOCTOU，同时保持无状态。
   - 备选：单端点 `dry_run` 标志 —— 可行，但显式两端点让「预览 → 确认」语义更清晰，前端状态更直白。

3. **校验归属（不做四维安全审核）**
   预览逐题执行字段完整性 / 取值域（type、difficulty）校验，复用 `QuestionCreate` 的 Pydantic 校验，逐题收集错误。不做四维安全审核——该引擎面向化学方程式，且单题 `create_question` 亦不做审核，保持一致。

4. **写入策略**
   逐题 `INSERT` + `vector_search.index_question()`；单题失败捕获后计入「失败」并继续，不整体回滚（对齐 spec「部分成功不整体回滚」）。soft-delete 语义与逐题写入一致。

## Risks / Trade-offs

- [逐题落库 + 建向量索引，量大时慢] → 单次上限（≤ 200 题）在接口层校验。
- [逐题失败导致部分成功，教师需对失败项补录] → 结果统计逐题给出原因，前端提供「仅看失败」过滤。
- [无服务端 token，commit 时若题库已变化] → 重校验兜底，失败项在结果中标注。
