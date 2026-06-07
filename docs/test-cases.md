# GuiGraph 版本变更管理系统 — 测试用例文档

> **版本**: v1.0 | **日期**: 2026-06-05 | **状态**: 待评审

---

## 目录

1. [测试概述](#1-测试概述)
2. [测试环境](#2-测试环境)
3. [测试用例](#3-测试用例)
   - 3.1 系统健康检查
   - 3.2 认证模块
   - 3.3 用户模块
   - 3.4 组织架构模块
   - 3.5 变更管理模块
   - 3.6 Git 集成模块
   - 3.7 Jenkins 集成模块
   - 3.8 仪表盘模块
   - 3.9 审计日志模块
   - 3.10 升级日志模块
   - 3.11 字典管理模块
   - 3.12 AI 模块
   - 3.13 知识库模块
   - 3.14 Wiki 模块
   - 3.15 附件管理模块
   - 3.16 前端 E2E 测试
4. [测试数据准备](#4-测试数据准备)
5. [测试执行流程](#5-测试执行流程)
6. [缺陷管理](#6-缺陷管理)

---

## 1. 测试概述

### 1.1 测试目标

验证 GuiGraph 版本变更管理系统的功能完整性、性能稳定性和安全性，确保系统满足 PRD 中定义的所有业务需求。

### 1.2 测试范围

| 模块 | 测试类型 | 优先级 |
|------|----------|--------|
| 认证模块 | API 测试 + E2E | P0 |
| 用户模块 | API 测试 + E2E | P0 |
| 组织架构模块 | API 测试 + E2E | P1 |
| 变更管理模块 | API 测试 + E2E | P0 |
| Git 集成模块 | API 测试 | P1 |
| Jenkins 集成模块 | API 测试 | P1 |
| 仪表盘模块 | E2E | P2 |
| 审计日志模块 | API 测试 | P2 |
| 升级日志模块 | API 测试 | P2 |
| 字典管理模块 | API 测试 | P2 |
| AI 模块 | API 测试 | P2 |
| 知识库模块 | API 测试 | P2 |
| Wiki 模块 | API 测试 | P2 |
| 附件管理模块 | API 测试 | P2 |

### 1.3 测试策略

- **单元测试**: 使用 pytest 进行后端单元测试
- **集成测试**: 使用 TestClient 进行 API 集成测试
- **E2E 测试**: 使用 Playwright 进行前端 E2E 测试
- **性能测试**: 使用 Locust 进行 API 性能测试（可选）
- **安全测试**: 使用 OWASP ZAP 进行安全扫描（可选）

---

## 2. 测试环境

### 2.1 环境配置

| 服务 | 地址 | 说明 |
|------|------|------|
| 后端 API | http://localhost:10011 | FastAPI 服务 |
| 前端页面 | http://localhost:10010 | Vue 3 开发服务器 |
| API 文档 | http://localhost:10011/docs | Swagger UI |
| 健康检查 | http://localhost:10011/health | 健康检查端点 |
| 数据库 | SQLite | 后端 guigraph.db |

### 2.2 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 系统管理员 | guoxudong | 1 | 全部权限 |
| 编辑者 | test_editor | 1 | 创建/编辑变更 |
| 查看者 | test_viewer | 1 | 仅查看 |

### 2.3 依赖工具

- Python 3.10+
- pytest 8.3+
- pytest-asyncio 0.23+
- httpx 0.27+
- Playwright 1.40+（前端 E2E）

---

## 3. 测试用例

### 3.1 系统健康检查

#### TC-001: 健康检查接口

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-001 |
| **用例名称** | 系统健康检查 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 GET 请求到 `/health` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"status": "ok", "app": "GuiGraph"}` |
| **优先级** | P0 |

#### TC-002: 根路径接口

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-002 |
| **用例名称** | 根路径信息 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 GET 请求到 `/` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "Welcome to GuiGraph API", "docs": "/docs"}` |
| **优先级** | P1 |

---

### 3.2 认证模块

#### TC-101: 用户名密码登录成功

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-101 |
| **用例名称** | 用户名密码登录成功 |
| **前置条件** | 后端服务已启动，管理员账号已创建 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/login`<br>2. 请求体：`{"username": "guoxudong", "password": "1"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `access_token`, `refresh_token`, `token_type: "bearer"`, `expires_in: 7200` |
| **优先级** | P0 |

#### TC-102: 用户名密码登录失败（密码错误）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-102 |
| **用例名称** | 用户名密码登录失败（密码错误） |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/login`<br>2. 请求体：`{"username": "guoxudong", "password": "wrong"}` |
| **预期结果** | 返回 HTTP 401，响应体包含错误信息 |
| **优先级** | P0 |

#### TC-103: 用户名密码登录失败（用户不存在）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-103 |
| **用例名称** | 用户名密码登录失败（用户不存在） |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/login`<br>2. 请求体：`{"username": "nonexistent", "password": "1"}` |
| **预期结果** | 返回 HTTP 401，响应体包含错误信息 |
| **优先级** | P0 |

#### TC-104: 用户名密码登录失败（参数缺失）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-104 |
| **用例名称** | 用户名密码登录失败（参数缺失） |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/login`<br>2. 请求体：`{"username": "guoxudong"}` |
| **预期结果** | 返回 HTTP 422，响应体包含验证错误信息 |
| **优先级** | P0 |

#### TC-105: 刷新访问令牌

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-105 |
| **用例名称** | 刷新访问令牌 |
| **前置条件** | 已获取有效的 refresh_token |
| **测试步骤** | 1. 先调用登录接口获取 refresh_token<br>2. 发送 POST 请求到 `/api/v1/auth/refresh?refresh_token=<token>` |
| **预期结果** | 返回 HTTP 200，响应体包含新的 `access_token` 和 `refresh_token` |
| **优先级** | P0 |

#### TC-106: 刷新访问令牌失败（无效 token）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-106 |
| **用例名称** | 刷新访问令牌失败（无效 token） |
| **前置条件** | 无 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/refresh?refresh_token=invalid_token` |
| **预期结果** | 返回 HTTP 401，响应体包含错误信息 |
| **优先级** | P0 |

#### TC-107: 退出登录

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-107 |
| **用例名称** | 退出登录 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/logout`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "退出成功"}` |
| **优先级** | P1 |

#### TC-108: 微信登录二维码（未配置）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-108 |
| **用例名称** | 微信登录二维码（未配置） |
| **前置条件** | 微信 OAuth 未配置 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/auth/wechat/qrcode` |
| **预期结果** | 返回 HTTP 501，响应体包含错误信息 |
| **优先级** | P2 |

---

### 3.3 用户模块

#### TC-201: 获取用户信息

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-201 |
| **用例名称** | 获取用户信息 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/user/profile`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含用户信息（id, username, nickname, status, roles 等） |
| **优先级** | P0 |

#### TC-202: 获取用户信息失败（未授权）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-202 |
| **用例名称** | 获取用户信息失败（未授权） |
| **前置条件** | 无 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/user/profile`（不带 Authorization header） |
| **预期结果** | 返回 HTTP 401 |
| **优先级** | P0 |

#### TC-203: 更新用户信息

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-203 |
| **用例名称** | 更新用户信息 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 PUT 请求到 `/api/v1/user/profile`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"nickname": "新昵称", "email": "new@example.com"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "更新成功"}` |
| **优先级** | P1 |

#### TC-204: 上传头像（图片文件）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-204 |
| **用例名称** | 上传头像（图片文件） |
| **前置条件** | 已获取有效的 access_token，准备图片文件 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/user/avatar`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. Body: multipart/form-data，字段 `file` 为图片文件 |
| **预期结果** | 返回 HTTP 200，响应体包含 `avatar_url` 和 `message` |
| **优先级** | P1 |

#### TC-205: 上传头像（非图片文件）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-205 |
| **用例名称** | 上传头像（非图片文件） |
| **前置条件** | 已获取有效的 access_token，准备非图片文件（如 .txt） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/user/avatar`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. Body: multipart/form-data，字段 `file` 为非图片文件 |
| **预期结果** | 返回 HTTP 400，响应体包含错误信息 |
| **优先级** | P1 |

#### TC-206: 绑定微信账号

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-206 |
| **用例名称** | 绑定微信账号 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/user/bind-wechat`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"code": "wechat_auth_code"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "绑定成功"}` |
| **优先级** | P2 |

---

### 3.4 组织架构模块

#### TC-301: 获取组织架构树

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-301 |
| **用例名称** | 获取组织架构树 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/org/structure`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含组织架构树（公司、部门、团队） |
| **优先级** | P0 |

#### TC-302: 创建部门

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-302 |
| **用例名称** | 创建部门 |
| **前置条件** | 已获取有效的 access_token（系统管理员权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/org/departments`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"name": "测试部门", "code": "test_dept", "company_id": 1}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的部门信息 |
| **优先级** | P0 |

#### TC-303: 更新部门

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-303 |
| **用例名称** | 更新部门 |
| **前置条件** | 已创建部门 |
| **测试步骤** | 1. 发送 PUT 请求到 `/api/v1/org/departments/{dept_id}`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"name": "更新后的部门名称"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "更新成功"}` |
| **优先级** | P1 |

#### TC-304: 创建团队

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-304 |
| **用例名称** | 创建团队 |
| **前置条件** | 已创建部门 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/org/teams`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"name": "测试团队", "code": "test_team", "department_id": 1}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的团队信息 |
| **优先级** | P0 |

#### TC-305: 添加团队成员

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-305 |
| **用例名称** | 添加团队成员 |
| **前置条件** | 已创建团队和用户 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/org/teams/{team_id}/members`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"user_id": 1, "role": "member"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "添加成功"}` |
| **优先级** | P0 |

#### TC-306: 移除团队成员

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-306 |
| **用例名称** | 移除团队成员 |
| **前置条件** | 团队中已有成员 |
| **测试步骤** | 1. 发送 DELETE 请求到 `/api/v1/org/teams/{team_id}/members/{user_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "移除成功"}` |
| **优先级** | P1 |

#### TC-307: 创建团队（权限不足）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-307 |
| **用例名称** | 创建团队（权限不足） |
| **前置条件** | 使用编辑者角色账号 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/org/teams`<br>2. Header: `Authorization: Bearer <editor_token>`<br>3. 请求体：`{"name": "测试团队", "code": "test_team", "department_id": 1}` |
| **预期结果** | 返回 HTTP 403 |
| **优先级** | P1 |

---

### 3.5 变更管理模块

#### TC-401: 查询变更列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-401 |
| **用例名称** | 查询变更列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/changes?page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含分页数据（items, total, page, page_size） |
| **优先级** | P0 |

#### TC-402: 查询变更列表（带筛选条件）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-402 |
| **用例名称** | 查询变更列表（带筛选条件） |
| **前置条件** | 已有变更数据 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/changes?change_type=db&status=draft&page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含符合筛选条件的变更列表 |
| **优先级** | P1 |

#### TC-403: 获取变更详情

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-403 |
| **用例名称** | 获取变更详情 |
| **前置条件** | 已有变更数据 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/changes/{change_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含变更详情 |
| **优先级** | P0 |

#### TC-404: 创建变更

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-404 |
| **用例名称** | 创建变更 |
| **前置条件** | 已获取有效的 access_token（编辑者权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"version_id": 1, "change_type": "db", "content": "新增支付配置表", "change_reason": "requirement", "change_reason_detail": "业务需求"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的变更信息，状态为 "draft" |
| **优先级** | P0 |

#### TC-405: 创建变更（内容长度不足）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-405 |
| **用例名称** | 创建变更（内容长度不足） |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"version_id": 1, "change_type": "db", "content": "短", "change_reason": "requirement"}` |
| **预期结果** | 返回 HTTP 422，响应体包含验证错误信息（内容至少 10 个字符） |
| **优先级** | P1 |

#### TC-406: 更新变更

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-406 |
| **用例名称** | 更新变更 |
| **前置条件** | 已有草稿状态的变更 |
| **测试步骤** | 1. 发送 PUT 请求到 `/api/v1/changes/{change_id}`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"content": "更新后的变更内容"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "更新成功"}` |
| **优先级** | P1 |

#### TC-407: 审批变更（通过）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-407 |
| **用例名称** | 审批变更（通过） |
| **前置条件** | 已有变更数据 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes/{change_id}/approve`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"approved": true, "comment": "审批通过"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "审批成功"}` |
| **优先级** | P0 |

#### TC-408: 审批变更（拒绝）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-408 |
| **用例名称** | 审批变更（拒绝） |
| **前置条件** | 已有变更数据 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes/{change_id}/approve`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"approved": false, "comment": "需要补充说明"}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "审批成功"}`，变更状态为 "rejected" |
| **优先级** | P1 |

#### TC-409: 审批变更（权限不足）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-409 |
| **用例名称** | 审批变更（权限不足） |
| **前置条件** | 使用查看者角色账号 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes/{change_id}/approve`<br>2. Header: `Authorization: Bearer <viewer_token>`<br>3. 请求体：`{"approved": true}` |
| **预期结果** | 返回 HTTP 403 |
| **优先级** | P1 |

