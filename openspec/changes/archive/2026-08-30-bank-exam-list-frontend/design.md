# 题库管理与考试列表前端 — 设计

## Context

出题工作台是单页 4 Tab 应用（`question-workbench.html`，Vue 3 CDN + Tailwind CDN + KaTeX CDN，零构建）。Tab 1 已实现并符合设计系统 36（Academic Catalyst：Oxford Blue + 暖纸 + 实验笔记主题），Tab 2/3/4 为静态 mock。

后端已归档的规格（`question-bank`、`exam-lifecycle`）定义了数据模型与状态机，实际路由为 `/api/questions`、`/api/question-sets`、`/api/papers`、`/api/exams`。设计文档 25 中的路径（`/api/exam-bank/*`、`/api/exam/*`）已过时，且其「单实体 Exam」模型已被后端拆分为 Paper（组卷）+ Exam（按班）两层。动机详见 proposal.md。

## Goals / Non-Goals

**Goals:**
- 让 Tab 2、Tab 4 具备真实闭环（列表/CRUD/发布/导出），视觉延续 Academic Catalyst。
- 补上两个使能端点，使前端无需 mock 即可跑通。

**Non-Goals:**
- 不实现 Tab 3 历史真题库（真题数据源未落地）。
- 不实现批量导入、学生作答链路（`in_progress`/`grading` 自动进入）。
- 不改动既有数据模型（无 Alembic 迁移）。

## Decisions

### D1. Tab 4 采用 Paper 视角

**选择**：Tab 4 列表数据源为 `GET /api/papers`（试卷），Exam 作为「已发布试卷」的次级展示层。

**理由**：教师出卷工作流的核心对象是 Paper（草稿 → 组卷 → 发布）；Exam 是发布的产物（按班实例），不适合作为主列表。设计文档 40 的「考试列表」语义上混用了 Paper 的「草稿」与 Exam 的「已发布」，这里以 Paper 为准。

**备选**：以 Exam 为主列表——被否决，因为 Exam 无「草稿」概念，无法承载组卷前的编辑态。

### D2. 复用 Vue 3 CDN + Academic Catalyst，否决 exam-v2.html 的 Material 3

**选择**：直接在现有 `question-workbench.html` 的 Vue 实例中扩展 Tab 2/4 的数据与交互，沿用 oxford/teal/paper 色板与 `.card-labnote`。

**理由**：`question-workbench-frontend` 规格已明确「SHALL NOT 用 Material 3」；`exam-v2.html` 原型是 Material 3 实现，仅参考其信息架构（左文件夹 + 右题目网格；试卷卡片 + 状态标签），不抄其样式。

### D3. 新增两个后端使能端点（最小化）

**选择**：新增 `GET /api/question-sets/{id}/questions`（列文件夹题目）与 `GET /api/classes`（班级列表）。

**理由**：前者是 Tab 2「右侧题目网格」的必要数据源（现有 `GET /{id}` 仅返回 `question_count`）；后者是 Tab 4 发布选班与考试状态展示（class_id → 班级名）的必要数据源。均无数据模型变更。

**备选**：前端在 `GET /api/questions` 全量列表上客户端过滤——被否决，因为无法表达「某题属于某文件夹」这一关系，且失去 sort_order 排序。

### D4. 班级列表范围为「教师任教班级」

**选择**：`GET /api/classes` 复用 `organization-hierarchy` 的「数据范围隔离」语义——普通教师通过 TeacherClassSubject 过滤为任教班级。

**理由**：与既有隔离规格一致；发布限制在任教班级是 v1 的合理默认（教师通常向其任教班级发布）。发布端点的 `school_id` 校验（403）仍然生效，作为第二道防线。

**Trade-off**：若未来需「向本校任意班级发布」，班级列表需扩展为「本校全部班级」，此处 v1 不做。

### D5. 考试状态按 paper 分组在客户端完成

**选择**：已发布试卷的「班级 + 考试状态」通过 `GET /api/exams`（全量）客户端按 `paper_id` 分组，再经 `GET /api/classes` 解析班级名。

**理由**：教师量级（几十场考试、几十个班）下客户端分组足够快；避免为了一次性展示新增后端 `paper_id` 过滤参数。

**Trade-off**：`/api/exams` 无 class_name，需一次额外的班级列表调用做名称解析；若数据量增长再补 `paper_id` 过滤 + 联表 class_name。

### D6. 状态标签中文 + 配色映射

统一查表（语义色沿用设计系统 36）：

| 状态 | 中文 | 配色 |
|------|------|------|
| Paper.draft | 草稿 | 中性（accent/muted） |
| Paper.locked | 已发布 | Teal |
| Exam.published / in_progress | 已发布 / 进行中 | Teal |
| Exam.grading | 批阅中 | 警告黄 |
| Exam.completed | 已完成 | 通过绿 |
| Exam.archived | 已归档 | 中性灰 |
| Exam.cancelled | 已取消 | 阻断红 |

### D7. 导出复用现有端点

**选择**：导出走 `GET /api/papers/{id}/export?format=html|docx&include_answer=...`，HTML 在新标签打开预览，DOCX 触发下载。

**理由**：后端 `render_html`/`render_docx` 已实现，前端仅做链接/按钮。

## Risks / Trade-offs

- [前端需二次解析 class_id → 班级名] → 缓存 `GET /api/classes` 结果为 id→name 映射，一次加载复用。
- [发布后 Exam 状态会随学生作答变化，前端为快照] → 每次进入 Tab 4 或展开已发布试卷时重新拉取 `/api/exams`。
- [加题入口的题目选择器若走语义召回，依赖 ChromaDB] → 提供结构化过滤（`/api/questions`）作为降级，语义召回失败不阻塞选择。

## Open Questions

（无——D1 的 Paper 视角已由用户拍板；其余决策均有明确依据，不影响规格与任务分解。）
