## Purpose

定义试卷导出：将 Paper 导出为可打印文档（打印友好 HTML + 可选 Word .docx），含题目、分值、总分，可选是否含答案/解析。

## ADDED Requirements

### Requirement: 导出内容

系统 SHALL 导出 Paper 的标题、按 sort_order 排序的题目列表、每题分值、总分。

#### Scenario: 导出完整试卷

- **WHEN** 教师导出某 Paper
- **THEN** 系统 SHALL 包含标题、按 sort_order 排序的题目、每题分值、总分

### Requirement: 答案与解析开关

系统 SHALL 支持"是否含答案/解析"开关。

#### Scenario: 不含答案导出

- **WHEN** 教师选择"不含答案"导出
- **THEN** 系统 SHALL 隐藏 answer 与 analysis 字段

#### Scenario: 含答案导出

- **WHEN** 教师选择"含答案"导出
- **THEN** 系统 SHALL 包含每题 answer（与可选 analysis）

### Requirement: 导出格式

系统 SHALL 支持打印友好 HTML；Word（.docx）SHALL 为可选格式。

#### Scenario: HTML 导出

- **WHEN** 教师请求 HTML 格式
- **THEN** 系统 SHALL 返回可打印的 HTML 文档

#### Scenario: Word 导出

- **WHEN** 教师请求 .docx 格式
- **THEN** 系统 SHALL 返回 Word 文档

### Requirement: 导出状态约束

系统 SHALL 允许导出任意状态的 Paper（draft 可预览，locked 可正式导出）。

#### Scenario: 导出 draft 试卷

- **WHEN** 教师导出 draft 状态试卷
- **THEN** 系统 SHALL 允许（预览用途）
