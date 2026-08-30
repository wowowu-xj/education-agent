# auth-login

## Why

认证链路只差临门一脚：JWT 签发/校验（`app/core/jwt.py`）、密码哈希（`app/core/security.py`）、Account 模型、认证中间件白名单（已预留 `/api/auth/` 前缀）都已就绪，但缺一个真正签发 token 的登录接口和登录页。当前出题工作台要靠手工往 localStorage 塞 token 才能访问业务数据，用户访问 `/` 或 `/login.html` 直接 401——登录落地前没有可用的登录入口。

## What Changes

- 新增 `POST /api/auth/login`：用户名 + 明文密码 → 校验通过后签发 access token（24h）与 refresh token（7d）。
- 新增 `POST /api/auth/refresh`：用 refresh token 换新 access token（`jwt-authentication` spec 已声明该端点，本次一并落地，形成完整认证闭环）。
- 新增登录页 `chemai-backend/frontend/pages/login.html`（入口 `/pages/login.html`）：表单 → 调登录接口 → 存 token 到 localStorage → 跳转出题工作台。
- 提供开发种子账号（已知用户名/密码，bcrypt 哈希落库），供浏览器手动验证登录流程。
- 在 `app/main.py` 注册 auth 路由（中间件白名单已预留 `/api/auth/`，无需改中间件）。

## Capabilities

### New Capabilities

- `login-page`: 登录页前端——表单、token 存取、跳转、错误提示、已登录态处理。

### Modified Capabilities

- `jwt-authentication`: 新增「登录端点」与「刷新端点」契约（请求/响应结构、错误码、统一 401 语义），把 spec 中已引用但尚未实现的 `/api/auth/login`、`/api/auth/refresh` 落实为可验证的需求。

## Impact

- 后端：新增 `app/api/auth.py`（登录/刷新端点），`app/main.py` 注册 `auth_router`。
- 前端：新增 `chemai-backend/frontend/pages/login.html`（Vue 3 CDN + Tailwind CDN，无构建），入口 `/pages/login.html`（静态白名单 `/pages/` 已覆盖，无需改中间件）。
- 复用现有 `app/core/security.py`（`verify_password`）、`app/core/jwt.py`（`create_access_token` / `create_refresh_token`）、`app/models/account.py`，无新增第三方依赖。
- 开发种子账号：一次性命令/脚本重置 dev 库账号密码为已知凭据（当前 `u1` 的 `password_hash` 是占位值 `"h"`，非合法 bcrypt 哈希，无法用于登录）。
- **不在本期范围**（沿用项目 defer 惯例，另行排期）：`/api/parent/login`（家长独立通道）、学生端登录页与 student 账号的 school_id 解析链（Student → Class → Grade → School）。
