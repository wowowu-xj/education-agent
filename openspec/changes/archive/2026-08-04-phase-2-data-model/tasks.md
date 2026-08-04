# Phase-2 实施任务清单

> 实施完成时间：2026-08-03（代码审查修复完成于 2026-08-04）
> 验收状态：92 项测试全绿 / `mypy app` 无错误（22 个源文件）/ `alembic upgrade head` 成功
> 代码位置：`chemai-backend/`（主仓库目录）

## 1. 基础设施层

- [x] 创建 `app/models/__init__.py`（暴露所有模型）
- [x] 创建 `app/models/base.py`（Base + TimestampMixin + SoftDeleteMixin）
- [x] 创建 `app/core/__init__.py`
- [x] 创建 `app/core/enums.py`（枚举定义）
  - 偏差：计划写的是 `TeacherRole + TeacherStatus`，实际实现为
    `TeacherRole` + `ApprovalStatus`（教师入驻与学生注册共用同一套审批状态，
    避免重复定义），另补 `ParentRelation` / `BindingStatus` / `SchoolStage`，
    以及 `TEACHER_ROLE_DISPLAY` 中文展示映射表。
- [x] 创建 `app/core/security.py`（bcrypt hash/verify 函数）
- [x] 创建 `app/core/config.py`（读取 .env，SQLAlchemy URL）
- [x] 创建 `app/core/database.py`（engine + SessionLocal + get_db）

## 2. 认证中间件

- [x] 创建 `app/core/jwt.py`（encode/decode JWT，用 python-jose）
- [x] 创建 `app/middleware/__init__.py`
- [x] 创建 `app/middleware/auth.py`（JWT 中间件，白名单最小化）

## 3. 模型文件（按依赖顺序）

- [x] `app/models/school.py`（无依赖）
- [x] `app/models/grade.py`（依赖 School）
- [x] `app/models/class_.py`（依赖 Grade）
- [x] `app/models/teacher.py`（依赖 School）
- [x] `app/models/student.py`（依赖 Class）
- [x] `app/models/parent.py`（无依赖）
- [x] `app/models/account.py`（依赖 Teacher, Student）
- [x] `app/models/teacher_class_subject.py`（依赖 Teacher, Class）
- [x] `app/models/student_parent_binding.py`（依赖 Student, Parent）

## 4. Alembic 配置与迁移

- [x] 运行 `alembic init alembic`（如未初始化）
- [x] 修改 `alembic/env.py`：设置 `target_metadata = Base.metadata`
- [x] 修改 `alembic.ini`：配置 `sqlalchemy.url`
- [x] 生成初始迁移 `alembic revision --autogenerate -m "init"`
  - 当前迁移：`20260804_dcc811e0f1a6_init_identity_and_organization_tables.py`
  - 说明：迁移共重建两次。首版 `1d541464b736` 因主键类型修正（见「7」第 1 条）
    重新生成为 `460ee30b2c85`；后者又因 P1/P2 约束补全（见「8」）重新生成为
    当前的 `dcc811e0f1a6`。两次重建时业务表均为 0 行，无数据损失；
    `upgrade head` → `downgrade base` → `upgrade head` 往返已验证。
- [x] 检查并手动补充 CHECK constraint
  - autogenerate 已正确带出 `ck_accounts_teacher_xor_student`，无需手补；
    已核对实际库内 DDL 确认约束生效。
- [x] 应用迁移 `alembic upgrade head`

## 5. 测试

- [x] 创建 `tests/__init__.py`
- [x] 创建 `tests/conftest.py`（SQLite in-memory fixture）
- [x] ~~创建 `tests/models/__init__.py`~~
  - 偏差：本阶段测试文件共 7 个，未建 `tests/models/` 子目录，
    统一平铺在 `tests/` 下。待 Phase-3 测试文件增多后再分层。
