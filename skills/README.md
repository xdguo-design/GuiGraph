# 技能注册表

本目录包含系统的所有技能模块，每个技能提供特定领域的功能能力和权限边界。

---

## 技能列表

| 技能 | 路径 | 说明 |
|------|------|------|
| Git 管理 | `git-management/SKILL.md` | Git 仓库、分支、合并操作 |
| Jenkins 集成 | `jenkins-integration/SKILL.md` | Jenkins 构建触发、状态查询 |
| Agent 权限策略 | `agent-policy/SKILL.md` | Agent 行为边界、权限矩阵、操作线路 |
| 升级日志管理 | `upgrade-log/SKILL.md` | 升级记录管理、日志分析、回滚操作 |

---

## 技能使用规范

### 1. 加载技能

当任务匹配某个技能时，使用 `skill` 工具加载：

```
skill(name: "git-management")
skill(name: "jenkins-integration")
skill(name: "agent-policy")
```

### 2. 技能更新流程

```
1. 修改对应 SKILL.md 文件
2. 更新版本号（在 SKILL.md 底部）
3. 更新此注册表的版本记录
4. 通知相关方技能已更新
```

### 3. Agent 提示词编辑

Agent 的提示词存储在 `agent-policy/SKILL.md` 的 **五、Agent 提示词模板** 章节。

修改提示词时：
1. 确保不突破权限边界
2. 更新后重新加载 Agent 策略
3. 测试验证新提示词的行为

---

## 版本记录

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-06-04 | v1.1 | 新增升级日志管理 Skill |
| 2026-06-04 | v1.0 | 初始版本，包含 3 个技能 |
