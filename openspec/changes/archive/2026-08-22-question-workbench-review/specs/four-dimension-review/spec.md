## Purpose

为 AI 生成的化学题目提供四维度质量审核机制（科学性、难度匹配、知识点覆盖、区分度），通过结构化状态机管理审核生命周期，确保未通过审核的题目不得进入题库。

## ADDED Requirements

### Requirement: 四维审核提交

系统 SHALL 提供 `POST /api/review/submit` 端点，接受题目 ID 并创建审核任务。审核任务创建后 SHALL 进入 `pending` 状态。

#### Scenario: 成功提交审核

- **WHEN** 教师对题目发起审核请求，请求体为 `{"question_id": "<uuid>"}`
- **THEN** 系统 SHALL 创建 Review 记录，状态为 `pending`
- **AND** 返回 `{"review_id": "<uuid>", "status": "pending"}`

#### Scenario: 题目不存在

- **WHEN** 提交的 question_id 在数据库中不存在
- **THEN** 系统 SHALL 返回 HTTP 404
- **AND** 响应体 SHALL 包含 `{"detail": "题目不存在"}`

#### Scenario: 题目已在审核中

- **WHEN** 提交的题目已有一条状态为 pending 或 reviewing 的审核记录
- **THEN** 系统 SHALL 返回 HTTP 409
- **AND** 响应体 SHALL 包含 `{"detail": "该题目已有进行中的审核"}`

### Requirement: 审核状态机流转

审核任务 SHALL 遵循状态机流转：`pending → reviewing → passed` 或 `pending → reviewing → rejected`。状态转换 MUST 在 service 层显式执行，不可跳过中间状态。

#### Scenario: 开始审核

- **WHEN** 审核引擎开始处理一条 pending 状态的审核
- **THEN** 系统 SHALL 将状态更新为 `reviewing`
- **AND** 记录 started_at 时间戳

#### Scenario: 审核通过

- **WHEN** 四维评分均达到通过阈值
- **THEN** 系统 SHALL 将状态更新为 `passed`
- **AND** 记录 completed_at 时间戳
- **AND** 题目状态 SHALL 同步更新为 approved

#### Scenario: 审核未通过

- **WHEN** 任一维度评分未达到通过阈值
- **THEN** 系统 SHALL 将状态更新为 `rejected`
- **AND** 记录 completed_at 时间戳
- **AND** 响应中 SHALL 包含各维度具体评分和未通过原因

#### Scenario: 非法状态转换

- **WHEN** 尝试将 passed 状态的审核直接改为 rejected
- **THEN** 系统 SHALL 拒绝该操作
- **AND** 返回 HTTP 409 及状态转换规则冲突提示

### Requirement: 四维评分结构

每条审核记录 SHALL 包含四个维度的评分（0-100），总分 SHALL 为四维的加权平均。通过阈值 SHALL 为每个维度 ≥ 60 且总分 ≥ 70。

#### Scenario: 计算审核总分

- **WHEN** 审核四维评分为 `science: 80, difficulty_match: 75, knowledge_coverage: 70, discrimination: 65`
- **THEN** 总分 SHALL = (80 + 75 + 70 + 65) / 4 = 72.5
- **AND** 各维度均 ≥ 60、总分 ≥ 70，审核 SHALL 通过

#### Scenario: 单维度不达标

- **WHEN** 审核四维评分为 `science: 85, difficulty_match: 55, knowledge_coverage: 80, discrimination: 75`
- **THEN** difficulty_match < 60，审核 SHALL 不通过
- **AND** 响应 SHALL 标注 difficulty_match 为未通过维度

### Requirement: 查询审核详情

系统 SHALL 提供 `GET /api/review/{review_id}` 端点返回审核详情，包含四维评分、状态、时间戳和未通过原因。

#### Scenario: 查询进行中的审核

- **WHEN** 查询一条状态为 reviewing 的审核
- **THEN** 系统 SHALL 返回审核详情，评分字段可为 null
- **AND** status 字段 SHALL 为 "reviewing"

#### Scenario: 查询已完成的审核

- **WHEN** 查询一条状态为 passed 的审核
- **THEN** 系统 SHALL 返回完整的四维评分和总分
- **AND** 包含审核完成时间戳

#### Scenario: 审核记录不存在

- **WHEN** 查询的 review_id 不存在
- **THEN** 系统 SHALL 返回 HTTP 404

### Requirement: 审核列表查询

系统 SHALL 提供 `GET /api/review/list` 端点，支持按状态筛选和分页。

#### Scenario: 按状态筛选

- **WHEN** 请求 `GET /api/review/list?status=pending`
- **THEN** 系统 SHALL 仅返回状态为 pending 的审核记录

#### Scenario: 分页查询

- **WHEN** 请求 `GET /api/review/list?page=1&page_size=20`
- **THEN** 系统 SHALL 返回第 1 页的 20 条记录
- **AND** 响应 SHALL 包含 total、page、page_size 分页元数据
