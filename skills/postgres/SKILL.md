---
name: postgres
description: "PostgreSQL 专用技能，支持高级查询、索引优化、JSON 操作。"
triggers:
  - "postgres"
  - "postgres"
source:
  project: postgres
  url: ""
  license: ""
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:32:49
---

# Postgres

PostgreSQL 专用技能，支持高级查询、索引优化、JSON 操作。

## 核心功能

- 高级 SQL（窗口函数、CTE）
- JSON/JSONB 操作
- VACUUM/ANALYZE
## 功能

- 高级 SQL（窗口函数、CTE）
- JSON/JSONB 操作
- 全文搜索（FTS）
- 索引创建和优化
- VACUUM/ANALYZE
- 备份和恢复命令

## 使用方式

```bash
# 执行高级 SQL 查询
openclaw postgres query "SELECT ..."

# 管理索引
openclaw postgres index ...

# 执行 VACUUM/ANALYZE
openclaw postgres vacuum ...
```


## 适用场景

- 当用户需要 postgresql 专用技能，支持高级查询、索引优化、json 操作。 时

## 注意事项

*基于 skill-creator SOP 强化*
*更新时间: 2026-02-11*