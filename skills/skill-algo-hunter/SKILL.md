---
name: skill-algo-hunter
description: |
  主动发现并捕获新算法。监控 arxiv cs.AI 和 GitHub trending，定期发现新算法 → RESEARCH 模式深度研究 → 追加到 skill-algo-master 的 algorithms.md。

  **触发场景**：
  - cron 定时触发（每天/每周）
  - feZ 说"扫一下最近有什么新算法"
  - feZ 说"检查 arxiv 有没有新算法"

  **不触发**：feZ 在讨论具体业务逻辑，没有算法研究需求
---

# skill-algo-hunter — 算法猎手

主动发现 + 深度研究 + 归档到 skill-algo-master。

---

## 猎取流程

```
① 扫描信号源
    ↓
② 过滤算法相关论文/项目
    ↓
③ 排序：stars/引用/paper 质量
    ↓
④ RESEARCH 模式深度研究 Top 3
    ↓
⑤ 归档到 algorithms.md + 决策表
    ↓
⑥ 报告摘要
```

---

## ① 信号源扫描

| 来源 | 扫描目标 | 优先级 |
|------|---------|--------|
| arxiv cs.AI | 过去7天新提交 | ⭐⭐⭐⭐⭐ |
| GitHub trending（Python/JS）| 过去24小时热榜 | ⭐⭐⭐ |
| Hacker News | 算法相关讨论 | ⭐⭐ |
| Papers With Code | 近期热门论文 | ⭐⭐⭐ |

### arxiv 扫描

```bash
# 获取 cs.AI 最近7天新提交
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending" \
  | grep -E "<title>|<summary>" | head -40
```

### GitHub Trending

```bash
# 获取 Python trending
curl -s "https://api.github.com/search/repositories?q=algorithm+OR+%22data+structure%22+created:>$(date -v-7d +%Y-%m-%d)&sort=stars&per_page=10"
```

---

## ② 算法过滤关键词

在标题/摘要中出现以下词 → 标记为候选：

```
algorithm, data structure, optimization, graph, neural network,
transformer, reinforcement learning, clustering, classification,
regression, prediction, detection, segmentation, generation,
embedding, alignment, inference, training, compression,
approximation, heuristic, heuristic, sampling, search
```

**过滤排除词**（不是算法论文）：
```
web, mobile, database, security（纯安全，非加密算法）,
network protocol, operating system, hardware, visualization
```

---

## ③ 排序评分

| 指标 | 权重 | 说明 |
|------|------|------|
| GitHub stars | 30% | 社区热度 |
| arxiv 引用 | 25% | 学术影响力 |
| Papers With Code | 20% | 代码可用性 |
| 标题关键词匹配 | 15% | 算法核心词 |
| 新鲜度 | 10% | 越新越高 |

---

## ④ RESEARCH 模式深度研究

对 Top 3 候选执行 skill-algo-master RESEARCH 模式：

```
触发 skill-algo-master
  → 7步SOP研究
  → 得到完整报告
  → 追加 algorithms.md
```

**注意**：不替代 skill-algo-master，直接调用其 RESEARCH 能力。

---

## ⑤ 归档

研究完成后：

1. 追加到 `~/.openclaw/workspace/skills/skill-algo-master/references/algorithms.md`
2. 在 skill-algo-master SKILL.md 决策表追加一行（移除 ⚠️ 标注）
3. 更新 `references/hunt-log.md`（狩猎日志）

---

## ⑥ 报告格式

```
## 算法猎手报告 — YYYY-MM-DD

### 信号源扫描
- arxiv cs.AI：发现 N 篇候选
- GitHub trending：发现 N 个项目

### 候选池（Top 5）
| 排名 | 名称 | 来源 | 评分 |
|------|------|------|------|
| 1 | xxx | arxiv | 8.5 |
| 2 | xxx | GitHub | 7.2 |

### 已归档
- [算法名] → algorithms.md ✅

### 决策表已更新
- skill-algo-master SKILL.md 已移除 ⚠️
```

---

## cron 配置

建议每天 10AM 编程学习后执行一次：

```bash
# 在编程学习 cron 后追加
python3 skills/skill-algo-hunter/scripts/algo_hunter.py
```

或通过 HEARTBEAT 触发（每24小时一次）。

---

## references

- `scripts/algo_hunter.py` — 扫描脚本
- `references/hunt-log.md` — 狩猎日志
