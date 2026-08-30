# Tasks

## 1. 登录端点（TDD）

- [x] 1.1 编写登录失败测试（RED）：`tests/test_auth.py` 断言「用户名不存在」与「密码错误」均返回 401 且响应体同形（`{"error":"invalid_credentials","message":"用户名或密码错误"}`）
- [x] 1.2 编写登录成功测试（RED）：正确凭据返回 200，含 access_token/refresh_token/token_type/user，access payload 含 user_id/role/type=access
- [x] 1.3 编写软删账号测试（RED）：`deleted_at` 非空的账号登录返回 401
- [x] 1.4 实现 `app/api/auth.py` 登录端点（`verify_password` + `create_access_token`/`create_refresh_token`，school_id 走 teacher 关系），使 1.1–1.3 通过（GREEN）

## 2. 刷新端点（TDD）

- [x] 2.1 编写刷新失败测试（RED）：无效/过期 refresh token 返回 401（`invalid_token`）；access token 冒充 refresh 返回 401
- [x] 2.2 编写刷新成功测试（RED）：有效 refresh token 返回 200 + 新 access_token（payload 保留 user_id/role/school_id）
- [x] 2.3 实现刷新端点（`decode_token` 校验 type=refresh 后重签），使 2.1–2.2 通过（GREEN）

## 3. 路由注册

- [x] 3.1 `app/main.py` 注册 `auth_router`（中间件白名单 `/api/auth/` 已预留，无需改中间件）

## 4. 登录页前端

- [x] 4.1 新建 `frontend/pages/login.html`（入口 `/pages/login.html`）：Vue 3 CDN + Tailwind CDN，设计系统 36 暖纸主题
- [x] 4.2 登录表单提交 → `POST /api/auth/login`，成功存 `chemai_access_token` / `chemai_refresh_token` 并跳转 `/pages/question-workbench.html`
- [x] 4.3 失败展示「用户名或密码错误」，空字段拦截；已持 token 访问登录页直接跳转工作台

## 5. 开发种子账号

- [x] 5.1 提供一次性种子脚本/命令，重置 dev 库账号为已知凭据（username=`teacher`、password=`Chemai@1234`，bcrypt 落库）

## 6. 验证

- [x] 6.1 后端测试全绿（`pytest`），`openspec validate auth-login --strict` 通过
- [x] 6.2 浏览器手动验证：打开 `/pages/login.html` → 登录 → 自动进入出题工作台并可拉取业务数据（无需再手工塞 token）
