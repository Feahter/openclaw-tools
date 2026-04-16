# weekly-self-review

## 描述

每周自省扫描技能，对标 **Hermes Agent nudge 机制**。每周一 09:00 自动运行，扫描上周 session 日志，识别高频短查询和意图领域，生成技能建议并推送飞书。

## 核心能力

### 1. 高频短查询识别
- 扫描 memory/ 目录中最近 7 天的日志文件
- 提取用户短 query（≤15字），统计频率
- ≥5 次出现 → 触发 skill 创建建议

### 2. 意图领域统计
- 10 个预设领域：八字/命理、天气、新闻、搜索、写作、代码、提醒、文件整理、飞书、邮件
- 统计每个领域的关键词出现次数
- ≥10 次 → 建议扩充覆盖度

### 3. Hermes nudge 等效
- Hermes：任务后自动生成 SKILL.md + Nudge 推送
- 本 skill：每周扫描 + skill 建议推送
- 差异：Hermes 实时触发，本 skill 每周一次

## 使用方式

```bash
python3 skills/weekly-self-review/scripts/weekly_self_review.py
```

## Cron 配置

```
每周一 09:00
0 9 * * 1
```

## 状态文件

`~/.openclaw/workspace/.state/weekly-review-state.json`

```json
{
  "last_review": "2026-04-15T09:00:00",
  "last_patterns": {
    "short_queries": {"查天气": 8, "八字": 6},
    "intent_domains": {"天气": 12, "八字/命理": 8}
  },
  "last_skills_suggested": [...]
}
```

## 输出示例（飞书推送）

```
📊 本周自省报告

🔍 高频短查询（出现 ≥5 次）
  查天气 × 8
  八字分析 × 6

🎯 意图领域分布
  天气: 12 次
  八字/命理: 8 次

💡 技能建议
  • 「查天气」×8 → 建议建 dedicated skill
  • 「天气」领域上周出现 12 次，建议检查现有 skill 覆盖度
```

## 与 Hermes 的差距

| 能力 | Hermes | 本 skill |
|------|--------|---------|
| 实时检测任务完成 | ✅ | ❌ |
| 立即生成 SKILL.md | ✅ | ❌ |
| 周/日周期扫描 | ✅ | ✅ |
| 推送飞书 | ✅ | ✅ |
| 意图领域识别 | ✅ | ✅ |

**差距原因**：OpenClaw 没有任务完成 hook，只能靠 cron 轮询。要真正对标 Hermes 需要 OpenClaw 底层支持 `on_task_complete` 事件。
