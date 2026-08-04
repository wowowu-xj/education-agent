# Phase-2 数据模型设计

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                  认证与身份层                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Account                    Parent                  │
│  ├─ teacher_id (nullable)   ├─ phone               │
│  ├─ student_id (nullable)   ├─ password_hash       │
│  └─ CHECK (互斥)            └─ (独立认证)           │
│       │                                             │
│       ├──────► Teacher                              │
│       │        ├─ role (Enum)                       │
│       │        └─ school_id ──┐                     │
│       │                       │                     │
│       └──────► Student        │                     │
│                └─ class_id ───┼──┐                  │
│                               │  │                  │
└───────────────────────────────┼──┼──────────────────┘
                                │  │
┌─────────────────────────────────────────────────────┐
│                    组织架构层                          │
├─────────────────────────────────────────────────────┤
│                                │  │                  │
│       School ◄─────────────────┘  │                  │
│         │                         │                  │
│         ▼                         │                  │
│       Grade                       │                  │
│         │                         │                  │
│         ▼                         │                  │
│       Class ◄─────────────────────┘                  │
│                                                     │
└─────────────────────────────────────────────────────┘
                │
┌─────────────────────────────────────────────────────┐
│                   关系与绑定层                         │
├─────────────────────────────────────────────────────┤
│                │                                     │
│  TeacherClassSubject (任课关系)                      │
│  ├─ teacher_id                                      │
│  ├─ class_id                                        │
│  └─ is_head_teacher                                 │
│                                                     │
│  StudentParentBinding (亲子绑定)                     │
│  ├─ student_id                                      │
│  ├─ parent_id                                       │
│  └─ bind_code (6位)                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 模型详述

### Base 基类

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
```

### 认证层

**Account**（双可空外键 + CHECK constraint）
- `id`: BIGINT PK
- `username`: VARCHAR(50) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `teacher_id`: BIGINT FK → Teacher.id (nullable)
- `student_id`: BIGINT FK → Student.id (nullable)
- `created_at`, `updated_at`
- **CHECK constraint**: `(teacher_id IS NULL) != (student_id IS NULL)`

**Teacher**（含4种子角色）
- `id`: BIGINT PK
- `name`: VARCHAR(50) NOT NULL
- `phone`: VARCHAR(20) UNIQUE
- `role`: ENUM('admin', 'academic_admin', 'subject_lead', 'teacher') NOT NULL
- `school_id`: BIGINT FK → School.id
- `status`: ENUM('pending', 'approved', 'rejected') NOT NULL
- `created_at`, `updated_at`, `deleted_at`

**Student**
- `id`: BIGINT PK
- `name`: VARCHAR(50) NOT NULL
- `student_number`: VARCHAR(20) UNIQUE
- `class_id`: BIGINT FK → Class.id
- `barrier_distribution`: JSON ({"concept": 0.3, "reading": 0.5, "expression": 0.2})
- `bind_code`: VARCHAR(6) (家长绑定码)
- `created_at`, `updated_at`, `deleted_at`

**Parent**（独立认证）
- `id`: BIGINT PK
- `name`: VARCHAR(50) NOT NULL
- `phone`: VARCHAR(20) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `created_at`, `updated_at`

### 组织层

**School**
- `id`: BIGINT PK
- `name`: VARCHAR(100) NOT NULL
- `region`: VARCHAR(50)
- `created_at`, `updated_at`, `deleted_at`

**Grade**
- `id`: BIGINT PK
- `name`: VARCHAR(20) NOT NULL (如"高一")
- `school_id`: BIGINT FK → School.id NOT NULL
- `created_at`, `updated_at`

**Class**
- `id`: BIGINT PK
- `name`: VARCHAR(50) NOT NULL (如"高一(3)班")
- `grade_id`: BIGINT FK → Grade.id NOT NULL
- `student_count`: INT DEFAULT 0
- `created_at`, `updated_at`, `deleted_at`

### 关系层

**TeacherClassSubject**（任课关系）
- `id`: BIGINT PK
- `teacher_id`: BIGINT FK → Teacher.id NOT NULL
- `class_id`: BIGINT FK → Class.id NOT NULL
- `subject`: VARCHAR(20) DEFAULT '化学'
- `is_head_teacher`: BOOLEAN DEFAULT FALSE
- `created_at`, `updated_at`

**StudentParentBinding**（亲子绑定）
- `id`: BIGINT PK
- `student_id`: BIGINT FK → Student.id NOT NULL
- `parent_id`: BIGINT FK → Parent.id NOT NULL
- `relationship`: VARCHAR(20) (父亲/母亲/其他监护人)
- `is_active`: BOOLEAN DEFAULT TRUE
- `created_at`, `updated_at`

## 枚举定义

```python
# app/core/enums.py
from enum import Enum

class TeacherRole(str, Enum):
    ADMIN = "admin"
    ACADEMIC_ADMIN = "academic_admin"
    SUBJECT_LEAD = "subject_lead"
    TEACHER = "teacher"

class TeacherStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
```

## 认证中间件设计

JWT 中间件白名单（仅以下路径跳过认证）：
- `/api/auth/*`
- `/api/parent/login`
- `/docs`
- `/redoc`
- `/openapi.json`
- `/health`

其余 `/api/*` 路径强制 JWT 验证。

## Alembic 迁移策略

单一迁移链，初始迁移创建所有9张表：

```bash
alembic revision --autogenerate -m "init: create identity and organization tables"
```

手动检查并补充：
- Account 的 CHECK constraint（autogenerate 可能遗漏）
- 索引优化（phone/student_number 的 UNIQUE 索引）

## 测试策略

仅测试关键不变量：

1. **test_account.py**: Account 的 CHECK constraint（尝试同时设置或同时置空 teacher_id 和 student_id 应失败）
2. **test_teacher.py**: TeacherRole 枚举完整性（4个值都能正常存取）
3. **test_parent.py**: 密码哈希和验证流程（bcrypt 正确工作）

使用 SQLite in-memory 数据库，pytest fixture 自动建表和清理。
