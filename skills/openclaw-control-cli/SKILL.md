---
name: openclaw-control-cli
description: |
  CLI tools for OpenClaw gateway management. Two implementations:
  - Python (config file): safe offline config editing, no auth needed
  - Node.js (WebSocket): full gateway protocol, real-time status, requires gateway auth

  Use when user wants to:
  - Check gateway status / health
  - Configure proxy settings
  - List active sessions or channels
  - Get/set gateway config values
  - Manage gateway via protocol

triggers:
  - "代理设置"
  - "gateway status"
  - "openclaw 配置"
  - "proxy"
  - "gateway 会话"
  - "channel 状态"
metadata:
  openclaw:
    emoji: "🔧"
---

# OpenClaw Control CLI

提供两种实现，推荐按场景选用：

| 工具 | 场景 | 认证 |
|------|------|------|
| **Python** (`openclaw-control-cli.py`) | 离线配置编辑、代理设置 | 文件读写权限即可 |
| **Node.js** (`openclaw-control-cli.js`) | 实时状态、会话管理、完整 gateway 控制 | gateway token/password |

---

## Python 版：配置文件直写

适合离线场景，直接读写 `~/.qclaw/openclaw.json`，不需要 gateway 在线。

**路径**：`{openclaw_workspace_dir}/scripts/openclaw-control-cli.py`

```bash
# 查看状态
python3 .../openclaw-control-cli.py status

# 代理管理
python3 .../openclaw-control-cli.py proxy show
python3 .../openclaw-control-cli.py proxy set http://127.0.0.1:7890
python3 .../openclaw-control-cli.py proxy clear

# 配置管理
python3 .../openclaw-control-cli.py config get
python3 .../openclaw-control-cli.py config get gateway.port
python3 .../openclaw-control-cli.py config set gateway.port 28790

# 编辑配置文件
python3 .../openclaw-control-cli.py edit
```

**注意**：修改后需重启 QClaw 应用；配置文件自动备份为 `.json.bak`。

---

## Node.js 版：Gateway WebSocket 协议

通过 OpenClaw gateway 的 WebSocket API，支持实时状态查询和原子配置写入。

**路径**：`{openclaw_workspace_dir}/scripts/openclaw-control-cli.js`

**前置条件**：需要安装 `ws` 包（`npm install ws`）

**连接并查询状态**：
```bash
OPENCLAW_TOKEN=your_token node .../openclaw-control-cli.js connect
```

**可用命令**：
```bash
# 连接 + 查看状态
node .../openclaw-control-cli.js connect

# 查看 gateway 健康
node .../openclaw-control-cli.js status

# 查看活跃 session
node .../openclaw-control-cli.js sessions

# 查看 channel 状态
node .../openclaw-control-cli.js channels

# 查看配置
node .../openclaw-control-cli.js config

# 设置代理（连接后）
node .../openclaw-control-cli.js connect --proxy http://127.0.0.1:7890
```

**环境变量**：
```bash
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:28789  # gateway 地址（默认）
OPENCLAW_TOKEN=xxx   # gateway token（二选一）
OPENCLAW_PASSWORD=xxx  # gateway password（二选一）
```

**认证 scope**：JS 版使用 `role: operator`，需要以下权限：
- `operator.admin` — 配置管理
- `operator.approvals` — 审批管理
- `operator.pairing` — 配对管理

---

## Gateway Protocol 架构（JS 版）

```
Client (CLI)  --WebSocket-->  Gateway (ws://127.0.0.1:28789)
                              │
                              ├── health        → 健康检查
                              ├── sessions.list → 活跃会话
                              ├── channels.status → 通道状态
                              ├── config.get/set → 原子配置读写
                              └── connect.hello  → 初始化握手
```

**原子写入机制**：JS 版的 `config.set` 使用乐观锁——读取时获取 `baseHash`，写入时验证 hash 未变，防止并发冲突。Python 版直接写文件无此保护。

---

## 选择指南

| 需求 | 推荐 |
|------|------|
| 设置代理（离线） | Python |
| 查看实时健康状态 | JS |
| 查看活跃会话 | JS |
| 查看 channel 状态 | JS |
| 批量修改配置（离线） | Python |
| 原子配置写入（在线） | JS |
| 脱离 gateway 运行 | Python |
