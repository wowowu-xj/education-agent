# question-batch-import Specification (delta)

## Purpose

提供题库题目的批量导入能力，将大批量录入从逐题手动录入收敛为一次「上传 → 预览校验 → 确认写入 → 结果统计」操作。

## ADDED Requirements

### Requirement: 批量解析与预览校验

系统 SHALL 解析批量导入的输入内容，并逐题校验；预览阶段 SHALL NOT 写入题库，SHALL 返回可导入题数与逐题校验错误明细。

#### Scenario: 预览不落库

- **WHEN** 教师提交批量导入内容进入预览
- **THEN** 系统 SHALL 解析并校验，返回题目明细与错误，SHALL NOT 写入题库

#### Scenario: 校验错误明细

- **WHEN** 部分题目缺少必填字段或取值非法（题型/难度超出 vocabulary）
- **THEN** 系统 SHALL 逐题标注错误原因，其余题目仍可预览通过

### Requirement: 确认写入与结果统计

系统 SHALL 在教师确认后批量写入通过校验的题目，并返回成功 / 失败数及逐题原因；校验失败的题目 SHALL 失败而非整体回滚。

#### Scenario: 批量写入

- **WHEN** 教师确认导入通过校验的题目
- **THEN** 系统 SHALL 批量落库并为每道题建向量索引

#### Scenario: 结果统计

- **WHEN** 批量写入完成
- **THEN** 系统 SHALL 返回成功 / 失败数及逐题原因

#### Scenario: 部分成功不整体回滚

- **WHEN** 导入内容中既有通过也有未通过校验的题目
- **THEN** 系统 SHALL 写入通过部分，跳过未通过部分，而非整体失败

### Requirement: 导入数据隔离

批量导入 SHALL 归属当前教师，SHALL NOT 越权写入他人题目；导入题目 SHALL 复用 question-bank 数据模型与软删语义。

#### Scenario: 归属当前教师

- **WHEN** 教师批量导入题目
- **THEN** 系统 SHALL 将题目归属该教师（teacher_id）