---

### 3.6 Git 集成模块

#### TC-501: 获取 Git 仓库列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-501 |
| **用例名称** | 获取 Git 仓库列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/git/repos`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含仓库列表 |
| **优先级** | P0 |

#### TC-502: 添加 Git 仓库

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-502 |
| **用例名称** | 添加 Git 仓库 |
| **前置条件** | 已获取有效的 access_token（团队管理员权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/git/repos`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"team_id": 1, "name": "pay-service", "url": "https://github.com/org/pay-service.git", "auth_type": "token", "auth_token": "ghp_xxx"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的仓库信息 |
| **优先级** | P0 |

#### TC-503: 获取分支列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-503 |
| **用例名称** | 获取分支列表 |
| **前置条件** | 已有 Git 仓库 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/git/repos/{repo_id}/branches`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含分支列表 |
| **优先级** | P0 |

#### TC-504: 为用户授权 Git 仓库

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-504 |
| **用例名称** | 为用户授权 Git 仓库 |
| **前置条件** | 已有 Git 仓库和用户 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/git/repos/{repo_id}/auth`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"user_id": 1}` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "授权成功"}` |
| **优先级** | P1 |

#### TC-505: 撤销用户授权

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-505 |
| **用例名称** | 撤销用户授权 |
| **前置条件** | 用户已有 Git 仓库授权 |
| **测试步骤** | 1. 发送 DELETE 请求到 `/api/v1/git/repos/{repo_id}/auth/{user_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "撤销成功"}` |
| **优先级** | P1 |

