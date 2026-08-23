## Purpose

将化学方程式字符串解析为结构化的反应物和产物列表，作为四维审核引擎的共享前置步骤。

## ADDED Requirements

### Requirement: 方程式分隔符解析

系统 SHALL 支持三种分隔符拆分反应物与产物：`→`、`=`、`->`，按优先级匹配。

#### Scenario: LaTeX 箭头分隔

- **WHEN** 输入 `2H_2 + O_2 \rightarrow 2H_2O`
- **THEN** 系统 SHALL 拆分为反应物 `["2H_2", "O_2"]` 和产物 `["2H_2O"]`

#### Scenario: ASCII 箭头分隔

- **WHEN** 输入 `2H2 + O2 -> 2H2O`
- **THEN** 系统 SHALL 识别 `->` 并正确拆分

#### Scenario: 等号分隔

- **WHEN** 输入 `2H2 + O2 = 2H2O`
- **THEN** 系统 SHALL 识别 `=` 并正确拆分

#### Scenario: 无分隔符时返回错误

- **WHEN** 输入字符串不包含任何有效分隔符
- **THEN** 系统 SHALL 返回解析错误 `parse_error`

### Requirement: 化合物拆分与括号保护

系统 SHALL 按 `+` 号拆分化合物，同时保护括号内的 `+` 号不被误拆。

#### Scenario: 简单拆分

- **WHEN** 反应物为 `2NaOH + H_2SO_4`
- **THEN** 系统 SHALL 拆分为 `["2NaOH", "H_2SO_4"]`

#### Scenario: 括号保护

- **WHEN** 化合物包含离子式如 `[Cu(NH_3)_4]^{2+} + 2OH^-`
- **THEN** 系统 SHALL 跟踪括号嵌套深度，仅在深度为 0 时遇 `+` 才拆分

### Requirement: 系数剥离

系统 SHALL 从化合物字符串中剥离前导数字作为系数，余下部分作为化学式。

#### Scenario: 有系数化合物

- **WHEN** 化合物为 `2H_2O`
- **THEN** 系统 SHALL 返回 `coefficient=2, formula="H_2O"`

#### Scenario: 无系数化合物

- **WHEN** 化合物为 `NaCl`
- **THEN** 系统 SHALL 返回 `coefficient=1, formula="NaCl"`

### Requirement: 括号展开

系统 SHALL 递归处理化学式中的括号——将 `(原子团)n` 格式展开为各元素的原子数乘以 n。

#### Scenario: 单层括号展开

- **WHEN** 化学式为 `Ca(OH)_2`
- **THEN** 系统 SHALL 展开 OH×2 得到 O:2, H:2，加上 Ca:1

#### Scenario: 多层嵌套括号

- **WHEN** 化学式含嵌套括号如 `Fe_2(SO_4)_3`
- **THEN** 系统 SHALL 先展开外层 (SO₄)₃ 再展开内层，得到正确原子数

### Requirement: 元素符号正则匹配

系统 SHALL 使用正则 `[A-Z][a-z]?` 匹配元素符号，后跟可选下标数字。

#### Scenario: 单字母元素

- **WHEN** 化学式为 `H_2O`
- **THEN** 系统 SHALL 匹配 H:2, O:1

#### Scenario: 双字母元素

- **WHEN** 化学式为 `Fe_2O_3`
- **THEN** 系统 SHALL 匹配 Fe:2, O:3（而非 F 和 e 分别匹配）

#### Scenario: 带下标数字

- **WHEN** 化学式为 `C_6H_{12}O_6`
- **THEN** 系统 SHALL 正确解析 LaTeX 下标 `_{12}` 中的数字 12
