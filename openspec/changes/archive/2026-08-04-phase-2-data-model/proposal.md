# Phase-2 数据模型与认证体系实现提案

## 问题陈述

ChemAI 后端已完成目录结构和文档初始化（phase-1），现需实现数据库模型层和认证中间件（phase-2），为后续 API 开发提供数据基础。

当前状态：
- `chemai-backend/` 目录结构已建立
- CLAUDE.md、CONTEXT.md、requirements.txt 已就绪
- 分支 `phase-2/data-model` 已从 main 切出
- 设计文档已完成（23权限分级、34数据模型、35API设计）

缺失：
- 无任何 SQLAlchemy 模型文件
- Alembic 未配置
- 认证中间件未实现
- 核心枚举类型未定义

## 目标

实现 9 个核心数据表和认证基础设施，支持：
- 六角色体系（admin/教务管理员/学科组长/teacher/student/parent）
- 组织架构（学校→年级→班级→学生）
- 任课关系和家长绑定
- JWT 认证中间件（最小化白名单）

**非目标**：
- 考试、题目、诊断等业务模型（Phase 3+）
- API 路由实现
- 前端集成

## 范围

### 包含
- 9 张核心表：Account, Teacher, Student, Parent, School, Grade, Class, TeacherClassSubject, StudentParentBinding
- Base 基类（created_at/updated_at/deleted_at）
- TeacherRole 枚举
- 密码哈希工具（passlib bcrypt）
- JWT 中间件（白名单：`/api/auth/`, `/api/parent/login`, `/docs`, `/health`）
- Alembic 初始迁移
- 关键不变量测试（Account CHECK constraint、TeacherRole 完整性、密码验证）

### 不包含
- Service 层业务逻辑
- API 路由
- ExamRecord/Question/StudentAnswer 等业务表
- 前端代码

## 实现策略

采用 SQLAlchemy 2.0 声明式风格（`Mapped[T]` + 类型注解），整型自增主键，单一 Alembic 迁移链。

关键设计决策（基于 17 个 grilling 决策）：
- Parent 独立认证（不使用 Account 表）
- Account 双可空外键（teacher_id + student_id，CHECK constraint 互斥）
- Teacher.role 用 Python Enum（全英文值）
- 全表自动时间戳，关键表软删除
- Question 表（未来）用 JSON 字段存选项

## 成功标准

- `alembic upgrade head` 成功创建所有表
- `mypy app/models/` 类型检查通过
- 关键不变量测试通过
- Python shell 能正常 CRUD 所有模型
