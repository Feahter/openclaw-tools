---
name: feishu-debug
description: 飞书机器人故障排查与修复指南
triggers:
  - "飞书挂了"
  - "飞书不工作"
  - "feishu not working"
  - "feishu error"
  - "飞书配置"
  - "feishu config"
source:
  project: OpenClaw
  url: https://github.com/aianthony/openclaw
---

# 飞书机器人故障排查与修复指南

## 诊断步骤

### 1. 检查 Gateway 日志

```bash
tail -100 ~/.openclaw/logs/gateway.err.log | grep -i feishu
```

常见错误模式：

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Feishu account "default" not configured` | 未配置 appId/appSecret | 在 `channels.feishu` 添加凭证 |
| `cardkit:card:write required` | 缺少卡片消息权限 | 飞书开放平台开通权限 |
| `missing_scope` | 缺少 API 权限 | 飞书开放平台添加事件订阅 |
| `MODULE_NOT_FOUND` | 外部桥接器路径错误 | 检查 feishu-openclaw 服务状态 |

### 2. 检查配置位置

**正确的配置位置**: `channels.feishu` (不是 `plugins.entries.feishu`)

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxx",
      "appSecret": "your-secret"
    }
  }
}
```

**错误的位置** (会导致 `Unrecognized key` 错误):
```json
{
  "plugins": {
    "entries": {
      "feishu": {  // ❌ 错误位置
        "appId": "..."
      }
    }
  }
}
```

### 3. 验证配置

```bash
openclaw status
```

如果配置正确，会看到:
```
[plugins] feishu: Registered feishu_*
```

### 4. 重启 Gateway

```bash
# 方法 1: openclaw 命令
pgrep -f "openclaw-gateway" | xargs kill
openclaw gateway start

# 方法 2: launchctl
launchctl unload ~/Library/LaunchAgents/com.clawdbot.gateway.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.gateway.plist
```

## 常见问题速查

### Q: 配置文件在哪里?
A: `~/.openclaw/openclaw.json`

### Q: 如何备份配置?
A: 配置文件会自动备份为 `openclaw.json.bak`

### Q: 配置格式是什么?
A: OpenClaw 使用 JSON5 格式，支持注释

### Q: 飞书应用在哪里创建?
A: https://open.feishu.cn/app

### Q: 需要哪些权限?
A:
- `im:message` - 收发消息
- `im:message:send_as_bot` - 以机器人发消息
- `im:resource` - 上传下载图片
- `cardkit:card:write` - 卡片消息 (可选，流式回复需要)

### Q: 如何测试配置是否生效?
A: 在飞书里给机器人发消息，检查日志:
```bash
tail -f ~/.openclaw/logs/gateway.err.log | grep feishu
```

## 故障排查流程图

```
┌─────────────────┐
│ 检查日志错误信息  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 配置未生效?      │
│ (看下一条)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   是         否
    │         │
    ▼         ▼
┌───────┐  ┌────────────────┐
│检查位置│  │检查具体错误类型 │
└───┬───┘  └───────┬────────┘
    │              │
    ▼              ▼
channels.feishu  ┌─────────────────────┐
    │            │                     │
    ▼            ▼                     ▼
┌───────┐   凭证错误      权限错误      服务错误
│修复位置│  ┌─────┐    ┌──────┐    ┌──────┐
└───┬───┘  │添加  │    │开通  │    │重启  │
    │      │appId│    │权限  │    │服务  │
    └─────►└─────┘    └──────┘    └──────┘
```

## 快速修复命令

```bash
# 1. 检查状态
openclaw status

# 2. 查看飞书日志
tail -50 ~/.openclaw/logs/gateway.err.log | grep feishu

# 3. 重启 Gateway
pgrep -f "openclaw-gargs kill &&ateway" | x openclaw gateway start

# 4. 验证配置语法
node -e "JSON.parse(require('fs').readFileSync('/Users/fuzhuo/.openclaw/openclaw.json'))" && echo "OK"
```

## 相关文件位置

- 配置: `~/.openclaw/openclaw.json`
- 日志: `~/.openclaw/logs/gateway.err.log`
- 备份: `~/.openclaw/openclaw.json.bak`
- 凭证目录: `~/.openclaw/credentials/`
- 桥接器: `~/.openclaw/workspace/feishu-openclaw/`
