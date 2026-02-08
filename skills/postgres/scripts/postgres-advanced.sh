#!/bin/bash
# PostgreSQL 高级操作脚本

# 高级查询示例：窗口函数
postgres_advanced_query() {
    local query="$1"
    psql -c "$query"
}

# 高级查询示例：CTE (Common Table Expressions)
postgres_cte_query() {
    local query="$1"
    psql -c "$query"
}

# JSON/JSONB 操作
postgres_json_query() {
    local table="$1"
    local json_column="$2"
    psql -c "SELECT $json_column FROM $table"
}

# 全文搜索 (FTS) 查询
postgres_fts_search() {
    local table="$1"
    local column="$2"
    local search_term="$3"
    psql -c "SELECT * FROM $table WHERE to_tsvector($column) @@ to_tsquery('$search_term')"
}

# 创建GIN索引用于全文搜索
postgres_create_gin_index() {
    local table="$1"
    local column="$2"
    psql -c "CREATE INDEX ${table}_${column}_gin_idx ON $table USING GIN (to_tsvector('english', $column))"
}

# 创建B-Tree索引
postgres_create_btree_index() {
    local table="$1"
    local column="$2"
    psql -c "CREATE INDEX ${table}_${column}_idx ON $table ($column)"
}

# 复合索引
postgres_create_composite_index() {
    local table="$1"
    local columns="$2"
    psql -c "CREATE INDEX ${table}_composite_idx ON $table ($columns)"
}

# VACUUM (清理 dead tuples)
postgres_vacuum() {
    local table="$1"
    psql -c "VACUUM $table"
}

# VACUUM ANALYZE (清理 + 更新统计信息)
postgres_vacuum_analyze() {
    local table="$1"
    psql -c "VACUUM ANALYZE $table"
}

# ANALYZE (更新统计信息)
postgres_analyze() {
    local table="$1"
    psql -c "ANALYZE $table"
}

# 查看查询执行计划
postgres_explain() {
    local query="$1"
    psql -c "EXPLAIN $query"
}

# 查看查询执行计划 (详细)
postgres_explain_analyze() {
    local query="$1"
    psql -c "EXPLAIN ANALYZE $query"
}

# 备份数据库 (pg_dump)
postgres_backup() {
    local db_name="$1"
    local backup_file="$2"
    pg_dump -Fc "$db_name" > "$backup_file"
}

# 恢复数据库 (pg_restore)
postgres_restore() {
    local backup_file="$1"
    local db_name="$2"
    pg_restore -C -d "$db_name" "$backup_file"
}

# 逻辑备份 (SQL格式)
postgres_dump_sql() {
    local db_name="$1"
    local sql_file="$2"
    pg_dump "$db_name" > "$sql_file"
}

# 导入SQL文件
postgres_import_sql() {
    local sql_file="$1"
    psql -f "$sql_file"
}

# 查看表大小
postgres_table_size() {
    local table="$1"
    psql -c "SELECT pg_size_pretty(pg_relation_size('$table'))"
}

# 查看所有表大小
postgres_all_tables_size() {
    psql -c "SELECT relname, pg_size_pretty(pg_relation_size(relid)) AS size FROM pg_stat_user_tables ORDER BY pg_relation_size(relid) DESC"
}

# 查看索引大小
postgres_index_size() {
    local index="$1"
    psql -c "SELECT pg_size_pretty(pg_relation_size('$index'))"
}

# 查看数据库大小
postgres_db_size() {
    local db_name="$1"
    psql -c "SELECT pg_size_pretty(pg_database_size('$db_name'))"
}

# 连接信息
postgres_connection_info() {
    psql -c "SELECT version(), current_user, current_database(), now()"
}

# 显示活动连接
postgres_active_connections() {
    psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active'"
}

# 终止指定连接
postgres_terminate_connection() {
    local pid="$1"
    psql -c "SELECT pg_terminate_backend($pid)"
}

# 死锁检测
postgres_check_locks() {
    psql -c "SELECT * FROM pg_locks WHERE granted = false"
}

# 慢查询日志分析
postgres_slow_queries() {
    psql -c "SELECT query, calls, mean_time, total_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 20"
}

# 启用 pg_stat_statements
postgres_enable_stat_statements() {
    psql -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements"
}
