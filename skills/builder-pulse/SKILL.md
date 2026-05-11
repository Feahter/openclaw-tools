---
name: builder-pulse
description: >
  AI 独立开发者日报生成器。每天收集精选情报，生成结构化报告并推送飞书。
  触发：今日资讯、builder-pulse、日报、AI情报、独立开发者、产品发布、趋势分析。
keywords:
  - builder-pulse
  - 日报
  - 资讯
  - 情报
  - 独立开发者
  - AI产品
---

# 🤖 BuilderPulse — AI 独立开发者日报

## 核心定位

把握全世界 Builder 的脉搏——每天为独立开发者/创业者精选值得关注的 AI 产品、趋势和机会。

## 报告结构

1. **今日 AI 产品发布** — 精选 3-5 个值得关注的 AI 产品
2. **GitHub Trending** — 增长快、有潜力的开源项目
3. **Hacker News 热点** — 开发者社区热议话题
4. **趋势洞察** — 今日最重要的 1-2 个趋势判断

## 信息源

| 源 | 内容 | 权重 |
|---|------|------|
| Hacker News | AI/Indie 产品发布 | 高 |
| GitHub Trending | 开源项目热度 | 高 |
| Product Hunt | 新产品发布 | 中 |
| IndieHackers | 商业模式/盈利 | 中 |

## 过滤规则

**入选标准**：
- 与 AI/独立开发者直接相关
- 最近 24-48 小时发布
- 有实际价值（非纯 hype）

**排除标准**：
- 纯营销内容
- 已广泛报道的重复信息
- 与目标用户无关的泛泛产品

## 使用方式

### 手动触发（推荐测试）
```
@符小助 今日资讯
@符小助 builder-pulse
@符小助 生成日报
```

### 自动推送
每天 9:00 AM 自动生成并推送飞书

## 输出格式

```markdown
# 🤖 BuilderPulse 日报
**日期**: YYYY-MM-DD

---

## 📰 今日 AI 产品发布
- [产品名] — [一句话描述]
- ...

## 🚀 GitHub Trending
- **[repo]** (⭐N) — [描述]

## 💡 趋势洞察
[今日最重要的趋势判断]

---

*由 BuilderPulse 自动生成*
```

## 测试用例

### Test 1: 正常生成
**Input:** `今日资讯`
**Expected:** 生成包含 HN/GitHub/趋势 的完整日报

### Test 2: 只看 GitHub
**Input:** `GitHub Trending`
**Expected:** 仅返回 GitHub 相关内容

### Test 3: 空结果处理
**Input:** 某信息源完全失败
**Expected:** 其他源正常返回，失败源显示"获取失败"

## 已知限制

- Product Hunt 需要 API Token（当前降级处理）
- GitHub API 有 Rate Limit（1小时60次）
- 抱怨收集功能待实现（需要更多数据源）

## 脚本结构

```
scripts/
├── builder_pulse.py      # 主脚本：信息获取 + 报告生成
└── send_to_feishu.py    # 飞书推送（如已配置 webhook）
```

## 触发准确性优化

> description 优化参考 skill-creator 规范：
> - 触发词放在前面
> - 用"当...时使用"而非"用于..."
> - 关键词明确
