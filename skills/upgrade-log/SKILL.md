# Skill: 升级日志管理

## 概述

提供系统升级日志的完整管理能力，包括升级记录查询、详情查看、回滚操作、日志导出等。

---

## 核心功能

### 1. 升级日志查询

| 操作 | 说明 |
|------|------|
| `list_logs` | 获取升级日志列表（支持多条件筛选） |
| `get_log_detail` | 获取单次升级的完整详情 |
| `compare_versions` | 对比两个版本的差异 |

### 2. 升级操作

| 操作 | 说明 |
|------|------|
| `create_log` | 创建升级记录（系统内部调用） |
| `rollback` | 执行版本回滚 |
| `export_log` | 导出升级日志（Markdown/Excel） |

### 3. 状态监控

| 操作 | 说明 |
|------|------|
| `get_upgrade_status` | 获取当前升级任务状态 |
| `get_upgrade_history` | 获取升级历史统计 |

---

## 权限边界

### 允许的操作

- ✅ 查看升级日志列表
- ✅ 查看升级详情
- ✅ 查看本团队相关的升级记录
- ✅ 导出升级日志（系统管理员、审计员）

### 禁止的操作

- ❌ 执行升级回滚（仅系统管理员）
- ❌ 修改升级日志记录
- ❌ 删除升级日志记录
- ❌ 查看未授权的升级记录（跨团队）

---

## API 接口

### 查询升级日志列表

```
GET /api/v1/upgrade/logs

Query Params:
  version_from: 可选，升级前版本
  version_to: 可选，升级后版本
  status: 可选，pending/success/failed/rolled_back
  start_time: 可选，开始时间
  end_time: 可选，结束时间
  operator_id: 可选，操作人 ID
  page: 可选，页码
  size: 可选，每页数量

Response:
{
  "logs": [
    {
      "id": 1,
      "version_from": "v2.3.0",
      "version_to": "v2.3.1",
      "upgrade_type": "full",
      "status": "success",
      "start_time": "2026-06-04T14:00:00Z",
      "end_time": "2026-06-04T14:30:00Z",
      "duration_sec": 1800,
      "operator_id": 1001,
      "operator_name": "zhangsan"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

### 获取升级详情

```
GET /api/v1/upgrade/logs/{id}

Response:
{
  "id": 1,
  "version_from": "v2.3.0",
  "version_to": "v2.3.1",
  "upgrade_type": "full",
  "status": "success",
  "start_time": "2026-06-04T14:00:00Z",
  "end_time": "2026-06-04T14:30:00Z",
  "duration_sec": 1800,
  "operator_id": 1001,
  "operator_name": "zhangsan",
  "change_items": [
    {"id": 1001, "content": "新增支付配置表"},
    {"id": 1002, "content": "修改结算逻辑"}
  ],
  "git_commits": [
    {"sha": "a1b2c3d", "message": "新增支付配置表"},
    {"sha": "e4f5g6h", "message": "修改结算逻辑"}
  ],
  "jenkins_builds": [
    {"build_id": 12345, "job_name": "pay-service-ci", "status": "success"},
    {"build_id": 12346, "job_name": "settle-service-ci", "status": "success"}
  ],
  "log_details": "[14:00:00] 开始升级...\n[14:30:00] 升级完成",
  "error_msg": null
}
```

### 执行回滚

```
POST /api/v1/upgrade/logs/{id}/rollback

Body:
{
  "reason": "发现严重 Bug",
  "notify_users": true
}

Response:
{
  "rollback_log_id": 2,
  "status": "pending",
  "message": "回滚任务已创建"
}
```

### 导出升级日志

```
POST /api/v1/upgrade/logs/{id}/export

Body:
{
  "format": "markdown"  // markdown | excel
}

Response:
{
  "export_id": "exp-xxx",
  "download_url": "/api/v1/export/exp-xxx/download",
  "file_name": "升级日志_v2.3.0_to_v2.3.1.md"
}
```

---

## 使用示例

### 示例 1：查询升级历史

```javascript
// 获取最近 10 条升级记录
const logs = await upgrade.listLogs({
  page: 1,
  size: 10
});

// 筛选成功升级
const successLogs = logs.logs.filter(log => log.status === 'success');

// 显示升级时间线
successLogs.forEach(log => {
  console.log(`${log.version_from} → ${log.version_to} (${log.start_time})`);
});
```

### 示例 2：查看升级详情

```javascript
// 获取升级详情
const detail = await upgrade.getLogDetail(1);

// 显示关联信息
console.log('关联变更:', detail.change_items.map(c => c.content));
console.log('Git Commits:', detail.git_commits.map(c => c.sha));
console.log('Jenkins 构建:', detail.jenkins_builds.map(b => b.build_id));

// 显示详细日志
console.log(detail.log_details);
```

### 示例 3：执行回滚

```javascript
// 检查当前版本
const currentLog = await upgrade.listLogs({
  version_to: 'v2.3.1',
  size: 1
});

if (currentLog.logs[0].status === 'success') {
  // 执行回滚
  const result = await upgrade.rollback(currentLog.logs[0].id, {
    reason: '发现严重 Bug，需要回滚',
    notify_users: true
  });
  
  console.log('回滚任务已创建:', result.rollback_log_id);
}
```

---

## 升级状态机

```
pending → building → success | failed
                          ↓
                    rolled_back (回滚后)
```

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| `pending` | 待升级 | 等待执行 |
| `building` | 升级中 | 轮询状态 |
| `success` | 升级成功 | 记录日志，通知用户 |
| `failed` | 升级失败 | 记录错误，通知用户，可重试 |
| `rolled_back` | 已回滚 | 记录回滚日志 |

---

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `VERSION_NOT_FOUND` | 版本不存在 | 提示检查版本号 |
| `UPGRADE_IN_PROGRESS` | 升级正在进行中 | 提示等待当前升级完成 |
| `ROLLBACK_NOT_ALLOWED` | 不允许回滚 | 提示联系管理员 |
| `PERMISSION_DENIED` | 权限不足 | 提示申请权限 |
| `EXPORT_FAILED` | 导出失败 | 提示重试 |

---

## 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `upgrade.timeout` | 升级超时时间（秒） | 3600 |
| `upgrade.auto_rollback` | 失败时自动回滚 | false |
| `upgrade.notify_users` | 升级完成通知用户 | true |
| `upgrade.log_retention_days` | 日志保留天数 | 365 |

---

## 更新日志

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-06-04 | v1.0 | 初始版本 |
