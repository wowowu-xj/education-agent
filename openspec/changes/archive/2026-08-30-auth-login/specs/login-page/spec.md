# login-page Specification (delta)

## ADDED Requirements

### Requirement: 登录表单

登录页 SHALL 提供用户名与密码两个输入项及提交按钮，提交时调用 `POST /api/auth/login`。

#### Scenario: 提交登录

- **WHEN** 用户在登录页填写用户名与密码并提交
- **THEN** 系统 SHALL 调用登录接口
- **AND** 提交期间 SHALL 展示提交中状态并禁用重复提交

#### Scenario: 空字段拦截

- **WHEN** 用户留空用户名或密码直接提交
- **THEN** 系统 SHALL 阻止提交并提示必填

### Requirement: token 存取

登录成功后系统 SHALL 将 access_token（及 refresh_token）写入浏览器 localStorage，键名与出题工作台读取的键一致。

#### Scenario: 保存 token

- **WHEN** 登录接口返回 access_token
- **THEN** 系统 SHALL 写入 localStorage 键 `chemai_access_token`
- **AND** refresh_token SHALL 写入 localStorage 键 `chemai_refresh_token`

### Requirement: 登录跳转

登录成功后系统 SHALL 跳转到出题工作台页面。

#### Scenario: 跳转工作台

- **WHEN** 登录成功
- **THEN** 系统 SHALL 跳转到 `/pages/question-workbench.html`

### Requirement: 已登录态处理

当用户已持有有效 token 访问登录页时，系统 SHALL 直接跳转工作台，避免重复登录。

#### Scenario: 已有 token 跳过登录

- **WHEN** localStorage 中已存在 `chemai_access_token` 且用户访问登录页
- **THEN** 系统 SHALL 直接跳转出题工作台

### Requirement: 登录错误提示

登录失败时系统 SHALL 展示友好错误提示，SHALL NOT 泄露账号是否存在。

#### Scenario: 凭证错误提示

- **WHEN** 登录接口返回 401
- **THEN** 系统 SHALL 展示「用户名或密码错误」类提示
- **AND** SHALL NOT 区分用户名不存在与密码错误

### Requirement: 前端技术栈约束

登录页 MUST 使用 Vue 3 CDN + Tailwind CSS CDN，无构建步骤；静态资源 SHALL 位于 `chemai-backend/frontend/`，由 FastAPI 直接托管。

#### Scenario: 无构建加载

- **WHEN** 登录页在浏览器加载
- **THEN** 系统 SHALL 通过 CDN 加载 Vue 3 与 Tailwind
- **AND** 无需 npm install 或打包

### Requirement: 设计系统一致性

登录页视觉 SHALL 遵循设计系统 36（Academic Catalyst：Oxford Blue + 暖纸主题），而非 Material 3 风格。

#### Scenario: 主色调

- **WHEN** 渲染登录按钮等强调元素
- **THEN** 系统 SHALL 使用 Oxford Blue 而非 Material primary-container
