# Skill: Agent 权限策略

## 概述

定义 Agent 的行为边界、可执行功能、操作线路，确保 Agent 在安全范围内运行。

---

## 一、Agent 角色定义

| 角色 | 说明 | 适用场景 |
|------|------|----------|
| `admin` | 全权限 Agent | 系统管理、配置修改 |
| `developer` | 开发权限 Agent | 代码操作、Git 合并、Jenkins 触发 |
| `viewer` | 只读 Agent | 查询、检索、生成报告 |
| `auditor` | 审计 Agent | 日志查看、合规检查 |
| `custom` | 自定义权限 Agent | 按需配置 |

---

## 二、权限矩阵

### 2.1 功能权限

| 功能模块 | admin | developer | viewer | auditor |
|----------|:-----:|:---------:|:------:|:-------:|
| **Git 操作** | | | | |
| 查看分支列表 | ✅ | ✅ | ✅ | ✅ |
| 创建分支 | ✅ | ✅ | ❌ | ❌ |
| 删除分支 | ✅ | ❌ | ❌ | ❌ |
| 执行合并 | ✅ | ✅ | ❌ | ❌ |
| 强制推送 | ✅ | ❌ | ❌ | ❌ |
| 修改仓库配置 | ✅ | ❌ | ❌ | ❌ |
| **Jenkins 操作** | | | | |
| 触发构建 | ✅ | ✅ | ❌ | ❌ |
| 停止构建 | ✅ | ✅ | ❌ | ❌ |
| 查看构建日志 | ✅ | ✅ | ✅ | ✅ |
| 修改 Job 配置 | ✅ | ❌ | ❌ | ❌ |
| **变更管理** | | | | |
| 创建变更 | ✅ | ✅ | ❌ | ❌ |
| 编辑变更 | ✅ | ✅ | ❌ | ❌ |
| 审批变更 | ✅ | ✅ | ❌ | ❌ |
| 删除变更 | ✅ | ❌ | ❌ | ❌ |
| **组织管理** | | | | |
| 创建组 | ✅ | ❌ | ❌ | ❌ |
| 管理成员 | ✅ | ❌ | ❌ | ❌ |
| 授权 Git 项目 | ✅ | ❌ | ❌ | ❌ |
| **AI 能力** | | | | |
| AI 检索 | ✅ | ✅ | ❌ | ✅ |
| AI 生成说明书 | ✅ | ✅ | ❌ | ❌ |
| AI 文档分析 | ✅ | ✅ | ❌ | ❌ |
| 管理 AI 模型 | ✅ | ❌ | ❌ | ❌ |

### 2.2 数据权限

| 数据范围 | admin | developer | viewer | auditor |
|----------|:-----:|:---------:|:------:|:-------:|
| 本组数据 | ✅ | ✅ | ✅ | ✅ |
| 本部门数据 | ✅ | ✅ | ❌ | ✅ |
| 全系统数据 | ✅ | ❌ | ❌ | ✅ |
| 敏感配置 | ✅ | ❌ | ❌ | ❌ |

---

## 三、操作线路（Operation Lines）

### 3.1 变更创建线路

```
用户请求 → Agent 接收 → 权限检查 → 表单验证 → 数据写入 → 返回结果
    ↓
权限检查项：
  ├─ 用户是否有创建变更权限？
  ├─ 用户是否有权访问所选 Git 项目？
  └─ 用户是否有权访问所选领域/应用？
```

### 3.2 Git 合并线路

```
用户请求 → Agent 接收 → 权限检查 → Git 操作 → 结果处理 → 触发 Jenkins
    ↓
权限检查项：
  ├─ 用户是否有 Git 合并权限？
  ├─ 源分支是否受保护？
  ├─ 目标分支是否受保护？
  └─ 用户是否有权访问该仓库？
    ↓
结果处理：
  ├─ 成功 → 回写 commit_sha，触发 Jenkins
  ├─ 冲突 → 返回冲突文件，等待人工
  └─ 失败 → 返回错误原因
```

### 3.3 Jenkins 构建线路

```
用户请求 → Agent 接收 → 权限检查 → 触发构建 → 轮询状态 → 回写结果
    ↓
权限检查项：
  ├─ 用户是否有触发构建权限？
  ├─ Job 是否在授权列表中？
  └─ Jenkins 实例是否可用？
    ↓
轮询策略：
  ├─ 间隔：5 秒
  ├─ 超时：10 分钟
  └─ 失败重试：1 次
```

### 3.4 AI 检索线路

```
用户请求 → Agent 接收 → 权限检查 → RAG 查询 → 结果过滤 → 返回
    ↓
权限检查项：
  ├─ 用户是否有 AI 检索权限？
  ├─ 用户是否有权访问查询的数据范围？
  └─ 查询是否包含敏感信息？
    ↓
结果过滤：
  └─ 根据用户数据权限过滤返回结果
```

---

## 四、禁止操作清单

