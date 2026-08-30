# Paper 与 Exam 拆分为两个实体（发布后锁定）

产品设计文档（Part 4 §25）把"试卷/考试"混为一个概念（Exam Paper），但教师需要把同一份试卷同时发布给 A 班和 B 班，也可只给 A 班。因此把内容实体 **Paper**（组好的卷子）与按班实例 **Exam**（某班某次考试）拆成两个实体：Paper 通过 PaperQuestion 引用题目（N:M 共享引用），发布时生成 1:N 的 Exam；Paper 发布后锁定（draft → locked），避免改题影响已发布的考试。

**状态**：accepted

## 备选方案

- **单实体 + 复制快照**：只有一个 Exam，多班发布时复制题目快照。缺点是 N 个班产生 N 份重复题目数据，改一处需同步 N 处，也无法表达"试卷"这一可独立复用的内容。
- **两实体 + 共享引用（选定）**：Paper 只存题目引用（PaperQuestion），Exam 只引用 Paper 并绑定班级。一份 Paper 生成多个 Exam，改题只需改 Paper 一处。

## 后果

- Paper 发布后锁定（draft → locked），已发布试卷不可再改/删题，要改需复制新 Paper。
- 发布后删除拦截：被 Exam 引用的 Paper、被 locked Paper 引用的 Question，删除时返回 409。
- Exam 按班独立流转（published/in_progress/grading/completed/archived/cancelled），不物理删除，取消走 cancelled。
