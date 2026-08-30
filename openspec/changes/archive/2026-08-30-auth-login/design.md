# Design: auth-login

## 目标

落地登录闭环：教师凭 username + password 换取 JWT，登录页把 token 写入 localStorage 并跳转出题工作台。全部复用已就绪的 `security` / `jwt` / `Account`，不引入新依赖、不改认证中间件（白名单 `/api/auth/` 已预留）。

## 后端：`app/api/auth.py`

新建 `auth_router = APIRouter(prefix="/api/auth", tags=["认证"])`，注册进 `app/main.py`。

### 1. 登录端点 `POST /api/auth/login`

请求体 `LoginRequest`：

```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

响应 `LoginResponse`：

```python
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief          # {id, role}
```

处理流程：

1. 按 `username` 查 `Account`，过滤 `deleted_at IS NULL`。
2. 账号不存在 → 401（见「统一错误语义」）。
3. `verify_password(password, account.password_hash)` 失败 → 401（与上一步同形）。
4. 解析 `school_id`：
   - teacher 账号：`account.teacher.school_id`（经 relationship）。
   - student 账号：本期返回 `None`（学生端登录后续排期，见 proposal「不在本期范围」）。
5. `create_access_token(account.id, account.role, school_id)` + `create_refresh_token(...)`，返回。

**决策**：登录只走 `Account` 表（teacher/student 共用），`Parent` 独立通道不在本期。`role` 直接用 `Account.role`（已缓存、与 `Teacher.role` 同步），避免登录时再 JOIN Teacher 取角色。

### 2. 刷新端点 `POST /api/auth/refresh`

请求体 `RefreshRequest(refresh_token: str)`；响应 `{access_token, token_type}`。

处理：`decode_token(refresh_token)` → 校验 `type == "refresh"` → 用 payload 中的 `user_id`/`role`/`school_id` 重签 access token。解码失败或 type 不符 → 401。

### 3. 统一错误语义

登录/刷新端点返回业务层 401，采用后端统一错误结构（`{"error","message"}`），经 FastAPI `HTTPException` 承载在 `detail` 字段，实际线上响应体为：

```json
{"detail": {"error": "invalid_credentials", "message": "用户名或密码错误"}}
{"detail": {"error": "invalid_token", "message": "凭证无效或已过期"}}
```

这与 `app/api/deps.py`、`app/api/audit.py` 的 `HTTPException(detail={"error","message"})` 一致。注意与认证中间件的 401 形状（`{"detail","code"}`）不同——中间件守门、端点鉴权是两层，形状各有出处，本 change 不改中间件。

## 前端：`frontend/pages/login.html`（入口 `/pages/login.html`）

> 登录页放在 `pages/` 下而非前端根目录，因为认证中间件的静态白名单是 `/pages/`、`/css/`、`/js/`、`/m/` 前缀——根目录的 `/login.html` 会被中间件 401 拦下。放 `pages/` 即可免认证直达，无需改中间件白名单。

Vue 3 CDN + Tailwind CDN 单页（与出题工作台一致，无构建），设计系统 36（Oxford Blue + 暖纸）。

- 表单：`username`、`password`，提交 → `fetch('/api/auth/login', POST)`。
- 成功：`localStorage.setItem('chemai_access_token', ...)`、`localStorage.setItem('chemai_refresh_token', ...)` → `location.href = '/pages/question-workbench.html'`。
- 失败（401）：顶部展示「用户名或密码错误」，不区分具体原因。
- 已登录：`mounted` 时若 `localStorage` 已有 `chemai_access_token`，直接跳转工作台。
- 视觉：暖纸背景 + 左侧红边距线实验笔记卡片（沿用设计系统 36）。

token 键名沿用出题工作台现读的 `chemai_access_token`（`question-workbench.html` 的 `TOKEN_KEY`），刷新键 `chemai_refresh_token` 为新增、当前仅存储暂不消费。

## 开发种子账号

当前 dev 库 `accounts` 里 `u1` 的 `password_hash` 是占位字符串 `"h"`，非法 bcrypt，无法登录。提供一个一次性种子命令（脚本或文档化 python -c），将 dev 账号重置为已知凭据：

- username：`teacher`、password：`Chemai@1234`（bcrypt 落库）

落地方式：一条 `python -c`（用 `app.core.security.hash_password` 计算哈希后 UPDATE 现有账号，并把 username 改为 `teacher`），或独立 `scripts/seed_dev_account.py`。二选一，倾向脚本（可重复、可进 README）。

## 路由注册

`app/main.py`：`from app.api.auth import router as auth_router` → `app.include_router(auth_router)`。中间件白名单已含 `/api/auth/` 前缀，无需改动。

## 测试（TDD）

新增 `tests/test_auth.py`，复用 conftest 的 `engine`/`db`/`school`/`teacher` fixture：

- 用 `hash_password` 造一个真实账号，走 `TestClient` 调登录端点断言 200 + token payload。
- 覆盖：用户名不存在 / 密码错误（两者响应同形）、软删账号拒绝、refresh 换新、access 冒充 refresh 被拒。

## 非目标（明确 defer）

- `/api/parent/login`、家长端登录页。
- 学生端登录页与 student 账号的 school_id 解析链。
- token 刷新在前端的自动消费（本期仅存储 `chemai_refresh_token`）。
