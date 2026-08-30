## Why

产品设计文档（Part 4 §25）描述了题库管理与考试生命周期，但当前后端只有身份/组织数据模型和出题工作台前端，题库（Question/QuestionSet）、试卷（Paper）、考试（Exam）三个核心实体尚未建模。教师在出题工作台产出的题目没有落库目标，也无法组卷发布到班级。在写任何题库/考试代码之前，必须先冻结这六个实体 + 三个关联表的数据模型，以及 Paper/Exam 两层状态机，作为后端 ORM、API、前端三方的共享契约。

## What Changes

- 新增题目与题库文件夹数据模型：Question、QuestionSet、QuestionSetItem（N:M 共享引用），支持题库 CRUD 与软删
- 新增组卷与考试数据模型：Paper、PaperQuestion、Exam，支持组卷发布到多班
- 冻结 Paper（draft/locked）与 Exam（published/in_progress/grading/completed/archived/cancelled）两层状态机
- 定义发布后锁定与删除拦截规则（被引用题目/试卷不可删）
- 新增向量检索核心服务：对题库 Question 建 ChromaDB 向量索引（每个知识点一个向量），提供语义召回 API 与两层检索（关键词粗筛 → 向量精筛）
- 新增试卷导出：Paper 导出为可打印文档（含题目/分值/总分，可选含答案/解析）

## Capabilities

### New Capabilities
- `question-bank`: 题目（Question）与题库文件夹（QuestionSet/QuestionSetItem）的数据模型与 CRUD 契约
- `exam-lifecycle`: 组卷（Paper/PaperQuestion）与考试按班实例（Exam）的数据模型与两层状态机
- `question-vector-search`: 向量检索核心——ChromaDB 索引 + 语义召回 API + 两层检索（关键词粗筛 → 向量精筛）
- `paper-export`: 试卷导出——Paper 导出为可打印文档（含答案/解析开关）

## Impact

- **新增规格**: `specs/question-bank/`、`specs/exam-lifecycle/`、`specs/question-vector-search/`、`specs/paper-export/`
- **新增后端模型**: `chemai-backend/app/models/question.py`、`question_set.py`、`paper.py`、`exam.py`
- **新增枚举**: `PaperStatus`（draft/locked）、`ExamStatus`（published/in_progress/grading/completed/archived/cancelled），走 `enum_type` 小写下划线 + CHECK 约束约定
- **新增依赖**: ChromaDB（向量库）、dashscope text-embedding-v3（embedding）
- **依赖**: `question-vocabulary`（题型/难度枚举）、`identity-management`/`organization-hierarchy`（teacher/class 外键）
- **不实现**: 学生作答链路（AnswerRecord/成绩）、历史真题库（渠道二数据源）、联网搜索兜底（MiMo+DeepSeek）、RAG 注入、AI 生成、OCR
