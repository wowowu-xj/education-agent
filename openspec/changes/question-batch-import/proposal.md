## Why

教师常需一次性录入数十道题目（如从 Word / Excel 整理的历史真题），逐题手动录入成本高、易错。需要一个「上传 → 预览校验 → 确认写入 → 结果统计」的批量导入流程，把大批量录入从重复劳动变成一次批量操作。

## What Changes

- 新增批量导入后端能力：解析上传内容 → 预览校验（逐题报告校验错误，不落库）→ 确认写入（批量落库并建向量索引）→ 返回结果统计（成功 / 失败数及逐题原因）。
- 前端 Tab 2「题库管理」新增「批量导入」入口，三步流程：预览 → 确认 → 结果统计。
- 导入题目复用 `question-bank` 既有数据模型（`type`/`difficulty` 取值域引用 `question-vocabulary`），写入前逐题做字段与取值域校验，未通过者在结果中标注为失败。

## Capabilities

### New Capabilities

- `question-batch-import`: 批量导入的解析、预览校验、确认写入、结果统计契约。

### Modified Capabilities

- `question-workbench-frontend`: Tab 2 新增批量导入入口与三步 UI（预览 → 确认 → 结果统计）。

## Impact

- 后端：新增批量导入 API（`app/api/` 下新模块或并入 `questions`）、解析与校验服务（`app/services/`）。
- 前端：`chemai-backend/frontend/pages/question-workbench.html`（Tab 2）。
- 测试：新增批量导入集成测试（解析 / 校验 / 部分成功 / 全失败）。
