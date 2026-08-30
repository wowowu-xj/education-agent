## 1. 数据模型与枚举

- [x] 1.1 新增 `PaperStatus`（draft/locked）、`ExamStatus`（published/in_progress/grading/completed/archived/cancelled）枚举，走 `enum_type` 小写下划线 + CHECK 约束
- [x] 1.2 新增 Question 模型（teacher_id 可空 FK、options JSON、knowledge_points JSON、软删）
- [x] 1.3 新增 QuestionSet / QuestionSetItem 模型（QuestionSet 软删、QuestionSetItem 硬删 + unique(set_id, qid)）
- [x] 1.4 新增 Paper / PaperQuestion / Exam 模型（Paper 软删、PaperQuestion 硬删、Exam 不物理删）
- [x] 1.5 Alembic 迁移脚本 + 注册到 app/models/__init__.py

## 2. 题库 CRUD API

- [x] 2.1 `POST /api/questions` 创建题目（校验题型/难度枚举，AI 生成限 5 题型 / 手动 9 题型）
- [x] 2.2 `GET /api/questions` 列表（按题型/难度/知识点/来源地区/年份结构化过滤，教师数据隔离）
- [x] 2.3 `GET/PUT/DELETE /api/questions/{id}` 详情/更新/软删（被 locked Paper 引用返回 409）
- [x] 2.4 `POST/GET/PUT/DELETE /api/question-sets` 题库文件夹 CRUD（is_preset 不可删）
- [x] 2.5 `POST/DELETE /api/question-sets/{id}/questions` 加题/移题（QuestionSetItem，sort_order 排序）

## 3. 组卷发布 API

- [x] 3.1 `POST /api/papers` 创建试卷（draft）
- [x] 3.2 `GET/PUT/DELETE /api/papers/{id}` 试卷详情/更新/软删（locked 后 PUT 拒绝）
- [x] 3.3 `POST/DELETE /api/papers/{id}/questions` 组卷加题/移题（draft 可增删，sort_order 排序）
- [x] 3.4 `POST /api/papers/{id}/publish` 发布到 N 个班（生成 N 个 Exam，Paper → locked）
- [x] 3.5 发布校验：至少 1 题、题目未被独占（共享引用不排他）

## 4. 考试教师侧状态机 API

- [x] 4.1 `GET /api/exams` 考试列表（按班级/状态过滤）
- [x] 4.2 `POST /api/exams/{id}/cancel` 取消（published/in_progress → cancelled）
- [x] 4.3 `POST /api/exams/{id}/finalize` 批阅完成（grading → completed）
- [x] 4.4 非法迁移拒绝（如 completed → published 返回 409）

## 5. 向量检索核心

- [x] 5.1 ChromaDB 集成（collection 初始化 + 连接管理）
- [x] 5.2 Question 向量索引：每个 knowledge_point 生成一个向量，ID 形如 `<question_id>::kp-n`，嵌入文本="考点+题型+难度+来源+题目(前500字)+答案"
- [x] 5.3 embedding 接入 dashscope text-embedding-v3（1024 维），维度不匹配自动重建
- [x] 5.4 两层检索：关键词粗筛（知识点重叠度 + 精确匹配加权 + 难度排序 Top-20）→ ChromaDB 向量精筛（cosine Top-K，similarity ≥ 0.6）
- [x] 5.5 语义召回 API：`POST /api/questions/search`（文本查询 → 相似题）
- [x] 5.6 降级：ChromaDB 不可用 → 纯关键词；embedding 失败 → MD5 伪向量

## 6. 试卷导出

- [x] 6.1 导出打印友好 HTML（标题 + 按 sort_order 题目列表 + 每题分值 + 总分）
- [x] 6.2 内容开关：是否含答案/解析
- [x] 6.3 可选 Word .docx 导出（python-docx）
- [x] 6.4 导出 API：`GET /api/papers/{id}/export?format=html|docx&include_answer=...`

## 7. 测试

- [x] 7.1 L1 单元测试：枚举 CHECK、QuestionSetItem unique 约束、total_score/question_count 派生
- [x] 7.2 L2 集成测试：题库 CRUD、组卷发布、删除拦截 409、状态机非法迁移
- [x] 7.3 数据隔离测试：教师只能操作自己的题目/试卷/考试
- [x] 7.4 向量检索测试：索引构建、语义召回、降级路径
- [x] 7.5 试卷导出测试：HTML/docx 内容与开关

## 8. 收尾

- [x] 8.1 openspec validate exam-bank
- [x] 8.2 同步 CONTEXT.md 真题检索概要标注（向量检索核心已纳入 scope，联网兜底/历史真题库仍 defer）
