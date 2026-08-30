## Context

Exam 状态机现有教师侧迁移仅「发布 / 取消 / finalize」三个（`app/api/exams.py`），`in_progress`、`grading`、`archived` 不可达。学生作答链路未建，无法自动驱动 in_progress/grading。动机见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 以教师手动操作为驱动，使六态全生命周期可走通。
- 每次迁移留审计（操作人 + 时间戳）。

**Non-Goals:**
- 不实现学生作答 / 自动阅卷，不实现 in_progress/grading 的作答自动触发。
- 不引入审批流或多步状态机框架（沿用现有简单迁移）。

## Decisions

1. **新增三个教师侧迁移端点**
   `POST /api/exams/{id}/start`（published → in_progress）、`POST /api/exams/{id}/collect`（in_progress → grading）、`POST /api/exams/{id}/archive`（completed → archived）。沿用现有 finalize 的「单状态校验 + 409 拦截非法迁移」模式，路由风格与 `/cancel` 一致。
   - 备选：单一 `POST /api/exams/{id}/transition {to_status}` 通用端点 —— 通用但丢失每步的显式语义与权限，弃用。

2. **审计：append-only 迁移日志表**
   新增 `exam_status_transitions`（exam_id、from_status、to_status、operator_id、created_at），每次迁移追加一条。因「每次迁移记录」蕴含历史而非仅末态，故不用 Exam 上的 `last_transition_by/at` 两列。
   - 备选：Exam 加 `updated_by/updated_at` —— 无法回答「从哪态迁到哪态」的历史，弃用。

3. **教师身份**
   迁移以当前 JWT 教师为 operator，`operator_id` 取自 `get_current_teacher`。

4. **归档的不可逆性**
   `archived` 为终态，SHALL NOT 提供反向迁移（与 cancelled 并列终态），非法迁移一律 409。

## Risks / Trade-offs

- [开考/收卷为教师手动驱动，与真实学生作答脱节] → 学生作答链路落地时改为作答自动触发，本 change 仅补全教师侧可操作性，spec 已注明 defer。
- [新增迁移端点可能被误触发] → 单状态前置校验 + 409，前端按状态渲染按钮避免误点。
