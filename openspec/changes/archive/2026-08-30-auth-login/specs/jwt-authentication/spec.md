# jwt-authentication Specification (delta)

## ADDED Requirements

### Requirement: 登录端点

系统 SHALL 提供 `POST /api/auth/login` 端点，接受用户名与明文密码，校验通过后签发 access token（24h）与 refresh token（7d）。登录只鉴权、不决定业务权限，后续数据范围由各端点的依赖项按 role 过滤。

#### Scenario: 登录成功签发双 token

- **WHEN** 用户以正确的 username 与 password 提交登录
- **THEN** 系统 SHALL 返回 HTTP 200
- **AND** 响应体 SHALL 包含 access_token、refresh_token、token_type 与 user（含 id、role）
- **AND** access_token 的 payload SHALL 包含 `user_id=<Account.id>`、`role=<Account.role>`、`type="access"`
- **AND** refresh_token 的 payload SHALL 包含 `type="refresh"`

#### Scenario: 用户名不存在

- **WHEN** 用户提交不存在的 username
- **THEN** 系统 SHALL 返回 HTTP 401
- **AND** 响应体 SHALL 为 `{"detail": {"error": "invalid_credentials", "message": "用户名或密码错误"}}`（后端统一错误结构经 FastAPI `detail` 字段承载）
- **AND** 系统 SHALL NOT 泄露「用户名不存在」与「密码错误」之间的区别

#### Scenario: 密码错误

- **WHEN** 用户提交正确 username 但错误 password
- **THEN** 系统 SHALL 返回 HTTP 401
- **AND** 响应体 SHALL 与「用户名不存在」场景完全一致（防用户枚举）

#### Scenario: 已软删账号拒绝登录

- **WHEN** 用户以 `deleted_at` 非空的 Account 登录
- **THEN** 系统 SHALL 返回 HTTP 401（与凭证错误同形，不暴露账号状态）

### Requirement: 刷新端点

系统 SHALL 提供 `POST /api/auth/refresh` 端点，接受 refresh token，校验通过后签发新的 access token（24h）。

#### Scenario: 刷新成功换新 access token

- **WHEN** 客户端提交有效的 refresh token
- **THEN** 系统 SHALL 返回 HTTP 200 与新 access_token、token_type
- **AND** 新 access_token 的 payload SHALL 保留原 user_id、role、school_id

#### Scenario: refresh token 无效或过期

- **WHEN** 客户端提交无效、签名错误或已过期的 refresh token
- **THEN** 系统 SHALL 返回 HTTP 401
- **AND** 响应体 SHALL 为 `{"detail": {"error": "invalid_token", "message": "凭证无效或已过期"}}`

#### Scenario: 用 access token 冒充 refresh token

- **WHEN** 客户端提交 type="access" 的 token 到刷新端点
- **THEN** 系统 SHALL 返回 HTTP 401（仅接受 type="refresh"）
