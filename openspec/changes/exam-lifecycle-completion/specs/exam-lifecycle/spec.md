# exam-lifecycle Specification (delta)

## ADDED Requirements

### Requirement: 状态迁移审计

Exam 每次状态迁移 SHALL 记录操作人与时间戳，便于追溯。

#### Scenario: 迁移留痕

- **WHEN** 任一教师侧状态迁移发生
- **THEN** 系统 SHALL 记录操作人 id 与迁移时间

## MODIFIED Requirements

### Requirement: Exam 状态机（教师侧）

Exam SHALL 支持教师侧迁移：
- published → in_progress（开考）
- published → cancelled（取消）
- in_progress → grading（收卷进入阅卷）
- in_progress → cancelled（取消）
- grading → completed（finalize 批阅完成）
- completed → archived（归档）

in_progress/grading 的自动进入依赖学生作答链路，本期以教师手动开考 / 收卷驱动状态流转，学生作答链路触发仍 defer。

#### Scenario: 取消已发布考试

- **WHEN** 教师取消 published 状态的考试
- **THEN** status SHALL 迁移为 cancelled

#### Scenario: 开考

- **WHEN** 教师对 published 状态的考试执行开考
- **THEN** status SHALL 迁移为 in_progress

#### Scenario: 收卷进入阅卷

- **WHEN** 教师对 in_progress 状态的考试执行收卷
- **THEN** status SHALL 迁移为 grading

#### Scenario: 归档

- **WHEN** 教师对 completed 状态的考试执行归档
- **THEN** status SHALL 迁移为 archived

#### Scenario: 非法迁移被拒绝

- **WHEN** 尝试将 completed 状态迁移回 published
- **THEN** 系统 SHALL 返回 409
