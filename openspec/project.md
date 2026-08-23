# ChemAI（智辅化学）

## 项目名称

**ChemAI（智辅化学）** — AI 驱动的中学化学教学辅助平台。

## 业务目标

为中国的初中和高中化学教师、学生及家长提供智能化教学支持，核心业务场景包括：

- **AI 智能对话**：基于多角色（教师/家教/家长/管理员）的化学教育对话助手，支持学习咨询与功能导航。
- **出题工作台**：支持教师自主命题、AI 辅助生成题目、OCR 纸质试卷导入。
- **题目质量评估**：对 AI 生成的题目进行科学性、难度匹配、知识点覆盖、区分度四维度质量检测，未通过审核的内容不得进入题库。
- **障碍诊断引擎**：从两个正交维度诊断学生学习问题 — 障碍类型（概念理解/审题/表述）回答"怎么错"，迷思概念类别（化学平衡/氧化还原/摩尔计算/有机化学/化学用语/物构知识）回答"错在哪"。
- **题库管理与考试生命周期**：完整的考试状态流转（草稿 → 已发布 → 进行中 → 批阅中 → 已完成 → 已归档/已取消）。
- **自适应练习与错题本**：基于诊断结果智能推荐练习题，针对性训练薄弱环节。
- **家长端**：亲子绑定、周报推送、学情跟踪。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| **语言** | Python | 3.11+ |
| **Web 框架** | FastAPI + Uvicorn | 0.109 / 0.27 |
| **ORM** | SQLAlchemy | 2.0 |
| **数据库迁移** | Alembic | 1.13 |
| **数据库** | SQLite（开发）/ PyMySQL（生产） | — |
| **数据验证** | Pydantic + pydantic-settings | 2.6 |
| **认证** | python-jose (JWT) + passlib (bcrypt) | 3.3 / 1.7 |
| **向量数据库** | ChromaDB | 0.4 |
| **AI 层** | LangGraph + 通义千问 DashScope API | — |
| **HTTP 客户端** | httpx + requests | — |
| **定时任务** | APScheduler | 3.10 |
| **OCR** | 阿里云文档智能（DocumentMind） | — |
| **浏览器自动化** | Playwright | ≥1.40 |
| **前端** | Vanilla JS + Vue 3 CDN | — |
| **测试** | pytest + pytest-asyncio | 9.1 / 1.4 |
| **类型检查** | mypy | 1.8 |

## 项目约束

### 代码与文档
- **所有代码注释和文档使用中文**。
- Python 代码遵循 **PEP 8** 规范，使用类型注解（Type Hints）。
- 函数和类必须包含中文 docstring。

### API 设计
- 遵循 **RESTful** 设计原则，路由按模块组织在 `app/api/`。
- 请求/响应使用 Pydantic 模型验证。
- 错误响应统一格式：`{"error": "错误类型", "message": "详细说明"}`。

### 数据库
- 使用 SQLAlchemy ORM，模型文件放在 `app/models/`。
- 迁移脚本由 Alembic 管理，外键关系必须显式声明。
- 核心实体和关系实体采用软删除（deleted_at），纯关系表采用硬删除。
- 所有业务表自动拥有 `created_at`、`updated_at` 字段。

### 安全
- JWT 无状态认证，access token 24 小时，refresh token 7 天，不实现 token 黑名单。
- 生产环境强制校验 JWT 密钥强度（≥32 字符），禁止使用默认占位密钥。
- 密码使用 bcrypt 单向哈希，明文永不落盘。
- 数据范围隔离在 service 层显式实现，不依赖数据库 row-level security。

### AI 内容
- 所有 AI 生成的题目必须经过化学方程式安全审核校验，审核结果须记录到 `review_logs` 表。
- 化学方程式使用 LaTeX 格式（如 `$\ce{H2SO4}$`）。
- Agent 必须通过 Gateway 模块进行护栏校验（内容安全、权限检查、速率限制）。

### 测试
- 采用 TDD（测试驱动开发），测试文件镜像源码结构。
- 三级测试体系：L1 单元测试 / L2 集成测试 / L3 Golden 测试。

### 架构原则
- 先思考再编码，简单优先，手术式修改，目标驱动执行。
- 三行重复代码优于不成熟的抽象。
- 只写解决当前问题所需的最少代码。

## 目录说明

