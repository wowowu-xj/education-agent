# Tasks

## 1. 后端分页（TDD）

- [x] 1.1 编写 `GET /api/questions` 分页失败测试（RED）：断言分页结构 items/total/page/page_size、越界页返回空 items 且 total 不变
- [x] 1.2 实现分页参数与分页响应模型，使 1.1 通过（GREEN）

## 2. 后端组合筛选（TDD）

- [x] 2.1 编写组合筛选失败测试（RED）：断言 type/difficulty/knowledge_point 叠加为 AND 语义、knowledge_point JSON 数组包含判定
- [x] 2.2 实现组合筛选参数过滤，使 2.1 通过（GREEN）

## 3. Tab 2 前端分页与筛选

- [x] 3.1 题目列表接入分页控件：展示当前页/总页数/总条数，支持翻页
- [x] 3.2 组合筛选控件：题型/难度/知识点下拉（可多选叠加），筛选后重置到第一页
- [x] 3.3 「重置」清空全部筛选并刷新列表

## 4. 验证

- [x] 4.1 后端测试全绿（`pytest`），`openspec validate question-bank-list-pagination-filter --strict` 通过
- [ ] 4.2 浏览器手动验证 Tab 2 分页、组合筛选、重置、空结果态
