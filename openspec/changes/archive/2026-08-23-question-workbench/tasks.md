## 1. 词汇表冻结

- [x] 1.1 更新 CONTEXT.md：八种题型 → 九种（+inference）、难度 1-5 → 4 档
- [x] 1.2 校验 question-vocabulary spec 通过

## 2. 前端骨架

- [x] 2.1 搬运 exam-v2.html 至 frontend/pages/，复用其结构作为 Vue 模板底子
- [x] 2.2 交互重写为 Vue：Tab/子模式切换（v-show）、题型 chip（v-model 多选）

## 3. AI 生成面板

- [x] 3.1 题型 chip（5 种）+ 难度下拉（3 档）+ 知识点搜索（暂用静态占位数据）
- [x] 3.2 变体勾选框 + 蓝本题占位
- [x] 3.3 生成按钮 + 生成逻辑（当前 mock 数据，生成 API 落地后接入）

## 4. 题目卡片与审核徽章

- [x] 4.1 题目卡片列表（KaTeX 渲染）
- [x] 4.2 AuditReport 四维徽章（passed/warning/blocked 三态）

## 5. 手动录入 / OCR 面板

- [x] 5.1 手动录入表单（9 种题型、4 档难度）
- [x] 5.2 OCR 上传区（占位）

## 6. 收尾

- [x] 6.1 静态文件挂载 + 手动验证
- [x] 6.2 openspec validate question-workbench

## 7. 代码审查修复

- [x] 7.1 对齐 mock 状态词与引擎枚举：`q_003` 的 `product.status` 由 `blocked` 改为 `failed`（引擎 `ProductStatus` 仅含 passed/warning/failed）
- [x] 7.2 警告色 token 对齐 spec：`warn` 由深棕 `#8a5a00` 改为警告黄
- [x] 7.3 化学式 LaTeX 化：`BANK_ITEMS` 第二条 `excerpt` 的 Unicode 上下标改为 `\ce` 写法
- [x] 7.4 注释中文化：三处英文 HTML 注释改为中文
- [x] 7.5 状态→样式映射收拢：`auditIcon`/`auditBadgeClass`/`difficultyBadgeClass` 三处 if 级联改为查表
- [x] 7.6 `submitManual` 四维 `audit` 由 `DIM_ORDER` 派生，消除硬编码重复
- [x] 7.7 静态白名单补充中文注释（说明 `/m/`=移动端学生/家长页面等，消除神秘命名）
- [x] 7.8 无 `@click` 处理器的死按钮加 `@click` 占位提示（导出/新建目录/查看详情/创建考试/OCR 选择文件）
