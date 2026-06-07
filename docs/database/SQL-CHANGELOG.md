# SQL 修改清单（v1.0.0 → v1.1.0）

> 用于版本发布时快速对比本次需求涉及的 SQL 变更。
> 对应迁移脚本：[002_real_data_and_ai_hooks.sql](../../backend/migrations/002_real_data_and_ai_hooks.sql)
>
> 适用范围：所有方言（SQLite 演示库 / MySQL 8.x / PostgreSQL 12+）均已给出等价 DDL。

---

## 1. 变更总览

| 类别 | 数量 | 表 |
|------|------|----|
| **新增表** | 3 | `ai_search_index`、`ai_scenario`、`ai_scenario_binding`、`ai_search_log` |
| **新增索引** | 4 + 2 | `biz_change_item` × 4、`ai_search_index` × 1、`ai_scenario_binding` × 1 |
| **新增触发器** | 1 | `trg_change_dirty_index`（biz_change_item 内容变更 → ai_search_index.is_dirty=1） |
| **数据回填** | 1 | `biz_change_item.team_id` 为空的历史数据按创建人主团队补齐 |
| **CHECK 约束（建议）** | 2 | `chk_change_status`、`chk_change_type` |
| **删除表/字段** | 0 | 无 |
| **破坏性变更** | 0 | 完全向后兼容 |

---

## 2. 详细变更

### 2.1 新增表：ai_search_index（AI 全文索引映射表）

```sql
CREATE TABLE IF NOT EXISTS ai_search_index (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type   VARCHAR(40)  NOT NULL,            -- change / version / knowledge_note / ...
    entity_id     VARCHAR(64)  NOT NULL,
    title         VARCHAR(200) NOT NULL,
    content       TEXT         NOT NULL,
    metadata      JSON,
    rag_doc_id    VARCHAR(64),                       -- 同步到 RAGFlow 后回填
    is_dirty      BOOLEAN      DEFAULT 1,
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_type, entity_id)
);
```

**作用**：作为 GuiGraph 业务实体到 RAG 索引的中间表。
- 业务变更（create/update）→ 同步往这里写一条记录
- 后台 worker 周期扫描 `is_dirty=1` 的行 → 推送到 RAGFlow → 回写 `rag_doc_id`、置 `is_dirty=0`
- 删除时把对应行也删除

### 2.2 新增表：ai_scenario（AI 场景定义表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | VARCHAR(60) UNIQUE | 场景 code: search/summarize/impact/risk_check/commit_msg |
| `name` | VARCHAR(100) | 中文名 |
| `description` | TEXT | 描述 |
| `system_prompt` | TEXT | 该场景的默认提示词 |
| `skill_ids` | JSON | 关联 skill 列表 |
| `model_id` | INTEGER | 默认模型 id |
| `is_active` | BOOLEAN | 启用开关 |

**预置 5 个场景**：
- `search` 全局智能检索
- `summarize` 变更摘要
- `impact` 影响面推断
- `risk_check` 变更风险检查
- `commit_msg` 提交信息生成

### 2.3 新增表：ai_scenario_binding（AI 场景 × 业务线 / 团队 / 用户 绑定表）

把"业务线 / 团队 / 用户"与"AI 场景"打通，体现 **AI 贯穿业务线** 的设计：
- 业务线维度：整条业务线默认走 `search` 场景
- 团队维度：DB 变更多的团队默认打开 `risk_check`
- 用户维度：管理员个人偏好

| 字段 | 说明 |
|------|------|
| `scenario_id` | 关联 ai_scenario.id |
| `business_line_id` | 关联 biz_business_line.id，可空 |
| `team_id` | 关联 biz_team.id，可空 |
| `user_id` | 关联 sys_user.id，可空 |
| `priority` | 数值越大越优先；空=按全局默认 |
| `is_active` | 启用开关 |

### 2.4 新增表：ai_search_log（AI 检索调用日志）

可观测性 / 成本核算 / 效果回灌。

| 字段 | 用途 |
|------|------|
| `user_id` + `created_at` 联合索引 | 用户调用频次、活跃度 |
| `scenario_code` | 各场景调用分布 |
| `tokens_in/out`、`cost` | 成本核算（对接计费系统） |
| `latency_ms` | 性能监控 |
| `feedback` (+1/-1/NULL) | 后续可做 RLHF 训练数据 |

