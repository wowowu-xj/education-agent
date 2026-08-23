# ChemAI 领域词汇表

本文档定义 ChemAI（智辅化学）平台的核心术语和概念，供开发团队、AI Agent 和文档撰写时参考。

---

## 核心实体

### Student（学生）
平台注册用户，具有练习、考试、查看诊断报告和错题本的权限。
- 关联：Class、Grade、Account

### Class（班级）
学生的组织单位，由一名或多名教师管理。
- 关联：Teacher、Student、School

### Teacher（教师）
具有出题、组卷、发布考试、批阅试卷、查看班级学情的权限。
- 关联：Class、School、Account

### Parent（家长）
绑定学生账号，可查看学生周报、学情分析和练习记录。
- 关联：Student、Account

### School（学校）
组织层级的顶层实体，包含多个年级和班级。
- 关联：Grade、Class、Teacher

### Grade（年级）
学校内的年级划分，如"初三"、"高一"。
- 关联：School、Class

### Account（账号）
统一登录账号，可关联教师、学生或家长身份。
- 属性：username、password_hash、role（teacher/student/parent/admin）

---

## 学习概念

### Barrier Type（障碍类型）
学生答题错误的三种分类维度，描述"怎么错"：
- **concept**：概念理解错误（对化学原理、定义的理解偏差）
- **reading**：审题错误（题目条件遗漏、误读）
- **expression**：表述错误（化学方程式书写不规范、计算过程不完整）

### Barrier Distribution（障碍分布）
某学生或班级在三种障碍类型上的错误比例分布，用于个性化诊断。
- 格式：`{"concept": 0.5, "reading": 0.3, "expression": 0.2}`

### Knowledge Point（知识点）
化学课程大纲中的知识单元，如"化学平衡常数"、"氧化还原反应"。
- 关联：Question、Exam Paper

### Diagnosis（诊断）
基于学生答题记录生成的学习障碍分析报告，包含障碍类型分布和迷思概念识别。
- 输出：Barrier Distribution + Misconception Category

### Adaptive Practice（自适应练习）
根据学生诊断结果智能推荐的练习题集，针对性训练薄弱环节。
- 推荐策略：优先覆盖高频障碍类型和迷思概念

---

## 内容实体

### Exam Paper（试卷）
包含若干题目的考试卷，具有生命周期状态。
- 属性：title、total_score、duration（分钟）、state

### Question（题目）
试卷或题库中的单个题目，包含题干、选项、答案、解析。
- 属性：type、difficulty、knowledge_points、standard_answer

### Question Set / Question Bank（题库）
按知识点、难度、题型组织的题目集合，供教师选题组卷。
- 索引维度：知识点、难度、题型、年份

### Weekly Report（周报）
每周自动生成的学生学情报告，推送给学生和家长。
- 内容：本周练习量、正确率、障碍分布变化、知识点掌握度

---

## 诊断概念

### Misconception Category（迷思概念类别）
学生化学学习中常见的六类系统性认知偏差，描述"错在哪"：
1. **化学平衡**：平衡移动方向判断错误、转化率计算错误
2. **氧化还原**：氧化剂还原剂混淆、电子转移数计算错误
3. **摩尔计算**：物质的量浓度换算错误、阿伏伽德罗常数应用错误
4. **有机化学**：同分异构体判断错误、有机反应类型混淆
5. **化学用语**：离子方程式书写错误、电子式结构式混淆
6. **物构知识**（物质结构与性质）：原子结构错误、化学键判断错误

### Barrier Type vs Misconception Category（正交关系）
两者是诊断的两个独立维度：
- **Barrier Type** 回答"怎么错"：概念理解/审题/表述
- **Misconception Category** 回答"错在哪"：化学平衡/氧化还原/摩尔计算/有机化学/化学用语/物构知识
- 示例：一道化学平衡题答错，可能是"概念理解障碍 + 化学平衡迷思"，也可能是"审题障碍 + 化学平衡迷思"

---

## 题目与考试概念

### Question Type（题目类型）
ChemAI 支持的九种题型：
- **single_choice**：单项选择题
- **multi_choice**：多项选择题
- **true_false**：判断题
- **fill_blank**：填空题
- **short_answer**：简答题
- **essay**：论述题
- **calculation**：计算题
- **experiment**：实验题
- **inference**：推断题

