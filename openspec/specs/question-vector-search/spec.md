# question-vector-search Specification

## Purpose
定义向量检索服务核心：对题库 Question 建 ChromaDB 向量索引（每个知识点一个向量），提供语义召回 API 与两层检索（关键词粗筛 → 向量精筛）。联网搜索兜底、RAG 注入、历史真题库数据源不在本 spec。
## Requirements
### Requirement: 向量索引构建

系统 SHALL 为 Question 的每个 knowledge_point 生成一个向量，ID 形如 `<question_id>::kp-n`；嵌入文本 SHALL 为"考点+题型+难度+来源+题目(前500字)+答案"语义拼接，维度 SHALL 为 1024（dashscope text-embedding-v3）。

#### Scenario: 题目入库时建索引

- **WHEN** Question 落库
- **THEN** 系统 SHALL 为其每个 knowledge_point 生成一个向量
- **AND** ID SHALL 形如 `<question_id>::kp-n`

#### Scenario: 维度不匹配重建

- **WHEN** embedding 服务返回的向量维度与现有 collection 不一致
- **THEN** 系统 SHALL 清空并重建索引

### Requirement: 语义召回 API

系统 SHALL 提供语义召回 API：输入查询文本，返回相似题目，similarity 阈值 SHALL 为 ≥ 0.6。

#### Scenario: 语义查询返回 Top-K

- **WHEN** 教师输入查询文本
- **THEN** 系统 SHALL 按 cosine 相似度返回 Top-K 相似题
- **AND** 相似度 SHALL ≥ 0.6

#### Scenario: 结构化过滤叠加

- **WHEN** 教师同时指定题型/难度/知识点过滤条件
- **THEN** 系统 SHALL 在向量召回上叠加结构化过滤

### Requirement: 两层检索

系统 SHALL 采用两层检索：第一层关键词匹配（知识点重叠度 + 精确匹配加权 + 难度排序）取 Top-20 候选，第二层 ChromaDB 向量精筛（候选范围 `where id in [...]`）取 cosine Top-K；无候选时全量向量检索。

#### Scenario: 关键词命中后向量精筛

- **WHEN** 第一层关键词匹配命中候选
- **THEN** 系统 SHALL 仅在候选范围内做向量精筛

#### Scenario: 无关键词候选时全量检索

- **WHEN** 第一层关键词匹配无候选
- **THEN** 系统 SHALL 对全量向量做检索

### Requirement: 降级

系统 SHALL 在 ChromaDB 不可用时降级为纯关键词匹配；在 embedding 服务不可用时降级为 MD5 伪向量。

#### Scenario: ChromaDB 不可用

- **WHEN** ChromaDB 连接失败
- **THEN** 系统 SHALL 降级为纯关键词匹配，检索仍可用

#### Scenario: embedding 服务不可用

- **WHEN** dashscope embedding 调用失败
- **THEN** 系统 SHALL 降级为 MD5 伪向量（语义退化为精确）

