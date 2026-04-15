# OpenCode + Tmux 整合指南

## 概述

基于高星 tmux skill 的最佳实践，将 OpenCode 与 tmux 整合，实现持久会话和多任务并行。

## 架构

```
OpenClaw → opencode-tmux-bridge.py → tmux (socket 模式) → OpenCode
```

## 快速开始

### 1. 基本用法

```bash
# 运行单次任务
python tools/opencode-tmux-bridge.py "分析 tools 目录"

# 自定义超时
python tools/opencode-tmux-bridge.py "复杂任务" --timeout 300
```

### 2. 持久会话模式

```python
from tools.opencode_tmux_bridge import *

# 确保会话存在
ensure_session()

# 发送命令
send_command("分析代码")

# 获取输出
output = get_output(wait=15)
print(output)
```

### 3. 多会话并行

```bash
# 创建多个会话
SOCKET="/tmp/opencode-tmux-sockets/opencode.sock"

tmux -S $SOCKET new-session -d -s agent-1
tmux -S $SOCKET new-session -d -s agent-2  
tmux -S $SOCKET new-session -d -s agent-3

# 并行运行不同任务
tmux -S $SOCKET send-keys -t agent-1 "opencode run '任务1'" C-m
tmux -S $SOCKET send-keys -t agent-2 "opencode run '任务2'" C-m
tmux -S $SOCKET send-keys -t agent-3 "opencode run '任务3'" C-m

# 监控完成状态
for sess in agent-1 agent-2 agent-3; do
  if tmux -S $SOCKET capture-pane -p -t $sess -S -3 | grep -q "❯"; then
    echo "$sess: DONE"
  fi
done
```

## Socket 模式优势

| 特性 | 普通模式 | Socket 模式 |
|------|---------|------------|
| 权限隔离 | ❌ | ✅ |
| 多用户 | ❌ | ✅ |
| 并行会话 | 困难 | 容易 |
| 状态监控 | 基本 | 高级 |

## 关键命令

```bash
# 列出所有会话
tmux -S /tmp/opencode-tmux-sockets/opencode.sock list-sessions

# 连接到会话
tmux -S /tmp/opencode-tmux-sockets/opencode.sock attach -t opencode

# 杀死会话
tmux -S /tmp/opencode-tmux-sockets/opencode.sock kill-session -t opencode

# 等待特定文本
./scripts/wait-for-text.sh -t opencode:0.0 -p "完成" -T 30
```

## 监控完成状态

```bash
# 检查是否有 shell 提示符（表示命令完成）
tmux capture-pane -p -t session -S -3 | grep -q "❯" && echo "完成"
```

## 配置

环境变量:
- `CLAWDBOT_TMUX_SOCKET_DIR`: Socket 目录 (默认: /tmp/opencode-tmux-sockets)
