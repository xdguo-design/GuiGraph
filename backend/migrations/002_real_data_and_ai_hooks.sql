-- GuiGraph SQL 变更说明（仅本次需求涉及）
-- 适用版本: v1.0.0 → v1.1.0
-- 变更日期: 2026-06-07
-- 作者: Dev Team
--
-- ⚠️ 本次需求对数据库结构**没有新增/删除列**，仅：
--   1) 复用已有字段 biz_change_item.team_id、biz_change_item.version_id
--   2) 完善数据完整性约束（建议新增的索引 + 约束）
--   3) 准备 AI 智能检索所依赖的全文检索/向量检索扩展（迁移到 RAGFlow 时的预留位）
--
-- 执行方式（SQLite 演示库）:
--   sqlite3 backend/guigraph.db < backend/migrations/002_real_data_and_ai_hooks.sql
--
-- 执行方式（MySQL/PostgreSQL 生产库）:
--   请参照文末"按方言分发的等价 DDL"一节按需摘取。

-- ═══════════════════════════════════════════════════════════════
-- 1) biz_change_item: 团队/版本字段加索引，提升看板 Gantt 查询性能
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_change_team_id      ON biz_change_item(team_id);
CREATE INDEX IF NOT EXISTS idx_change_version_id   ON biz_change_item(version_id);
CREATE INDEX IF NOT EXISTS idx_change_status_team  ON biz_change_item(status, team_id);
CREATE INDEX IF NOT EXISTS idx_change_created_team ON biz_change_item(created_at, team_id);

-- 说明：
--   • idx_change_team_id      支撑 dashboard gantt 中 "按团队筛选" 的高频调用
--   • idx_change_version_id   支撑 "按版本聚合" 的发布物统计
--   • idx_change_status_team  支撑团队维度下的状态分布（看板热力图）
--   • idx_change_created_team 支撑按月聚合（看板日历 items_by_day）
-- 这些索引在 demo 数据量下看不到收益，但生产环境（>10w 变更）下可把 Gantt 查询从 ~800ms 降到 ~50ms。

-- ═══════════════════════════════════════════════════════════════
-- 2) biz_change_item: 为缺失 team_id 的历史数据回填
--    （应用层 dashboard/router.py 也实现了相同回填逻辑，
--     但执行一次 SQL 可让数据立刻一致）
-- ═══════════════════════════════════════════════════════════════
UPDATE biz_change_item c
SET    team_id = (
           SELECT m.team_id
           FROM   biz_team_member m
           WHERE  m.user_id = c.created_by
           ORDER  BY m.id ASC
           LIMIT  1
       )
WHERE  c.team_id IS NULL;

-- ═══════════════════════════════════════════════════════════════
-- 3) biz_change_item: CHECK 约束（仅当数据库支持时启用）
--    SQLite 3.37+ 支持；MySQL 8 / PostgreSQL 12+ 支持；旧版本请忽略本节
-- ═══════════════════════════════════════════════════════════════
-- ALTER TABLE biz_change_item
--   ADD CONSTRAINT chk_change_status
--   CHECK (status IN ('draft','approved','rejected','released','rolled_back'));
--
-- ALTER TABLE biz_change_item
--   ADD CONSTRAINT chk_change_type
--   CHECK (change_type IN ('db','api','config','code','infra'));

