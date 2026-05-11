---
name: gateway-health-monitor
description: >
  OpenClaw Gateway + LaunchAgent 健康监控 Skill
  触发：检查网关状态/健康/进程/gateway/launchd/端口
  

  
  触发词：网关状态/健康检查/gateway进程/launchd/端口检测
---

# Gateway Health Monitor

## 检查步骤

### 1. Gateway 进程检查
```bash
ps aux | grep openclaw-gateway | grep -v grep
lsof -i :18789 -i :28789 2>/dev/null | grep LISTEN
```

### 2. Delivery Queue 健康度
```bash
cat ~/.openclaw/delivery-queue/status.json
ls ~/.openclaw/delivery-queue/dead-letter/ | wc -l
```

### 3. Launchd 状态
```bash
launchctl list | grep openclaw
```

### 4. 判断逻辑
- `health: CRITICAL` → 立即告警 + 尝试重启
- `health: WARNING` → 记录 + 观察
- gateway 进程消失 → 尝试 launchctl start 或直接重启

### 5. 输出格式
```
## Gateway Health Report

| 通道 | 端口 | 状态 | PID | 上次健康 |
|------|------|------|-----|---------|
| feishu | 18789 | running | xxx | 18:12 |
| wechat | 28789 | running | xxx | 18:10 |

Delivery Queue: OK (0 failures)
Launchd: 2/2 running
```

## 异常处理

### Gateway 挂了
```bash
# 尝试重启 launchd
launchctl start ai.openclaw.gateway.feishu
launchctl start ai.openclaw.gateway.wechat

# 如果 launchd 不响应，直接重启进程
openclaw gateway start
```

### Delivery CRITICAL
调用 `delivery-queue.js --health` 并推送飞书告警给 feZ
