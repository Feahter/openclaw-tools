---
name: convoy-engine
description: |
  Convoy 多子Agent并行执行引擎。触发场景：(1) 需要多个子Agent并行执行独立任务 (2) 需要任务状态持久化 + 断点恢复 (3) 需要 DAG 依赖管理（串行链/并行分叉）(4) 需要结果聚合报告。
  核心设计：Convoy 引擎作为 OpenClaw AI Agent 的状态管理层，通过 sessions_spawn 工具调用来 spawn 子Agent，状态文件持久化到 ~/.openclaw/workspace/.state/convoy/。
  使用方式：先运行 convoy.py 定义任务，AI Agent 读取状态文件并调用 sessions_spawn 执行每个任务，最后聚合结果。
---

# Convoy Engine — 多子Agent并行执行引擎

> Convoy 不是 OpenClaw 内核的一部分，而是你在 sessions_spawn 之上构建的状态管理层。
> 它解决的是：子Agent崩溃怎么办？结果怎么聚合？断点怎么恢复？

## 核心架构

```
用户/AI Agent
    │
    ├─→ convoy.py run --task "研究X" --parallel 3
    │       └─→ 创建状态文件 (.state/convoy/{id}.json)
    │
    ├─→ AI Agent 读取状态文件
    │       ├─→ sessions_spawn(task=t1) ──→ 子Agent执行
    │       ├─→ sessions_spawn(task=t2) ──→ 子Agent执行  (并行)
    │       └─→ sessions_spawn(task=t3) ──→ 子Agent执行
    │
    └─→ AI Agent 更新状态文件 ──→ 结果聚合
```

**关键约束**：convoy.py 是状态管理层 + CLI 工具，**真正的 sessions_spawn 必须通过 AI Agent 的 tool call 执行**，无法从 Python 脚本直接调用。

## 快速开始

### 第一步：定义 Convoy 任务

```bash
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py run \
  --task "研究 OpenClaw Agent 架构" \
  --parallel 3
```

输出：
```
🚀 启动 Convoy convoy-abc123，3 个任务，并行数 3

执行步骤：
  1. sessions_spawn --task "研究 OpenClaw Agent 架构 [任务 1/3]" --label convoy-t1 --mode run
  2. sessions_spawn --task "研究 OpenClaw Agent 架构 [任务 2/3]" --label convoy-t2 --mode run
  3. sessions_spawn --task "研究 OpenClaw Agent 架构 [任务 3/3]" --label convoy-t3 --mode run

查看状态：convoy.py status --id convoy-abc123
```

### 第二步：AI Agent 执行 sessions_spawn

AI Agent 读取状态文件，对每个 pending 任务调用 `sessions_spawn`：

```python
# 伪代码（AI Agent 执行）
state = read_json("~/.openclaw/workspace/.state/convoy/convoy-abc123.json")
for task_id, task in state["tasks"].items():
    if task["status"] == "pending":
        spawn(
            task=task["prompt"],
            label=f"convoy-{task_id}",
            mode="run"
        )
        update_state(task_id, status="running", session_key=result.session_key)
```

### 第三步：轮询状态 + 结果聚合

子Agent完成后，读取状态文件聚合结果：

```bash
python3 ~/.openclaw/workspace/skills/convoy-engine/scripts/convoy.py status --id convoy-abc123
```

## CLI 命令参考

```bash
# 启动并行 Convoy（自动生成子任务）
convoy.py run --task "研究 X" --parallel 3

# 启动串行链 Convoy（t1→t2→t3）
convoy.py run --task "研究 X" --parallel 3 --chain

# 查看所有 Convoy
convoy.py status

# 查看指定 Convoy 详情
convoy.py status --id convoy-abc123

# 恢复被中断的 Convoy（重新 spawn pending/failed 任务）
convoy.py resume --id convoy-abc123

# 终止 Convoy
convoy.py kill --id convoy-abc123

# 清理 7 天前的历史记录
convoy.py clean --days 7
```

## 状态文件结构

