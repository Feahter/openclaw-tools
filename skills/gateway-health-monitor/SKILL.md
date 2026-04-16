# gateway-health-monitor

## 描述

飞书 Gateway 健康检查技能。监控 `gateway-feishu.log` 中的消息接收和回复（reaction event）情况，连续 2 次 reply rate 低于 50% 时触发飞书告警。

## 触发场景

- 每 5 分钟 cron 自动检查
- 手动诊断飞书不回复时运行

## 使用方式

```bash
python3 skills/gateway-health-monitor/scripts/gateway_health_checker.py
```

**Exit codes:**
- `0` = 健康
- `2` = 告警触发（reply rate 过低）
- `3` = 未知状态（无数据）

## 检测逻辑

1. 读取 `~/.openclaw/logs/gateway-feishu.log` 最近 15 分钟日志
2. 统计 `received message` 数量和 `reaction event` 数量
3. 计算 reply rate = replied / received
4. 连续 2 次 rate < 50% 且 total >= 2 → 告警
5. 告警通过 `print()` 输出（由 cron 任务捕获并推送飞书）

## 状态文件

`~/.openclaw/workspace/.state/gateway-health-state.json`

```json
{
  "consecutive_failures": 0,
  "last_check": "2026-04-15T18:00:00",
  "last_alert": null,
  "reply_rates": [0.8, 0.9, 1.0, 0.7]
}
```

## Cron 配置

```
每 5 分钟检查一次
*/5 * * * * cd /Users/fuzhuo/.openclaw/workspace && python3 skills/gateway-health-monitor/scripts/gateway_health_checker.py
```

告警触发时输出包含：`⚠️ 飞书 Gateway 告警` 标记，供 cron handler 识别并推送飞书。