- [x] 创建 `tests/test_account.py`（CHECK constraint 测试，7 项）
- [x] 创建 `tests/test_teacher.py`（TeacherRole 枚举测试，9 项）
- [x] 创建 `tests/test_parent.py`（密码哈希测试，6 项）
- [x] 创建 `tests/test_jwt.py`（JWT 编解码，4 项）
- [x] 创建 `tests/test_auth_middleware.py`（中间件白名单与 SSE 兼容，18 项）
- [x] 创建 `tests/test_middleware_streaming.py`（流式响应集成，3 项）
- [x] 创建 `tests/test_data_integrity.py`（P1 不变量回归测试，45 项）
- [x] 运行 `pytest tests/` 全部通过（92 项）

## 6. 验证

- [x] `mypy app` 无错误（22 个源文件，Success；已从 `app/models/` 扩到全 app）
- [x] `alembic upgrade head` 成功
- [x] `pytest tests/` 全绿（92 passed）
- [x] Python shell 手动验证：能创建 School → Grade → Class → Student → Account 完整链路
  - 10 个模型主键自增正常，16 条关系双向遍历正常，
    时间戳自动填充、软删除默认值、密码哈希校验均通过，
    `get_db` 依赖项正常 yield 与关闭；验证后 rollback，未留测试数据。

## 7. 实施中的额外修复（不在原计划内）

以下是实施过程中发现并修掉的真实缺陷，记录以备追溯：

1. **`BigInteger` 主键在 SQLite 上不自增**（影响全部 9 个模型）
   建表不报错，但插入即 `NOT NULL constraint failed: schools.id`。
   SQLite 只把 `INTEGER PRIMARY KEY` 当 rowid 别名，`BIGINT` 不认。
   修复：在 `app/models/base.py` 定义跨方言类型
   `BigIntType = BigInteger().with_variant(Integer, "sqlite")`，
   8 个模型文件同步切换。生产走 MySQL 时仍是 `BIGINT`，无迁移债。

2. **`app/core/security.py` 内三个 token 函数为死代码**
   `create_access_token` / `create_refresh_token` / `decode_token` 引用了
   `settings.JWT_SECRET` / `JWT_ALGORITHM` / `ACCESS_TOKEN_EXPIRE_HOURS`，
   而 `config.py` 中实际字段为小写的 `jwt_secret_key` / `jwt_algorithm` /
   `access_token_expire_minutes`，一调用即 `AttributeError`；且与
   `app/core/jwt.py` 完全重复。
   修复：删除这三个函数，`security.py` 只保留密码哈希，
   token 单一来源收敛到 `app/core/jwt.py`。

3. **bcrypt 5.0.0 与 passlib 1.7.4 不兼容**
   `passlib[bcrypt]` 无版本上限，pip 装到 5.0.0。passlib 初始化后端时会用
   超长字符串做探测哈希，bcrypt 5.0 改为抛 `ValueError` 而不再静默截断，
   导致连 6 字符密码也哈希失败；bcrypt ≥4.1 另移除 `__about__` 触发版本读取告警。
   修复：降至 4.0.1，并在 `requirements.txt` 显式锁定 `bcrypt==4.0.1` 防复发。

4. **补充文件**
   - `app/main.py`：`create_app()` 工厂 + `/health` 端点（中间件测试需要可挂载的 app）
   - `pytest.ini`：配置 `pythonpath`
   - `tests/test_jwt.py`（4 项）、`tests/test_auth_middleware.py`（18 项）
   - `requirements.txt` 新增 `mypy==1.8.0`（任务 6.1 依赖它，原清单未列）

## 8. 代码审查修复（2026-08-04）

Phase-2 代码走查发现 12 项问题，按 P0/P1/P2 分级全部修复：

### P0（安全，必须修）

1. **JWT 密钥硬编码默认值**：`config.py` 里 `jwt_secret_key` 带默认值，
   生产忘配 `.env` 也能起服务，等于用公开密钥签 token。
   修复：改为必填环境变量，缺失即启动失败。
2. **生产环境暴露 `/docs`**：Swagger 与 OpenAPI schema 无条件挂载。
   修复：按环境变量条件挂载，生产关闭。

### P1（数据完整性与正确性）

3. **一人两账号**：`accounts.teacher_id` / `student_id` 无唯一约束，
   同一教师可绑多个账号。修复：分别加 UNIQUE（NULL 不占唯一键，
   学生账号的 `teacher_id` 全为 NULL 不冲突）。