```json
{
  "convoy_id": "convoy-abc123",
  "created_at": "2026-04-13T22:30:00",
  "updated_at": "2026-04-13T22:31:00",
  "status": "running",
  "tasks": {
    "t1": {
      "status": "completed",
      "started_at": "2026-04-13T22:30:05",
      "completed_at": "2026-04-13T22:32:26",
      "session_key": "agent:main:subagent:abc123",
      "error": null,
      "retry_count": 0,
      "prompt": "研究 OpenClaw Agent 架构 [任务 1/3]",
      "depends_on": []
    },
    "t2": {
      "status": "running",
      "started_at": "2026-04-13T22:30:05",
      "completed_at": null,
      "session_key": "agent:main:subagent:def456",
      "error": null,
      "retry_count": 0,
      "prompt": "研究 OpenClaw Agent 架构 [任务 2/3]",
      "depends_on": []
    }
  },
  "results": {
    "t1": "<子Agent返回的完整结果>"
  },
  "errors": {},
  "total_cost": 0.0
}
```

## AI Agent 集成流程（完整）

```python
"""
Convoy Engine × OpenClaw Agent 集成

这个流程说明 AI Agent 如何与 convoy.py 配合使用。
"""

import json
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "workspace" / ".state" / "convoy"

def read_convoy(convoy_id: str) -> dict:
    return json.loads((STATE_DIR / f"{convoy_id}.json").read_text())

def update_task(convoy_id: str, task_id: str, **updates):
    state = read_convoy(convoy_id)
    for k, v in updates.items():
        state["tasks"][task_id][k] = v
    state["updated_at"] = datetime.now().isoformat()
    (STATE_DIR / f"{convoy_id}.json").write_text(json.dumps(state, indent=2))

# AI Agent 主循环
def run_convoy(convoy_id: str):
    while True:
        state = read_convoy(convoy_id)
        
        # 1. 找所有 pending 任务（考虑依赖）
        pending = [
            (tid, t) for tid, t in state["tasks"].items()
            if t["status"] == "pending" and all(
                state["tasks"][dep]["status"] == "completed"
                for dep in t.get("depends_on", [])
            )
        ]
        
        # 2. 启动可以执行的任务（不超过 max_parallel）
        running = sum(1 for t in state["tasks"].values() if t["status"] == "running")
        for task_id, task in pending:
            if running >= max_parallel:
                break
            result = sessions_spawn(
                task=task["prompt"],
                label=f"convoy-{convoy_id[:8]}-{task_id}",
                mode="run"
            )
            update_task(convoy_id, task_id,
                status="running",
                session_key=result["childSessionKey"]
            )
            running += 1
        
        # 3. 检查是否全部完成
        if all(t["status"] in ("completed", "failed", "skipped")
               for t in state["tasks"].values()):
            break
        
        sleep(10)  # 轮询间隔

# AI Agent 读取结果
def aggregate_results(convoy_id: str) -> str:
    state = read_convoy(convoy_id)
    report = f"# Convoy {convoy_id} 结果报告\n\n"
    for task_id, task in state["tasks"].items():
        report += f"## {task_id}: {task['status']}\n"
        if task_id in state.get("results", {}):
            report += state["results"][task_id] + "\n\n"
        elif task.get("error"):
            report += f"❌ 错误: {task['error']}\n\n"
    return report
```

## 与 ClawTeam-OpenClaw 的关系

| 维度 | Convoy Engine | ClawTeam-OpenClaw |
|------|--------------|-------------------|
| 定位 | 状态管理层 + 任务编排 | 生产级多Agent协作平台 |
| 执行依赖 | sessions_spawn (AI Agent tool) | 任意 CLI Agent |
| 状态持久化 | JSON 文件 | FileTaskStore (kanban) |
| 故障恢复 | 自动重试 | Circuit Breaker |
| 通信机制 | 共享状态文件 | FileTransport / ZMQ |
| 适用场景 | OpenClaw 内多子Agent并行 | 跨工具、跨机器协调 |

**推荐组合**：Convoy Engine 负责 OpenClaw 内的多子Agent并行任务，ClawTeam 负责跨工具/跨机器的复杂协作。

## 已知限制

1. **sessions_spawn 必须通过 AI Agent 调用**：Python 脚本无法直接调用 OpenClaw 内部工具
2. **结果回写需要 AI Agent 完成**：子Agent的结果目前不会自动写入状态文件，需要 AI Agent 在子Agent完成后的下一轮对话中主动更新
3. **Gateway 必须稳定**：子Agent的 spawn 依赖 Gateway 可用性，Gateway 不稳则 Convoy 无法运行
