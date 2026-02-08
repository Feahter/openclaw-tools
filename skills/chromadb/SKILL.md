# ChromaDB Skill

## Overview
A ChromaDB vector database skill for RAG (Retrieval-Augmented Generation) operations, supporting document embedding, storage, and retrieval.

## Metadata
- **name**: chromadb
- **description**: ChromaDB 向量数据库技能，用于 RAG（检索增强生成）的向量存储和相似性检索
- **version**: 1.0.0
- **dependencies**: 
  - chromadb
  - sentence-transformers

## Capabilities

### Collection Management
- Create collections for organizing vector data
- Delete collections to clean up resources
- List all existing collections

### Document Operations
- Add documents with automatic chunking
- Generate embeddings using sentence-transformers
- Persistent storage of vectors and metadata

### Similarity Search
- Perform similarity-based document retrieval
- Filter results by metadata
- Query nearest neighbors
- Configurable similarity metrics (cosine, Euclidean, dot product)

## Usage

### Basic Operations
```python
from scripts.chromadb-ops import (
    create_collection,
    add_documents,
    search,
    delete_collection,
    list_collections
)

# List all collections
collections = list_collections()

# Create a new collection
create_collection("my_collection")

# Add documents with embeddings
add_documents(
    collection_name="my_collection",
    documents=["Document text 1", "Document text 2"],
    metadata=[{"source": "file1"}, {"source": "file2"}],
    ids=["doc1", "doc2"]
)

# Search for similar documents
results = search(
    query="Search query",
    collection_name="my_collection",
    n_results=5,
    where={"source": "file1"}
)

# Delete a collection
delete_collection("my_collection")
```

## Configuration

### Embedding Model
Default: `sentence-transformers/all-MiniLM-L6-v2`

You can customize the embedding model by modifying the scripts/chromadb-ops.py file.

### Storage Path
By default, ChromaDB uses an ephemeral in-memory database. For persistence, set the `persist_directory` parameter:

```python
add_documents(
    collection_name="my_collection",
    documents=documents,
    persist_directory="./chroma_db"
)
```

## Dependencies
```
pip install chromadb sentence-transformers
```
