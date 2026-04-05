---
name: skill-unified-search
description: |
  统一搜索入口 - 意图识别自动路由，多工具串联，失败自动降级，健康度实时监控。
  
  触发：用户说"搜一下"、"帮我搜索"、"查一下"、"网上查"、"search"等搜索意图时，
  自动根据意图选择最优工具，无需用户指定具体 skill。
  
  支持：通用网页、社交媒体（Twitter/Reddit/YouTube/小红书/B站等）、GitHub、学术、实时新闻、金融数据。
triggers:
  - keywords: ["搜一下", "帮我搜索", "查一下", "网上查", "搜索", "search", "find", "lookup"]
    load: true
    priority: high
---

# 统一搜索入口

*一个入口，意图识别自动路由，多工具串联，失败自动降级。*

---

## Preamble

1. 读取 `memory/skills/skill-unified-search/context.md`（如存在，保存工具健康状态）
2. 根据用户意图选择工具
3. 执行搜索，失败则降级

---

## 意图路由规则

| 用户意图 | 首选工具 | 降级方案 | API Key |
|---------|---------|---------|---------|
| **社交媒体** |
| "搜推特/Twitter/X" | agent-reach | 无 | ❌ |
| "搜小红书" | agent-reach | 无 | ❌ |
| "搜B站/bilibili" | agent-reach | 无 | ❌ |
| "搜Reddit" | agent-reach | 无 | ❌ |
| "搜YouTube视频" | agent-reach | 无 | ❌ |
| "搜微博" | agent-reach | 无 | ❌ |
| "搜微信公众号" | agent-reach | 无 | ❌ |
| **开发相关** |
| "搜GitHub" | agent-reach 或 github skill | web-access | ❌ |
| "搜代码/技术问题" | multi-search-engine | online-search | ❌ |
| **实时信息** |
| "实时新闻/最新" | online-search | multi-search-engine | ❌ |
| "天气/股价/汇率" | online-search | multi-search-engine | ❌ |
| **学术/深度** |
| "学术/论文" | tavily-search | multi-search-engine | ✅ 需配置 |
| "深度研究" | tavily-search | multi-search-engine | ✅ 需配置 |
| **通用网页** |
| "搜一下 XXX"（无特定平台） | multi-search-engine | online-search | ❌ |
| "搜网页/网站" | multi-search-engine | online-search | ❌ |
| **特定网站** |
| "打开/访问 XXX.com" | web-access | agent-reach | ❌ |
| **金融数据** |
| "股票/基金/财报" | neodata-financial-search | multi-search-engine | ❌ |

---

## 执行流程

```
用户输入 → 意图识别 → 检查工具健康度 → 执行首选工具
                                        ↓
                                   失败？
                                        ↓
                                   尝试降级方案
                                        ↓
                                   全部失败？
                                        ↓
                                   返回错误 + 建议手动选择
```

---

## 工具健康状态

健康状态保存在 `memory/skills/skill-unified-search/context.md`：

```json
{
  "lastCheck": "2026-04-06T00:00:00Z",
  "tools": {
    "agent-reach": {"status": "healthy", "lastSuccess": "2026-04-06T01:00:00Z"},
    "multi-search-engine": {"status": "healthy", "lastSuccess": "2026-04-06T01:00:00Z"},
    "online-search": {"status": "healthy", "lastSuccess": "2026-04-06T01:00:00Z"},
    "tavily-search": {"status": "unknown", "lastSuccess": null, "note": "需要API Key"},
    "web-access": {"status": "healthy", "lastSuccess": "2026-04-06T00:30:00Z"}
  }
}
```

---

## 快速判断口诀

```
社交平台 → agent-reach
实时新闻 → online-search  
通用网页 → multi-search-engine
特定网站 → web-access
学术深度 → tavily-search（需Key）
金融数据 → neodata-financial-search
```

---

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 工具不存在 | 跳过，尝试降级方案 |
| API Key 缺失 | 跳过，尝试降级方案 |
| 网络超时 | 重试 1 次，失败则降级 |
| 内容解析失败 | 返回原始结果 + 警告 |

---

## 与现有 Skills 的关系

- **不替代** 现有搜索 skills，而是作为**路由层**
- 用户仍可**直接调用**具体 skill（如 `agent-reach 搜推特 XXX`）
- 本 skill 作为**默认入口**，降低选择成本

---

## 评估清单

- [ ] 意图识别准确率 ≥ 90%
- [ ] 降级成功率 ≥ 80%
- [ ] 首次成功率 ≥ 70%
- [ ] 用户无需手动指定工具

---

## 维护

- 每周检查工具健康状态
- 新增搜索 skill 时更新路由表
- API Key 变更时更新状态