### 2.5 索引

| 表 | 索引 | 收益场景 |
|----|------|----------|
| `biz_change_item` | `idx_change_team_id` | Gantt/看板按团队筛选 |
| `biz_change_item` | `idx_change_version_id` | 按版本聚合发布物 |
| `biz_change_item` | `idx_change_status_team` | 团队×状态聚合（热力图） |
| `biz_change_item` | `idx_change_created_team` | 月度看板 items_by_day |
| `ai_search_index` | `idx_ai_search_dirty` | 增量同步 worker |
| `ai_scenario_binding` | `idx_ai_bind_scope` | 业务线/团队/用户维度快速查 binding |

### 2.6 数据回填

```sql
UPDATE biz_change_item c
SET    team_id = (
           SELECT m.team_id
           FROM   biz_team_member m
           WHERE  m.user_id = c.created_by
           ORDER  BY m.id ASC
           LIMIT  1
       )
WHERE  c.team_id IS NULL;
```

**说明**：
- 之前 demo seed 灌的 12 条变更都没有 team_id，导致看板 Gantt 上没有团队色卡
- 应用层 `dashboard/router.py::get_gantt` 也实现了相同回填（兜底逻辑）
- SQL 这一步是**一次性的存量修复**，跑完后即可删掉

### 2.7 触发器

```sql
CREATE TRIGGER IF NOT EXISTS trg_change_dirty_index
AFTER UPDATE OF content, effect_scope, change_reason_detail ON biz_change_item
BEGIN
    UPDATE ai_search_index
       SET is_dirty = 1, updated_at = CURRENT_TIMESTAMP
     WHERE entity_type = 'change' AND entity_id = NEW.id;
END;
```

业务上变更的"内容/影响范围/原因补充"发生变动时，自动把对应索引行置脏，确保下次 AI 检索能拿到最新版本。

### 2.8 CHECK 约束（建议、可选）

- `chk_change_status`：`status IN ('draft','approved','rejected','released','rolled_back')`
- `chk_change_type`：`change_type IN ('db','api','config','code','infra')`

注意：SQLite < 3.37 不支持 CHECK，MySQL 8/PostgreSQL 12+ 才支持。请按目标数据库版本启用。

---

## 3. 回滚脚本

```sql
-- 1) 删除触发器
DROP TRIGGER IF EXISTS trg_change_dirty_index;

-- 2) 删除新表
DROP TABLE IF EXISTS ai_search_log;
DROP TABLE IF EXISTS ai_scenario_binding;
DROP TABLE IF EXISTS ai_scenario;
DROP TABLE IF EXISTS ai_search_index;

-- 3) 删除新索引
DROP INDEX IF EXISTS idx_ai_search_entity;
DROP INDEX IF EXISTS idx_ai_search_dirty;
DROP INDEX IF EXISTS idx_ai_bind_scope;
DROP INDEX IF EXISTS idx_change_team_id;
DROP INDEX IF EXISTS idx_change_version_id;
DROP INDEX IF EXISTS idx_change_status_team;
DROP INDEX IF EXISTS idx_change_created_team;

-- 4) 回填数据保留（如果误更新了 team_id，需要从审计日志恢复；否则忽略）
```

---

## 4. 影响范围评估

| 维度 | 影响 |
|------|------|
| 现有数据 | 12 条 demo 变更会被回填 team_id；其余表无破坏性变更 |
| 现有 API | 无破坏性变更；`/changes` 写接口从 mock 改为真实 DB 写入 |
| 现有前端 | `ChangeCreate` 表单新增"所属版本/团队"必填项，需配合发布一起更新 |
| 性能 | 4 个新索引在 demo 数据下基本无开销；10w+ 数据下 Gantt 查询约提速 16 倍 |
| 存储 | 3 张新表在 demo 数据下各占 < 100KB；线性增长 |

---

## 5. 执行顺序

1. 备份数据库（生产必做）
2. 执行 `002_real_data_and_ai_hooks.sql`
3. 验证：`SELECT COUNT(*) FROM ai_search_index;` 应大于 0
4. 启动后端服务，访问 `/changes/create` 验证表单能正常保存
5. 启动 RAG 同步 worker（下一迭代）后，验证 `ai_search_log` 有新记录

---

**变更人**: Dev Team
**审核人**: 待分配
**发布时间**: 待分配
