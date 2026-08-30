# Tasks

## 1. 相似度与降级返回（TDD）

- [x] 1.1 编写相似度返回失败测试（RED）：断言 search 结果附带 similarity（0~1）、按降序、降级路径标注 degraded
- [x] 1.2 修改检索服务返回命中项（question + similarity + degraded），使 1.1 通过（GREEN）
- [x] 1.3 修改 `/api/questions/search` 响应模型透传 similarity 与 degraded

## 2. 排除自身（TDD）

- [x] 2.1 编写排除自身失败测试（RED）：断言传入 exclude_question_id 后结果不含该题
- [x] 2.2 实现 exclude_question_id 过滤（服务层 + API 透传），使 2.1 通过（GREEN）

## 3. 前端相似题推荐 UI

- [x] 3.1 出题工作台相似题推荐入口，展示相似题列表
- [x] 3.2 每题展示相似度（百分比/进度条，降序），排除当前题
- [x] 3.3 降级弱化：degraded 时以「精确匹配」标签替代百分比展示

## 4. 验证

- [x] 4.1 后端测试全绿（`pytest`），`openspec validate similar-question-recommendation --strict` 通过
- [ ] 4.2 浏览器手动验证相似题推荐、相似度展示清晰、排除自身、降级标注
