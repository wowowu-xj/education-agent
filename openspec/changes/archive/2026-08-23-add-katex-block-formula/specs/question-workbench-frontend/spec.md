## MODIFIED Requirements

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
