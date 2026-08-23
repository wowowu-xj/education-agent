# question-workbench-frontend Specification

## Purpose
出题工作台前端页面，教师出题与题库管理的统一入口。单页 4 Tab 结构，Tab 1 内含三种出题子模式。视觉遵循设计系统 36（Academic Catalyst：Oxford Blue + 暖纸 + 实验笔记主题）。
## Requirements
### Requirement: 四 Tab 结构

页面 SHALL 提供 4 个 Tab：出题工作台、题库管理、历史真题库、考试列表。切换 Tab 时 SHALL 显示对应内容，无需整页刷新。

#### Scenario: 默认激活出题工作台

- **WHEN** 教师首次访问页面
- **THEN** 系统 SHALL 默认激活"出题工作台"Tab

#### Scenario: Tab 切换

- **WHEN** 教师点击任一 Tab
- **THEN** 系统 SHALL 隐藏其余 Tab 内容并显示目标内容
- **AND** 当前激活 Tab SHALL 有下划线指示

### Requirement: 出题子模式

Tab 1 出题工作台 SHALL 提供 3 种子模式：AI 生成（默认）、手动录入、OCR 导入。

#### Scenario: 默认 AI 生成

- **WHEN** 教师进入出题工作台 Tab
- **THEN** 系统 SHALL 默认激活"AI 生成"子模式

#### Scenario: 子模式切换

- **WHEN** 教师点击"手动录入"或"OCR 导入"
- **THEN** 系统 SHALL 切换至对应界面

### Requirement: 题型 chip 选择器

AI 生成子模式 SHALL 提供 5 个多选 chip：选择题、填空题、计算题、实验题、推断题。

#### Scenario: chip 集对齐词汇表

- **WHEN** 渲染题型 chip
- **THEN** 系统 SHALL 显示 5 种 AI 题型，SHALL NOT 出现"方程式配平"

#### Scenario: 多选

- **WHEN** 教师点击多个 chip
- **THEN** 系统 SHALL 允许多选，选中 chip 高亮

### Requirement: 难度下拉

AI 生成子模式的难度下拉 SHALL 提供 3 档：简单、中等、困难。

#### Scenario: 不展示竞赛档

- **WHEN** 教师展开难度下拉
- **THEN** 系统 SHALL 显示 easy/medium/hard 三档，SHALL NOT 显示 competition

#### Scenario: 不展示难度系数

- **WHEN** 渲染难度控件
- **THEN** 系统 SHALL NOT 使用 P 值系数（如 0.8-1.0）表示难度

### Requirement: 变体模式占位

AI 生成子模式 SHALL 提供"基于真题变体"勾选框，勾选后可指定蓝本题（占位）。

#### Scenario: 勾选变体模式

- **WHEN** 教师勾选"基于真题变体"
- **THEN** 系统 SHALL 显示蓝本题选择占位区（完整蓝本题浏览弹窗后续实现）

### Requirement: 审核徽章渲染

题目卡片 SHALL 渲染四维安全审核引擎的 AuditReport 徽章，四个维度分别展示状态。

#### Scenario: 四维徽章

- **WHEN** 生成题目返回 AuditReport
- **THEN** 系统 SHALL 展示 4 个维度徽章（系数/条件/产物/结构）

#### Scenario: 三态颜色

- **WHEN** 维度状态为 passed / warning / blocked
- **THEN** 徽章 SHALL 分别使用 通过绿 / 警告黄 / 阻断红
- **AND** overall_status = blocked 的题目 SHALL 在卡片上显著标识为不可用

### Requirement: KaTeX 化学式渲染

页面 SHALL 使用 KaTeX（含 mhchem）渲染题目中的 LaTeX 化学式。

#### Scenario: 题干渲染

- **WHEN** 题目正文包含 `$...$` 包裹的化学式
- **THEN** 系统 SHALL 渲染为可视化化学式（上下标、箭头、反应条件）

#### Scenario: 混合文本与公式

- **WHEN** 内容同时包含普通文本与化学式
- **THEN** 系统 SHALL 正确渲染混合内容，文本与公式协调

#### Scenario: 块级公式渲染

- **WHEN** 题目正文包含 `$$...$$` 包裹的化学方程式
- **THEN** 系统 SHALL 渲染为独立居中的显示公式（display math），与正文分行展示
- **AND** 显示公式 SHALL 支持上下标、箭头与反应条件（如 `->[通电]`）

### Requirement: 前端技术栈约束

页面 MUST 使用 Vue 3 CDN + Tailwind CSS CDN + KaTeX CDN，无构建步骤。静态资源 SHALL 位于 `chemai-backend/frontend/`，由 FastAPI 直接托管。

#### Scenario: 无构建加载

- **WHEN** 页面在浏览器加载
- **THEN** 系统 SHALL 通过 CDN 加载 Vue 3 / Tailwind / KaTeX
- **AND** 无需 npm install 或打包

### Requirement: 设计系统一致性

页面视觉 SHALL 遵循设计系统 36（Academic Catalyst），而非 Material 3 风格。

#### Scenario: 主色调

- **WHEN** 渲染按钮、Tab 下划线等强调元素
- **THEN** 系统 SHALL 使用 Oxford Blue 而非 Material primary-container

#### Scenario: 实验笔记主题

- **WHEN** 渲染出题工作台内容区
- **THEN** 系统 SHALL 应用暖纸背景、实验笔记卡片（左侧红色边距线）

