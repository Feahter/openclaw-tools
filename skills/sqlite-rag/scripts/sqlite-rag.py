#!/usr/bin/env python3
"""
SQLite RAG - SQLite 元数据存储模块，专为 RAG 系统设计
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any


class SQLiteRAG:
    """SQLite 元数据存储类，专为 RAG 系统设计"""

    def __init__(self, db_path: str = "rag_metadata.db"):
        """
        初始化 SQLiteRAG

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        """
        初始化数据库，创建必要的表

        Tables:
            documents: 存储文档元数据
            tags: 存储标签
            document_tags: 文档-标签关联表
            chunks: 存储 chunk 信息
            chunk_documents: chunk-文档关联表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                source TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建文档-标签关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')

        # 创建 chunks 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER NOT NULL,
                content TEXT,
                embedding_id TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)')

        conn.commit()

    def add_document(
        self,
        title: str,
        content_hash: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        添加文档元数据

        Args:
            title: 文档标题
            content_hash: 内容哈希值（用于去重）
            source: 来源路径或 URL
            metadata: 额外元数据（JSON 格式存储）

        Returns:
            int: 新增文档的 ID
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata or {})

        cursor.execute('''
            INSERT INTO documents (title, content_hash, source, metadata)
            VALUES (?, ?, ?, ?)
        ''', (title, content_hash, source, metadata_json))

        conn.commit()
        return cursor.lastrowid

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        获取文档元数据

        Args:
            doc_id: 文档 ID

        Returns:
            Dict: 文档信息，包含 tags 和 chunks
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        # 获取文档信息
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()

        if not row:
            return None

        doc = dict(row)
        doc['metadata'] = json.loads(doc['metadata'] or '{}')

        # 获取标签
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN document_tags dt ON t.id = dt.tag_id
            WHERE dt.document_id = ?
        ''', (doc_id,))
        doc['tags'] = [r['name'] for r in cursor.fetchall()]

        # 获取 chunks
        cursor.execute('''
            SELECT * FROM chunks WHERE document_id = ?
            ORDER BY chunk_index
        ''', (doc_id,))
        chunks = []
        for chunk_row in cursor.fetchall():
            chunk = dict(chunk_row)
            chunk['metadata'] = json.loads(chunk['metadata'] or '{}')
            chunks.append(chunk)
        doc['chunks'] = chunks

        return doc

    def update_document(
        self,
        doc_id: int,
        title: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新文档元数据

        Args:
            doc_id: 文档 ID
            title: 新标题
            source: 新来源
            metadata: 新元数据

        Returns:
            bool: 是否更新成功
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if source is not None:
            updates.append('source = ?')
            params.append(source)
        if metadata is not None:
            updates.append('metadata = ?')
            params.append(json.dumps(metadata))

        if not updates:
            return False

        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(doc_id)

        query = f'UPDATE documents SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        conn.commit()

        return cursor.rowcount > 0

    def delete_document(self, doc_id: int) -> bool:
        """
        删除文档及其关联数据

        Args:
            doc_id: 文档 ID

        Returns:
            bool: 是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()

        return cursor.rowcount > 0

    def add_tag(self, doc_id: int, tag_name: str) -> bool:
        """
        为文档添加标签

        Args:
            doc_id: 文档 ID
            tag_name: 标签名称

        Returns:
            bool: 是否添加成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 查找或创建标签
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        tag_row = cursor.fetchone()

        if tag_row:
            tag_id = tag_row['id']
        else:
            cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
            tag_id = cursor.lastrowid

        # 关联文档和标签
        try:
            cursor.execute(
                'INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)',
                (doc_id, tag_id)
            )
        except sqlite3.IntegrityError:
            # 已经存在关联
            return False

        conn.commit()
        return True

    def remove_tag(self, doc_id: int, tag_name: str) -> bool:
        """
        移除文档的标签

        Args:
            doc_id: 文档 ID
            tag_name: 标签名称

        Returns:
            bool: 是否移除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM document_tags
            WHERE document_id = ? AND tag_id = (
                SELECT id FROM tags WHERE name = ?
            )
        ''', (doc_id, tag_name))

        conn.commit()
        return cursor.rowcount > 0

    def get_tags(self, doc_id: int) -> List[str]:
        """
        获取文档的所有标签

        Args:
            doc_id: 文档 ID

        Returns:
            List[str]: 标签列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN document_tags dt ON t.id = dt.tag_id
            WHERE dt.document_id = ?
        ''', (doc_id,))

        return [r['name'] for r in cursor.fetchall()]

    def search_by_tag(self, tag_name: str) -> List[Dict[str, Any]]:
        """
        按标签搜索文档

        Args:
            tag_name: 标签名称

        Returns:
            List[Dict]: 匹配的文档列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT d.* FROM documents d
            JOIN document_tags dt ON d.id = dt.document_id
            JOIN tags t ON dt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY d.updated_at DESC
        ''', (tag_name,))

        import json
        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            doc['metadata'] = json.loads(doc['metadata'] or '{}')
            docs.append(doc)

        return docs

    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = 'updated_at',
        order: str = 'DESC'
    ) -> List[Dict[str, Any]]:
        """
        列出所有文档

        Args:
            limit: 返回数量限制
            offset: 偏移量
            order_by: 排序字段
            order: 排序方向（ASC/DESC）

        Returns:
            List[Dict]: 文档列表
        """
        import json

        allowed_order_by = ['created_at', 'updated_at', 'title', 'id']
        if order_by not in allowed_order_by:
            order_by = 'updated_at'

        order = order.upper() if order.upper() in ['ASC', 'DESC'] else 'DESC'

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(f'''
            SELECT * FROM documents
            ORDER BY {order_by} {order}
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            doc['metadata'] = json.loads(doc['metadata'] or '{}')
            docs.append(doc)

        return docs

    def search_documents(
        self,
        keyword: Optional[str] = None,
        source: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        多条件搜索文档

        Args:
            keyword: 标题关键词
            source: 来源匹配
            tag: 标签匹配
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 匹配的文档列表
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT DISTINCT d.* FROM documents d
        '''
        joins = []
        conditions = []

        if tag:
            joins.append('''
                JOIN document_tags dt ON d.id = dt.document_id
                JOIN tags t ON dt.tag_id = t.id
            ''')
            conditions.append('t.name = ?')

        if keyword:
            conditions.append('d.title LIKE ?')

        if source:
            conditions.append('d.source = ?')

        if joins:
            query += ' '.join(joins)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY d.updated_at DESC LIMIT ? OFFSET ?'

        params = []
        if tag:
            params.append(tag)
        if keyword:
            params.append(f'%{keyword}%')
        if source:
            params.append(source)
        params.extend([limit, offset])

        cursor.execute(query, params)

        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            doc['metadata'] = json.loads(doc['metadata'] or '{}')
            docs.append(doc)

        return docs

    def add_chunk(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        embedding_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        添加 chunk 信息

        Args:
            document_id: 所属文档 ID
            chunk_index: chunk 索引
            content: chunk 内容
            embedding_id: 对应的 embedding ID
            metadata: 额外元数据

        Returns:
            int: 新增 chunk 的 ID
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata or {})

        cursor.execute('''
            INSERT INTO chunks (document_id, chunk_index, content, embedding_id, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (document_id, chunk_index, content, embedding_id, metadata_json))

        conn.commit()
        return cursor.lastrowid

    def get_chunks(self, doc_id: int) -> List[Dict[str, Any]]:
        """
        获取文档的所有 chunks

        Args:
            doc_id: 文档 ID

        Returns:
            List[Dict]: chunk 列表
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM chunks WHERE document_id = ?
            ORDER BY chunk_index
        ''', (doc_id,))

        chunks = []
        for row in cursor.fetchall():
            chunk = dict(row)
            chunk['metadata'] = json.loads(chunk['metadata'] or '{}')
            chunks.append(chunk)

        return chunks

    def get_chunk(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个 chunk

        Args:
            chunk_id: chunk ID

        Returns:
            Dict: chunk 信息
        """
        import json

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM chunks WHERE id = ?', (chunk_id,))
        row = cursor.fetchone()

        if not row:
            return None

        chunk = dict(row)
        chunk['metadata'] = json.loads(chunk['metadata'] or '{}')
        return chunk

    def delete_chunks(self, doc_id: int) -> int:
        """
        删除文档的所有 chunks

        Args:
            doc_id: 文档 ID

        Returns:
            int: 删除的 chunk 数量
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM chunks WHERE document_id = ?', (doc_id,))
        conn.commit()

        return cursor.rowcount

    def get_document_stats(self) -> Dict[str, int]:
        """
        获取数据库统计信息

        Returns:
            Dict: 包含文档数、标签数、chunk 数的统计
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tags')
        tag_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM chunks')
        chunk_count = cursor.fetchone()[0]

        return {
            'documents': doc_count,
            'tags': tag_count,
            'chunks': chunk_count
        }


# 便捷函数
def init_db(db_path: str = "rag_metadata.db"):
    """初始化数据库"""
    rag = SQLiteRAG(db_path)
    rag.init_db()
    rag.close()


def add_document(
    title: str,
    content_hash: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: str = "rag_metadata.db"
) -> int:
    """添加文档"""
    rag = SQLiteRAG(db_path)
    doc_id = rag.add_document(title, content_hash, source, metadata)
    rag.close()
    return doc_id


def get_document(doc_id: int, db_path: str = "rag_metadata.db") -> Optional[Dict[str, Any]]:
    """获取文档"""
    rag = SQLiteRAG(db_path)
    doc = rag.get_document(doc_id)
    rag.close()
    return doc


def add_tag(doc_id: int, tag_name: str, db_path: str = "rag_metadata.db") -> bool:
    """添加标签"""
    rag = SQLiteRAG(db_path)
    result = rag.add_tag(doc_id, tag_name)
    rag.close()
    return result


def search_by_tag(tag_name: str, db_path: str = "rag_metadata.db") -> List[Dict[str, Any]]:
    """按标签搜索"""
    rag = SQLiteRAG(db_path)
    docs = rag.search_by_tag(tag_name)
    rag.close()
    return docs


def list_documents(
    limit: int = 100,
    offset: int = 0,
    db_path: str = "rag_metadata.db"
) -> List[Dict[str, Any]]:
    """列出所有文档"""
    rag = SQLiteRAG(db_path)
    docs = rag.list_documents(limit, offset)
    rag.close()
    return docs


if __name__ == "__main__":
    # 示例用法
    rag = SQLiteRAG("example_rag.db")

    # 初始化数据库
    print("初始化数据库...")
    rag.init_db()

    # 添加文档
    print("\n添加文档...")
    doc_id = rag.add_document(
        title="RAG 系统介绍",
        content_hash="hash123",
        source="file:///docs/rag_intro.txt",
        metadata={"author": "张三", "category": "技术文档"}
    )
    print(f"文档 ID: {doc_id}")

    # 添加标签
    print("\n添加标签...")
    rag.add_tag(doc_id, "RAG")
    rag.add_tag(doc_id, "AI")
    rag.add_tag(doc_id, "入门")

    # 获取文档
    print("\n获取文档信息...")
    doc = rag.get_document(doc_id)
    print(f"标题: {doc['title']}")
    print(f"标签: {doc['tags']}")

    # 添加 chunk
    print("\n添加 chunk...")
    rag.add_chunk(doc_id, 0, "RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的技术...")
    rag.add_chunk(doc_id, 1, "它通过从知识库中检索相关文档，然后使用语言模型生成答案...")

    # 搜索
    print("\n按标签搜索 'AI'...")
    docs = rag.search_by_tag("AI")
    for d in docs:
        print(f"  - {d['title']}")

    # 列出所有文档
    print("\n列出所有文档...")
    all_docs = rag.list_documents()
    for d in all_docs:
        print(f"  - {d['title']} (ID: {d['id']})")

    # 统计
    print("\n数据库统计...")
    stats = rag.get_document_stats()
    print(f"文档数: {stats['documents']}")
    print(f"标签数: {stats['tags']}")
    print(f"Chunk 数: {stats['chunks']}")

    rag.close()
    print("\n示例运行完成!")
