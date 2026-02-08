# rag-pipeline

RAG（检索增强生成）流程 Skill，整合 article-extractor + chromadb + sqlite-rag，提供完整的本地 RAG 能力。

## 功能

- **文档摄取**：从 URL/文件摄取文档
- **自动分块**：智能文档分块处理
- **向量存储**：调用 chromadb 存储向量
- **元数据管理**：调用 sqlite-rag 存储元数据
- **相似性检索**：高效向量检索
- **生成增强**：返回检索结果供生成使用

## 整合 Skills

- `article-extractor` - 内容提取
- `chromadb` - 向量存储
- `sqlite-rag` - 元数据存储

## 使用方式

```python
from rag_pipeline import rag_pipeline

# 文档摄取
rag_pipeline.ingest(url="https://example.com/article")

# 相似性检索
results = rag_pipeline.search(query="什么是机器学习", top_k=5)

# 获取上下文用于生成
context = rag_pipeline.get_context(query="什么是机器学习")

# 列出已索引文档
docs = rag_pipeline.list_documents()
```

## 依赖

- article-extractor Skill
- chromadb Skill
- sqlite-rag Skill
