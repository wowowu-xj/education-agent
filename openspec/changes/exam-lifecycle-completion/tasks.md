# Tasks

## 1. 迁移审计模型（TDD）

- [x] 1.1 编写迁移日志失败测试（RED）：断言每次状态迁移追加一条记录（exam_id/from/to/operator/时间戳）
- [x] 1.2 实现 `exam_status_transitions` 表模型与记录逻辑，使 1.1 通过（GREEN）

## 2. 三个迁移端点（TDD）

- [x] 2.1 编写开考/收卷/归档失败测试（RED）：断言 published→in_progress、in_progress→grading、completed→archived 合法迁移；非法迁移（如 completed→published）返回 409
- [x] 2.2 实现 `POST /api/exams/{id}/start`（开考），使 2.1 相关用例通过（GREEN）
- [x] 2.3 实现 `POST /api/exams/{id}/collect`（收卷），使 2.1 相关用例通过（GREEN）
- [x] 2.4 实现 `POST /api/exams/{id}/archive`（归档），使 2.1 相关用例通过（GREEN）

## 3. Tab 4 前端全生命周期

- [x] 3.1 六态标签完整展示（published/in_progress/grading/completed/archived/cancelled）
- [x] 3.2 按状态渲染操作：published 显示「开考」「取消」、in_progress 显示「收卷」「取消」、grading 显示「阅卷完成」、completed 显示「归档」

## 4. 验证

- [x] 4.1 后端测试全绿（`pytest`），`openspec validate exam-lifecycle-completion --strict` 通过
- [ ] 4.2 浏览器手动验证创建 → 发布 → 开考 → 收卷 → 阅卷完成 → 归档全流程无报错