### 4.1 绝对禁止（任何角色）

| 操作 | 说明 |
|------|------|
| `git.force_push` | 强制推送 |
| `git.delete_protected_branch` | 删除受保护分支 |
| `jenkins.delete_job` | 删除 Job |
| `jenkins.modify_security` | 修改安全配置 |
| `system.delete_user` | 删除用户 |
| `system.modify_auth` | 修改认证配置 |
| `data.export_sensitive` | 导出敏感数据 |
| `agent.modify_policy` | 修改自身权限策略 |

### 4.2 条件禁止

| 操作 | 条件 | 处理方式 |
|------|------|----------|
| `git.merge` | 目标分支受保护 | 需要额外审批 |
| `jenkins.trigger_build` | Job 需要审批 | 进入审批流程 |
| `change.approve` | 变更涉及多个组 | 需要跨组审批 |
| `ai.search` | 查询跨组数据 | 需要审计员权限 |

---

## 五、Agent 提示词模板

### 5.1 系统提示词（System Prompt）

```
你是一个版本变更管理系统的智能助手。

【你的身份】
- 角色：{role}
- 所属组：{team_name}
- 权限级别：{permission_level}

【你的边界】
你只能执行以下操作：
{allowed_operations}

你禁止执行以下操作：
{forbidden_operations}

【操作线路】
当你收到用户请求时，请按以下线路执行：
1. 验证用户身份和权限
2. 验证请求参数的合法性
3. 检查操作是否在允许范围内
4. 执行操作并返回结果
5. 记录操作日志

【安全规则】
- 不得执行任何 destructive 操作
- 不得泄露敏感信息（密码、Token、密钥）
- 不得绕过权限检查
- 遇到不确定的操作，先询问用户确认

【错误处理】
- 权限不足：明确告知用户缺少什么权限
- 操作失败：返回具体错误原因，不暴露内部细节
- 参数错误：提示用户修正参数
```

### 5.2 功能提示词（Function Prompt）

```
【功能】Git 合并

【前置条件】
- 用户有 git.merge 权限
- 源分支和目标分支存在
- 目标分支不受保护（或用户有保护分支操作权限）

【执行步骤】
1. 获取仓库信息
2. 验证分支存在性
3. 执行 git fetch
4. 执行 git merge
5. 处理结果（成功/冲突/失败）
6. 推送远程（如成功）
7. 回写变更条目

【输出格式】
成功：
{
  "status": "success",
  "commit_sha": "xxx",
  "message": "合并成功"
}

冲突：
{
  "status": "conflict",
  "conflict_files": ["file1.js", "file2.js"],
  "message": "存在合并冲突，请人工解决"
}

失败：
{
  "status": "failed",
  "error_code": "ERROR_CODE",
  "message": "具体错误信息"
}
```

---

## 六、权限配置文件

### 6.1 角色配置文件（JSON）

```json
{
  "role": "developer",
  "permissions": {
    "git": {
      "list_branches": true,
      "create_branch": true,
      "delete_branch": false,
      "merge": true,
      "force_push": false,
      "protected_branch_merge": false
    },
    "jenkins": {
      "trigger_build": true,
      "stop_build": true,
      "view_log": true,
      "modify_job": false
    },
    "change": {
      "create": true,
      "edit": true,
      "approve": true,
      "delete": false
    },
    "data_scope": "team"
  },
  "allowed_operations": [
    "git.list_branches",
    "git.merge",
    "jenkins.trigger_build",
    "jenkins.get_build_status",
    "change.create",
    "change.edit"
  ],
  "forbidden_operations": [
    "git.force_push",
    "git.delete_protected_branch",
    "jenkins.delete_job",
    "system.modify_auth"
  ]
}
```

### 6.2 权限更新流程

```
管理员修改权限配置 → 保存配置文件 → 重新加载 Agent 策略 → 生效
    ↓
变更项：
  ├─ 角色定义
  ├─ 权限矩阵
  ├─ 操作线路
  └─ 禁止操作清单
```

---

## 七、审计日志

### 7.1 记录内容

| 字段 | 说明 |
|------|------|
| `timestamp` | 操作时间 |
| `user_id` | 操作用户 |
| `agent_role` | Agent 角色 |
| `operation` | 操作类型 |
| `resource` | 操作资源 |
| `result` | 操作结果 |
| `ip_address` | 来源 IP |

### 7.2 审计查询

```
GET /api/v1/audit/logs

Query Params:
  user_id: 可选
  operation: 可选
  start_time: 可选
  end_time: 可选
  page: 可选
  size: 可选

Response:
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2026-06-04T14:30:00Z",
      "user_id": 1001,
      "agent_role": "developer",
      "operation": "git.merge",
      "resource": "repo:1, branch:feature/pay-v2 -> dev",
      "result": "success",
      "ip_address": "192.168.1.100"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

---

## 八、更新日志

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-06-04 | v1.0 | 初始版本 |
