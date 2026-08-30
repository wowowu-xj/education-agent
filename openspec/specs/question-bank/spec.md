# question-bank Specification

## Purpose
定义题库管理的数据模型与 CRUD 契约：题目（Question）、题库文件夹（QuestionSet）、文件夹-题目关联（QuestionSetItem）。题型/难度取值域引用 question-vocabulary，本 spec 不重复定义。
## Requirements
### Requirement: Question 数据模型

Question SHALL 包含以下字段，题型/难度取值域引用 question-vocabulary：
- id、teacher_id（可空，FK→teachers）、content、type（9 枚举）、options（JSON，可空，仅选择题）、answer、analysis（可空）、knowledge_points（JSON 数组）、difficulty（4 枚举）、score、source_name/region/year（可空）
- 软删字段（deleted_at），走 SoftDeleteMixin

#### Scenario: 手动录入完整题型

- **WHEN** 教师手动录入题目
- **THEN** type SHALL 允许全部 9 种题型
- **AND** difficulty SHALL 允许 4 档（含 competition）

#### Scenario: 来源元数据可空

- **WHEN** 题目无来源地区/年份信息
- **THEN** source_name/region/year SHALL 允许为 null

### Requirement: Question 软删与数据隔离

- **WHEN** 教师删除自己的题目
- **THEN** 系统 SHALL 软删（置 deleted_at），不物理删除
- **AND** 教师 SHALL NOT 操作他人题目（数据隔离）

#### Scenario: 被锁定试卷引用的题目不可删

- **WHEN** 题目被 locked 状态的 Paper 通过 PaperQuestion 引用
- **THEN** 删除该题目 SHALL 返回 409 拦截

### Requirement: QuestionSet 数据模型

QuestionSet SHALL 包含 name、teacher_id（必填）、description、region/year（可空）、is_preset（默认 false）；question_count 由 QuestionSetItem 实时 COUNT 派生，SHALL NOT 落库。

#### Scenario: 预设题库标记

- **WHEN** 题库为系统预设
- **THEN** is_preset SHALL 为 true
- **AND** 系统 SHALL 拒绝删除 is_preset=true 的题库

### Requirement: QuestionSet 软删与数据隔离

题库文件夹 SHALL 走软删；教师 SHALL NOT 操作他人题库（数据隔离）。

#### Scenario: 删除文件夹不级联删题

- **WHEN** 教师删除自己的题库文件夹
- **THEN** 系统 SHALL 软删
- **AND** 系统 SHALL NOT 级联删除其中的题目（共享引用，题目可能属于多个文件夹）

### Requirement: QuestionSetItem 关联（N:M 共享引用）

- **WHEN** 一道题被加入多个题库文件夹
- **THEN** 系统 SHALL 允许（N:M 共享引用）
- **AND** (question_set_id, question_id) SHALL 唯一（unique 约束）
- **AND** QuestionSetItem SHALL 为纯关系表，硬删除
- **AND** sort_order SHALL 决定文件夹内题目顺序

#### Scenario: 移题不删题

- **WHEN** 从题库文件夹移除一道题（删除 QuestionSetItem）
- **THEN** 系统 SHALL 仅删除关联记录，SHALL NOT 删除 Question 本身

### Requirement: 题库结构化过滤

题库选题 SHALL 支持按 type/difficulty/knowledge_points/source_name/region/year 结构化过滤，SHALL NOT 涉及向量检索（属后续历史真题库 change）。

#### Scenario: 按知识点过滤

- **WHEN** 教师按知识点过滤题库
- **THEN** 系统 SHALL 返回 knowledge_points 数组包含该知识点的题目

### Requirement: 文件夹内题目列表

系统 SHALL 提供列出某题库文件夹内题目的能力，返回题目按 QuestionSetItem.sort_order 排序，SHALL NOT 返回已软删题目。

#### Scenario: 按排序返回文件夹题目

- **WHEN** 教师请求某个题库文件夹的题目列表
- **THEN** 系统 SHALL 返回该文件夹内全部题目，按 sort_order 升序（同序按题目 id 稳定）

#### Scenario: 过滤软删题目

- **WHEN** 文件夹内某题已被软删
- **THEN** 系统 SHALL NOT 在列表中返回该题

#### Scenario: 无权限拦截

- **WHEN** 教师请求他人文件夹的题目列表
- **THEN** 系统 SHALL 返回 404