#### TC-506: 执行 Git 合并

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-506 |
| **用例名称** | 执行 Git 合并 |
| **前置条件** | 已有 Git 仓库，源分支和目标分支存在 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/git/merge`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"repo_id": 1, "source_branch": "feature/pay-v2", "target_branch": "dev", "commit_message": "merge feature branch"}` |
| **预期结果** | 返回 HTTP 200，响应体包含合并结果（success, message, commit_hash 等） |
| **优先级** | P0 |

#### TC-507: 获取合并日志

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-507 |
| **用例名称** | 获取合并日志 |
| **前置条件** | 已有合并记录 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/git/merge/logs?page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含合并日志列表 |
| **优先级** | P1 |

---

### 3.7 Jenkins 集成模块

#### TC-601: 获取 Jenkins 实例列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-601 |
| **用例名称** | 获取 Jenkins 实例列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/jenkins/instances`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 Jenkins 实例列表 |
| **优先级** | P1 |

#### TC-602: 添加 Jenkins 实例

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-602 |
| **用例名称** | 添加 Jenkins 实例 |
| **前置条件** | 已获取有效的 access_token（系统管理员权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/jenkins/instances`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"name": "Jenkins-Prod", "url": "https://jenkins.example.com", "auth_type": "token", "auth_token": "xxx"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的 Jenkins 实例信息 |
| **优先级** | P1 |

