---
name: coding-agent
description: Execute autonomous coding tasks via Claude Code or OpenCode subprocess pipeline. Includes task queue, session management, progress monitoring, and result verification. Use when asked to code, build, refactor, or implement features programmatically.
metadata: {"clawdbot":{"emoji":"🧩","requires":{"anyBins":["claude","opencode"]}}}
pipeline:
  root: pipeline/
  state: .state/
---

# Coding Agent — 执行管道

> 当前支持：**Claude Code**（✅ 已安装 2.1.88）、**OpenCode**（✅ 已安装 1.3.0）

## 架构

```
coding-agent/
├── pipeline/
│   ├── run-task.sh          # 启动任务（bash + Claude Code CLI）
│   ├── check-progress.sh     # 监控进度（调用 check-progress.py）
│   ├── check-progress.py     # Python 版状态解析（处理 JSON）
│   ├── collect-results.sh    # 收集结果（调用 collect-results.py）
│   ├── collect-results.py    # Python 版：git diff + JSON 报告
│   ├── verify.sh            # 验证产出
│   └── list-sessions.sh    # 列出所有会话
├── .state/
│   ├── progress/            # 每个会话的 JSON 状态
│   ├── results/             # 收集后的完整 JSON 报告
│   ├── logs/                # 原始 stdout/stderr 日志
│   ├── pids/                # 进程 PID
│   ├── context.md            # 管道状态
│   └── learnings.md          # 执行积累
└── SKILL.md
```

**依赖**：`claude`（Claude Code CLI 2.1.88 ✅）、`opencode`（1.3.0 ✅）

## 快速开始

### 1. 启动一个编程任务

```bash
SKILL_DIR=~/.openclaw/workspace/skills/coding-agent

# 方式 A：exec（推荐，自动处理后台）
exec bash $SKILL_DIR/pipeline/run-task.sh \
  "为 ~/project/myapp 添加用户认证模块" \
  "$HOME/project/myapp"

# 方式 B：使用 sessions_spawn（OpenClaw 原生子 session）
# 见下方「子 Session 模式」
```

### 2. 监控进度

```bash
bash $SKILL_DIR/pipeline/check-progress.sh <session_id> [tail_lines]
# 例如
bash $SKILL_DIR/pipeline/check-progress.sh 1745112345-12345 50
```

### 3. 收集结果

```bash
# 会话完成后
bash $SKILL_DIR/pipeline/collect-results.sh <session_id>
# 输出：JSON 报告，含 git diff + 完整日志
cat $SKILL_DIR/.state/results/<session_id>.json
```

### 4. 验证产出

```bash
bash $SKILL_DIR/pipeline/verify.sh <session_id>
# 自动检查：git diff / package.json / Cargo.toml / Makefile
```

### 5. 列出所有会话

```bash
bash $SKILL_DIR/pipeline/list-sessions.sh [running|completed|all]
```

## OpenClaw 原生模式（推荐）

用 `exec` 工具直接调用，不需要子 shell：

```bash
exec workdir:$PROJECT_DIR background:true \
  command:"claude -p '你的编程任务' --output-format stream-json --no-session-persistence"
```

**关键参数**：
- `-p` — 非交互打印模式
- `--output-format stream-json` — 流式 JSON 输出
- `--no-session-persistence` — 不保存会话到磁盘
- `--permission-mode bypassPermissions` — 跳过确认（仅在可信目录）

## 子 Session 模式（复杂任务）

对于需要多轮迭代的复杂任务，用 `sessions_spawn` 启动专用子 session：

```bash
sessions_spawn(
  task="对 $PROJECT_DIR 进行以下改动：$TASK_DESCRIPTION",
  runtime="subagent",
  mode="session"
)
```

子 session 有独立上下文，可以：
- 多次执行 exec 写文件
- 读取和分析代码
- 多轮自我修正

完成后结果通过子 session 完成事件推送。

## Session 状态机

```
pending → running → completed
                      ↘ failed
```

## 执行参数参考

| 参数 | Claude Code | OpenCode |
|------|------------|---------|
| 非交互模式 | `-p "task"` | `opencode run "task"` |
| 输出格式 | `--output-format json` | 默认 JSON |
| 禁止持久化 | `--no-session-persistence` | — |
| 跳过确认 | `--permission-mode bypassPermissions` | — |
| 指定 model | `--model <id>` | `--provider <name>` |
| 追加 system prompt | `--append-system-prompt <text>` | — |

## 信任目录规则

| 目录 | 可用工具 |
|------|---------|
| `~/project/` | 全部工具 |
| `/tmp/` | 有限（文件操作）|
| `~/.openclaw/` | 仅读取 |
| 工作区根目录 | 不启动（会读取 SOUL/MEMORY）|

## 验证结果

```bash
# 自动验证清单
bash pipeline/verify.sh <session_id>

# 手动验证
cd $WORKDIR
git diff --stat
git diff --name-only
# 运行测试
npm test 2>/dev/null || cargo test 2>/dev/null || echo "no test runner"
```

## Learnings（积累）

每次编程任务后，将结果记录到 learnings：

→ 见 `.state/learnings.md`