### Difficulty（难度）
题目难度等级，4 档：
- **easy**：简单
- **medium**：中等
- **hard**：困难
- **competition**：竞赛（仅手动录入，不做 AI 出题）

### Question Quality Assessment（题目质量评估）

AI 生成题目在通过方程式安全审核后，由 LLM 执行的题目级教学价值评估。四个维度：
1. **科学正确性**：化学知识准确性、表述规范性、无事实错误
2. **难度匹配**：题目实际难度是否符合标注难度
3. **知识点覆盖**：题目是否准确考查目标知识点
4. **区分度**：题目是否能有效区分不同水平学生

评估结果：`{"pass": true/false, "issues": [...], "score": 0-100}`

> **注意**：此题质量评估位于安全审核的**下游**。题目必须先通过 Chemical Equation Safety Audit 确保方程式无错误，再进行质量评估。两者是管道关系，不是并列关系。

---

## 审核引擎

### Chemical Equation Safety Audit（化学方程式安全审核）

位于 LLM 生成层与用户可见输出层之间的最后一道安全门。任何产生化学方程式的路径（AI 出题、方程式配平、对话辅导、实验模拟）都必须经过审核引擎校验。与 Question Quality Assessment 的区别：

- **安全审核**回答"方程式有没有错"——确定性算法，< 50ms，硬拦截
- **质量评估**回答"题目好不好"——LLM 判断，软评分

审核管道：
```
LLM 生成 → 化学式归一化 → 方程式安全审核 → 题目质量评估 → 入库/展示
                            │
                            ├── passed → 放行
                            └── blocked → 打回重生成
```

### Coefficient Balancing（系数配平审核）

维度 1。使用元素原子计数法逐元素验证方程式配平：对反应物侧和产物侧的每种元素分别统计原子总数，逐一比对。不检查电荷守恒，不做有机反应的完整配平。

- 判定标准：**100% 配平正确**（Hard Red Line，86 道确定性测试全部通过）
- 算法：剥离系数 → 展开括号 → 正则匹配元素符号和下标 → 累加 → 逐元素比较
- 状态：仅 `passed` 或 `blocked`（无 warning 中间状态）

### Reaction Conditions（反应条件审核）

维度 2。基于 14 类条件关键词规则库，检测方程式是否标注了必要的反应条件。

14 类条件：点燃、加热(△)、高温、催化剂、通电/电解、光照、加压/高压、一定条件、浓、稀、过量、足量、适量、高温高压。

- 判定逻辑：反应类型 → 条件映射表匹配 → 缺失则 `failed`（必须标注）或 `warning`（建议标注）
- 可检测矛盾条件组合（如浓+稀、过量+适量同时出现）
- 状态：`passed` / `warning` / `failed`

### Product Stability（产物稳定性审核）

维度 3。检测产物的化学合理性——不稳定产物自动分解、沉淀应标注状态、氧化还原产物与氧化剂强度匹配。

规则库覆盖：
- **气体逸出规则**：H₂CO₃ → CO₂↑ + H₂O、NH₄OH → NH₃↑ + H₂O
- **沉淀生成规则**：Ca²⁺ + CO₃²⁻ → CaCO₃↓ 等 8 组离子组合
- **氧化还原产物规则**：浓 H₂SO₄ → SO₂（非 H₂）、Fe + 弱氧化剂 → Fe²⁺（非 Fe³⁺）
- **特殊反应类型**：双水解、络合溶解、歧化反应、归中反应

- 检测方式：正则匹配 + 规则表，不涉及深度化学语义
- 已知局限：不判断浓/稀条件的不同产物路径，不验证沉淀溶解性表
- 状态：`passed` / `warning` / `failed`

### Molecular Structure（分子结构审核）

维度 4。校验化学式的书写格式规范性。

| 规则类 | 检测项 |
|--------|--------|
| 元素符号 | 首字母大写、第二字母小写（Fe 非 fe/FE） |
| 下标数字 | 数字在元素符号后、括号后跟下标 |
| 括号匹配 | 栈结构验证 (), [], {} 配对 |
| 离子电荷 | LaTeX 格式 `Fe^{3+}` 非 `Fe+3` |
| LaTeX 格式 | mhchem 标准语法 `$\ce{...}$` |

- 状态：`passed` / `failed`

### Audit Report（审核报告）

