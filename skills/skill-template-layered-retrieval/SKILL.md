---
name: skill-template-layered-retrieval
description: Template for building document Q&A systems with layered retrieval. Use this pattern when you need to query large structured documents (insurance policies, legal contracts, technical manuals) without overwhelming context limits. The pattern splits documents into hierarchical units (chapters/sections/paragraphs), stores in SQLite, and retrieves through a 3-layer filter (category → subsection → content). Triggers on phrases like "文档问答", "分层检索", "保险文档查询", "知识库问答", or any request to build a document retrieval system.
---

# Skill Template: Layered Retrieval Document Q&A

A reusable template for building document Q&A systems that avoid context overflow through hierarchical retrieval.

## When to Use This Pattern

- Large structured documents (100+ pages)
- Hierarchical content (chapters → sections → subsections → paragraphs)
- Need precise answers without dumping entire document into context
- Documents follow consistent formatting (## headers, numbered lists, etc.)

## Architecture

```
Document Ingestion Pipeline:
├── parse_document.py      → Extract structure, split into units
├── store_sqlite.py        → Hierarchical storage (category → section → content)
└── verify_structure.py    → Validate parsing accuracy

Query Pipeline:
├── classify_intent.py     → Determine which category the question belongs to
├── retrieve_candidates.py → Layer 1: Filter by category
├── narrow_scope.py        → Layer 2: Filter by subsection
├── fetch_content.py       → Layer 3: Get specific paragraphs
└── generate_answer.py     → Synthesize final answer
```

## Data Model (SQLite)

```sql
CREATE TABLE document_units (
    id INTEGER PRIMARY KEY,
    category TEXT,           -- Layer 1: 大类 (e.g., "产品条款")
    subsection TEXT,         -- Layer 2: 细分 (e.g., "重疾保障")
    unit_type TEXT,          -- "chapter" | "section" | "paragraph"
    title TEXT,              -- Original heading
    content TEXT,            -- Full text content
    parent_id INTEGER,       -- Foreign key to parent unit
    metadata JSON            -- Page number, source file, etc.
);

CREATE INDEX idx_category ON document_units(category);
CREATE INDEX idx_subsection ON document_units(subsection);
CREATE FULLTEXT INDEX idx_content ON document_units(content);
```

## Layered Retrieval Flow

```
User Question: "重疾险的等待期是多久？"

Layer 1 (Category Filter):
    → Classify: "保险条款" → "重疾险"
    → Retrieve: All units where category = "重疾险"
    → Result: 15 units (chapters/sections)

Layer 2 (Subsection Filter):
    → Match: "等待期" in subsection titles
    → Retrieve: Units where subsection LIKE "%等待期%"
    → Result: 3 units

Layer 3 (Content Fetch):
    → Full-text search: "等待期" within the 3 units
    → Retrieve: Exact paragraphs containing answer
    → Result: 2 paragraphs (context fits in LLM window)

Generate Answer:
    → Synthesize from 2 paragraphs
    → Cite source locations
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **SQLite over Vector DB** | Document structure is deterministic; exact match + FTS is sufficient and lighter |
| **3-layer filter** | Each layer reduces context by ~10x; final fetch is < 1k tokens |
| **Chapter as minimum unit** | Insurance/legal docs have clear ## headings; natural split points |
| **Metadata preservation** | Enable "see page 47 of Policy v2.3" citations |

## Implementation Checklist

- [ ] Document has consistent heading structure (##, ###)
- [ ] Parse script extracts hierarchy correctly
- [ ] SQLite schema matches document depth (2-4 levels typical)
- [ ] Layer 1 classifier has > 90% accuracy on sample questions
- [ ] Layer 2 retrieval returns < 10 candidates
- [ ] Layer 3 final context < 2000 tokens
- [ ] Answer includes source citations

## Variations

| Scenario | Modification |
|----------|--------------|
| Unstructured docs (PDF scans) | Add OCR + heading detection preprocessing |
| Multi-document corpus | Add `document_id` column, Layer 0: select document |
| Frequently updated docs | Add versioning, `valid_from`/`valid_to` dates |
| Cross-reference heavy | Add `related_units` JSON column for graph traversal |

## Example: Insurance Policy Q&A

**Input Document**: 200-page insurance policy  
**Structure**: 产品条款 → 保障责任 → 具体病种 → 理赔条件  
**Sample Questions**:
- "甲状腺癌算重疾吗？" → Layer 1: 重疾保障 → Layer 2: 病种列表 → Layer 3: 甲状腺癌定义
- "等待期内出险怎么办？" → Layer 1: 合同生效 → Layer 2: 等待期条款 → Layer 3: 处理规则

## Migration Path

1. **Prototype** (Day 1): Python scripts + SQLite, CLI interface
2. **Validate** (Day 2): Test with 50 real questions, measure accuracy
3. **Package** (Day 3): Wrap as OpenClaw Skill with proper triggers

**PI First**: Build the pipeline with raw Python, verify it works, then add Skill wrapper.

## References

- Original case: [保险公司 AI 培训项目](../cases/insurance-ai-training.md)
- Related pattern: [网文创作知识库](TODO) — same hierarchical approach (大纲 → 章节 → 段落)
