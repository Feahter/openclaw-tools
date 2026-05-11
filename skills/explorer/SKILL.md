---
name: explorer
description: >
  探索者 Agent，网络海洋的航海日志。每天出海发现有趣项目，打捞珍宝。
  触发：探索、今日出海、发现新项目、打捞、explorer、航海日志、发现有趣项目。
keywords:
  - explorer
  - 探索
  - 出海
  - 打捞
  - 航海
  - 发现
---

# 🚢 Explorer — 探索者 Agent

## What it does

把网络视为海洋，每天出海航行发现有趣项目，打捞 feZ 会感兴趣的珍奇异宝。与 BuilderPulse 互补：Explorer 更广撒网多源探索，BuilderPulse 更深分析+趋势解读。

## When to trigger

- 用户说"探索"、"今日出海"、"发现新项目"
- 用户说"打捞"、"航海日志"
- Cron 6:30 AM 自动触发
- 用户说"explorer"、"发现有趣项目"

## Step 1: 出海准备

1. 确定今日兴趣方向（如：AI Agent + 本地运行）
2. 加载已发现项目库（去重）

## Step 2: 撒网探索

并行获取多源：
1. Hacker News（AI 相关，30%权重）
2. GitHub Trending（Python/ML，25%权重）
3. GitHub 最近7天活跃项目（20%权重）
4. IndieHackers（商业模式，15%权重）
5. Google Trends（热度，10%权重）

## Step 3: 筛选珍宝

**包含条件**：
- AI/Agent/编程领域
- 最近 7 天更新
- ⭐ ≥ 100 或 votes ≥ 20

**排除条件**：
- 30天内已记录
- 纯营销内容
- 无代码/无法落地

## Step 4: 生成报告

输出探索日志，标记珍宝候选供后续研究。

## Output format

```markdown
🚢 探索者日志 | YYYY-MM-DD

🌊 出海方向：[今日兴趣方向]

🎣 撒网收获：
1. [项目] - ⭐N - [一句话描述]
   来源：xxx
2. ...

💎 珍宝候选（可研究）：
1. [项目] - [值得研究的原因]
2. ...

⚓ 锚定：下次探索方向

---
```

## Examples

**Input:** "探索"
**Output:** 探索日志（3-5个发现 + 珍宝候选）

**Input:** "今日出海"
**Output:** 当日探索日志

**Input:** 6:30 AM Cron 触发
**Output:** 自动探索 + 邮件/飞书推送

## Test cases

| Input | Expected | 说明 |
|-------|----------|------|
| "探索" | 报告含 3+ 项目 | 手动触发 |
| "explorer" | 探索日志 | 关键词触发 |
| 空触发（cron） | 自动生成报告 | 定时任务 |

## 与其他 Skills 协同

- 🚢 Explorer（6:30）→ 撒网发现
- 📰 BuilderPulse（8:30）→ 汇总分析
- 📚 编程学习（10:30）→ 深度研究

## 去重机制

已发现项目保存在 `~/.openclaw/workspace/memory/explorer-discovered.json`，30天内不重复发现。