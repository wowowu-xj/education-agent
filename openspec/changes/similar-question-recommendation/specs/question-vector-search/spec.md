# question-vector-search Specification (delta)

## ADDED Requirements

### Requirement: 排除自身

系统 SHALL 支持在相似题检索中排除指定题目。

#### Scenario: 排除当前题

- **WHEN** 教师请求相似题并传入 exclude_question_id
- **THEN** 结果 SHALL NOT 包含该题

### Requirement: 相似度降级语义

embedding 服务不可用（MD5 伪向量降级）时，返回结果的相似度语义 SHALL 退化为精确匹配，系统 SHALL 在响应中标注降级，使前端得以弱化相似度展示。

#### Scenario: 降级标注

- **WHEN** 检索走 MD5 伪向量降级路径
- **THEN** 系统 SHALL 在响应中标注相似度为降级语义

## MODIFIED Requirements

### Requirement: 语义召回 API

系统 SHALL 提供语义召回 API：输入查询文本，返回相似题目及每题相似度分数，similarity 阈值 SHALL 为 ≥ 0.6，结果按相似度降序。

#### Scenario: 语义查询返回 Top-K

- **WHEN** 教师输入查询文本
- **THEN** 系统 SHALL 按 cosine 相似度返回 Top-K 相似题
- **AND** 每道题 SHALL 附带 similarity 分数（0~1）
- **AND** 相似度 SHALL ≥ 0.6
- **AND** 结果 SHALL 按相似度降序排列

#### Scenario: 结构化过滤叠加

- **WHEN** 教师同时指定题型/难度/知识点过滤条件
- **THEN** 系统 SHALL 在向量召回上叠加结构化过滤
