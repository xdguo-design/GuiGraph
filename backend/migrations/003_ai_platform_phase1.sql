-- Phase 1: AI 中台骨架 — 扩展模型表 + 新增审计日志和 Prompt 模板表
-- 注意：SQLite 不支持 COMMENT，去掉注释

-- ── 1. 扩展 ai_model_config 表 ──────────────────────────────────
ALTER TABLE ai_model_config ADD COLUMN model_id VARCHAR(100) NOT NULL DEFAULT '';
ALTER TABLE ai_model_config ADD COLUMN tier VARCHAR(20) NOT NULL DEFAULT 'fast';
ALTER TABLE ai_model_config ADD COLUMN rate_limit_rpm INTEGER NOT NULL DEFAULT 60;
ALTER TABLE ai_model_config ADD COLUMN cost_per_1m FLOAT DEFAULT NULL;
ALTER TABLE ai_model_config ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT 0;

-- ── 2. 扩展 scenario_binding 表 ─────────────────────────────────
ALTER TABLE scenario_binding ADD COLUMN tier VARCHAR(20) NOT NULL DEFAULT 'fast';

-- ── 3. 新增 ai_usage_log 表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scenario VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_msg TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_scenario ON ai_usage_log(scenario);
CREATE INDEX IF NOT EXISTS idx_ai_usage_user ON ai_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_created ON ai_usage_log(created_at);

-- ── 4. 新增 ai_prompt_template 表 ───────────────────────────────
CREATE TABLE IF NOT EXISTS ai_prompt_template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    scenario VARCHAR(50) NOT NULL,
    template TEXT NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── 5. 插入默认模型配置 ────────────────────────────────────────
INSERT OR IGNORE INTO ai_model_config (name, model_type, provider, model_id, tier, env_tags, base_url, max_output_tokens, temperature, rate_limit_rpm, cost_per_1m, priority, is_default, active, created_by)
VALUES ('智谱 GLM-5.1', 'llm', 'zhipu', 'glm-5.1', 'complex', '["all"]', 'https://open.bigmodel.cn/api/paas/v4', 8192, 0.7, 60, 28.0, 1, 1, 1, 1);

INSERT OR IGNORE INTO ai_model_config (name, model_type, provider, model_id, tier, env_tags, base_url, max_output_tokens, temperature, rate_limit_rpm, cost_per_1m, priority, is_default, active, created_by)
VALUES ('智谱 GLM-4.7', 'llm', 'zhipu', 'glm-4.7', 'fast', '["all"]', 'https://open.bigmodel.cn/api/paas/v4', 4096, 0.7, 200, 1.5, 1, 1, 1, 1);

-- ── 6. 插入默认场景绑定 ─────────────────────────────────────────
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('change_doc_generator', 'complex', (SELECT id FROM ai_model_config WHERE model_id='glm-5.1' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('change_impact_analysis', 'complex', (SELECT id FROM ai_model_config WHERE model_id='glm-5.1' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('code_review', 'complex', (SELECT id FROM ai_model_config WHERE model_id='glm-5.1' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('merge_conflict_solve', 'complex', (SELECT id FROM ai_model_config WHERE model_id='glm-5.1' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('smart_search', 'fast', (SELECT id FROM ai_model_config WHERE model_id='glm-4.7' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('build_diagnosis', 'fast', (SELECT id FROM ai_model_config WHERE model_id='glm-4.7' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('dashboard_insight', 'fast', (SELECT id FROM ai_model_config WHERE model_id='glm-4.7' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('auto_tag_note', 'fast', (SELECT id FROM ai_model_config WHERE model_id='glm-4.7' LIMIT 1), 'all', 1);
INSERT OR IGNORE INTO scenario_binding (scenario_name, tier, model_id, env, priority)
VALUES ('commit_message_gen', 'fast', (SELECT id FROM ai_model_config WHERE model_id='glm-4.7' LIMIT 1), 'all', 1);
