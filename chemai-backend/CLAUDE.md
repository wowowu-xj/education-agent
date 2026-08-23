# ChemAI 后端项目行为准则

## 项目背景

**ChemAI（智辅化学）** 是一个AI驱动的中学化学教学辅助平台，为中国初中和高中化学教师、学生及家长提供智能化教学支持。

### 核心功能模块
- **AI Agent对话系统**：基于LangGraph的多角色智能对话（教师/家教/家长/管理员）
- **出题工作台**：支持教师自主命题、AI辅助生成题目、OCR导入试卷
- **题目质量评估**：科学性、难度匹配、知识点覆盖、区分度四维度质量检测
- **障碍诊断引擎**：识别学生学习障碍类型（概念理解/审题/表述）与迷思概念类别（化学平衡/氧化还原/摩尔计算/有机化学/化学用语/物构知识）
- **题库管理与考试生命周期**：从草稿→发布→进行中→批阅→完成→归档的完整流程
- **学生练习与错题本**：自适应练习推荐与个性化复习
- **家长端**：周报推送与学情跟踪

### 技术栈
- **后端**：Python 3.11+ / FastAPI / SQLAlchemy / SQLite
- **向量数据库**：ChromaDB
- **AI层**：LangGraph / 通义千问DashScope API
- **前端**：Vanilla JS + Vue 3 CDN
- **OCR**：阿里云文档智能（DocumentMind）

---

## 行为准则（4条核心原则）

### 1. 先思考再编码
- 开始实现前，明确陈述你的假设和设计思路
- 不确定时主动提问，而非猜测需求
- 对于复杂功能，先描述实现方案，等待确认后再动手

### 2. 简单优先
- 只写解决当前问题所需的最少代码
- 避免过度设计和提前优化
- 三行重复代码优于不成熟的抽象

### 3. 手术式修改
- 只触及必须修改的代码
- 匹配已有代码风格（命名、格式、注释）
- 不在修复bug时同时重构无关代码

### 4. 目标驱动执行
- 将任务转化为可验证的目标
- 完成后验证目标是否达成
- 对于多步骤任务，每步完成后确认再继续

---

## 项目特定规范

### 代码风格
- **所有代码注释和文档使用中文**
- Python代码遵循 **PEP 8** 规范
- 使用类型注解（Type Hints）提升代码可读性
- 函数和类必须包含中文docstring

### 数据库
- 使用 **SQLAlchemy ORM** 定义模型
- 模型文件放在 `app/models/`
- 迁移脚本由 **Alembic** 管理，放在 `alembic/versions/`
- 外键关系必须显式声明

### API设计
- 遵循 **RESTful** 设计原则
- 路由定义在 `app/api/` 按模块组织
- 请求/响应使用 Pydantic 模型验证
- 错误响应遵循统一格式：`{"error": "错误类型", "message": "详细说明"}`

### 测试策略
- 采用 **TDD（测试驱动开发）**
- 测试文件放在 `tests/` 目录，镜像源码结构
- 测试层级：
  - **L1 单元测试**：函数级别的纯逻辑测试
  - **L2 集成测试**：跨模块交互测试
  - **L3 Golden测试**：端到端真实场景测试（与baseline对比）

### 化学内容规范
- 化学方程式使用 **LaTeX** 格式：`$\ce{H2SO4}$` 或 `$$\ce{2H2 + O2 -> 2H2O}$$`
- 化学符号必须经过 **chemistry_parser** 模块校验
- 所有AI生成的化学内容须经 **化学方程式安全审核** 校验后方可输出

### AI Agent规范
- Agent定义在 `agent/` 目录
- 工具函数放在 `agent/tools/`，每个工具必须包含：
  - 函数签名（带类型注解）
  - 中文docstring（描述用途、参数、返回值）
  - 输入验证逻辑
- Prompt模板放在 `agent/prompts/`，使用Jinja2语法
- Agent必须通过 **Gateway** 模块进行护栏校验（内容安全、权限检查、速率限制）

---

## 标准开发流程（工具链）

### 思考层（规划与评审）
```bash
/office-hours      # 问题探讨与头脑风暴
/plan-ceo-review   # CEO视角的产品方案评审
/plan-eng-review   # 工程视角的技术方案评审
```

### 规格层（需求管理）
```bash
/opsx:propose      # 提出需求规格
/opsx:apply        # 应用已批准的规格
/opsx:archive      # 归档已完成的规格
```

### 实现层（TDD循环）
1. **RED**：编写失败的测试用例
2. **GREEN**：让Claude生成通过测试的最少代码
3. **REFACTOR**：重构代码，保持测试通过

### 质量层（分级测试）
```bash
# L1 单元测试
pytest tests/unit/

# L2 集成测试
pytest tests/integration/

# L3 Golden测试（与baseline对比）
pytest tests/golden/ --compare-baseline
```

### 流程层（标准工作流）
```bash
/review            # 代码审查
/cso               # 安全审查
/qa                # 质量保证检查
/ship              # 发布部署
/retro             # 复盘总结
/investigate       # 问题调查
```

### 骨架层（版本管理）
```bash
git checkout -b feature/xxx    # 创建功能分支
git commit -m "feat: xxx"      # 提交变更
git tag v1.0.0                 # 打标签
git merge feature/xxx          # 合并分支
git revert <commit-hash>       # 回滚变更
git push origin main           # 推送远程
```

---

## 特殊注意事项

### AI内容生成
- 所有AI生成的题目必须经过 **化学方程式安全审核** 校验
- 审核未通过的内容不得进入题库
- 审核结果必须记录在数据库（`review_logs` 表）

### 障碍诊断
- **障碍类型**（Barrier Type）与 **迷思概念类别**（Misconception Category）是正交关系：
  - 障碍类型回答"怎么错"：概念理解/审题/表述
  - 迷思概念类别回答"错在哪"：化学平衡/氧化还原/摩尔计算/有机化学/化学用语/物构知识
- 诊断结果必须同时包含两个维度

### 考试生命周期
- 考试状态转换必须严格遵循流程：
  ```
  draft → published → in_progress → grading → completed
                                           ↓
                                      archived
                                           ↓
                                      cancelled
  ```
- 状态转换必须记录操作人和时间戳

### OCR与任务轮询
- OCR任务采用 **异步轮询** 机制
- 前端每5秒轮询一次任务状态
- 任务失败时必须提供 **降级方案**（手动录入入口）

---

## 参考资源

- **项目文档**：`D:\化学\docs\`
- **设计文档**：Part 4 产品设计
- **领域词汇表**：`CONTEXT.md`
- **GraphQL Schema**：待定
- **API文档**：FastAPI自动生成（`/docs`）

---

**最后更新**：2026-08-02
