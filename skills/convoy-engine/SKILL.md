# Convoy Engine — 多子Agent并行执行引擎

**触发场景**：
- 研究任务需要多角度并行调研（竞品 + 纵向历史 + 用户反馈）
- 大任务需要拆解并行加速
- 任务中途崩溃需要断点恢复
- 不想被单个Agent卡住

**核心设计**：Convoy = 多个子Agent首尾相连/并行运行 + 共享状态文件 + 崩溃自愈

---

## 核心概念

### 什么是 Convoy？

```
Convoy = 多个子Agent共享一个状态文件
       + 崩溃后从断点恢复（不从头重跑）
       + 并行执行（多个同时跑）
       + DAG 依赖拓扑（某些任务依赖前置任务完成）
```

### Convoy vs 普通并行

| 维度 | 普通并行 (sessions_spawn) | Convoy |
|------|--------------------------|--------|
| 状态持久化 | 无，session结束就丢失 | 状态文件保存，断点可恢复 |
| 崩溃处理 | 任务直接失败 | 自动重试，最多重 N 次 |
| 依赖管理 | 无 | DAG 拓扑，支持串行链 |
| 结果聚合 | 手动收集 | 共享 results/ 字段 |

---

## 使用方式

### 基础命令

```bash
# 启动并行 Convoy（3个子任务，并行执行）
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py run \
  --task "研究 AI Agent 现状与趋势" --parallel 3

# 查看所有 Convoy
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py status

# 查看具体 Convoy 详情
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py status --id convoy-abc123

# 恢复被中断的 Convoy
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py resume --id convoy-abc123

# 终止 Convoy
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py kill --id convoy-abc123

# 清理超过7天的历史记录
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py clean --days 7
```

### 串行链模式

```bash
# 链式执行（每个任务依赖前一个完成）
python3 convoy.py run \
  --task "研究 X 公司技术栈" --parallel 3 --chain
# t1 先跑 → t2 依赖 t1 → t3 依赖 t2
```

### 状态文件

Convoy 运行状态保存在：
```
~/.openclaw/workspace/.state/convoy/{convoy-id}.json
```

内容结构：
```json
{
  "convoy_id": "convoy-abc123",
  "status": "running",
  "created_at": "2026-04-13T10:00:00",
  "updated_at": "2026-04-13T10:05:00",
  "tasks": {
    "t1": {"status": "completed", "started_at": "...", "completed_at": "..."},
    "t2": {"status": "running", "started_at": "..."},
    "t3": {"status": "pending", "depends_on": ["t2"]}
  },
  "results": {
    "t1": "t1的输出结果..."
  },
  "errors": {},
  "total_cost": 0.0
}
```

---

## 触发条件

**自动触发（推荐）**：
在 cron job 或 heartbeat 中调用 convoy.py：
```
*/30 * * * * python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py run --task "..." --parallel 3
```

**手动触发**：
当你需要让一个大任务不卡住、不丢进度时

---

## 状态说明

| 状态 | 含义 |
|------|------|
| `pending` | 等待执行 |
| `running` | 执行中 |
| `completed` | 完成 |
| `failed` | 失败（已重试 N 次） |
| `skipped` | 被跳过（依赖未满足） |
| `killed` | 被手动终止 |

---

## Convoy 设计哲学

**核心原则**：Convoy 不保证单个任务成功，它保证**整体流程不中断**。

- 单个子任务失败 → 重试 → 再失败 → 标记 failed，继续其他任务
- 崩溃恢复 → 从上次状态继续，不从头跑
- 目标是**交付完整 pipeline**，不是每个子任务都完美

---

## 当前实现限制

⚠️ 当前版本（v0.1）是**状态管理 + CLI 框架**，子任务执行依赖外部 sessions_spawn 触发。
完整集成（子任务真正 spawn + 执行）需要后续迭代。

**下一步**：集成 sessions_spawn API，让 convoy.py 直接启动子Agent并追踪结果。
