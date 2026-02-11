---
name: tapestry
description: "知识图谱构建技能，用于文档关联和知识网络管理"
triggers:
  - "tapestry"
  - "tapestry"
source:
  project: tapestry
  url: ""
  license: ""
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:32:49
---

# Tapestry

知识图谱构建技能，用于文档关联和知识网络管理
## description
知识图谱构建技能，用于文档关联和知识网络管理

## features
- **文档解析**: 支持文本、PDF、Markdown 格式的文档解析
- **实体提取**: 从文档中自动提取人名、地名、机构名等实体
- **关系建立**: 建立文档间和实体间的关联关系
- **知识检索**: 基于图结构的知识检索和路径查询
- **可视化准备**: 输出适合可视化的图数据格式

## usage
```bash
# 解析文档并构建知识图谱
python scripts/tapestry-core.py parse --input <文档路径> --format <格式>

# 提取实体
python scripts/tapestry-core.py extract --text <文本内容>

# 建立关系
python scripts/tapestry-core.py relate --doc1 <文档1> --doc2 <文档2>

# 检索知识
python scripts/tapestry-core.py query --entity <实体名> --depth <深度>

# 导出可视化数据
python scripts/tapestry-core.py export --format <格式> --output <输出路径>
```

## dependencies
- networkx: 图构建和分析
- spacy: 自然语言处理和实体识别
- PyPDF2: PDF 解析
- python-dotenv: 配置管理

## storage
- 图数据存储: `data/graph.json`
- 文档索引: `data/documents.json`
- 实体库: `data/entities.json`

## author
OpenClaw

## version
1.0.0


## 适用场景

- 当用户需要 知识图谱构建技能，用于文档关联和知识网络管理 时

## 注意事项

*基于 skill-creator SOP 强化*
*更新时间: 2026-02-11*