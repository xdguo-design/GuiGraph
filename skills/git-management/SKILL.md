# Skill: Git 管理

## 概述

提供 Git 仓库的完整管理能力，包括分支操作、合并、冲突处理等。

---

## 核心功能

### 1. 仓库管理

| 操作 | 说明 |
|------|------|
| `add_repo` | 添加 Git 仓库（URL + 认证） |
| `remove_repo` | 删除 Git 仓库 |
| `list_repos` | 列出当前用户可访问的仓库 |
| `update_repo` | 更新仓库配置 |

### 2. 分支操作

| 操作 | 说明 |
|------|------|
| `list_branches` | 获取仓库所有分支 |
| `create_branch` | 创建新分支 |
| `delete_branch` | 删除分支 |
| `switch_branch` | 切换当前分支 |

### 3. 合并操作

| 操作 | 说明 |
|------|------|
| `merge_branch` | 执行分支合并 |
| `merge_with_conflict` | 合并（含冲突检测） |
| `abort_merge` | 中止合并 |

### 4. 状态查询

| 操作 | 说明 |
|------|------|
| `get_status` | 获取工作区状态 |
| `get_log` | 获取提交历史 |
| `get_diff` | 获取分支差异 |
| `get_remote` | 获取远程信息 |

---

## 权限边界

### 允许的操作

- ✅ 读取用户已授权的 Git 仓库
- ✅ 拉取分支列表
- ✅ 执行合并（需有合并权限）
- ✅ 创建/删除分支（需有分支管理权限）
- ✅ 查看提交历史

### 禁止的操作

- ❌ 访问未授权的仓库
- ❌ 强制推送（force push）
- ❌ 删除受保护分支（main/master/release）
- ❌ 修改仓库认证信息（需管理员）
- ❌ 执行 destructive 操作（reset --hard 等）

---

## API 接口

### 获取分支列表

```
GET /api/v1/git/repos/{repoId}/branches

Response:
{
  "branches": [
    {"name": "main", "commit": "a1b2c3d", "protected": true},
    {"name": "dev", "commit": "e4f5g6h", "protected": true},
    {"name": "feature/pay-v2", "commit": "i7j8k9l", "protected": false}
  ]
}
```

### 执行合并

```
POST /api/v1/git/merge

Body:
{
  "repo_id": 1,
  "source_branch": "feature/pay-v2",
  "target_branch": "dev",
  "change_id": 1001,
  "commit_message": "Merge feature/pay-v2 into dev for CHG-001"
}

Response:
{
  "status": "success|failed|conflict",
  "commit_sha": "a1b2c3d4e5f6...",
  "conflict_files": ["src/pay/core.js"],  // 冲突时返回
  "error_msg": "冲突详情..."
}
```

### 获取合并日志

```
GET /api/v1/git/merge/logs?change_id=1001

Response:
{
  "logs": [
    {
      "time": "2026-06-04T14:30:00Z",
      "action": "merge",
      "status": "success",
      "commit_sha": "a1b2c3d",
      "user": "zhangsan"
    }
  ]
}
```

---

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `AUTH_FAILED` | 认证失败 | 提示检查凭据 |
| `BRANCH_NOT_FOUND` | 分支不存在 | 提示检查分支名 |
| `MERGE_CONFLICT` | 合并冲突 | 返回冲突文件，提示人工解决 |
| `PROTECTED_BRANCH` | 保护分支禁止操作 | 提示联系管理员 |
| `PERMISSION_DENIED` | 权限不足 | 提示申请权限 |
| `NETWORK_TIMEOUT` | 网络超时 | 提示重试 |

---

## 使用示例

### 示例 1：创建变更时关联 Git 项目

```javascript
// 1. 获取用户可访问的仓库
const repos = await git.listRepos();

// 2. 用户选择仓库后，获取分支
const branches = await git.listBranches({ repoId: 1 });

// 3. 创建变更时保存关联
await change.create({
  ...formData,
  git_repo_id: 1,
  git_branch_source: "feature/pay-v2",
  git_branch_target: "dev"
});
```

### 示例 2：版本合并流程

```javascript
// 1. 检查权限
if (!auth.hasPermission('git.merge')) {
  throw new Error('PERMISSION_DENIED');
}

// 2. 执行合并
const result = await git.merge({
  repo_id: 1,
  source_branch: "feature/pay-v2",
  target_branch: "dev",
  change_id: 1001
});

// 3. 处理结果
if (result.status === 'conflict') {
  // 返回冲突文件，等待人工解决
  return { status: 'conflict', conflict_files: result.conflict_files };
}

// 4. 合并成功后触发 Jenkins
if (result.status === 'success') {
  await jenkins.triggerBuild({
    change_id: 1001,
    branch: "dev"
  });
}
```

---

## 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `git.timeout` | Git 命令超时时间（秒） | 30 |
| `git.retry_count` | 失败重试次数 | 3 |
| `git.cache_branches` | 是否缓存分支列表 | true |
| `git.cache_ttl` | 分支缓存有效期（秒） | 300 |
| `git.protected_branches` | 受保护分支列表 | `["main", "master", "release"]` |

---

## 更新日志

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-06-04 | v1.0 | 初始版本 |
