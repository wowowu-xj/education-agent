# question-workbench-frontend Specification (delta)

## ADDED Requirements

### Requirement: 考试全生命周期展示与操作

Tab 4「考试列表」SHALL 展示 Exam 完整六态，并按当前状态渲染对应操作。

#### Scenario: 六态标签

- **WHEN** 展示某个 Exam
- **THEN** 系统 SHALL 以六态标签展示其当前状态（published / in_progress / grading / completed / archived / cancelled）

#### Scenario: 按状态渲染操作

- **WHEN** Exam 状态为 published
- **THEN** 系统 SHALL 提供「开考」与「取消」操作
- **AND** 状态为 in_progress SHALL 提供「收卷」与「取消」
- **AND** 状态为 grading SHALL 提供「阅卷完成」
- **AND** 状态为 completed SHALL 提供「归档」