#### TC-603: 触发构建

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-603 |
| **用例名称** | 触发构建 |
| **前置条件** | 已有 Jenkins 实例 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/jenkins/build`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"job_name": "pay-service-ci", "params": {"BRANCH": "feature/pay-v2"}}` |
| **预期结果** | 返回 HTTP 200，响应体包含构建 ID 和状态 |
| **优先级** | P0 |

#### TC-604: 获取构建状态

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-604 |
| **用例名称** | 获取构建状态 |
| **前置条件** | 已触发构建 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/jenkins/build/{build_id}/status`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含构建状态（running, success, failed 等） |
| **优先级** | P1 |

#### TC-605: 获取构建日志

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-605 |
| **用例名称** | 获取构建日志 |
| **前置条件** | 已触发构建 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/jenkins/build/{build_id}/log`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含构建日志内容 |
| **优先级** | P1 |

#### TC-606: 回写构建状态到变更

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-606 |
| **用例名称** | 回写构建状态到变更 |
| **前置条件** | 已有变更和构建记录 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/changes/{change_id}/jenkins-status?build_id=123&status=success`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "更新成功"}` |
| **优先级** | P1 |

---

### 3.8 仪表盘模块

#### TC-701: 获取仪表盘数据

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-701 |
| **用例名称** | 获取仪表盘数据 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/dashboard`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含统计数据（total_changes, pending_changes 等）和最近变更列表 |
| **优先级** | P1 |

#### TC-702: 获取变更时间线

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-702 |
| **用例名称** | 获取变更时间线 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/dashboard/timeline?func_point_id=1`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含时间线数据 |
| **优先级** | P2 |

