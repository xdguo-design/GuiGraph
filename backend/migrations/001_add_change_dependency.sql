-- GuiGraph 变更依赖关系表迁移脚本
-- 执行方式: sqlite3 guigraph.db < migrations/001_add_change_dependency.sql

-- 创建变更依赖关系表
CREATE TABLE IF NOT EXISTS biz_change_dependency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_change_id INTEGER NOT NULL,
    to_change_id INTEGER NOT NULL,
    dependency_type VARCHAR(10) DEFAULT 'FS' NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_change_id) REFERENCES biz_change_item(id) ON DELETE CASCADE,
    FOREIGN KEY (to_change_id) REFERENCES biz_change_item(id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_dep_from_change ON biz_change_dependency(from_change_id);
CREATE INDEX IF NOT EXISTS idx_dep_to_change ON biz_change_dependency(to_change_id);
CREATE INDEX IF NOT EXISTS idx_dep_type ON biz_change_dependency(dependency_type);

-- 插入示例数据（可选，用于测试）
-- 假设已有变更 ID 1, 2, 3，创建依赖关系: 1 -> 2, 2 -> 3
-- INSERT INTO biz_change_dependency (from_change_id, to_change_id, dependency_type, created_by)
-- VALUES
--     (1, 2, 'FS', 1),
--     (2, 3, 'FS', 1);
