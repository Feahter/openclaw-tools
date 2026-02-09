---
name: feishu
description: 飞书 AI 对话机器人集成 - 完整接入方案
triggers:
  - "feishu"
  - "飞书"
  - "lark"
  - "飞书机器人"
  - "连接飞书"
  - "feishu bot"
source:
  project: AlexAnys/feishu-openclaw
  url: https://github.com/AlexAnys/feishu-openclaw
  license: MIT
---

# 飞书 AI 对话机器人

集成 feishu-openclaw 桥接器，实现飞书与 AI 助手的完整双向对话。

## 功能特性

- ✅ 收发消息 - 支持单聊/群聊
- ✅ 媒体处理 - 图片/视频/文件收发
- ✅ 自动下载 - 图片自动转 AI 可读格式
- ✅ 开机自启 - macOS launchd 保活
- ✅ 进程隔离 - 与 Gateway 独立运行

## 使用场景

- "连接飞书" → 开始飞书集成流程
- "飞书状态" → 检查桥接服务状态
- "飞书日志" → 查看最近运行日志
- "停止飞书" → 停止桥接服务

## 前置要求

- macOS 系统
- Node.js ≥ 18
- Clawdbot/Gateway 已启动
- 飞书账号 + 开发者权限

## 集成步骤

### 1. 创建飞书机器人

```bash
# 访问飞书开放平台
# https://open.feishu.cn/app
```

1. 登录飞书开放平台
2. 点击「创建自建应用」
3. 填写应用名称（如 "AI Assistant"）
4. 进入「应用能力」→ 添加「机器人」
5. 进入「权限管理」，开通以下权限：

```
im:message          # 获取与发送消息
im:message:send_as_bot   # 以机器人身份发消息
im:message.group_at_msg  # 接收群聊 @ 消息
im:message.p2p_msg       # 接收单聊消息
im:resource         # 上传/下载图片与文件
```

6. 进入「事件与回调」→ 添加事件：

```
事件: im.message.receive_v1
接收方式: 使用长连接接收事件（关键！）
```

7. 发布应用（创建版本 → 申请上线）
8. 记录 App ID 和 App Secret

### 2. 安装桥接器

```bash
# 克隆项目
cd /Users/fuzhuo/.openclaw/workspace
git clone https://github.com/AlexAnys/feishu-openclaw.git
cd feishu-openclaw

# 安装依赖
npm install
```

### 3. 配置凭证

```bash
# 创建 secrets 目录
mkdir -p ~/.clawdbot/secrets

# 保存 App Secret（替换为你的值）
echo "your-app-secret" > ~/.clawdbot/secrets/feishu_app_secret

# 设置权限
chmod 600 ~/.clawdbot/secrets/feishu_app_secret
```

### 4. 启动服务

```bash
# 测试运行（替换 App ID）
FEISHU_APP_ID=cli_xxxxxxxxx node bridge.mjs

# 验证：在飞书里发消息给机器人，确认能收到回复
```

### 5. 开机自启

```bash
# 生成 launchd 配置
node setup-service.mjs

# 加载服务
launchctl load ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist

# 查看状态
launchctl list | grep feishu
```

## 管理命令

```bash
# 查看日志
tail -n 200 ~/.clawdbot/logs/feishu-bridge.err.log

# 停止服务
launchctl unload ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 发消息但收不到 | 检查飞书平台是否勾选"长连接接收" |
| 图片 AI 看不到 | 确认已开通 im:resource 权限 |
| 机器人不回复 | 查看日志定位问题 |
| 启动失败 | 检查 Node.js 版本 (≥18) |

## 调试模式

```bash
# 开启调试日志
cd /path/to/feishu-openclaw
echo "FEISHU_BRIDGE_DEBUG=1" > .env

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.feishu-bridge.plist

# 查看详细日志
tail -n 200 ~/.clawdbot/logs/feishu-bridge.err.log
```

## 注意事项

- 电脑关机后机器人会离线
- 需要 24/7 在线请部署到服务器
- 媒体文件默认保存在 `~/.clawdbot/media/`
- 安全起见，App Secret 不要提交到 Git
