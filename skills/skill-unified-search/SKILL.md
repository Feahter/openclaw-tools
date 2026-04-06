---
name: skill-unified-search
description: >
  统一搜索路由入口。当用户说"搜一下"、"帮我查"、"查一下"、"网上搜"、"search"、"find"、"look up"
  等搜索意图时，必须优先使用此 skill 来决定调用哪个搜索工具，而不是直接猜测。
  
  覆盖场景：通用网页搜索、社交媒体（Twitter/小红书/B站/Reddit/YouTube/微博）、
  GitHub 代码搜索、实时新闻、学术论文、金融数据、特定网站访问。
  
  核心价值：避免在 10+ 个搜索 skill 中盲目选择，通过意图识别自动路由到最优工具，
  失败时自动降级，无需用户手动指定具体 skill。
  
  关键词：搜一下, 帮我搜, 查一下, 网上查, 搜索, search, find, lookup, 查资料,
  搜推特, 搜小红书, 搜B站, 搜GitHub, 搜新闻, 查股票, 查论文
triggers:
  - keywords: ["搜一下", "帮我搜", "查一下", "网上查", "搜索", "search", "find", "lookup", "查资料"]
    load: true
    priority: high
---

# 统一搜索路由入口

*一个入口，意图识别自动路由，失败自动降级。*

---

## 执行流程（每次搜索必须遵循）

```
Step 1: 识别意图 → 查路由表 → 确定首选工具
Step 2: 读取首选工具的 SKILL.md → 按其指引执行
Step 3: 失败？→ 读取降级工具的 SKILL.md → 重试
Step 4: 全部失败 → 告知用户 + 建议手动方案
```

**关键原则**：路由到工具后，必须实际读取并执行该工具的 SKILL.md，不能只是"建议用户去用"。

---

## 意图路由表

### 社交媒体类

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| 推特/Twitter/X、小红书、B站/Bilibili、Reddit、YouTube、微博、微信公众号、LinkedIn | **agent-reach** | 无（平台专属） |

→ 执行：读取 `~/.openclaw/workspace/skills/agent-reach/agent_reach/skill/SKILL.md`

### 开发 & 代码类

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| GitHub、开源项目、代码仓库 | **agent-reach**（GitHub 命令）| github skill |
| 技术问题、Stack Overflow、编程 | **multi-search-engine** | online-search |

→ 执行：读取对应 skill 的 SKILL.md

### 实时信息类

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| 最新新闻、今天发生了什么、实时 | **online-search** | multi-search-engine |
| 天气、股价、汇率、比分 | **online-search** | multi-search-engine |

→ 执行：读取 `~/Library/Application Support/QClaw/openclaw/config/skills/online-search/SKILL.md`

### 学术 & 深度研究类

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| 论文、学术、研究报告、深度分析 | **tavily-search**（需 API Key）| multi-search-engine |

→ 执行：读取 `~/.openclaw/workspace/skills/tavily-search/SKILL.md`，若无 Key 直接降级

### 金融数据类

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| 股票、基金、财报、指数、行情 | **neodata-financial-search** | multi-search-engine |

→ 执行：读取 `~/Library/Application Support/QClaw/openclaw/config/skills/neodata-financial-search/SKILL.md`

### 通用网页类（默认）

| 意图关键词 | 首选工具 | 降级方案 |
|-----------|---------|---------|
| 无特定平台的通用搜索 | **multi-search-engine** | online-search |
| 访问特定网址/网站 | **web-access** | agent-reach |

→ 执行：读取 `~/.openclaw/workspace/skills/multi-search-engine/SKILL.md`

---

## 快速判断口诀

```
社交平台名词 → agent-reach
"最新/实时/今天" → online-search
"股票/基金/财报" → neodata-financial-search
"论文/学术" → tavily-search（需Key）
"GitHub/代码" → agent-reach 或 github skill
其他一切 → multi-search-engine
```

---

## 工具可用性速查

| 工具 | 需要 API Key | 需要 Node.js | 当前状态 |
|------|------------|------------|---------|
| agent-reach | ❌ | ❌ | ✅ 可用 |
| multi-search-engine | ❌ | ❌ | ✅ 可用 |
| online-search | ❌ | ✅ | ⚠️ 需 Node |
| tavily-search | ✅ | ❌ | ⚠️ 需配置 Key |
| neodata-financial-search | ❌ | ❌ | ✅ 可用 |
| web-access | ❌ | ✅ | ⚠️ 需 Node + Chrome |

> ⚠️ 当前环境 Node.js = v22.21.1（已可用），online-search 和 web-access 应可正常运行。

---

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 工具 SKILL.md 不存在 | 跳过，尝试降级方案 |
| API Key 缺失 | 跳过，尝试降级方案 |
| 网络超时 | 重试 1 次，失败则降级 |
| 所有工具均失败 | 告知用户 + 建议：1) 配置 API Key 2) 检查网络 |

---

## Quick-start 示例

**用户说**：「搜一下 OpenClaw 最佳实践」

**路由决策**：无特定平台 → multi-search-engine（首选）

**执行**：
1. 读取 `~/.openclaw/workspace/skills/multi-search-engine/SKILL.md`
2. 按其指引执行搜索
3. 返回结果

---

**用户说**：「搜推特上关于 AI Agent 的讨论」

**路由决策**：推特 → agent-reach

**执行**：
1. 读取 `~/.openclaw/workspace/skills/agent-reach/agent_reach/skill/SKILL.md`
2. 使用 Twitter 搜索命令
3. 返回结果

---

## 维护说明

- 新增搜索 skill 时：更新路由表 + 工具可用性速查
- API Key 变更时：更新工具可用性速查
- 工具失效时：在速查表标记 🔴，并更新降级方案
