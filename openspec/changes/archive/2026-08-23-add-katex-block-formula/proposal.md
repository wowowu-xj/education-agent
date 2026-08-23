## Why

出题工作台题干可能包含块级显示公式（如完整化学方程式 `$$\ce{2H2O ->[通电] 2H2 ↑ + O2 ↑}$$`），但现有 `question-workbench-frontend` 规格的「KaTeX 化学式渲染」要求只声明了行内 `$...$` 的渲染，块级 `$$...$$` 的行为未被规格约束。QA 验收发现块级公式曾因实现缺陷而不渲染，修复后应将该行为固化进规格，作为可回归验证的契约。

## What Changes

- 修改 `question-workbench-frontend` 规格：为「KaTeX 化学式渲染」要求新增一条「块级公式渲染」场景，声明 `$$...$$` 包裹的化学式 SHALL 渲染为独立居中的显示公式。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `question-workbench-frontend`: 为「KaTeX 化学式渲染」要求补充块级 `$$...$$` 显示公式场景，与既有行内 `$...$` 场景并列。

## Impact

- **规格文件**：`openspec/specs/question-workbench-frontend/spec.md`（delta 合并后新增一条场景）。
- **代码**：无新增改动——实现已就绪（`renderStem` 已通过 `katex.renderToString` 的 `displayMode` 支持 `$$...$$` 块级渲染），本变更为规格补全与回归契约固化。
- **依赖**：KaTeX CDN + mhchem（既有）。