```
教育agent/                          # 项目根目录
├── README.md                       # 项目简介
├── CLAUDE.md                       # 项目级 AI 行为准则（graphify 知识图谱规则）
├── .gitignore                      # Git 忽略规则
│
├── chemai-backend/                 # 🔥 后端主工程
│   ├── CLAUDE.md                   # 后端行为准则（4条核心原则 + 技术规范）
│   ├── CONTEXT.md                  # 领域词汇表（核心实体、学习概念、诊断概念等）
│   ├── requirements.txt            # Python 依赖清单
│   ├── pytest.ini                  # pytest 配置
│   ├── alembic.ini                 # Alembic 数据库迁移配置
│   ├── chemai.db                   # SQLite 开发数据库
│   │
│   ├── app/                        # 应用主代码
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── api/                    # API 路由（按模块组织）
│   │   ├── models/                 # SQLAlchemy ORM 模型
│   │   │   ├── base.py             # 基类（通用字段自动化）
│   │   │   ├── account.py          # 统一登录账号
│   │   │   ├── student.py          # 学生
│   │   │   ├── teacher.py          # 教师（含审批状态）
│   │   │   ├── parent.py           # 家长（独立认证）
│   │   │   ├── school.py           # 学校
│   │   │   ├── grade.py            # 年级
│   │   │   ├── class_.py           # 班级
│   │   │   ├── teacher_class_subject.py  # 教师任课关系
│   │   │   ├── student_parent_binding.py # 亲子绑定
│   │   │   └── events.py           # 事件/审计日志
│   │   ├── core/                   # 核心模块
│   │   │   ├── config.py           # 应用配置（环境变量驱动）
│   │   │   ├── database.py         # 数据库连接管理
│   │   │   ├── security.py         # 密码哈希与验证
│   │   │   ├── jwt.py              # JWT 签发与解析
│   │   │   └── enums.py            # 枚举定义
│   │   └── middleware/
│   │       └── auth.py             # JWT 认证中间件
│   │
│   ├── agent/                      # AI Agent 定义（LangGraph）
│   │   ├── tools/                  # Agent 工具函数
│   │   └── prompts/                # Prompt 模板（Jinja2）
│   │
│   ├── chem_skills/                # 化学领域技能模块
│   │   ├── chemistry_parser/       # 化学符号/方程式解析校验
│   │   ├── chemistry_exam/         # 考试/出题引擎
│   │   ├── chemistry_diagnosis/    # 障碍诊断引擎
│   │   ├── chemistry_improvement/  # 学习改进推荐
│   │   ├── chemistry_memory/       # 学习记忆与复习
│   │   └── chemistry_notification/ # 通知推送
│   │
│   ├── frontend/                   # 前端静态资源
│   │   ├── pages/                  # 页面
│   │   ├── css/                    # 样式
│   │   ├── js/                     # 脚本
│   │   └── m/                      # 移动端
│   │
│   ├── tests/                      # 测试用例（TDD）
│   │   ├── conftest.py             # pytest fixtures
│   │   ├── test_account.py         # 账户相关测试
│   │   ├── test_teacher.py         # 教师相关测试
│   │   ├── test_parent.py          # 家长相关测试
│   │   ├── test_jwt.py             # JWT 认证测试
│   │   ├── test_auth_middleware.py # 中间件测试
│   │   ├── test_middleware_streaming.py  # 流式中间件测试
│   │   └── test_data_integrity.py  # 数据完整性测试
│   │
│   ├── alembic/                    # Alembic 数据库迁移脚本
│   │   └── versions/               # 迁移版本文件
│   │
│   └── data/                       # 数据文件
│
├── docs/                           # 项目文档
│   └── agents/                     # Agent 协作规范
│       ├── domain.md               # 领域文档规范
│       ├── issue-tracker.md        # Issue 跟踪规范
│       └── triage-labels.md        # Triage 标签体系
│
├── openspec/                       # OpenSpec 规格驱动管理
│   ├── config.yaml                 # 配置文件（schema: spec-driven）
│   ├── project.md                  # 本文件 — 项目总览
│   ├── specs/                      # 正式规格文档
│   │   ├── identity-management/    # 身份管理规格
│   │   ├── jwt-authentication/     # JWT 认证规格
│   │   └── organization-hierarchy/ # 组织层级规格
│   └── changes/                    # 变更记录
│       └── archive/                # 已归档的变更
│
├── graphify-out/                   # Graphify 知识图谱输出
│   ├── graph.json                  # 知识图谱数据
│   ├── cache/                      # 查询缓存
│   └── wiki/                       # 代码库导航 wiki
│
└── .claude/                        # Claude Code 配置
    ├── CLAUDE.md                   # Claude 会话配置
    ├── skills/                     # 技能定义
    └── worktrees/                  # Git 工作树（临时）
```
