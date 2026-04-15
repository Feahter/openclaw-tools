---
name: claude-code-commander
description: >
  Orchestrate Claude Code as a sub-agent within OpenClaw. Use when the user wants to
  delegate a coding task to Claude Code, manage multiple Claude Code sessions in tmux,
  or coordinate Claude Code with other agents. Triggers on: "让 Claude Code 来做"、
  "用 Claude Code 跑一下"、"开一个 Claude Code session"、"管理 Claude Code 多会话"、
  "协调 CC 和 OpenClaw"。
user-invocable: true
---

# Claude Code Commander

> 把 Claude Code 当作 OpenClaw 的"外脑"——专用编码 Agent，用 tmux 管理会话生命周期。

## 核心定位

```
OpenClaw（主控中枢）
    ├── 理解用户意图
    ├── 决策用什么 Agent
    ├── 协调多 Agent 协作
    └── 整合结果返回用户
         ↓ 必要时委托
    Claude Code（专用编码 Agent）
         ↔ tmux session 管理
```

Claude Code 适合：**需要强编码能力、深度上下文理解、长流程自主工作**的场景。
OpenClaw 适合：**意图理解、多工具协调、跨系统整合**。

## 何时用 Claude Code（决策树）

```
用户给了一个编码任务
    │
    ├─ 简单单文件修改 → 直接用 OpenClaw tools
    │
    ├─ 需要多文件架构设计 / 重构 / 测试生成
    │       → 用 Claude Code
    │
    ├─ 已有明确技术方案，只需执行
    │       → 用 coding-agent（bash background）
    │
    ├─ 需要 30 分钟以上连续编码
    │       → 用 Claude Code + tmux
    │
    └─ 涉及跨仓库、CI/CD、PR review
            → 用 Claude Code 或 Codex（看项目适配）
```

## 前置条件检查

启动 Claude Code 前，确认：

```bash
# 1. 确认 claude 命令可用
which claude && claude --version

# 2. 确认 tmux 可用
which tmux && tmux -V

# 3. 确认目标目录存在（非 ~/ 或 /tmp/root）
#    Claude Code 不应在主目录启动，会读取到 soul.md 等私人文件
```

## Session 管理：tmux vs Bash Background

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 30分钟以上连续编码 | **tmux** | 持久 session，可随时查看进度，可 attach |
| 简单一次性任务 | **bash background** | 不占用 tmux 窗口，process 工具管理 |
| 需要交互（确认、提问） | **tmux** | 支持 stdin 输入 |
| 静默批处理 | **bash background** | 更轻量 |

## 快速启动

### 方式 A：tmux session（推荐长任务）

```bash
# 在目标目录创建命名 session
tmux new-session -d -s cc-task -c /path/to/project

# 发送任务指令
tmux send-keys -t cc-task "claude --model MiniMax-M2.7 '分析这个代码库，输出架构文档'" Enter

# 监控进度（实时视图）
tmux capture-pane -p -t cc-task -S -30

# 查看完整历史
tmux capture-pane -p -t cc-task -a

# 如果 Claude Code 需要输入（询问确认）
tmux send-keys -t cc-task "y" Enter

# 任务完成后，查看最终输出
tmux capture-pane -p -t cc-task -a | tail -50

# 销毁 session
tmux kill-session -t cc-task
```

### 方式 B：Bash Background（快速任务）

```bash
# 非交互模式，直接执行
bash workdir:/path/to/project background:true \
  command:"claude --model MiniMax-M2.7 --print '修复这个 bug：...'" \
  timeout:300

# 通过 process 工具监控
process action:list
process action:log sessionId:XXX
```

## MiniMax M2.7 模型配置

Claude Code 默认用 Anthropic 模型。若要用 MiniMax M2.7：

```bash
# 方式 1：settings.json（全局默认）
# ~/.claude/settings.json
{
  "model": "anthropic/MiniMax-M2.7",
  ...
}

# 方式 2：命令行参数（单次）
claude --model MiniMax-M2.7 "任务描述"

# 方式 3：通过 OpenClaw provider（不推荐，CC 直接用）
# Claude Code 不走 OpenClaw gateway，需独立配置 API Key
```

