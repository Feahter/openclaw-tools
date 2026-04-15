---
name: wiki-query
description: |
  Search your personal wiki knowledge base built by llm-wiki-agent.
  Searches concept pages, entity pages, and source summaries by keyword.
  
  Use when:
  - feZ asks about something that was discussed/decided before
  - feZ wants to recall a past insight, framework, or method
  - feZ says "我记得之前研究过..." or "之前那个关于..."
  
  Triggers: wiki查询, wiki搜索, 查一下wiki, 之前那个框架, 之前那个方法, 之前那个结论
---

# Wiki Query — Personal Knowledge Base Search

查询 llm-wiki-agent 构建的个人 wiki 知识库。

## 工作原理

```
用户 query → wiki-query.py → 关键词搜索 → 匹配文件 → 返回标题+摘要
```

## 使用方式

### 基础查询

```
python3 {skill_dir}/scripts/wiki_query.py "TalentMind"
python3 {skill_dir}/scripts/wiki_query.py "任务三问"
python3 {skill_dir}/scripts/wiki_query.py "决策框架"
```

### 在对话中使用

当 feZ 提到"之前那个关于..."时，执行查询并注入结果：

```bash
python3 {skill_dir}/scripts/wiki_query.py "<关键词>" --limit 3
```

读取返回的相关文件完整内容，注入上下文。

## Wiki 内容范围

| 目录 | 内容 |
|------|------|
| `concepts/` | 概念、框架、方法论 |
| `entities/` | 人物、公司、项目实体 |
| `sources/` | 原始来源摘要 |
| `overview.md` | 跨来源活综述 |

## 限制

- 纯关键词匹配，不支持语义相似搜索
- 依赖 llm-wiki-agent 先摄入过相关内容
- 如果 wiki 为空，提示先使用 llm-wiki-agent 摄入材料

## Wiki 路径

`~/.openclaw/workspace/skills/llm-wiki-agent/wiki/`
