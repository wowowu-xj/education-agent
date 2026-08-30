# question-workbench-frontend Specification (delta)

## ADDED Requirements

### Requirement: 相似题推荐 UI

出题工作台 SHALL 提供相似题推荐入口，展示相似题列表及每题相似度，并排除当前题。

#### Scenario: 相似度展示

- **WHEN** 展示相似题列表
- **THEN** 每道题 SHALL 显示相似度（百分比或进度条），按相似度降序

#### Scenario: 排除自身

- **WHEN** 教师对某题请求相似题
- **THEN** 推荐结果 SHALL NOT 包含该题自身

#### Scenario: 降级弱化

- **WHEN** 相似度为降级语义（精确匹配退化）
- **THEN** 前端 SHALL 弱化相似度展示（如标注「精确匹配」而非百分比）