---

### 3.9 审计日志模块

#### TC-801: 查询审计日志

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-801 |
| **用例名称** | 查询审计日志 |
| **前置条件** | 已获取有效的 access_token（系统管理员权限） |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/audit?page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含审计日志列表 |
| **优先级** | P2 |

#### TC-802: 查询审计日志（带筛选条件）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-802 |
| **用例名称** | 查询审计日志（带筛选条件） |
| **前置条件** | 已有审计日志数据 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/audit?user_id=1&operation=login&page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含符合筛选条件的审计日志列表 |
| **优先级** | P2 |

---

### 3.10 升级日志模块

#### TC-901: 查询升级日志

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-901 |
| **用例名称** | 查询升级日志 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/upgrade?page=1&page_size=10`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含升级日志列表 |
| **优先级** | P2 |

#### TC-902: 获取升级详情

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-902 |
| **用例名称** | 获取升级详情 |
| **前置条件** | 已有升级日志数据 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/upgrade/{log_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含升级详情（版本、状态、耗时、关联变更等） |
| **优先级** | P2 |

#### TC-903: 执行升级回滚

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-903 |
| **用例名称** | 执行升级回滚 |
| **前置条件** | 已有升级日志数据（系统管理员权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/upgrade/{log_id}/rollback`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含回滚结果 |
| **优先级** | P2 |

#### TC-904: 导出升级日志

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-904 |
| **用例名称** | 导出升级日志 |
| **前置条件** | 已有升级日志数据（系统管理员权限） |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/upgrade/{log_id}/export`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含导出结果 |
| **优先级** | P2 |

---

### 3.11 字典管理模块

#### TC-1001: 获取领域列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1001 |
| **用例名称** | 获取领域列表 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/dictionary/domains` |
| **预期结果** | 返回 HTTP 200，响应体包含领域列表 |
| **优先级** | P2 |

#### TC-1002: 创建领域

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1002 |
| **用例名称** | 创建领域 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/dictionary/domains`<br>2. 请求体：`{"name": "支付", "code": "payment"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的领域信息 |
| **优先级** | P2 |

#### TC-1003: 获取应用列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1003 |
| **用例名称** | 获取应用列表 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/dictionary/applications` |
| **预期结果** | 返回 HTTP 200，响应体包含应用列表 |
| **优先级** | P2 |

#### TC-1004: 创建应用

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1004 |
| **用例名称** | 创建应用 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/dictionary/applications`<br>2. 请求体：`{"name": "pay-service", "code": "pay-service"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的应用信息 |
| **优先级** | P2 |

#### TC-1005: 获取组件列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1005 |
| **用例名称** | 获取组件列表 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/dictionary/components` |
| **预期结果** | 返回 HTTP 200，响应体包含组件列表 |
| **优先级** | P2 |

#### TC-1006: 创建组件

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1006 |
| **用例名称** | 创建组件 |
| **前置条件** | 后端服务已启动 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/dictionary/components`<br>2. 请求体：`{"name": "PaymentForm", "code": "PaymentForm"}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的组件信息 |
| **优先级** | P2 |

---

### 3.12 AI 模块

#### TC-1101: RAG 语义搜索

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1101 |
| **用例名称** | RAG 语义搜索 |
| **前置条件** | 已配置 RAGFlow |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/ai/rag/search?query=支付配置`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含搜索结果列表 |
| **优先级** | P2 |

#### TC-1102: AI 文档分析

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1102 |
| **用例名称** | AI 文档分析 |
| **前置条件** | 已配置 AI 服务 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/ai/rag/analyze`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"document": "支付配置变更文档内容..."}` |
| **预期结果** | 返回 HTTP 200，响应体包含分析结果 |
| **优先级** | P2 |

#### TC-1103: AI 生成摘要

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1103 |
| **用例名称** | AI 生成摘要 |
| **前置条件** | 已配置 AI 服务 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/ai/generate/summary`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"content": "变更内容描述..."}` |
| **预期结果** | 返回 HTTP 200，响应体包含生成的摘要 |
| **优先级** | P2 |

#### TC-1104: 获取 AI 模型列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1104 |
| **用例名称** | 获取 AI 模型列表 |
| **前置条件** | 已获取有效的 access_token（系统管理员权限） |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/ai/models`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 AI 模型列表 |
| **优先级** | P2 |