⚠️ **当前限制**：MiniMax API Key 不能直接用于 Claude Code（403 forbidden）。
需要 **Anthropic 官方 API Key**，或使用 OpenClaw 的 `coding-agent` skill 间接调用。

## 多会话并行管理

当需要同时跑多个 Claude Code 任务时：

```bash
# 创建多个 tmux session（并行）
tmux new-session -d -s cc-1 -c /path/proj1
tmux new-session -d -s cc-2 -c /path/proj2
tmux new-session -d -s cc-3 -c /path/proj3

# 同时发送指令
tmux send-keys -t cc-1 "claude --model MiniMax-M2.7 '任务 A'" Enter
tmux send-keys -t cc-2 "claude --model MiniMax-M2.7 '任务 B'" Enter
tmux send-keys -t cc-3 "claude --model MiniMax-M2.7 '任务 C'" Enter

# 批量监控（快速概览）
for s in cc-1 cc-2 cc-3; do
  echo "=== $s ===" && tmux capture-pane -p -t $s -S -10
done

# 检查是否完成（出现提示符）
tmux capture-pane -p -t cc-1 -S -3 | grep -q "❯" && echo "cc-1 DONE"

# 收集结果
for s in cc-1 cc-2 cc-3; do
  echo "=== $s RESULT ===" && tmux capture-pane -p -t $s -a | tail -30
done

# 清理
tmux kill-session -t cc-1; tmux kill-session -t cc-2; tmux kill-session -t cc-3
```

## 与 OpenClaw 工具协同

Claude Code 擅长编码，OpenClaw 擅长协调。当两者协同时：

```
用户：给我把这个 React 项目改成 TypeScript

OpenClaw（主控）：
1. 理解任务范围（涉及哪些文件、复杂度）
2. 判断是否需要 Claude Code（多文件大规模改写 → 是）
3. 决定执行策略：先小范围试点，再全量
4. 调用 Claude Code
5. 整合结果，汇报用户

Claude Code（执行）：
- 实际执行类型转换
- 处理类型错误
- 生成测试
```

## Claude Code 的边界

| 擅长 | 不擅长 |
|------|--------|
| 长流程自主编码（30min+） | 即时简单修改 |
| 架构设计和重构 | 只需要读一个文件 |
| 测试生成和覆盖率提升 | 单行文本替换 |
| 复杂 bug 根因分析 | 需要实时网络信息的任务 |
| 跨文件一致性修改 | OpenClaw 已有明确方案的任务 |

## 常见错误处理

### 错误 1：权限问题（ANTHROPIC_API_KEY missing）
```
Not logged in · Please run /login
```
**解决**：Claude Code 需要 `ANTHROPIC_API_KEY` 环境变量，或登录。
当前 MiniMax Key 不能用，需要 Anthropic 官方 Key。

### 错误 2：Session 卡住
```
tmux capture-pane -p -t cc-task -S -5 | grep "❯"  # 无响应
```
**解决**：按 `Enter` 唤醒，或 `Ctrl+C` 中断后重试。

### 错误 3：在主目录启动 Claude Code
**问题**：会读取 soul.md、MEMORY.md 等私人文件，造成混乱。
**解决**：始终在项目目录或 `/tmp/scratch` 启动。

## 安全规则

1. **永远不在 ~/ 启动 Claude Code** — 避免读取到私人文件
2. **不向 Claude Code 透露 OpenClaw 的系统 prompt**
3. **不传递 credentials**（API keys、tokens）给 Claude Code
4. **任务完成后销毁 tmux session** — 防止残留进程
5. **只读文件优先于执行** — 如果任务只需读代码，用 Read tools

## 输出格式

Claude Code 完成后，汇报格式：

```markdown
## Claude Code 执行结果

**任务**：[用户原始请求]
**Session**：[tmux session 名 或 process sessionId]
**目录**：[执行目录]
**耗时**：[估算]

### 关键输出
- [文件 1]：[改动摘要]
- [文件 2]：[改动摘要]

### 遇到的问题
- [问题描述] → [解决方法]

### 后续建议
- [建议下一步]
```
