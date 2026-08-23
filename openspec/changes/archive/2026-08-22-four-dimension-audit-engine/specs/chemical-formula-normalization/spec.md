## Purpose

将 LLM 输出的非标准化学式格式统一转换为审核引擎可解析的标准形式，作为四维安全审核的前置处理管道。

## ADDED Requirements

### Requirement: 统一 LaTeX 箭头符号

系统 SHALL 扫描 `$...$` 包裹的 LaTeX 片段，将 Unicode 箭头统一转换为 LaTeX 命令。

#### Scenario: Unicode 箭头转 LaTeX 命令

- **WHEN** LaTeX 片段包含 `→`
- **THEN** 系统 SHALL 替换为 `\rightarrow`

#### Scenario: 可逆箭头转 LaTeX 命令

- **WHEN** LaTeX 片段包含 `⇌`
- **THEN** 系统 SHALL 替换为 `\rightleftharpoons`

#### Scenario: 气体/沉淀符号转 LaTeX 命令

- **WHEN** LaTeX 片段包含 `↑` 或 `↓`
- **THEN** 系统 SHALL 分别替换为 `\uparrow` 和 `\downarrow`

### Requirement: 裸化学式自动包装

系统 SHALL 检测文本中未被 `$...$` 包裹的常见化学式，自动将数字下标转为 LaTeX 格式并用 `$` 符号包裹。

#### Scenario: 常见化学式自动包裹

- **WHEN** 文本包含 `H2O`（在白名单中）且未被 `$` 包裹
- **THEN** 系统 SHALL 转换为 `$H_2O$`

#### Scenario: 复合化学式下标转换

- **WHEN** 文本包含 `Fe2O3`
- **THEN** 系统 SHALL 转换为 `$Fe_2O_3$`

#### Scenario: 英文单词不被误包装

- **WHEN** 文本包含 3 个以上连续小写字母的字符串（如 `water`、`chemical`）
- **THEN** 系统 SHALL 不触发化学式包装

#### Scenario: 已有 LaTeX 包裹的化学式不重复处理

- **WHEN** 文本已包含 `$H_2O$` 格式的化学式
- **THEN** 系统 SHALL 跳过，不重复包装

### Requirement: 白名单驱动

归一化模块 SHALL 维护一个约 50 个常见化学式的白名单，仅对白名单中的化学式触发自动包装。

#### Scenario: 白名单命中时触发

- **WHEN** 文本匹配列表中的化学式（如 H2O、CO2、NaCl、Fe2O3）
- **THEN** 系统 SHALL 自动包装为 LaTeX 格式

#### Scenario: 非白名单化学式不触发

- **WHEN** 文本包含白名单之外的化学式（如生僻化合物）
- **THEN** 系统 SHALL 保持原文不变
