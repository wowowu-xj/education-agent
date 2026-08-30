# question-workbench-frontend Specification (delta)

## ADDED Requirements

### Requirement: 题库列表分页控件

Tab 2「题库管理」题目列表 SHALL 提供分页控件，展示当前页与总页数，可切换页。

#### Scenario: 翻页

- **WHEN** 教师点击上一页 / 下一页或页码
- **THEN** 系统 SHALL 拉取对应页题目并刷新列表

#### Scenario: 分页信息

- **WHEN** 渲染题目列表
- **THEN** 系统 SHALL 展示当前页 / 总页数 / 总条数

### Requirement: 题库组合筛选

Tab 2 SHALL 提供题型、难度、知识点组合筛选控件，多条件可叠加，可重置。

#### Scenario: 组合筛选

- **WHEN** 教师选择题型 + 难度 + 知识点
- **THEN** 系统 SHALL 以 AND 语义过滤题目列表，并重置到第一页

#### Scenario: 重置筛选

- **WHEN** 教师点击「重置」
- **THEN** 系统 SHALL 清空全部筛选条件并刷新列表
