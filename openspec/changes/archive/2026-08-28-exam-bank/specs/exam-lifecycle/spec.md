## Purpose

定义组卷与考试生命周期的数据模型与状态机：试卷（Paper）、试卷-题目关联（PaperQuestion）、按班考试实例（Exam）。Paper 承载"组卷编辑"（draft/locked 两态），Exam 承载"按班作答流转"（六态）。

## ADDED Requirements

### Requirement: Paper 数据模型

Paper SHALL 包含 title、teacher_id（必填）、duration（可空，分钟）、status（draft/locked）；total_score 由 PaperQuestion 关联题目分值求和派生，SHALL NOT 落库；走软删。

#### Scenario: 试卷创建

- **WHEN** 教师创建试卷
- **THEN** status SHALL 初始为 draft

### Requirement: PaperQuestion 关联（N:M 有序）

Paper 与 Question SHALL 通过 PaperQuestion 形成 N:M 有序关联。

#### Scenario: 加题并排序

- **WHEN** 教师往试卷加题
- **THEN** 系统 SHALL 通过 PaperQuestion 关联（paper_id、question_id、sort_order）
- **AND** sort_order SHALL 决定试卷内题目顺序
- **AND** PaperQuestion SHALL 为纯关系表，硬删除

### Requirement: Paper 锁定（发布后不可改）

- **WHEN** Paper 状态为 draft
- **THEN** 教师 SHALL 可增删改题目（增删 PaperQuestion）
- **WHEN** Paper 状态为 locked
- **THEN** 系统 SHALL 拒绝增删改题目
- **AND** 系统 SHALL 拒绝更新 Paper（如标题/时长）

#### Scenario: 发布后改题被拒绝

- **WHEN** 尝试向 locked 试卷加题/删题
- **THEN** 系统 SHALL 返回 409

### Requirement: Exam 数据模型

Exam SHALL 包含 paper_id（FK→Paper）、class_id（FK→Class）、exam_date、status（published/in_progress/grading/completed/archived/cancelled）；Exam SHALL NOT 物理删除（取消走 cancelled）。

#### Scenario: 一纸多班独立

- **WHEN** 同一 Paper 发布到多个班级
- **THEN** 每个班级 SHALL 生成一个独立 Exam，状态互不影响

### Requirement: 发布（Paper → Exam）

- **WHEN** 教师将 Paper 发布到 N 个班级
- **THEN** 系统 SHALL 为每个班级生成一个 Exam，status=published
- **AND** Paper status SHALL 迁移为 locked
- **AND** Paper SHALL 至少含 1 题，否则拒绝发布

#### Scenario: 发布到 A、B 两班

- **WHEN** 教师把 Paper P 发布到 A 班和 B 班
- **THEN** 系统 SHALL 生成 Exam(P,A) 与 Exam(P,B) 两个实例

### Requirement: 发布目标校验

Paper 发布 SHALL 校验目标班级：班级不存在 SHALL 返回 404；班级不属于教师本校（school_id 不匹配）SHALL 返回 403。校验失败 SHALL NOT 生成任何 Exam。

#### Scenario: 发布到不存在的班级

- **WHEN** 教师将 Paper 发布到包含不存在班级的列表
- **THEN** 系统 SHALL 返回 404
- **AND** 系统 SHALL NOT 生成任何 Exam

#### Scenario: 发布到别校班级被拒绝

- **WHEN** 教师将 Paper 发布到包含非本校班级的列表
- **THEN** 系统 SHALL 返回 403
- **AND** 系统 SHALL NOT 生成任何 Exam

### Requirement: Exam 状态机（教师侧）

Exam SHALL 支持教师侧迁移：
- published → cancelled（取消）
- in_progress → cancelled（取消）
- grading → completed（finalize 批阅完成）

in_progress/grading 的自动进入依赖学生作答链路，本期仅枚举占位。

#### Scenario: 取消已发布考试

- **WHEN** 教师取消 published 状态的考试
- **THEN** status SHALL 迁移为 cancelled

#### Scenario: 非法迁移被拒绝

- **WHEN** 尝试将 completed 状态迁移回 published
- **THEN** 系统 SHALL 返回 409

### Requirement: 删除拦截

被 Exam 引用的 Paper SHALL 不可删；取消考试 SHALL NOT 物理删除。

#### Scenario: 发布后试卷不可删

- **WHEN** 删除被 Exam 引用的 Paper
- **THEN** 系统 SHALL 返回 409

#### Scenario: 取消不物理删除

- **WHEN** 取消考试
- **THEN** 系统 SHALL 迁移 Exam 为 cancelled
- **AND** 系统 SHALL NOT 物理删除
