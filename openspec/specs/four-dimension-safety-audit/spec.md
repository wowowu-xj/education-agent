# four-dimension-safety-audit Specification

## Purpose
为 ChemAI 所有化学方程式输出提供四维度确定性安全审核，确保系数配平 100% 正确、反应条件完整、产物合理、分子结构规范。这是 LLM 生成内容在用户可见前的最后一道安全门。
## Requirements
### Requirement: 系数配平审核（维度 1）

系统 SHALL 使用元素原子计数法验证方程式配平：分别统计反应物侧和产物侧每种元素的原子总数，逐元素比对。

#### Scenario: 配平正确通过

- **WHEN** 输入 `2H_2 + O_2 \rightarrow 2H_2O`
- **THEN** 系统 SHALL 返回 `status: passed`
- **AND** detail 包含 `left_elements: {H:4, O:2}` 和 `right_elements: {H:4, O:2}`

#### Scenario: 未配平被拦截

- **WHEN** 输入 `Fe + O_2 \rightarrow Fe_2O_3`
- **THEN** 系统 SHALL 返回 `status: blocked`
- **AND** message SHALL 标注差异：`Fe: 左1 vs 右2, O: 左2 vs 右3`

#### Scenario: 含括号化学式配平

- **WHEN** 输入 `Ca(OH)_2 + CO_2 \rightarrow CaCO_3 + H_2O`
- **THEN** 系统 SHALL 正确展开 Ca(OH)₂ 中的括号后比较原子数
- **AND** 返回 `status: passed`

#### Scenario: 有机反应不强制配平

- **WHEN** 输入有机燃烧方程式如 `C_2H_5OH + O_2 \rightarrow CO_2 + H_2O`
- **THEN** 系统 SHALL 标记为 `status: warning`（有机反应通常不写完整配平式，需人工审核）

### Requirement: 反应条件审核（维度 2）

系统 SHALL 基于 14 类条件关键词规则库和反应类型-条件映射表检测反应条件标注完整性。

#### Scenario: 燃烧反应缺点燃条件

- **WHEN** 方程式包含燃烧物种（CH₄/C₂H₅OH/S/P/Fe）但未标注"点燃"
- **THEN** 系统 SHALL 返回 `status: failed`
- **AND** missing_conditions SHALL 包含 `"点燃"`

#### Scenario: 催化分解反应缺催化剂标注

- **WHEN** 方程式包含 H₂O₂/KClO₃/KMnO₄ 但未标注催化剂
- **THEN** 系统 SHALL 返回 `status: warning`
- **AND** message SHALL 建议标注催化剂

#### Scenario: 非燃烧反应无需条件

- **WHEN** 输入 `2H_2 + O_2 \rightarrow 2H_2O`（H₂ 不在 combustion_species 中）
- **THEN** 系统 SHALL 返回 `status: passed`

#### Scenario: 矛盾条件检测

- **WHEN** 同一方程式同时出现"浓"和"稀"关键词
- **THEN** 系统 SHALL 返回 `status: failed`
- **AND** message SHALL 标注矛盾条件组合

#### Scenario: 条件已正确标注

- **WHEN** 输入 `CH_4 + 2O_2 \xrightarrow{点燃} CO_2 + 2H_2O`
- **THEN** 系统 SHALL 检测到"点燃"条件，返回 `status: passed`

### Requirement: 产物稳定性审核（维度 3）

系统 SHALL 检测产物化学合理性：不稳定产物自动分解、沉淀生成、氧化还原产物与氧化剂强度匹配。

#### Scenario: 不稳定碳酸自动分解

- **WHEN** 产物包含 H₂CO₃
- **THEN** 系统 SHALL 返回 `status: failed`
- **AND** issues SHALL 提示 "H₂CO₃ = CO₂↑ + H₂O，不存在游离态"

#### Scenario: 沉淀产物检测

- **WHEN** 反应物含 Ca²⁺ 和 CO₃²⁻
- **THEN** 系统 SHALL 检测到沉淀规则匹配
- **AND** 若产物 CaCO₃ 未标注 ↓，issues SHALL 建议标注沉淀符号

#### Scenario: 浓硫酸氧化性产物验证

- **WHEN** 方程式为 `Cu + 2H_2SO_4(浓) \rightarrow ...`
- **THEN** 系统 SHALL 验证产物应为 SO₂（非 H₂）
- **AND** 若产物错误地写为 H₂，返回 `status: failed`

#### Scenario: 稳定产物直接通过

- **WHEN** 产物均为稳定化合物且无规则匹配
- **THEN** 系统 SHALL 返回 `status: passed`

### Requirement: 分子结构审核（维度 4）

系统 SHALL 校验化学式的书写格式规范性：元素符号大小写、括号匹配、离子电荷表示、LaTeX 格式。

#### Scenario: 元素符号格式正确

- **WHEN** 化学式使用正确大小写如 `Fe`、`Na`、`Cl`
- **THEN** 系统 SHALL 返回 `status: passed`

#### Scenario: 元素符号大小写错误

- **WHEN** 化学式出现 `fe`（应为 `Fe`）或 `FE`
- **THEN** 系统 SHALL 返回 `status: failed`
- **AND** message SHALL 标注格式错误的具体元素

#### Scenario: 括号不匹配

- **WHEN** 化学式出现未闭合的括号如 `Ca(OH_2`
- **THEN** 系统 SHALL 通过栈验证检测到不匹配
- **AND** 返回 `status: failed`

#### Scenario: 离子电荷格式正确

- **WHEN** 使用 LaTeX 格式 `Fe^{3+}` 或 mhchem `$\ce{Fe^3+}$`
- **THEN** 系统 SHALL 返回 `status: passed`

### Requirement: 综合判定与 AuditReport 输出

审核引擎 SHALL 汇总四个维度的审核结果，输出结构化 AuditReport。

#### Scenario: 全部通过

- **WHEN** 四个维度 status 均为 `passed`
- **THEN** overall_status SHALL 为 `passed`

#### Scenario: 任一维度 blocked

- **WHEN** 任一维度 status 为 `blocked`
- **THEN** overall_status SHALL 为 `blocked`
- **AND** overall_message SHALL 标注被拦截的维度

#### Scenario: 仅有 warning 不触发拦截

- **WHEN** 维度 1/3/4 为 `passed`，维度 2 为 `warning`
- **THEN** overall_status SHALL 为 `passed`
- **AND** overall_message SHALL 附带警告信息

### Requirement: 同步即时返回

审核引擎 SHALL 同步执行并即时返回结果（纯算法，不依赖 LLM 调用）。单方程式审核延迟 MUST < 50ms。

#### Scenario: 单方程审核延迟

- **WHEN** 调用审核引擎审核一个含 4 个化合物的方程式
- **THEN** 审核计算完成时间 SHALL < 50ms

### Requirement: HARD RED LINE 保障

系数配平审核 MUST 对 86 道确定性测试全部返回正确结果。任一测试失败意味着上线阻断。

#### Scenario: 86 道测试全部通过

- **WHEN** CI 管道运行 86 道确定性配平测试
- **THEN** 全部 86 道 MUST 通过
- **AND** 任一失败 SHALL 阻断部署

