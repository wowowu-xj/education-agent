# question-bank Specification (delta)

## ADDED Requirements

### Requirement: 题目列表分页

题目列表接口 SHALL 支持分页，返回分页元数据，避免一次性加载全部题目。

#### Scenario: 分页返回

- **WHEN** 教师请求第 page 页、每页 page_size 条题目
- **THEN** 系统 SHALL 返回该页题目 items、总数 total、当前页 page、每页条数 page_size

#### Scenario: 越界页

- **WHEN** 教师请求超出范围的页码
- **THEN** 系统 SHALL 返回空 items 且 total 保持不变

## MODIFIED Requirements

### Requirement: 题库结构化过滤

题库选题 SHALL 支持按 type/difficulty/knowledge_points/source_name/region/year 结构化过滤；多个筛选条件 SHALL 可叠加（AND 语义），SHALL NOT 涉及向量检索（属后续历史真题库 change）。

#### Scenario: 按知识点过滤

- **WHEN** 教师按知识点过滤题库
- **THEN** 系统 SHALL 返回 knowledge_points 数组包含该知识点的题目

#### Scenario: 组合筛选叠加

- **WHEN** 教师同时指定题型、难度、知识点等多个筛选条件
- **THEN** 系统 SHALL 返回同时满足全部条件的题目（AND 语义）
