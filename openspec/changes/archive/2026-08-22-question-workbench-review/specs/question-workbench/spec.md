## Purpose

为教师提供统一的出题工作台页面，支持手动命题、AI 辅助生成题目、OCR 导入试卷三种出题方式，并在页面中实时渲染化学公式。

## ADDED Requirements

### Requirement: Tab 切换出题模式

页面 SHALL 提供三个 Tab 页签：手动命题、AI 生成、OCR 导入。用户切换 Tab 时 SHALL 展示对应的操作界面，无需整页刷新。

#### Scenario: 默认显示手动命题 Tab

- **WHEN** 教师首次访问出题工作台页面
- **THEN** 系统 SHALL 默认激活"手动命题"Tab
- **AND** 显示题目表单（题型选择、题干输入、选项编辑、答案设置、知识点标签）

#### Scenario: 切换到 AI 生成 Tab

- **WHEN** 教师点击"AI生成"Tab
- **THEN** 系统 SHALL 切换至 AI 辅助生成界面
- **AND** 显示生成条件输入区（知识点、难度、题型、题目数量）
- **AND** 其他 Tab 内容 SHALL 隐藏

#### Scenario: 切换到 OCR 导入 Tab

- **WHEN** 教师点击"OCR导入"Tab
- **THEN** 系统 SHALL 切换至 OCR 导入界面
- **AND** 显示图片上传区域和识别结果预览区

### Requirement: 化学公式 KaTeX 实时渲染

页面 SHALL 使用 KaTeX 渲染所有化学公式。题干、选项、解析中的 LaTeX 化学公式（如 `$\ce{H2SO4}$`）MUST 实时渲染为可视化的化学式。

#### Scenario: 题干中输入化学公式

- **WHEN** 教师在题干输入框中输入 `$\ce{2H2 + O2 -> 2H2O}$`
- **THEN** 系统 SHALL 在预览区实时渲染为可视化化学方程式

#### Scenario: 选项中的化学公式渲染

- **WHEN** 题目选项包含 LaTeX 化学公式标记
- **THEN** 系统 SHALL 在每个选项中独立渲染化学公式

#### Scenario: 混合文本与公式

- **WHEN** 题目内容同时包含普通文本和化学公式（如"下列物质中，$\ce{NaOH}$ 与 $\ce{HCl}$ 反应的产物是"）
- **THEN** 系统 SHALL 正确渲染混合内容，文本和公式样式协调一致

### Requirement: 手动命题表单

手动命题 Tab SHALL 提供完整的题目编辑表单，包含题型选择器、题干编辑器、选项编辑器（选择题）、答案设置、解析编辑器、知识点标签、难度选择。

#### Scenario: 选择题型

- **WHEN** 教师从题型下拉框中选择"单项选择题"
- **THEN** 系统 SHALL 显示 4 个选项输入框
- **AND** 显示正确答案单选按钮

#### Scenario: 切换到填空题

- **WHEN** 教师切换题型为"填空题"
- **THEN** 系统 SHALL 隐藏选项编辑区
- **AND** 显示填空答案输入框

#### Scenario: 保存题目草稿

- **WHEN** 教师填写题目信息并点击"保存草稿"
- **THEN** 系统 SHALL 将题目状态设为 draft
- **AND** 提示"草稿已保存"

#### Scenario: 提交审核

- **WHEN** 教师完成题目编辑并点击"提交审核"
- **THEN** 系统 SHALL 调用四维审核 API
- **AND** 题目状态 SHALL 变更为 pending_review

### Requirement: Tailwind CSS 响应式布局

页面 SHALL 使用 Tailwind CSS 实现响应式布局，在桌面端和平板端均可正常使用。

#### Scenario: 桌面端布局

- **WHEN** 视口宽度 ≥ 1024px
- **THEN** 系统 SHALL 显示双栏布局（左侧表单区，右侧预览区）

#### Scenario: 平板端布局

- **WHEN** 视口宽度 < 1024px
- **THEN** 系统 SHALL 切换为单栏布局，预览区移至表单下方

### Requirement: 前端技术栈约束

页面 MUST 使用 Vue 3 CDN、Tailwind CSS CDN、KaTeX CDN 实现，不依赖构建工具。所有静态资源 SHALL 放在 `chemai-backend/frontend/` 目录下由 FastAPI 直接托管。

#### Scenario: CDN 加载 Vue 3

- **WHEN** 页面在浏览器中加载
- **THEN** 系统 SHALL 通过 CDN 加载 Vue 3 全局构建版本
- **AND** 无需 npm install 或打包步骤

#### Scenario: CDN 加载 Tailwind CSS

- **WHEN** 页面在浏览器中加载
- **THEN** 系统 SHALL 通过 CDN 加载 Tailwind CSS
- **AND** 样式类在 HTML 中直接可用

#### Scenario: CDN 加载 KaTeX

- **WHEN** 页面检测到 LaTeX 公式标记
- **THEN** 系统 SHALL 通过 CDN 加载 KaTeX 的 CSS 和 JS
- **AND** 调用 KaTeX 渲染引擎处理公式
