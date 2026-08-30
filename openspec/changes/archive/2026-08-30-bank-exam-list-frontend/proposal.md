# 题库管理与考试列表前端

## Why

出题工作台页面（`question-workbench.html`）已实现 Tab 1「出题工作台」的完整视觉与交互，但 Tab 2「题库管理」、Tab 4「考试列表」仍是**静态 mock**（`BANK_ITEMS`、`EXAM_LIST` 硬编码，点击触发 `notImplemented` 弹窗）。设计文档 25/36/40 定义了这两个 Tab 的信息架构与视觉约束，但没有任何 OpenSpec 规格约束其真实行为——也没有任何 API 接线。同时设计文档 25 里的 API 路径（`/api/exam-bank/*`、`/api/exam/*`）已过时，后端实际采用 `Paper（组卷，draft/locked）+ Exam（按班实例，六态）` 两层模型，前端必须反映这一现实。

## What Changes

- **Tab 2「题库管理」接入真实 API**：文件夹（QuestionSet）列表 / 创建 / 重命名 / 删除（`is_preset` 不可删），选中文件夹后展示其中题目，加题 / 移题。
- **Tab 4「考试列表」按 Paper 视角重做**：列表数据源为试卷（Paper），卡片展示标题、题数、总分、状态（草稿/已发布）；支持创建、编辑、删除、发布（选班 → 生成 N 个 Exam → Paper 锁定）、导出（HTML/DOCX）；已发布试卷展示其关联考试（班级 + 考试状态）。
- **补两个后端使能端点**（前端闭环的必要依赖，当前后端缺失）：
  - `GET /api/question-sets/{id}/questions`：列出文件夹内题目（按 sort_order）。
  - `GET /api/classes`：教师任教的班级列表（供发布选班用）。
- **状态标签语义**：新增 Paper（draft/locked）与 Exam（六态）的中文标签 + Academic Catalyst 配色映射。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `question-workbench-frontend`: 新增 Tab 2「题库管理」与 Tab 4「考试列表（Paper 视角）」的前端行为需求（文件夹/题目/试卷的 CRUD 交互、发布与导出、状态标签、空态/加载态/错误态）。
- `question-bank`: 新增「文件夹内题目列表」端点需求（`GET /api/question-sets/{id}/questions`）。
- `organization-hierarchy`: 新增「班级列表」端点需求（`GET /api/classes`，按教师任教班级过滤）。

## Impact

- **前端**：`chemai-backend/frontend/pages/question-workbench.html`（Tab 2 / Tab 4 区块重写，接入真实 API；沿用现有 Academic Catalyst 视觉与 Vue 3 CDN 结构）。
- **后端**：`app/api/question_sets.py`（新增 list-questions 端点）、`app/api/classes.py`（新增班级列表端点，复用 `get_current_teacher` 依赖与任课关系过滤）。
- **数据模型**：无迁移（复用 QuestionSet / QuestionSetItem / Paper / PaperQuestion / Exam 现有表结构）。
- **不触及**：Tab 3「历史真题库」（真题库数据源与向量检索尚未落地，留待后续 change）、批量导入题目、学生作答链路（`in_progress`/`grading` 的自动进入）。
