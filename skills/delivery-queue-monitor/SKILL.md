---
name: delivery-queue-monitor
description: >
  Delivery Queue 主动监控与告警 Skill
  触发：delivery/投递/死信/dead-letter/健康度/consecutive/announce失败
  
  功能：
  1. 读取 delivery-queue/status.json 健康度
  2. 检查 dead-letter/ 是否有新死信
  3. 判断 health 状态（OK/WARNING/CRITICAL）
  4. CRITICAL 时主动推送飞书给 feZ
  5. 记录每日投递统计到 memory/
  
  触发词：检查投递状态/delivery健康/死信检查/投递失败
---

# Delivery Queue Monitor

## 快速检查

```bash
cat ~/.openclaw/delivery-queue/status.json
ls ~/.openclaw/delivery-queue/dead-letter/ | wc -l
```

## 判断逻辑

| health | 状态 | 动作 |
|--------|------|------|
| OK | 无问题 | 只记录 |
| WARNING | 3+连续失败 | 记录 + 观察 |
| CRITICAL | 5+连续失败 | 立即飞书告警 |

## 每日统计
写入 `memory/YYYY-MM-DD.md`:
```
## Delivery Queue 统计
- total_deliveries: X
- total_failures: X
- consecutive_failures: X
- health: OK/WARNING/CRITICAL
```

## 异常处理流程
1. 读取 status.json
2. 检查 dead-letter 数量
3. 如果 CRITICAL → 调用 feishu_im_user_message 推送告警
4. 写入 memory 记录
