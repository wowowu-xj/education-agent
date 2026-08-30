## Context

见 proposal.md。出题工作台前端已就绪（question-workbench-frontend），题目领域词汇表已冻结（question-vocabulary）。本 change 把题目、题库、试卷、考试四个概念落为数据模型。核心张力来自设计文档把"试卷/考试"混为一个概念，而业务需要"一份试卷同时发布给多个班"。

## Goals / Non-Goals

**Goals:**
- 冻结 Question/QuestionSet/QuestionSetItem/Paper/PaperQuestion/Exam 六实体 + 三关联表的数据模型
- 冻结 Paper（两态）与 Exam（六态）两层状态机
- 定义发布后锁定与删除拦截规则

**Non-Goals:**
- 学生作答链路（AnswerRecord、成绩、判卷）
- 历史真题库（渠道二数据源）、联网搜索兜底（MiMo+DeepSeek）、RAG 注入（依赖出题服务）
- AI 生成题目、OCR 导入
- Paper 解锁（发布后不可逆）

## Decisions

### Decision 1: Paper 与 Exam 拆为两个实体

**选择**: 内容实体 Paper（组好的卷子）+ 按班实例 Exam（某班某次考试）。

**理由**: 教师需要把同一份试卷同时发布给 A 班和 B 班，也可只给 A 班。若只有一个 Exam，多班发布只能复制题目快照，产生 N 份重复数据且无法表达"试卷"这一可复用内容。

**替代方案**: 单实体 + 复制快照——N 个班 N 份重复题目，改一处需同步 N 处，拒绝。

### Decision 2: 共享引用 + 发布后锁定

**选择**: Paper 通过 PaperQuestion 引用 Question（共享引用，N:M），发布后 Paper 锁定（draft → locked），不再改题。

**理由**: 改 Paper 一处即影响所有已引用班级，锁定避免"已发布考试题目被偷偷改掉"。要改题必须复制新 Paper，保留旧考试的题目引用语义不变。

**替代方案**: 复制快照（发布时把题目内容复制进 Exam）——可保留历史，但题目与题库脱节，无法统计"这道题被哪些试卷用过"，拒绝。

### Decision 3: 核心实体软删、纯关系表硬删

**选择**: Question/QuestionSet/Paper 走 SoftDeleteMixin（deleted_at 软删）；QuestionSetItem/PaperQuestion 纯关系表硬删；Exam 不物理删（走 cancelled）。

**理由**: 对齐项目既有约定（core entities 软删、pure relation tables 硬删）。Exam 被成绩/历史引用，物理删会断链。

### Decision 4: question_count 与 total_score 派生不落库

**选择**: QuestionSet.question_count 与 Paper.total_score 由关联表实时求和，不存字段。

**理由**: 存字段需在每次加题/删题/改分值时同步维护，易不一致。SQLite 单库量级下实时 COUNT/SUM 足够快。

### Decision 5: 本期只接教师侧状态迁移

**选择**: 只实现发布（→published）、取消（→cancelled）、finalize（→completed）；in_progress/grading 枚举占位，自动进入依赖学生作答链路，defer。

**理由**: 学生作答链路（AnswerRecord、交卷）在本 change scope 之外，in_progress（学生开始作答）与 grading（全部交卷）的触发点不存在，只能占位。

### Decision 6: 删除拦截（409）

**选择**: 被 Exam 引用的 Paper、被 locked Paper 引用的 Question 删除时返回 409；未被引用的可软删。

**理由**: locked Paper 的题目是已发布考试的一部分，删除会破坏考试完整性。

### Decision 7: 向量检索仅核心

**选择**: 向量检索只做核心——ChromaDB 索引（每个知识点一个向量）+ 语义召回 API + 两层检索（关键词粗筛 → 向量精筛）。

**理由**: 三层递进搜索的第三层（联网兜底）依赖外部搜索 API，RAG 注入依赖尚未实现的 AI 出题服务，历史真题库依赖尚未排期的数据源，均需单独排期。核心已能对教师自有题库做语义召回。

**替代方案**: 一次性实现完整三层递进 + RAG——依赖项过多，违背"简单优先"，拒绝。

### Decision 8: 向量检索降级策略

**选择**: ChromaDB 不可用 → 纯关键词匹配；embedding 服务不可用 → MD5 伪向量（语义退化为精确）。

**理由**: 检索是辅助功能，不应因向量库/外部 embedding 故障阻塞出题主链路，降级保证可用性。

### Decision 9: 试卷导出格式

**选择**: 导出为打印友好 HTML（零依赖）+ 可选 Word（.docx，python-docx）。

**理由**: HTML 打印视图零新增依赖，覆盖"打印/分享"主诉求；Word 供教师二次编辑，作为可选增强。

**替代方案**: 直接 PDF——需引入 reportlab/weasyprint 等重依赖，且教师难以编辑，拒绝。

## Open Questions

- Paper 解锁（draft ← locked）是否需要在未来支持"撤回发布"？当前设计锁定不可逆，撤回走 Exam.cancelled。
- 学生作答链路落地后，in_progress/grading 的自动进入由交卷事件触发，还是教师手动开始？
- 预设题库（is_preset=true）由谁维护、内容从哪来？（渠道二历史真题库尚未排期）
- 向量检索是否跨教师共享？（本期仅教师自有题库，历史真题库数据源落地后是否扩大召回范围）
- 试卷导出是否需要 PDF？（当前 HTML + Word，PDF 依赖重，暂缓）
