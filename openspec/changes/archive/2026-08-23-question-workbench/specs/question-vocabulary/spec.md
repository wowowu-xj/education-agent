## Purpose

定义 ChemAI 题目领域词汇表：题型枚举（9 种）、难度枚举（4 档）、LLM 输出别名到枚举值的映射。这是前端出题工作台 chip、后端 Question 模型 enum、LLM 出题 prompt 三方的单一契约，任何一处取值 MUST 以本 spec 为准。

## ADDED Requirements

### Requirement: 题型枚举

系统 SHALL 支持 9 种题型，枚举值 MUST 为全英文小写下划线。

| value | 中文 |
|-------|------|
| single_choice | 单项选择题 |
| multi_choice | 多项选择题 |
| true_false | 判断题 |
| fill_blank | 填空题 |
| short_answer | 简答题 |
| essay | 论述题 |
| calculation | 计算题 |
| experiment | 实验题 |
| inference | 推断题 |

#### Scenario: 有效题型值

- **WHEN** 题目 type 字段为上述 9 个枚举值之一
- **THEN** 系统 SHALL 接受该值

#### Scenario: 无效题型值被拒绝

- **WHEN** 题目 type 字段为其他值（如 "choice"、"方程式配平"、"推断"）
- **THEN** 系统 SHALL 拒绝，不落库

#### Scenario: AI 生成题型子集

- **WHEN** AI 生成题目的题型集合
- **THEN** 系统 SHALL 限定为 5 种：single_choice、fill_blank、calculation、experiment、inference

#### Scenario: 手动录入完整题型集

- **WHEN** 教师手动录入题目
- **THEN** 系统 SHALL 允许全部 9 种题型

### Requirement: 难度枚举

系统 SHALL 支持 4 档难度，枚举值 MUST 为全英文小写：easy、medium、hard、competition。

#### Scenario: 有效难度值

- **WHEN** 题目 difficulty 字段为 easy/medium/hard/competition 之一
- **THEN** 系统 SHALL 接受该值

#### Scenario: AI 生成难度子集

- **WHEN** AI 生成题目
- **THEN** 难度 SHALL 限定为 easy/medium/hard
- **AND** 前端 SHALL 不展示 competition 选项（竞赛级不做 AI 出题）

#### Scenario: 手动录入含竞赛档

- **WHEN** 教师手动录入竞赛级题目
- **THEN** 系统 SHALL 允许 difficulty = competition

#### Scenario: 难度系数不混用

- **WHEN** 题目需要记录区分度/通过率等心理测量指标
- **THEN** 系统 SHALL 使用独立字段（如 discrimination）
- **AND** 该值 SHALL NOT 进入 difficulty 枚举（难度系数 P 值与难度等级方向相反）

### Requirement: LLM 输出别名映射

出题服务解析 LLM 返回 JSON 时 SHALL 将短别名映射到规范枚举值。

| LLM 输出 type | 枚举值 |
|---------------|--------|
| choice | single_choice |
| fill | fill_blank |
| calc | calculation |
| experiment | experiment |
| inference | inference |

#### Scenario: 别名正确映射

- **WHEN** LLM 返回 type 字段为 "choice"
- **THEN** 系统 SHALL 映射为 single_choice

#### Scenario: 未识别别名被拒绝

- **WHEN** LLM 返回 type 字段不在映射表中（如 "equation_balance"）
- **THEN** 系统 SHALL 标记该题需人工审核，不自动落库

### Requirement: 单一真源

题型与难度的取值域 SHALL 由本 spec 唯一定义，CONTEXT.md、前端 chip、后端 enum、LLM prompt SHALL 与本 spec 一致。

#### Scenario: CONTEXT.md 与枚举一致

- **WHEN** 查阅 CONTEXT.md 的题型与难度小节
- **THEN** 其 SHALL 列出 9 种题型与 4 档难度
- **AND** SHALL NOT 出现 "八种题型" 或 "1-5 级" 的旧定义
