# 身份管理规格

## Purpose

定义 ChemAI 系统中教师、学生、家长三类用户的身份存储、认证凭证和角色权限模型。系统 SHALL 支持双通道认证：教师/学生走统一账户体系，家长走独立认证通道。

## ADDED Requirements

### Requirement: 教师-学生统一账户体系

系统 SHALL 提供 Account 表存储教师和学生的登录凭证。每条 Account 记录 MUST 恰好关联一个 Teacher 或 Student 记录（互斥）。

#### Scenario: 创建教师账户

- **WHEN** 管理员为审批通过的教师创建账户
- **THEN** 系统 SHALL 创建 Account 记录，其中 teacher_id 非空、student_id 为空
- **AND** password_hash 字段 SHALL 存储 bcrypt 哈希后的密码

#### Scenario: 创建学生账户

- **WHEN** 教务管理员为学生创建账户
- **THEN** 系统 SHALL 创建 Account 记录，其中 student_id 非空、teacher_id 为空

#### Scenario: 违反互斥约束时拒绝

- **WHEN** 尝试创建 teacher_id 和 student_id 同时非空（或同时为空）的 Account
- **THEN** 数据库 SHALL 通过 CHECK constraint 拒绝该操作
- **AND** 应用层 SHALL 返回业务规则冲突错误

### Requirement: 教师角色枚举

Teacher 表 SHALL 通过 role 字段区分四种子角色：admin、academic_admin、subject_lead、teacher。角色值 MUST 为全英文，避免中英混杂。

#### Scenario: 有效角色值

- **WHEN** 创建 Teacher 记录时 role 字段为 "admin" / "academic_admin" / "subject_lead" / "teacher" 之一
- **THEN** 系统 SHALL 接受该记录

#### Scenario: 无效角色值被拒绝

- **WHEN** 尝试创建 role 字段为其他值（如 "教务管理员"、"root"）的 Teacher
- **THEN** 数据库 SHALL 通过 ENUM 类型约束拒绝

### Requirement: 家长独立认证

Parent 表 SHALL 直接存储 phone 和 password_hash 字段，不通过 Account 表进行身份关联。家长登录 SHALL 走独立的 `/api/parent/login` 端点。

#### Scenario: 家长注册

- **WHEN** 家长通过 /api/parent/register 提交手机号和密码
- **THEN** 系统 SHALL 直接在 Parent 表创建记录，password_hash 存储 bcrypt 哈希

#### Scenario: 家长登录不查询 Account 表

- **WHEN** 家长通过 /api/parent/login 提交凭证
- **THEN** 系统 SHALL 仅查询 Parent 表验证密码
- **AND** 签发的 JWT payload 中 role="parent"，不包含 school_id

### Requirement: 教师入驻审批状态

Teacher 表 SHALL 通过 status 字段（pending / approved / rejected）表达审批状态。只有 status="approved" 的教师才能创建 Account 记录并登录。

#### Scenario: 待审批教师无法登录

- **WHEN** status="pending" 的教师尝试通过 /api/auth/login 登录
- **THEN** 系统 SHALL 拒绝登录，返回错误提示"账户待审批"

#### Scenario: 审批通过后自动创建账户

- **WHEN** 管理员通过 /api/teacher-applications/{id}/approve 批准申请
- **THEN** 系统 SHALL 更新 Teacher.status="approved"
- **AND** 系统 SHALL 创建 Account 记录，默认密码为手机号后 6 位（bcrypt 哈希）

### Requirement: 亲子绑定关系

系统 SHALL 通过 StudentParentBinding 表建立家长与学生的多对多绑定关系。绑定 MUST 通过学生生成的 6 位绑定码验证。

#### Scenario: 绑定成功

- **WHEN** 家长提交正确的 (student_id, bind_code) 组合
- **THEN** 系统 SHALL 创建 StudentParentBinding 记录，is_active=true

#### Scenario: 绑定码错误

- **WHEN** 家长提交的 bind_code 与 Student.bind_code 不匹配
- **THEN** 系统 SHALL 拒绝绑定，返回业务规则冲突错误

#### Scenario: 一对多绑定

- **WHEN** 一位家长绑定多个子女
- **THEN** 系统 SHALL 允许为同一 parent_id 创建多条 StudentParentBinding 记录