#### TC-1105: 管理 MCP 服务器

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1105 |
| **用例名称** | 管理 MCP 服务器 |
| **前置条件** | 已获取有效的 access_token（系统管理员权限） |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/ai/mcp`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 MCP 服务器列表 |
| **优先级** | P2 |

---

### 3.13 知识库模块

#### TC-1201: 获取知识库列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1201 |
| **用例名称** | 获取知识库列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/knowledge`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含知识库笔记列表 |
| **优先级** | P2 |

#### TC-1202: 创建知识库笔记

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1202 |
| **用例名称** | 创建知识库笔记 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/knowledge`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"title": "支付配置说明", "content": "支付配置相关内容..."}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的笔记信息 |
| **优先级** | P2 |

#### TC-1203: AI 生成笔记

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1203 |
| **用例名称** | AI 生成笔记 |
| **前置条件** | 已有知识库笔记，已配置 AI 服务 |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/knowledge/{note_id}/ai-generate`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 AI 生成的内容 |
| **优先级** | P2 |

---

### 3.14 Wiki 模块

#### TC-1301: 获取 Wiki 空间列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1301 |
| **用例名称** | 获取 Wiki 空间列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/wiki/spaces`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 Wiki 空间列表 |
| **优先级** | P2 |

#### TC-1302: 获取 Wiki 文档列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1302 |
| **用例名称** | 获取 Wiki 文档列表 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/wiki/docs`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 Wiki 文档列表 |
| **优先级** | P2 |

