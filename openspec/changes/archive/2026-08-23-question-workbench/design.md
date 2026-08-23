## Context

见 proposal.md。四维安全审核引擎（four-dimension-audit-engine）已实现，前端直接消费其 AuditReport。本 change 只冻结词汇表 + 搭前端，不做题目质量评估。

## Goals / Non-Goals

**Goals:**
- 冻结题目领域词汇表（题型 9 种、难度 4 档、LLM 别名映射）
- 4 Tab + 子模式前端骨架，渲染四维审核徽章

**Non-Goals:**
- 题目质量评估（Question Quality Assessment，属于后续 change，与方程式审核是管道关系）
- OCR 完整流水线（本阶段仅占位上传区）
- 变体题完整实现（本阶段仅勾选框 + 蓝本题占位）

## Decisions

### Decision 1: 词汇表作为独立 capability

**选择**: question-vocabulary 与 question-workbench-frontend 拆为两个 spec。

**理由**: 词汇表被前端 chip、后端 enum、LLM prompt 三方引用，比"前端页面"更底层稳定。

### Decision 2: AI 生成难度只 3 档

**选择**: 前端不展示 competition。

**理由**: 文档 25 §1 明确"不做竞赛级出题"，竞赛仅手动录入。

### Decision 3: 审核徽章复用已实现引擎

**选择**: 前端渲染 four-dimension-audit-engine 的 AuditReport，不新造审核 API。

**理由**: 引擎已实现且同步 <50ms；题目质量评估是另一条独立管道。

### Decision 4: 变体题与知识点数据源暂用占位

**选择**: 变体题本阶段只留"基于真题变体"勾选框 + 蓝本题占位；知识点搜索 chip 先用静态占位数据。

**理由**: knowledge_graph.json 尚未生成，variant-browser 弹窗属于后续迭代。待知识图谱服务落地后接入 `GET /api/question/kps`。

### Decision 5: 技术栈采用 Vue 3 CDN，复用原型结构

**选择**: 页面用 Vue 3 CDN 实现，搬运 exam-v2.html 的结构/CSS 作为模板底子，交互重写为 Vue（v-show 切 Tab、v-for 渲染题目列表、v-model 绑定 chip）。

**理由**: 真页面的动态状态（题目列表、选项增减、OCR 轮询）用 Vue 响应式更省代码；Vue 3 CDN 仍是零构建，不违反"零构建步骤"原则。原型（vanilla JS）是生成工具的静态 mockup 产物，其结构/CSS 可复用，交互逻辑重写。

**替代方案**: 纯 vanilla JS 直接搬原型 — 静态部分快，但动态列表/表单/轮询需手写 DOM 操作，越到后面越乱。

## Open Questions

- 变体题（variant_qid）完整交互（蓝本题浏览弹窗）何时排期？
- 知识点搜索的数据源（knowledge_graph.json）何时由知识图谱服务生成？