4. **级联删除失控**：外键未声明 `ondelete`，ORM 默认把子表外键置 NULL。
   修复：组织层级用 RESTRICT（有学生的班级、有教师的学校删不掉），
   `accounts` 随 teacher/student CASCADE；关系上加 `passive_deletes="all"`
   防止 ORM 抢在数据库之前置 NULL。
5. **关系表可重复**：`teacher_class_subject` 与 `student_parent_binding`
   缺唯一约束，同一组合可插多行。修复：分别加复合 UNIQUE。
6. **中间件破坏 SSE**：`BaseHTTPMiddleware` 会缓冲流式响应体，
   问答接口的逐字输出会被攒成一整包。修复：重写为纯 ASGI 中间件。
7. **枚举存储格式与时区**：`Enum` 列按成员名存大写；`DateTime` 无时区，
   `datetime.utcnow()` 产出 naive 时间，与前端 aware 时间做运算即 TypeError。
   修复：枚举改存小写值 + CHECK constraint 白名单；
   新增 `UTCDateTime` TypeDecorator，naive 入库按 UTC 解释，
   非 UTC 输入统一归一化，读出必带 tzinfo。

### P2（工程化）

8. `Teacher.role` 变更未同步到 `Account.role`：加 `before_flush` 监听器
   （`app/models/events.py`）。踩坑：`commit()` 后属性处于 expired 状态，
   直接赋新值时 SQLAlchemy 不回读旧值，`attr_history.deleted` 为空，
   必须用 `.added` 判断变更。
9. 全部 9 个模型改写为 SQLAlchemy 2.0 `Mapped[]` 注解风格。
10. 约束统一命名（`ck_*` / `uq_*` / `ix_*`），便于迁移与排障定位。
11. `alembic/env.py` 加 `render_item` 钩子：autogenerate 会把 `UTCDateTime`
    渲染成 `app.models.base.UTCDateTime(...)` 却不生成对应 import，
    `alembic upgrade` 直接 `NameError`。钩子映射为 `sa.DateTime(timezone=True)`
    （底层 DDL 完全一致，且迁移脚本不再依赖应用代码）。
12. `.gitignore` 补全；`requirements.txt` 全部锁定版本。

### 验收

- `tests/test_data_integrity.py` 新增 45 项不变量回归测试，覆盖上述
  P1-3 / P1-4 / P1-5 / P1-7、时区语义、role 同步、软删除、约束命名。
- 针对迁移后的实际库做行为探针，逐条确认约束真的生效
  （而非只在 ORM 层拦截）。
- OPTIONS 预检测试加固：原来只断言 `!= 401`，现在额外断言响应无
  `www-authenticate` 头和 `code` 字段（两者只出现在中间件 401 响应里），
  并加反向用例——同路径无 token 的 GET 必须 401，证明豁免只针对 OPTIONS。

## 9. 遗留事项（转 Phase-3）

- SQLite → MySQL 切换：当前 `DATABASE_URL` 仍指向 SQLite，
  `BigIntType` 已为切换预留，但尚未在 MySQL 上实测。
- **软删除不自动过滤**：查询不会自动排除 `deleted_at IS NOT NULL` 的行，
  数据访问层必须显式加 `.where(Model.deleted_at.is_(None))`。
  Phase-3 引入 repository 层后在那里统一收口。
- **软删除与唯一约束冲突**：被软删的行仍占用唯一键，软删 `username='zhang'`
  之后无法再建同名账号。彻底解法是部分唯一索引（`WHERE deleted_at IS NULL`），
  但生产库是 MySQL，不支持该特性。等真出现「删除后重建同名」需求，
  再改为唯一键带 `deleted_at`，或物理删除 + 归档表。
  （已在 `app/models/base.py` 的 `SoftDeleteMixin` docstring 内记录。）
- `TEACHER_ROLE_DISPLAY` 目前只在 `enums.py` 内，尚未接入 API 响应序列化。
- BarrierConfig 跨学段语义（同一 Teacher 配置同时作用于初中与高中）未做校验。
- passlib 引用 Python 3.13 将移除的 `crypt` 模块，当前 3.11 无影响，
  长期需评估迁移到 `bcrypt` 原生 API 或 `argon2`。
