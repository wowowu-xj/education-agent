# organization-hierarchy Specification

## Purpose
定义 ChemAI 的四级组织架构（学校→年级→班级→学生），以及教师与班级之间的任课关系。该架构 SHALL 作为多租户数据隔离的边界依据。
## Requirements
### Requirement: 四级组织层级

系统 SHALL 通过 School → Grade → Class → Student 的四级引用链表达组织架构。每一级 SHALL 通过外键指向上一级。

#### Scenario: 创建完整层级

- **WHEN** 管理员依次创建 School、Grade（引用 School）、Class（引用 Grade）、Student（引用 Class）
- **THEN** 系统 SHALL 建立完整的引用链
- **AND** 从 Student 出发能沿引用链回溯到 School

#### Scenario: 违反外键约束时拒绝

- **WHEN** 尝试创建 school_id 指向不存在的 School 的 Grade
- **THEN** 数据库 SHALL 通过外键约束拒绝

### Requirement: 教师任课关系

系统 SHALL 通过 TeacherClassSubject 表表达 Teacher 与 Class 的多对多关系。每条任课记录 SHALL 标注是否为班主任（is_head_teacher）。

#### Scenario: 一师多班

- **WHEN** 同一 Teacher 被分配到多个 Class 任课
- **THEN** 系统 SHALL 允许创建多条 (teacher_id, class_id) 对不同的 TeacherClassSubject 记录

#### Scenario: 一班多师

- **WHEN** 同一 Class 有多位任课教师
- **THEN** 系统 SHALL 允许创建多条 (teacher_id, class_id) 对不同的 TeacherClassSubject 记录

#### Scenario: 一班仅一班主任

- **WHEN** 尝试为同一 Class 创建第二条 is_head_teacher=true 的任课记录
- **THEN** 应用层 SHALL 拒绝该操作（数据库层不强制，由 service 层校验）

### Requirement: 数据范围隔离

系统 SHALL 通过 service 层的 role 分支逻辑实现数据范围隔离。数据库层 NOT 依赖 row-level security，隔离逻辑 MUST 在 service 层显式表达。

#### Scenario: admin 角色查看全部数据

- **WHEN** role="admin" 的用户请求班级列表
- **THEN** service 层 SHALL 返回所有 Class 记录，不附加 WHERE 过滤

#### Scenario: 教务管理员/学科组长本校数据

- **WHEN** role="academic_admin" 或 "subject_lead" 的用户请求班级列表
- **THEN** service 层 SHALL 附加 WHERE school_id = 当前用户.school_id

#### Scenario: 普通教师任教班级

- **WHEN** role="teacher" 的用户请求班级列表
- **THEN** service 层 SHALL 通过 JOIN TeacherClassSubject 过滤为该教师任教的班级

#### Scenario: 家长仅子女数据

- **WHEN** role="parent" 的用户请求子女学习数据
- **THEN** service 层 SHALL 通过 JOIN StudentParentBinding 过滤为该家长已绑定的学生

### Requirement: 软删除保留历史

Student、Teacher、Class、School 表 SHALL 使用软删除（deleted_at 字段），支持误删恢复。TeacherClassSubject、StudentParentBinding 等关系表 SHALL 使用硬删除。

#### Scenario: 学生软删除

- **WHEN** 教务管理员删除 Student 记录
- **THEN** 系统 SHALL 设置 Student.deleted_at = 当前时间
- **AND** 后续查询 SHALL 自动过滤 deleted_at IS NULL 的记录

#### Scenario: 关系表硬删除

- **WHEN** 解除教师任课关系
- **THEN** 系统 SHALL 从 TeacherClassSubject 表物理删除该记录

### Requirement: 通用字段自动化

所有业务表 SHALL 自动拥有 created_at 和 updated_at 字段。软删除表 SHALL 额外拥有 deleted_at 字段。

#### Scenario: 创建时自动填充 created_at

- **WHEN** 创建任意业务表记录
- **THEN** 系统 SHALL 自动设置 created_at = 当前 UTC 时间

#### Scenario: 更新时自动刷新 updated_at

- **WHEN** 更新任意业务表记录
- **THEN** 系统 SHALL 自动刷新 updated_at = 当前 UTC 时间

