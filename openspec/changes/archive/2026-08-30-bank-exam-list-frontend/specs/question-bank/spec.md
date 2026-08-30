# question-bank Specification (delta)

## ADDED Requirements

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
