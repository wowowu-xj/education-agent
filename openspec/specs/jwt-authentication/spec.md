# jwt-authentication Specification

## Purpose
定义 ChemAI 的无状态 JWT 认证机制，包括最小化白名单策略、token 有效期、payload 结构。系统 SHALL 在中间件层统一校验所有需认证的 API 请求。
## Requirements
### Requirement: JWT 中间件全局校验

系统 SHALL 通过 HTTP 中间件对所有 `/api/*` 请求进行 JWT 校验。白名单路径 SHALL 跳过校验，其余路径 MUST 携带有效 Authorization: Bearer token。

#### Scenario: 白名单路径跳过认证

- **WHEN** 请求路径为 `/api/auth/login` 或 `/api/parent/login` 或 `/docs` 或 `/health`
- **THEN** 中间件 SHALL 直接放行，不校验 token

#### Scenario: 非白名单路径需要 token

- **WHEN** 请求路径为 `/api/classes/` 且 Authorization header 缺失或无效
- **THEN** 中间件 SHALL 返回 HTTP 401
- **AND** 响应体 SHALL 包含 `{"detail": "Authentication required"}`

#### Scenario: 有效 token 通过校验

- **WHEN** 请求携带有效 JWT token
- **THEN** 中间件 SHALL 解析 payload 并将 user_id、role、school_id 注入请求上下文
- **AND** 请求 SHALL 继续传递到端点处理函数

### Requirement: 最小化白名单策略

JWT 中间件白名单 MUST 仅包含以下路径前缀：`/api/auth/`、`/api/parent/login`、`/docs`、`/redoc`、`/openapi.json`、`/health`。其余路径（包括 `/api/classes/`、`/api/question/`、`/api/exam-bank/` 等）SHALL 强制认证。

#### Scenario: `/api/classes/` 需要认证

- **WHEN** 未携带 token 访问 `/api/classes/`
- **THEN** 中间件 SHALL 返回 HTTP 401

#### Scenario: `/api/question/` 需要认证

- **WHEN** 未携带 token 访问 `/api/question/historical`
- **THEN** 中间件 SHALL 返回 HTTP 401

### Requirement: JWT payload 结构

系统签发的 access token payload MUST 包含以下字段：user_id、role、school_id（家长无此字段）、type="access"、iat、exp。签名算法 SHALL 使用 HS256。

#### Scenario: 教师 token payload

- **WHEN** 教师通过 `/api/auth/login` 登录成功
- **THEN** 系统 SHALL 签发 JWT，其 payload 包含 `{"user_id": <id>, "role": "teacher", "school_id": <school_id>, "type": "access", "iat": <timestamp>, "exp": <timestamp+24h>}`

#### Scenario: 家长 token payload

- **WHEN** 家长通过 `/api/parent/login` 登录成功
- **THEN** 系统 SHALL 签发 JWT，其 payload 包含 `{"user_id": <parent_id>, "role": "parent", "type": "access", "iat": <timestamp>, "exp": <timestamp+24h>}`
- **AND** payload NOT 包含 school_id 字段

### Requirement: Token 有效期

access token 有效期 SHALL 为 24 小时。refresh token 有效期 SHALL 为 7 天。系统 NOT 实现 token 黑名单或即时吊销机制（无状态设计）。

#### Scenario: Token 过期后拒绝

- **WHEN** 请求携带的 token 已超过 exp 时间
- **THEN** 中间件 SHALL 返回 HTTP 401
- **AND** 响应体 SHALL 包含 `{"detail": "Token expired"}`

#### Scenario: 刷新 token

- **WHEN** 客户端使用 refresh token 请求 `/api/auth/refresh`
- **THEN** 系统 SHALL 验证 refresh token 有效性（未过期、type="refresh"）
- **AND** 签发新的 access token（24h 有效期）

### Requirement: 密码哈希不可逆

系统 SHALL 使用 passlib bcrypt 算法对 Account.password_hash 和 Parent.password_hash 字段进行单向哈希。密码明文 MUST 不落盘。

#### Scenario: 注册时哈希密码

- **WHEN** 创建 Account 或 Parent 记录时提供明文密码
- **THEN** 系统 SHALL 使用 bcrypt.hash() 生成哈希
- **AND** 仅将哈希后的字符串存入 password_hash 字段

#### Scenario: 登录时验证密码

- **WHEN** 用户提交用户名和明文密码登录
- **THEN** 系统 SHALL 查询 password_hash
- **AND** 使用 bcrypt.verify(明文, hash) 验证
- **AND** 验证失败时返回 HTTP 401