#### TC-1303: 创建 Wiki 文档

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1303 |
| **用例名称** | 创建 Wiki 文档 |
| **前置条件** | 已获取有效的 access_token |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/wiki/docs`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. 请求体：`{"title": "支付系统文档", "content": "# 支付系统\n\n## 概述\n..."}` |
| **预期结果** | 返回 HTTP 200，响应体包含创建的文档信息 |
| **优先级** | P2 |

---

### 3.15 附件管理模块

#### TC-1401: 上传附件

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1401 |
| **用例名称** | 上传附件 |
| **前置条件** | 已获取有效的 access_token，已配置 MinIO |
| **测试步骤** | 1. 发送 POST 请求到 `/api/v1/attachment/upload`<br>2. Header: `Authorization: Bearer <access_token>`<br>3. Body: multipart/form-data，字段 `file` 为文件，`biz_type` 为 "change" |
| **预期结果** | 返回 HTTP 200，响应体包含附件信息（file_id, file_url, file_name 等） |
| **优先级** | P2 |

#### TC-1402: 下载附件

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1402 |
| **用例名称** | 下载附件 |
| **前置条件** | 已上传附件 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/attachment/download/{file_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体为文件内容 |
| **优先级** | P2 |

#### TC-1403: 删除附件

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1403 |
| **用例名称** | 删除附件 |
| **前置条件** | 已上传附件 |
| **测试步骤** | 1. 发送 DELETE 请求到 `/api/v1/attachment/delete/{file_id}`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含 `{"message": "删除成功"}` |
| **优先级** | P2 |

#### TC-1404: 查询附件列表

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1404 |
| **用例名称** | 查询附件列表 |
| **前置条件** | 已上传附件 |
| **测试步骤** | 1. 发送 GET 请求到 `/api/v1/attachment/list?biz_type=change&biz_id=1`<br>2. Header: `Authorization: Bearer <access_token>` |
| **预期结果** | 返回 HTTP 200，响应体包含附件列表 |
| **优先级** | P2 |

---

### 3.16 前端 E2E 测试

#### TC-1501: 登录页面加载

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1501 |
| **用例名称** | 登录页面加载 |
| **前置条件** | 前端服务已启动 |
| **测试步骤** | 1. 打开 http://localhost:10010/login<br>2. 检查页面标题和表单元素 |
| **预期结果** | 页面显示登录表单，包含用户名、密码输入框和登录按钮 |
| **优先级** | P0 |

#### TC-1502: 登录流程（成功）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1502 |
| **用例名称** | 登录流程（成功） |
| **前置条件** | 前端服务已启动，后端服务已启动 |
| **测试步骤** | 1. 打开 http://localhost:10010/login<br>2. 输入用户名 "guoxudong"<br>3. 输入密码 "1"<br>4. 点击登录按钮 |
| **预期结果** | 页面跳转到仪表盘页面（/dashboard） |
| **优先级** | P0 |

#### TC-1503: 登录流程（失败）

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1503 |
| **用例名称** | 登录流程（失败） |
| **前置条件** | 前端服务已启动，后端服务已启动 |
| **测试步骤** | 1. 打开 http://localhost:10010/login<br>2. 输入用户名 "guoxudong"<br>3. 输入密码 "wrong"<br>4. 点击登录按钮 |
| **预期结果** | 页面显示错误提示，不跳转 |
| **优先级** | P0 |

#### TC-1504: 仪表盘页面加载

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1504 |
| **用例名称** | 仪表盘页面加载 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/dashboard<br>2. 检查页面元素 |
| **预期结果** | 页面显示仪表盘内容（统计卡片、最近变更等） |
| **优先级** | P1 |

#### TC-1505: 变更列表页面加载

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1505 |
| **用例名称** | 变更列表页面加载 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/changes<br>2. 检查页面元素 |
| **预期结果** | 页面显示变更列表表格和筛选条件 |
| **优先级** | P1 |

#### TC-1506: 创建变更页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1506 |
| **用例名称** | 创建变更页面 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/changes/create<br>2. 检查页面元素 |
| **预期结果** | 页面显示变更创建表单（类型、内容、原因等字段） |
| **优先级** | P1 |

#### TC-1507: 变更详情页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1507 |
| **用例名称** | 变更详情页面 |
| **前置条件** | 已登录，已有变更数据 |
| **测试步骤** | 1. 导航到 http://localhost:10010/changes/{id}<br>2. 检查页面元素 |
| **预期结果** | 页面显示变更详情（描述、状态、审批按钮等） |
| **优先级** | P1 |

#### TC-1508: 组织架构页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1508 |
| **用例名称** | 组织架构页面 |
| **前置条件** | 已登录（系统管理员权限） |
| **测试步骤** | 1. 导航到 http://localhost:10010/org<br>2. 检查页面元素 |
| **预期结果** | 页面显示组织架构树（公司、部门、团队） |
| **优先级** | P1 |

#### TC-1509: 用户中心页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1509 |
| **用例名称** | 用户中心页面 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/user<br>2. 检查页面元素 |
| **预期结果** | 页面显示用户信息表单（昵称、邮箱、头像等） |
| **优先级** | P1 |

#### TC-1510: Git 仓库页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1510 |
| **用例名称** | Git 仓库页面 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/git<br>2. 检查页面元素 |
| **预期结果** | 页面显示 Git 仓库列表表格 |
| **优先级** | P1 |

#### TC-1511: Jenkins 页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1511 |
| **用例名称** | Jenkins 页面 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 导航到 http://localhost:10010/jenkins<br>2. 检查页面元素 |
| **预期结果** | 页面显示 Jenkins 实例列表表格 |
| **优先级** | P1 |

#### TC-1512: 退出登录

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1512 |
| **用例名称** | 退出登录 |
| **前置条件** | 已登录 |
| **测试步骤** | 1. 点击右上角用户头像<br>2. 点击退出登录按钮 |
| **预期结果** | 页面跳转到登录页面，localStorage 中的 token 被清除 |
| **优先级** | P1 |

#### TC-1513: 未登录访问受保护页面

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1513 |
| **用例名称** | 未登录访问受保护页面 |
| **前置条件** | 未登录 |
| **测试步骤** | 1. 直接打开 http://localhost:10010/dashboard |
| **预期结果** | 页面自动跳转到登录页面 |
| **优先级** | P0 |

#### TC-1514: Token 过期自动跳转

| 项目 | 内容 |
|------|------|
| **用例编号** | TC-1514 |
| **用例名称** | Token 过期自动跳转 |
| **前置条件** | 已登录，token 已过期 |
| **测试步骤** | 1. 手动清除 localStorage 中的 token<br>2. 刷新页面 |
| **预期结果** | 页面自动跳转到登录页面 |
| **优先级** | P1 |

---

## 4. 测试数据准备

### 4.1 基础数据

```python
# 管理员账号（系统自动创建）
admin_user = {
    "username": "guoxudong",
    "password": "1",
    "nickname": "郭旭东",
    "role": "system_admin"
}

# 测试部门
test_department = {
    "name": "研发部门",
    "code": "dev_dept",
    "company_id": 1
}

# 测试团队
test_team = {
    "name": "支付团队",
    "code": "pay_team",
    "department_id": 1,
    "description": "负责支付系统开发"
}

