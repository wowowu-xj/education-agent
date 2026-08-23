## Context

当前项目已有 FastAPI 后端骨架、SQLAlchemy ORM 数据层、JWT 认证中间件。前端使用 Vanilla JS + Vue 3 CDN 模式，静态资源由 FastAPI 直接托管。四维审核概念已定义在 CONTEXT.md 中（四个维度、评分 0-100），但尚未落地为 API 和状态机。出题工作台页面不存在，教师端缺少统一入口。

## Goals / Non-Goals

**Goals:**
- 提供单文件 Vue 3 出题工作台页面，三个 Tab 覆盖手动命题、AI 生成、OCR 导入
- 实现四维审核的完整 REST API 和状态机
- 最小化新增依赖，复用现有 CDN 模式和 FastAPI 技术栈

**Non-Goals:**
- 本阶段不实现 AI 生成题目的实际推理逻辑（仅预留 Tab 界面和 API 接口）
- 本阶段不实现 OCR 导入的完整前端交互（仅预留 Tab 界面）
- 不实现审核引擎的实际 AI 评分算法（使用规则引擎占位，后续迭代接入 LLM）
- 不修改现有身份认证和组织层级 specs

## Decisions

### Decision 1: 单文件 Vue 3 组件 vs 多文件拆分

**选择**: 单文件 HTML 包含所有 Vue 3 组件逻辑。

**理由**: 项目使用 CDN 模式无构建工具，多文件拆分会导致 HTTP 请求增多且无模块化加载。单文件维护成本低，后续如需拆分可在引入构建工具时重构。

**替代方案**: 多文件 + ES modules — 浏览器兼容性和模块加载顺序管理成本高，与 CDN 模式冲突。

### Decision 2: 审核状态机实现方式

**选择**: 在 service 层实现显式状态机类 `ReviewStateMachine`，使用状态转换表（dict）定义合法转换。

**理由**: 显式状态机比 if-else 分支更易测试和维护，转换规则集中定义，新增状态只需加一行配置。service 层实现与现有数据范围隔离模式一致（见 organization-hierarchy spec）。

**替代方案**: 
- 数据库 ENUM + 应用层校验 — 规则分散在多个端点，容易遗漏
- 状态机库（transitions） — 引入新依赖，对四个状态来说过重

### Decision 3: 审核评分占位策略

**选择**: 使用规则引擎占位（随机评分 + 固定规则），通过环境变量 `REVIEW_ENGINE_MODE` 切换。

**理由**: LLM 驱动的真实审核评分需要模型调优和大量测试，不适合在第一版落地。规则占位保证 API 和状态机立即可测，后续替换为 LLM 引擎不改 API 契约。

**替代方案**: 直接接入 LLM — 评分质量不可控，调试困难，延迟高

### Decision 4: 前端路由

**选择**: 不出现在 FastAPI 路由，直接通过 Tab 组件在单页面内切换。

**理由**: 三个出题模式是同一工作流的三种入口，切换频率高，SFC 内 Tab 切换比页面跳转体验更好。

### Decision 5: 审核结果同步 vs 异步

**选择**: 同步提交审核任务，异步轮询结果。`POST /api/review/submit` 立即返回 review_id，前端每 3 秒轮询 `GET /api/review/{review_id}` 直到状态为 passed/rejected。

**理由**: 与项目已有的 OCR 任务轮询机制一致（见 CLAUDE.md）。LLM 审核可能需要 5-30 秒，同步等待会超时。

**替代方案**: WebSocket 推送 — 当前项目无 WebSocket 基础设施，过度设计

## Risks / Trade-offs

- **[风险] 单文件 Vue 组件过大** → 按 Tab 拆分 Vue 子组件在同一文件内定义，保持逻辑分区清晰；超过 500 行时再考虑拆分
- **[风险] 占位评分引擎无法真实反映题目质量** → 环境变量明确标注 `stub` 模式，UI 提示"审核引擎为占位模式"，避免误用
- **[风险] 轮询增加服务器负载** → 前端轮询间隔 3 秒，审核完成后停止轮询；后端 review 查询为简单主键索引，无性能瓶颈
- **[权衡] CDN 依赖外部服务** → 使用国内 CDN（unpkg.zhimg.com 或 bootcdn），KaTeX 首次加载约 200KB，后续浏览器缓存

## Open Questions

- AI 生成的 prompt 模板放在 `agent/prompts/question_generation/` 还是 `chem_skills/chemistry_exam/prompts/`？
- 审核评分各维度权重是否需要可配置（当前四维等权 25%）？
