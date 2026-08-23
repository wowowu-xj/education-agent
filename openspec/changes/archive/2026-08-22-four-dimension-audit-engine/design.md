## Context

参见 proposal.md。CONTEXT.md 已更新领域模型，文档 26 提供了完整的算法设计和审核报告结构。现有项目中 `chem_skills/chemistry_parser/` 和 `chem_skills/chemistry_audit/` 目录均为空（仅 .gitkeep），`app/api/` 尚无审核相关路由。

## Goals / Non-Goals

**Goals:**
- 实现文档 26 定义的四维安全审核引擎：系数配平、反应条件、产物稳定性、分子结构
- 化学式归一化前置管道
- 同步即时返回的审核 API（`GET /api/audit/equation`）
- 86 道确定性配平测试 100% 通过（HARD RED LINE）

**Non-Goals:**
- 不做 LLM 驱动的题目质量评估（Question Quality Assessment，属于后续 change）
- 不做审核状态机/异步轮询（纯算法 < 50ms，不需要）
- 不做电荷守恒检查（仅原子守恒）
- 不做有机反应的完整配平

## Decisions

### Decision 1: 模块拆分 — 归一化、解析器、审核器三层

**选择**: 三个独立模块，单向依赖管道。

```
chemistry_parser    →  chemistry_audit.parser    →  chemistry_audit.{balance,conditions,stability,structure}
    (归一化)               (方程式解析)                   (四维审核)
```

**理由**: 归一化解决"格式统一"问题，解析器解决"结构化"问题，审核器解决"校验"问题。三层各司其职，可独立测试、独立替换。

**替代方案**: 合并到一个大模块 — 耦合度高，其中一步的修改可能影响全部。

### Decision 2: 规则数据外置为 JSON

**选择**: 14 条件关键词、沉淀规则表、氧化还原产物规则以 JSON 文件存放在 `chem_skills/chemistry_audit/rules/`。

**理由**: 规则是化学知识，不是算法逻辑。JSON 格式方便化学教师 review 和更新，也便于参数化测试生成。

**替代方案**: 规则硬编码在 Python 字典中 — 更新需要改代码、跑测试，对非开发人员不友好。

### Decision 3: 审核引擎单例模式

**选择**: AuditEngine 类以模块级单例暴露，通过 `audit_equation()` 快捷函数调用。

**理由**: 引擎无状态、无 IO，纯计算函数。单例避免重复实例化开销，与文档 26 的全局实例设计一致。pytest 中可直接导入函数测试，无需 mock。

**替代方案**: 每次调用实例化 — 无实际收益，增加 boilerplate。

### Decision 4: 同步 API，不做异步状态机

**选择**: `GET /api/audit/equation?eq=...` 同步即时返回 AuditReport JSON。

**理由**: 文档 26 明确审核延迟 < 50ms。异步 poll 模式是为 OCR（秒级延迟）设计的，审核引擎不需要。同步 API 更简单，前端可直接在保存题目时实时调用，获得即时反馈。

**替代方案**: POST submit + GET poll — 过度设计，额外增加 pending/reviewing 状态管理开销。

### Decision 5: 独立 API 端点 vs 嵌入出题流程

**选择**: 提供独立的 `GET /api/audit/equation` 端点，同时审核函数也可被其他模块直接导入调用。

**理由**: 独立端点解耦审核引擎与出题工作台——Agent 工具、方程式配平工具、实验模拟都可以直接调用同一个 API。审核函数同时暴露为 Python 函数，出题服务可在生成 pipeline 中直接调用，不经过 HTTP。

### Decision 6: 86 道测试数据管理

**选择**: 手写 JSON/YAML 测试数据文件放在 `tests/data/` 目录，pytest 参数化加载。

**理由**: 测试数据是化学领域知识资产，应独立于测试逻辑。参数化加载让新增测试只加数据不改代码。后续化学教师可独立贡献测试用例。

**替代方案**: 测试数据内嵌在 test 函数的 `@pytest.mark.parametrize` 中 — 86 道题会让测试文件过长，且数据与逻辑混杂。

## Risks / Trade-offs

- **[风险] 正则匹配无法覆盖所有化学式变体** → 分子结构审核的局限性在文档 26 §5.2 中已明确，LLM 补充审核 prompt 在后续迭代中引入
- **[风险] LaTeX 下标 `_{12}` 解析复杂度高** → parser 优先支持 `_2` 单数字下标格式，`_{12}` 多字符下标作为 phase 2 增强
- **[风险] 86 道测试数据编写需要化学专业知识** → 从文档 26 的 4 个示例开始 + 规则反向生成，后续由化学教师补充
- **[权衡] 条件审核召回率 ≥ 80% 不是 100%** → 对不确定的 case 返回 `warning` 而非 `blocked`，不阻断用户但留痕，由 LLM 补充判断
- **[权衡] 稳定性审核仅用正则 + 规则表** → 深层次化学语义（浓/稀酸的不同产物）由 LLM 补充

## Open Questions

- 规则 JSON 文件是否需要版本号？（化学知识会更新——教材改版、新课标调整）
- `chemistry_parser` 的裸化学式白名单应该基于现有代码中的列表还是重新整理？
