"""
RAG Pipeline - 检索增强生成流程

整合内容提取、向量存储、元数据管理，提供完整的本地 RAG 能力。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """文档数据结构"""
    id: str
    content: str
    metadata: Dict[str, Any]
    chunks: List[str] = None


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float


class RAGPipeline:
    """RAG 检索增强生成流程"""

    def __init__(self):
        self.chromadb = None
        self.sqlite_rag = None
        self.article_extractor = None
        self._initialize_clients()

    def _initialize_clients(self):
        """初始化各组件客户端"""
        try:
            from skills.chromadb.scripts.chromadb_client import ChromaDBClient
            self.chromadb = ChromaDBClient()
        except ImportError:
            pass

        try:
            from skills.sqlite_rag.scripts.sqlite_rag import SQLiteRAG
            self.sqlite_rag = SQLiteRAG()
        except ImportError:
            pass

        try:
            from skills.article_extractor.scripts.article_extractor import ArticleExtractor
            self.article_extractor = ArticleExtractor()
        except ImportError:
            pass

    def ingest(self, url: str = None, file_path: str = None, content: str = None,
               chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        文档摄取流程

        Args:
            url: 文档 URL
            file_path: 文件路径
            content: 直接传入的内容
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小

        Returns:
            List[str]: 摄取的文档 ID 列表
        """
        # 1. 提取内容
        if url:
            text = self._extract_from_url(url)
        elif file_path:
            text = self._extract_from_file(file_path)
        elif content:
            text = content
        else:
            raise ValueError("必须提供 url、file_path 或 content")

        # 2. 分块处理
        chunks = self._chunk_text(text, chunk_size, chunk_overlap)

        # 3. 生成分块 ID
        import hashlib
        doc_id = hashlib.md5(text.encode()).hexdigest()[:16]
        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

        # 4. 存储到向量数据库
        if self.chromadb:
            self.chromadb.add(doc_id, chunks)

        # 5. 存储元数据
        if self.sqlite_rag:
            self.sqlite_rag.add_document(
                doc_id=doc_id,
                content=text,
                metadata={
                    "source": url or file_path or "direct_input",
                    "chunk_count": len(chunks),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap
                }
            )

        return chunk_ids

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        相似性检索

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            List[SearchResult]: 搜索结果列表
        """
        if not self.chromadb:
            # 降级：使用 sqlite-rag 的搜索
            if self.sqlite_rag:
                results = self.sqlite_rag.search(query, top_k)
                return [
                    SearchResult(
                        id=r.get("id", ""),
                        content=r.get("content", ""),
                        metadata=r.get("metadata", {}),
                        score=r.get("score", 0.0)
                    )
                    for r in results
                ]
            raise RuntimeError("ChromaDB and SQLite-RAG not available")

        # 使用 chromadb 进行向量搜索
        results = self.chromadb.search(query, top_k)

        return [
            SearchResult(
                id=r["id"],
                content=r["content"],
                metadata=r.get("metadata", {}),
                score=r.get("score", 0.0)
            )
            for r in results
        ]

    def get_context(self, query: str, top_k: int = 5) -> str:
        """
        获取上下文用于生成

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            str: 格式化的上下文文本
        """
        results = self.search(query, top_k)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[{i}] {result.content}\n"
                f"    来源: {result.metadata.get('source', 'Unknown')}"
            )

        return "\n\n".join(context_parts)

    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        列出已索引文档

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 文档信息列表
        """
        if self.sqlite_rag:
            return self.sqlite_rag.list_documents(limit)
        return []

    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档 ID

        Returns:
            bool: 是否成功
        """
        success = True

        if self.chromadb:
            self.chromadb.delete(doc_id)

        if self.sqlite_rag:
            self.sqlite_rag.delete_document(doc_id)

        return success

    def _extract_from_url(self, url: str) -> str:
        """从 URL 提取内容"""
        if self.article_extractor:
            return self.article_extractor.extract(url)
        raise RuntimeError("Article extractor not available")

    def _extract_from_file(self, file_path: str) -> str:
        """从文件提取内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _chunk_text(self, text: str, chunk_size: int = 1000,
                    overlap: int = 200) -> List[str]:
        """文本分块"""
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            start = end - overlap

            if start >= text_len:
                break

        return chunks


# 单例实例
rag_pipeline = RAGPipeline()


def ingest(url: str = None, file_path: str = None, content: str = None,
          chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """文档摄取"""
    return rag_pipeline.ingest(url, file_path, content, chunk_size, chunk_overlap)


def search(query: str, top_k: int = 5) -> List[SearchResult]:
    """检索"""
    return rag_pipeline.search(query, top_k)


def get_context(query: str, top_k: int = 5) -> str:
    """获取上下文"""
    return rag_pipeline.get_context(query, top_k)


def list_documents(limit: int = 100) -> List[Dict[str, Any]]:
    """列出文档"""
    return rag_pipeline.list_documents(limit)


def delete_document(doc_id: str) -> bool:
    """删除文档"""
    return rag_pipeline.delete_document(doc_id)
