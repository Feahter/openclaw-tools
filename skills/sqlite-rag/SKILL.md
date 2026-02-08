# SQLite RAG Skill

## 基础信息

- **name**: sqlite-rag
- **description**: SQLite 元数据存储技能，专为 RAG 系统设计，存储文档元数据、标签、来源、chunk 信息
- **version**: 1.0.0
- **author**: OpenClaw

## 功能

- **文档元数据存储**: 存储文档的标题、内容摘要、来源、创建时间等元数据
- **标签管理**: 支持标签的增删改查，方便文档分类和检索
- **来源追踪**: 记录文档的来源信息，便于溯源
- **Chunk 映射管理**: 管理文档与 chunk 的映射关系

## 主要能力

- 创建/连接 SQLite 数据库
- 插入/查询文档元数据
- 标签增删改查
- 按标签搜索文档
- 列出所有文档
- 管理 chunk 映射

## 依赖

- Python 3.7+
- sqlite3（Python 内置，无需额外安装）

## 使用示例

```python
from sqlite_rag import SQLiteRAG

# 初始化
rag = SQLiteRAG("rag_metadata.db")

# 初始化数据库
rag.init_db()

# 添加文档
doc_id = rag.add_document(
    title="示例文档",
    content_hash="abc123...",
    source="file:///path/to/doc.txt",
    metadata={"author": "张三", "category": "技术文档"}
)

# 添加标签
rag.add_tag(doc_id, "Python")
rag.add_tag(doc_id, "RAG")

# 按标签搜索
docs = rag.search_by_tag("Python")

# 获取文档
doc = rag.get_document(doc_id)

# 列出所有文档
all_docs = rag.list_documents()
```