四维安全审核的结构化输出 JSON，格式：
```json
{
  "question_id": "q_20260804_001",
  "equation": "原始方程式",
  "audits": {
    "balance":   {"status": "passed|blocked", "message": "...", "detail": {"left_elements": {}, "right_elements": {}}},
    "condition": {"status": "passed|warning|failed", "message": "...", "conditions_found": [], "missing_conditions": []},
    "product":   {"status": "passed|warning|failed", "message": "...", "issues": []},
    "structure": {"status": "passed|failed", "message": "..."}
  },
  "overall_status": "passed|blocked",
  "overall_message": "综合判定描述"
}
```

综合判定：任一维度 `blocked` → 整体 `blocked`。`warning` 不触发拦截。

### Chemical Formula Normalization（化学式归一化）

审核引擎的前置处理步骤。将 LLM 输出中的非标准化学式格式统一为审核引擎可解析的标准形式：

1. 统一箭头：`→` → `\rightarrow`，`⇌` → `\rightleftharpoons`
2. 统一气体/沉淀符号：`↑` → `\uparrow`，`↓` → `\downarrow`
3. 裸化学式自动包装：检测无 `$...$` 包裹的化学式（H₂O、CO₂等约 50 个白名单），自动转换为 LaTeX 格式并 `$` 包裹
4. 词界保护：3 个以上连续小写字母视为英文单词，不触发化学式包装

### Hard Red Line（红线）

不可协商的安全约束。当前仅一项：**系数配平准确率 = 100%**。任何配平错误的方程式都意味着向学生输出错误知识，这是教学产品的底线。

违反红线的方程式触发 **HARD BLOCK**：无论如何不能输出给用户，触发重新生成并上报监控告警。

### Exam State（考试状态）
考试生命周期的七种状态：
- **draft**：草稿（教师编辑中）
- **published**：已发布（学生可见但未开始）
- **in_progress**：进行中（学生答题中）
- **grading**：批阅中（教师或AI批阅）
- **completed**：已完成（批阅结束，成绩已发布）
- **archived**：已归档（历史记录）
- **cancelled**：已取消（考试作废）

状态转换规则：`draft → published → in_progress → grading → completed → archived`

---

## Agent 概念

### Intent（意图）
Agent 识别的用户对话意图类型：
- **chat**：闲聊或咨询（如"化学平衡怎么学"）
- **navigate**：功能导航（如"我要出题"）

### Single Agent（单Agent）
基于 LangGraph `create_react_agent` 实现的单一智能体架构。
- 特点：工具调用 + 推理循环，适合中等复杂度任务

### Tool（工具）
Agent 可调用的外部函数，如 `search_question`、`create_exam`、`diagnose_student`。
- 规范：每个工具必须有类型注解和中文 docstring

### Persona（角色）
Agent 的四种角色设定，决定对话风格和权限范围：
- **teacher**：教师助手（出题、组卷、查看学情）
- **tutor**：学生家教（答疑、练习推荐、学习建议）
- **parent**：家长助手（周报解读、学情跟踪）
- **admin**：管理员（系统配置、数据管理）

### Guard State（护栏状态）
Agent 对话的安全检测状态：
- **safe**：内容安全，正常响应
- **blocked**：触发护栏规则，拒绝响应
- 检测维度：敏感词、越权操作、恶意注入

### Gateway（网关）
Agent 请求的统一入口，负责：
- 内容安全检测（Guard）
- 权限验证（Permission）
- 速率限制（Rate Limit）
- 日志记录（Logging）

---

## OCR 概念

### Upload Session（上传会话）
用户一次上传操作的会话标识，关联多张图片的 OCR 任务。
- 生命周期：创建 → 识别中 → 完成/失败

### Preview（预览）
OCR 识别结果的可视化预览界面，用户可修正识别错误。
- 功能：框选区域、编辑文本、调整题号

### Exam Import（试卷导入）
通过 OCR 将纸质试卷转换为结构化题目数据的流程。
- 步骤：上传图片 → OCR识别 → 预览修正 → 确认导入

### Grading（判卷）
通过 OCR 识别学生答卷，结合标准答案进行自动批阅。
- 支持：选择题自动判分、主观题AI辅助评分

### Fallback（降级）
OCR 识别失败或准确率过低时的备用方案。
- 策略：提示用户手动录入或重新上传清晰图片

### Task Polling（任务轮询）
前端每隔固定时间（如5秒）查询 OCR 任务状态的机制。
- 状态值：`pending`（排队中）、`processing`（识别中）、`completed`（完成）、`failed`（失败）

---

**最后更新**：2026-08-22