# 测试 Git 仓库
test_git_repo = {
    "team_id": 1,
    "name": "pay-service",
    "url": "https://github.com/org/pay-service.git",
    "auth_type": "token",
    "auth_token": "ghp_test_token"
}

# 测试 Jenkins 实例
test_jenkins_instance = {
    "name": "Jenkins-Test",
    "url": "https://jenkins.test.com",
    "auth_type": "token",
    "auth_token": "test_token"
}

# 测试变更
test_change = {
    "version_id": 1,
    "change_type": "db",
    "content": "新增支付配置表，用于存储支付渠道配置信息",
    "change_reason": "requirement",
    "change_reason_detail": "业务需求：支持多支付渠道配置",
    "related_requirement_no": "REQ-2026-001"
}
```

### 4.2 测试文件

- 图片文件：`test_avatar.jpg`（用于头像上传测试）
- 文档文件：`test_document.pdf`（用于附件上传测试）

---

## 5. 测试执行流程

### 5.1 后端测试

```bash
# 进入后端目录
cd D:\GuiGraph\backend

# 激活虚拟环境
.venv\Scripts\activate

# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_auth.py -v
pytest tests/test_user.py -v
pytest tests/test_health.py -v

# 生成测试报告
pytest tests/ -v --html=reports/report.html
```

### 5.2 前端 E2E 测试

```bash
# 进入前端目录
cd D:\GuiGraph\frontend

# 安装 Playwright
npm install -D @playwright/test
npx playwright install

# 运行 E2E 测试
npx playwright test

# 查看测试报告
npx playwright show-report
```

### 5.3 测试执行顺序

1. **P0 测试**：优先执行，确保核心功能正常
2. **P1 测试**：次要优先级，确保主要功能正常
3. **P2 测试**：低优先级，确保辅助功能正常

---

## 6. 缺陷管理

### 6.1 缺陷等级

| 等级 | 说明 | 示例 |
|------|------|------|
| **致命** | 系统崩溃、数据丢失、核心功能不可用 | 登录失败、数据库连接错误 |
| **严重** | 主要功能异常、影响业务流程 | 变更创建失败、审批流程错误 |
| **一般** | 功能部分异常、有 workaround | 筛选条件不生效、分页错误 |
| **轻微** | 界面问题、文案错误 | 按钮样式错误、提示文案不准确 |

### 6.2 缺陷报告模板

```markdown
**缺陷标题**: [简短描述]

**缺陷等级**: 致命/严重/一般/轻微

**重现步骤**:
1. 步骤 1
2. 步骤 2
3. 步骤 3

**预期结果**: [描述预期行为]

**实际结果**: [描述实际行为]

**环境信息**:
- 浏览器: [Chrome/Firefox/Edge]
- 操作系统: [Windows 10/11]
- 测试数据: [相关数据]

**截图/日志**: [附上相关截图或日志]
```

---

## 附录

### A. 测试用例统计

| 模块 | 用例数 | P0 | P1 | P2 |
|------|--------|----|----|----|
| 系统健康检查 | 2 | 1 | 1 | 0 |
| 认证模块 | 8 | 4 | 2 | 2 |
| 用户模块 | 6 | 2 | 3 | 1 |
| 组织架构模块 | 7 | 3 | 3 | 1 |
| 变更管理模块 | 9 | 4 | 4 | 1 |
| Git 集成模块 | 7 | 3 | 3 | 1 |
| Jenkins 集成模块 | 6 | 1 | 4 | 1 |
| 仪表盘模块 | 2 | 0 | 1 | 1 |
| 审计日志模块 | 2 | 0 | 0 | 2 |
| 升级日志模块 | 4 | 0 | 0 | 4 |
| 字典管理模块 | 6 | 0 | 0 | 6 |
| AI 模块 | 5 | 0 | 0 | 5 |
| 知识库模块 | 3 | 0 | 0 | 3 |
| Wiki 模块 | 3 | 0 | 0 | 3 |
| 附件管理模块 | 4 | 0 | 0 | 4 |
| 前端 E2E | 14 | 4 | 8 | 2 |
| **总计** | **88** | **22** | **29** | **37** |

### B. 测试覆盖率目标

- **单元测试覆盖率**: ≥ 80%
- **API 测试覆盖率**: ≥ 90%
- **E2E 测试覆盖率**: ≥ 70%

### C. 测试环境要求

- Python 3.10+
- Node.js 18+
- npm 9+
- 浏览器：Chrome 120+ / Firefox 121+ / Edge 120+

---

**文档结束**
