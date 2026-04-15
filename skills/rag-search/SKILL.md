---
name: rag-search
description: "Minimal RAG search skill for backend retrieval."
triggers:
  - "rag-search"
  - "rag search"
source:
  project: rag-search
  url: ""
  license: ""
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:32:49
---

# Rag Search

Minimal RAG search skill for backend retrieval.
## ⚠️ Important

**This skill is intended to be used as a backend retrieval component and should not be invoked directly by end users.**

Use `occupational_health_qa` or `occupational_health_report_writer` for direct user requests.

## Usage

```
你：调用 rag-search，查询"GBZ 2.1-2019 苯 职业接触限值"
```

## Returns

Returns structured search results with:
- `content`: Original text from the document
- `source`: File name / standard number
- `clause`: Clause number (if available)
- `regulation_level`: Regulation level (国家法律/国家标准/行业标准/etc)
- `score`: Relevance score (0-1)

## Example Response

```json
{
  "results": [
    {
      "content": "苯的时间加权平均容许浓度（PC-TWA）为6 mg/m³...",
      "source": "GBZ 2.1-2019.pdf",
      "clause": "第4.1条",
      "regulation_level": "国家标准",
      "score": 0.93
    }
  ]
}
```


## 适用场景

- 当用户需要 minimal rag search skill for backend retrieval 时

## 注意事项

*基于 skill-creator SOP 强化*
*更新时间: 2026-02-11*