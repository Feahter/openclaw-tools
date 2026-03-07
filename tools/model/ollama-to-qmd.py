#!/usr/bin/env python3
"""
Ollama Embedding to QMD Vector Store
用 Ollama 生成向量，写入 qmd 的 SQLite vec0 表

用法:
    python3 ollama-to-qmd.py              # 嵌入所有未向量化的文档
    python3 ollama-to-qmd.py --force      # 强制重新嵌入所有文档
    python3 ollama-to-qmd.py --dry-run     # 只显示要处理的文档，不实际嵌入
"""

import sqlite3
import json
import os
import sys
import argparse
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    qmd_index: str = os.path.expanduser("~/.cache/qmd/index.sqlite")
    ollama_url: str = "http://localhost:11434/api/embeddings"
    ollama_model: str = "nomic-embed-text"
    embedding_dim: int = 768
    batch_size: int = 10
    max_content_length: int = 8000

config = Config()


def get_ollama_embedding(text: str, model: str = None) -> list[float]:
    """调用 Ollama API 获取 embedding"""
    import urllib.request
    import urllib.error
    
    model = model or config.ollama_model
    
    payload = {
        "model": model,
        "prompt": text[:config.max_content_length]
    }
    
    req = urllib.request.Request(
        config.ollama_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['embedding']
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_doc_hash(content: str, seq: int = 0) -> str:
    """生成文档哈希 (hash_seq)"""
    raw = f"{content[:1000]}{seq}"
    return hashlib.sha256(raw.encode()).hexdigest()[:64]


def get_all_docs_needing_embedding(db_path: str, force: bool = False) -> list:
    """获取需要向量化的文档"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if force:
        cursor.execute("""
            SELECT d.path, c.doc, d.hash
            FROM documents d
            JOIN content c ON d.hash = c.hash
            WHERE d.active = 1
        """)
    else:
        cursor.execute("""
            SELECT d.path, c.doc, d.hash
            FROM documents d
            JOIN content c ON d.hash = c.hash
            LEFT JOIN content_vectors cv ON d.hash = cv.hash
            WHERE d.active = 1 AND cv.hash IS NULL
        """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [(r['path'], r['doc'][:config.max_content_length], r['hash']) for r in results]


def check_existing_vectors(db_path: str) -> dict:
    """检查现有向量状态"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE active = 1")
    total_docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT hash) FROM content_vectors")
    embedded_docs = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total_docs,
        "embedded": embedded_docs,
        "pending": total_docs - embedded_docs
    }


def embed_documents(dry_run: bool = False, force: bool = False, model: str = None):
    """批量嵌入文档到 qmd"""
    
    model = model or config.ollama_model
    
    # 检查向量状态
    status = check_existing_vectors(config.qmd_index)
    print(f"📊 向量状态: {status['embedded']}/{status['total']} 已嵌入, {status['pending']} 待处理")
    
    if status['pending'] == 0 and not force:
        print("✅ 所有文档已向量完成!")
        return
    
    # 获取需要处理的文档
    docs = get_all_docs_needing_embedding(config.qmd_index, force)
    print(f"📄 将处理 {len(docs)} 个文档...")
    
    if dry_run:
        print("\n📝 Dry Run - 以下文档将被向量化:")
        for i, (path, _, _) in enumerate(docs[:10]):
            print(f"  {i+1}. {path}")
        if len(docs) > 10:
            print(f"  ... 还有 {len(docs) - 10} 个")
        return
    
    if not docs:
        print("✅ 没有需要处理的文档")
        return
    
    # 连接数据库准备写入
    conn = sqlite3.connect(config.qmd_index)
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    for i, (path, content, doc_hash) in enumerate(docs):
        print(f"🔄 [{i+1}/{len(docs)}] 处理: {path[:50]}...", end=" ", flush=True)
        
        # 生成向量
        embedding = get_ollama_embedding(content, model)
        
        if embedding is None:
            print("❌ 获取向量失败")
            error_count += 1
            time.sleep(1)
            continue
        
        # 写入 vectors_vec 表
        try:
            hash_seq = f"{doc_hash}|0"
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            
            cursor.execute("""
                INSERT OR REPLACE INTO vectors_vec (hash_seq, embedding)
                VALUES (?, ?)
            """, (hash_seq, embedding_str))
            
            # 更新 content_vectors 表
            cursor.execute("""
                INSERT OR REPLACE INTO content_vectors (hash, seq, pos, model, embedded_at)
                VALUES (?, 0, 0, ?, datetime('now'))
            """, (doc_hash, model.replace("-", "")))
            
            success_count += 1
            print("✅")
            
        except Exception as e:
            print(f"❌ 写入失败: {e}")
            error_count += 1
        
        if (i + 1) % config.batch_size == 0:
            conn.commit()
            print(f"\n📦 批量提交 ({i+1}/{len(docs)})")
        
        time.sleep(0.1)
    
    conn.commit()
    conn.close()
    
    final_status = check_existing_vectors(config.qmd_index)
    print(f"\n🎉 完成!")
    print(f"   成功: {success_count}")
    print(f"   失败: {error_count}")
    print(f"   总计: {final_status['embedded']}/{final_status['total']} 已嵌入")


def main():
    parser = argparse.ArgumentParser(description="Ollama → QMD 向量嵌入工具")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新嵌入所有文档")
    parser.add_argument("--dry-run", "-n", action="store_true", help="只显示待处理文档，不实际嵌入")
    parser.add_argument("--model", "-m", default=config.ollama_model, help=f"Ollama embedding 模型")
    
    args = parser.parse_args()
    
    print(f"🤖 使用模型: {args.model}")
    print(f"📁 QMD 索引: {config.qmd_index}")
    print()
    
    embed_documents(dry_run=args.dry_run, force=args.force, model=args.model)


if __name__ == "__main__":
    main()
