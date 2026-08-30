# organization-hierarchy Specification (delta)

## ADDED Requirements

### Requirement: 班级列表端点

系统 SHALL 提供查询班级列表的端点，按当前教师角色做数据范围隔离（沿用「数据范围隔离」需求），供发布试卷等场景选班。

#### Scenario: 普通教师查看任教班级

- **WHEN** 普通教师请求班级列表
- **THEN** 系统 SHALL 通过 TeacherClassSubject 过滤，仅返回该教师任教的班级

#### Scenario: 返回班级标识

- **WHEN** 系统返回班级列表
- **THEN** 每项 SHALL 至少包含班级 id 与名称（供前端展示与提交 class_ids）