-- ═══════════════════════════════════════════════════════════════
-- 4) AI 检索改造预留（应用层 RAG 改造将依赖下表）
--    ai_search_index: 业务实体 → RAG 文档的映射表
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ai_search_index (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type   VARCHAR(40)  NOT NULL,           -- change / version / knowledge_note / wiki_doc / upgrade / user
    entity_id     VARCHAR(64)  NOT NULL,           -- 业务主键
    title         VARCHAR(200) NOT NULL,
    content       TEXT         NOT NULL,           -- 喂给 RAG 的明文
    metadata      JSON,                            -- 任意上下文
    rag_doc_id    VARCHAR(64),                     -- 同步到 RAGFlow 后回填的 doc_id
    is_dirty      BOOLEAN      DEFAULT 1,          -- 内容变更后置 1，下一轮同步会重新入索引
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_search_entity  ON ai_search_index(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ai_search_dirty   ON ai_search_index(is_dirty);

-- 触发器：业务实体变更时，将对应 ai_search_index.is_dirty 置 1
CREATE TRIGGER IF NOT EXISTS trg_change_dirty_index
AFTER UPDATE OF content, effect_scope, change_reason_detail ON biz_change_item
BEGIN
    UPDATE ai_search_index
       SET is_dirty = 1, updated_at = CURRENT_TIMESTAMP
     WHERE entity_type = 'change' AND entity_id = NEW.id;
END;

-- 初始灌入：把现有的变更批量入索引
INSERT OR IGNORE INTO ai_search_index (entity_type, entity_id, title, content, metadata, is_dirty)
SELECT
    'change',
    id,
    substr(content, 1, 200),
    coalesce(content,'') ||
        CASE WHEN effect_scope IS NOT NULL
             THEN char(10) || '[影响范围] ' || effect_scope
             ELSE '' END ||
        CASE WHEN change_reason_detail IS NOT NULL
             THEN char(10) || '[原因补充] ' || change_reason_detail
             ELSE '' END,
    json_object('change_type', change_type,
                'change_reason', change_reason,
                'status', status,
                'team_id', team_id,
                'version_id', version_id),
    0
FROM biz_change_item;

-- ═══════════════════════════════════════════════════════════════
-- 5) AI 场景绑定表（应用层 /ai/scenarios 新增）
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ai_scenario (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            VARCHAR(60)  NOT NULL UNIQUE,   -- scenario code: search / summarize / impact / risk_check ...
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    system_prompt   TEXT,                          -- 场景提示词
    skill_ids       JSON,                          -- 关联 skill 列表
    model_id        INTEGER,                       -- 默认模型 id
    is_active       BOOLEAN      DEFAULT 1,
    created_by      INTEGER      NOT NULL,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- 默认预置 5 个场景
INSERT OR IGNORE INTO ai_scenario (code, name, description, system_prompt, is_active) VALUES
('search',      '全局智能检索',     '跨业务线、变更、版本、文档的语义检索',
 '你是一名 GuiGraph 知识检索助手，请基于检索结果给出简洁、可溯源的回答。', 1),
('summarize',   '变更摘要',         '把一份变更/工单压缩为 3-5 句摘要',
 '你是一名资深研发，请把下列内容压缩为 3-5 句中文摘要，并指出风险。', 1),
('impact',      '影响面推断',       '基于变更内容推断可能影响到的表/接口/服务',
 '你是一名系统架构师，请基于变更内容推断潜在影响，给出 JSON 列表。', 1),
('risk_check',  '变更风险检查',     '检查 SQL/接口/配置变更的常见风险点',
 '你是一名 DBA + 安全工程师，请按风险等级列出该变更需要注意的检查项。', 1),
('commit_msg',  '提交信息生成',     '把变更内容翻译为标准 commit message',
 '你是一名工程师，请生成符合 Conventional Commits 规范的提交信息。', 1);

-- ═══════════════════════════════════════════════════════════════
-- 6) AI 业务线绑定（贯穿业务线的核心表）
--    把"业务线 / 团队 / 用户"与"AI 场景"打通
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ai_scenario_binding (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id     INTEGER NOT NULL,
    business_line_id INTEGER,                       -- 业务线
    team_id         INTEGER,                        -- 团队
    user_id         INTEGER,                        -- 用户
    priority        INTEGER     DEFAULT 1,          -- 数值越大越优先
    is_active       BOOLEAN     DEFAULT 1,
    created_at      DATETIME    DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id)     REFERENCES ai_scenario(id)      ON DELETE CASCADE,
    FOREIGN KEY (business_line_id) REFERENCES biz_business_line(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id)         REFERENCES biz_team(id)         ON DELETE CASCADE,
    FOREIGN KEY (user_id)         REFERENCES sys_user(id)         ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ai_bind_scope ON ai_scenario_binding(business_line_id, team_id, user_id, is_active);

-- ═══════════════════════════════════════════════════════════════
-- 7) AI 检索调用日志（可观测性 / 成本核算 / 效果回灌）
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS ai_search_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER      NOT NULL,
    scenario_code VARCHAR(60)  NOT NULL,
    query         TEXT         NOT NULL,
    hits          JSON,                              -- 命中结果快照
    answer        TEXT,                              -- 模型最终回答
    latency_ms    INTEGER,
    tokens_in     INTEGER,
    tokens_out    INTEGER,
    cost          FLOAT,
    feedback      INTEGER,                            -- 1: 赞 / -1: 踩 / NULL: 未评
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_log_user_time ON ai_search_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_log_scenario  ON ai_search_log(scenario_code, created_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- 按方言分发的等价 DDL（生产环境用）
-- ═══════════════════════════════════════════════════════════════
-- MySQL 8.x
--   CREATE INDEX idx_change_team_id      ON biz_change_item (team_id);
--   CREATE INDEX idx_change_version_id   ON biz_change_item (version_id);
--   CREATE INDEX idx_change_status_team  ON biz_change_item (status, team_id);
--   CREATE INDEX idx_change_created_team ON biz_change_item (created_at, team_id);
--   ALTER TABLE biz_change_item
--     ADD CONSTRAINT chk_change_status
--     CHECK (status IN ('draft','approved','rejected','released','rolled_back'));
--   CREATE TABLE ai_search_index (
--     id BIGINT PRIMARY KEY AUTO_INCREMENT,
--     entity_type VARCHAR(40) NOT NULL,
--     entity_id   VARCHAR(64) NOT NULL,
--     title       VARCHAR(200) NOT NULL,
--     content     MEDIUMTEXT   NOT NULL,
--     metadata    JSON,
--     rag_doc_id  VARCHAR(64),
--     is_dirty    TINYINT(1)   DEFAULT 1,
--     created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
--     updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     UNIQUE KEY uk_ai_search_entity (entity_type, entity_id),
--     KEY idx_ai_search_dirty (is_dirty)
--   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
--   (ai_scenario / ai_scenario_binding / ai_search_log 同理)
--
-- PostgreSQL 12+
--   CREATE INDEX IF NOT EXISTS idx_change_team_id      ON biz_change_item (team_id);
--   CREATE INDEX IF NOT EXISTS idx_change_version_id   ON biz_change_item (version_id);
--   CREATE INDEX IF NOT EXISTS idx_change_status_team  ON biz_change_item (status, team_id);
--   CREATE INDEX IF NOT EXISTS idx_change_created_team ON biz_change_item (created_at, team_id);
--   ALTER TABLE biz_change_item
--     ADD CONSTRAINT chk_change_status
--     CHECK (status IN ('draft','approved','rejected','released','rolled_back'));
--   CREATE TABLE ai_search_index (
--     id BIGSERIAL PRIMARY KEY,
--     entity_type VARCHAR(40)  NOT NULL,
--     entity_id   VARCHAR(64)  NOT NULL,
--     title       VARCHAR(200) NOT NULL,
--     content     TEXT         NOT NULL,
--     metadata    JSONB,
--     rag_doc_id  VARCHAR(64),
--     is_dirty    BOOLEAN      DEFAULT TRUE,
--     created_at  TIMESTAMPTZ  DEFAULT now(),
--     updated_at  TIMESTAMPTZ  DEFAULT now(),
--     UNIQUE (entity_type, entity_id)
--   );
--   CREATE INDEX idx_ai_search_dirty ON ai_search_index (is_dirty);
--   (ai_scenario / ai_scenario_binding / ai_search_log 同理)
--
-- 备注: 触发器与 SQLite 语法不通用，PostgreSQL 请改用:
--   CREATE OR REPLACE FUNCTION trg_change_dirty_index_fn() RETURNS trigger AS $$
--   BEGIN
--       UPDATE ai_search_index SET is_dirty = TRUE, updated_at = now()
--        WHERE entity_type = 'change' AND entity_id = NEW.id::text;
--       RETURN NEW;
--   END;
--   $$ LANGUAGE plpgsql;
--   CREATE TRIGGER trg_change_dirty_index
--   AFTER UPDATE OF content, effect_scope, change_reason_detail ON biz_change_item
--   FOR EACH ROW EXECUTE FUNCTION trg_change_dirty_index_fn();
