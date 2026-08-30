# question-workbench-frontend Specification (delta)

## ADDED Requirements

### Requirement: 题库文件夹列表

Tab 2「题库管理」SHALL 展示本教师全部题库文件夹（QuestionSet），每项 SHALL 显示名称与题目数量。

#### Scenario: 加载文件夹列表

- **WHEN** 教师进入「题库管理」Tab
- **THEN** 系统 SHALL 从题库文件夹 API 拉取本教师文件夹列表
- **AND** 每项 SHALL 显示文件夹名称与派生题目数

#### Scenario: 预设文件夹标记

- **WHEN** 文件夹 is_preset 为 true
- **THEN** 系统 SHALL 视觉上区分预设文件夹
- **AND** SHALL NOT 提供删除入口

#### Scenario: 空态

- **WHEN** 教师尚无任何题库文件夹
- **THEN** 系统 SHALL 显示空态引导（含「新建文件夹」入口）

### Requirement: 题库文件夹 CRUD

Tab 2 SHALL 支持创建、重命名、删除题库文件夹；删除 is_preset 文件夹 SHALL 被拦截。

#### Scenario: 创建文件夹

- **WHEN** 教师点击「新建文件夹」并输入名称
- **THEN** 系统 SHALL 调用创建接口并刷新列表

#### Scenario: 删除预设文件夹被拦截

- **WHEN** 教师尝试删除 is_preset=true 的文件夹
- **THEN** 系统 SHALL 不展示删除入口，或调用后展示 409 冲突提示

#### Scenario: 删除普通文件夹

- **WHEN** 教师删除自己的普通文件夹
- **THEN** 系统 SHALL 弹确认，确认后软删并刷新列表

### Requirement: 文件夹题目展示

选中文件夹后 SHALL 展示其中的题目，题目卡片 SHALL 显示题干摘要、题型、难度标签。

#### Scenario: 查看文件夹题目

- **WHEN** 教师点击某个文件夹
- **THEN** 系统 SHALL 拉取该文件夹内的题目（按 sort_order 排序）并展示为卡片网格

#### Scenario: 题目卡片字段

- **WHEN** 渲染文件夹内题目卡片
- **THEN** 每张卡片 SHALL 显示题干摘要、题型标签、难度标签

#### Scenario: 空文件夹

- **WHEN** 选中文件夹内无题目
- **THEN** 系统 SHALL 显示空态（引导「从出题工作台生成或加入题目」）

### Requirement: 加题与移题

Tab 2 SHALL 支持将题目加入文件夹、从文件夹移除；移除 SHALL NOT 删除题目本身。

#### Scenario: 移题

- **WHEN** 教师从文件夹移除一道题
- **THEN** 系统 SHALL 仅解除关联并刷新列表
- **AND** SHALL NOT 删除题目实体

#### Scenario: 重复加题被拦截

- **WHEN** 教师将一道已在该文件夹中的题再次加入
- **THEN** 系统 SHALL 展示冲突提示

### Requirement: 试卷列表

Tab 4「考试列表」SHALL 以试卷（Paper）为列表数据源，每张卡片 SHALL 显示标题、题目数、总分、状态。

#### Scenario: 加载试卷列表

- **WHEN** 教师进入「考试列表」Tab
- **THEN** 系统 SHALL 从试卷 API 拉取本教师试卷列表
- **AND** 卡片 SHALL 显示标题、题目数、总分、状态（草稿/已发布）

#### Scenario: 空态

- **WHEN** 教师尚无任何试卷
- **THEN** 系统 SHALL 显示空态引导（「请先创建一份试卷」）

### Requirement: 试卷 CRUD

Tab 4 SHALL 支持创建、编辑、删除试卷；已发布（locked）试卷 SHALL 只读，被 Exam 引用的试卷删除 SHALL 被拦截。

#### Scenario: 创建试卷

- **WHEN** 教师点击「创建试卷」并输入标题
- **THEN** 系统 SHALL 创建 draft 试卷并刷新列表

#### Scenario: 锁定试卷只读

- **WHEN** 试卷状态为 locked
- **THEN** 系统 SHALL 隐藏编辑入口
- **AND** SHALL NOT 允许修改标题

#### Scenario: 已发布试卷不可删

- **WHEN** 教师尝试删除已被 Exam 引用的试卷
- **THEN** 系统 SHALL 展示 409 冲突提示

### Requirement: 发布试卷

Tab 4 SHALL 支持将 draft 试卷发布到班级：选择班级后生成对应 Exam，Paper 迁移为 locked。

#### Scenario: 发布到多个班级

- **WHEN** 教师选择一张至少含 1 题的 draft 试卷并选中若干班级发布
- **THEN** 系统 SHALL 为每个班级生成一个 Exam
- **AND** 试卷状态 SHALL 迁移为已发布（locked）

#### Scenario: 空试卷不可发布

- **WHEN** 教师尝试发布无题目的试卷
- **THEN** 系统 SHALL 展示提示（至少需要 1 道题）

### Requirement: 导出试卷

Tab 4 SHALL 支持导出试卷为 HTML 或 Word，可选择是否含答案。

#### Scenario: 导出 Word

- **WHEN** 教师选择导出并指定 docx 格式
- **THEN** 系统 SHALL 下载 Word 文档附件

#### Scenario: 导出预览

- **WHEN** 教师选择导出并指定 html 格式
- **THEN** 系统 SHALL 展示打印友好预览

### Requirement: 考试状态展示

已发布试卷 SHALL 展示其关联考试（班级与考试状态），考试状态 SHALL 使用六态中文标签。

#### Scenario: 查看已发布班级

- **WHEN** 试卷已发布
- **THEN** 系统 SHALL 展示该试卷关联的班级及其考试状态

#### Scenario: 取消考试

- **WHEN** 教师取消一个已发布/进行中的考试
- **THEN** 该考试状态 SHALL 展示为已取消

### Requirement: 状态标签语义

Paper 与 Exam 状态 SHALL 使用统一的中文标签与语义配色，遵循设计系统 36 的语义色。

#### Scenario: Paper 两态

- **WHEN** 渲染试卷状态
- **THEN** 草稿 SHALL 使用中性色，已发布 SHALL 使用 Teal

#### Scenario: Exam 六态

- **WHEN** 渲染考试状态
- **THEN** 已发布/进行中 SHALL 用 Teal，批阅中 SHALL 用警告黄，已完成 SHALL 用通过绿，已归档 SHALL 用中性色，已取消 SHALL 用阻断红
