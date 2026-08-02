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
ChemAI 支持的八种题型：
- **single_choice**：单项选择题
- **multi_choice**：多项选择题
- **true_false**：判断题
- **fill_blank**：填空题
- **short_answer**：简答题
- **essay**：论述题
- **calculation**：计算题
- **experiment**：实验题

### Difficulty（难度）
题目难度等级，1-5级：
- **1**：基础概念识记
- **2**：简单应用
- **3**：中等综合
- **4**：较难推理
- **5**：高难度创新

### Four-Dimension Review（四维审核）
AI生成题目的质量检测机制，四个维度：
1. **科学性**：化学知识准确性、方程式正确性、表述规范性
2. **难度匹配**：题目实际难度是否符合标注难度
3. **知识点覆盖**：题目是否准确考查目标知识点
4. **区分度**：题目是否能有效区分不同水平学生

审核结果：`{"pass": true/false, "issues": [...], "score": 0-100}`

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

**最后更新**：2026-08-02
