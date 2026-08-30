## Why

当前 Exam 状态机只落地了教师侧「发布 → published / 取消 → cancelled / finalize → completed」三个迁移；`in_progress`、`grading`、`archived` 三态无法进入或流转。考试全生命周期（创建 → 发布 → 进行中 → 阅卷 → 完成 → 归档）因此在中间断裂，前端也无法展示完整流转。

## What Changes

- 补全 Exam 状态机教师侧迁移端点：`published → in_progress`（开考）、`in_progress → grading`（收卷进入阅卷）、`completed → archived`（归档）；`grading → completed`（finalize）已存在。
- 每次状态迁移记录操作人与时间戳。
- 前端 Tab 4「考试列表」展示完整六态，并按当前状态渲染对应操作按钮（开考 / 收卷 / 归档），替换目前仅发布 / 取消 / 阅卷完成的交互。
- 学生作答链路的自动进入（作答触发 in_progress/grading）仍 defer；本 change 以教师手动开考 / 收卷作为状态流转的驱动入口，使全生命周期可在无学生端时走通。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `exam-lifecycle`: Exam 状态机新增 `in_progress` / `grading` / `archived` 迁移契约与审计记录。
- `question-workbench-frontend`: Tab 4 完整六态展示与开考 / 收卷 / 归档操作。

## Impact

- 后端：`app/api/exams.py`（新增迁移端点）、`app/models`（迁移审计字段，如 `updated_by`/`updated_at` 或迁移日志）。
- 前端：`chemai-backend/frontend/pages/question-workbench.html`（Tab 4）。
- 测试：`tests/test_exam_lifecycle.py`（非法迁移 409 / 合法迁移 / 审计）。
