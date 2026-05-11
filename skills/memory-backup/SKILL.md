# memory-backup

## 描述

记忆文件增量备份技能。将 `memory/` 目录中的文本文件增量备份到 `~/.openclaw/workspace/.state/backups/`，保留 7 天 rolling history。可选推送到 GitHub（需要 `GITHUB_TOKEN` 环境变量）。

## 触发场景

- 每天 23:00 cron 自动备份
- 手动触发：`python3 skills/memory-backup/scripts/memory_backup.py`

## 备份范围

**备份：**
- `memory/*.md` — 每日记忆文件
- `memory/**/` — 子目录中的 md 文件
- `memory/research/` — 研究文件
- `memory/tasks/` — 任务状态

**不备份：**
- `.db`, `.sqlite`, `.sqlite-wal`, `.sqlite-shm`（二进制数据库）
- `.log` 文件
- `.trash/`, `node_modules/`, `__pycache__/`

## 增量逻辑

- 基于 `mtime + size` 指纹判断文件是否变化
- 无变化跳过，有变化才写盘
- 每次备份生成 `YYYY-MM-DD/_manifest.json` 记录备份内容

## 状态文件

`~/.openclaw/workspace/.state/backups/backup-state.json`

```json
{
  "last_backup": "2026-04-15T23:00:00",
  "backup_count": 42,
  "last_hash": {
    "memory/2026-04-15.md": "1744700000_1234"
  }
}
```

## 清理策略

- 超过 7 天的备份自动删除
- 每次备份时触发清理

## 依赖

- Python 3 标准库（无需额外依赖）
- 可选：`GITHUB_TOKEN` 环境变量用于推送到 GitHub（当前未实现推送逻辑）
