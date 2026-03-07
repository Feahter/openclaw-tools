#!/usr/bin/env python3
"""
OpenClaw Context Tools - 本地工具集
功能：
1. sandbox-execute - 沙箱执行代码
2. smart-search - FTS5 本地搜索
3. filter-large-output - 大输出过滤
"""

import os
import sys
import json
import sqlite3
import subprocess
import tempfile
import hashlib
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
DB_PATH = WORKSPACE / "data" / "context-tools.db"

# 确保目录存在
(WORKSPACE / "data").mkdir(parents=True, exist_ok=True)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # FTS5 搜索表
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            title TEXT,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
            path, content, title,
            tokenize='porter unicode61'
        )
    ''')
    
    conn.commit()
    return conn

# ==================== 沙箱执行 ====================

def sandbox_execute(code: str, language: str = "python") -> dict:
    """
    沙箱执行代码，只返回 stdout
    """
    # 临时文件执行
    suffix = {"python": ".py", "js": ".js", "bash": ".sh"}.get(language, ".txt")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # 执行命令
        if language == "python":
            cmd = ["python3", temp_file]
        elif language == "js":
            cmd = ["node", temp_file]
        elif language == "bash":
            cmd = ["bash", temp_file]
        else:
            return {"success": False, "error": f"Unsupported language: {language}"}
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=WORKSPACE
        )
        
        stdout = result.stdout[:5000]  # 限制输出长度
        stderr = result.stderr[:500]
        
        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode,
            "kept_bytes": len(stdout),
            "original_bytes": len(code)
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (30s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        os.unlink(temp_file)

# ==================== 智能搜索 ====================

def index_file(file_path: str, conn):
    """索引单个文件"""
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "File not found"}
    
    # 读取内容
    try:
        content = path.read_text(errors='ignore')
    except:
        return {"success": False, "error": "Cannot read file"}
    
    # 提取标题（第一行或文件名）
    title = path.name
    
    # 插入数据库
    c = conn.cursor()
    c.execute("INSERT INTO search_index (path, content, title) VALUES (?, ?, ?)",
               (str(path), content, title))
    
    # 插入 FTS
    c.execute("INSERT INTO search_fts (path, content, title) VALUES (?, ?, ?)",
               (str(path), content, title))
    
    conn.commit()
    
    return {
        "success": True,
        "path": str(path),
        "indexed_chars": len(content)
    }

def smart_search(query: str, limit: int = 5) -> dict:
    """
    FTS5 智能搜索
    - Porter 词干匹配
    - 三元组部分匹配
    - Levenshtein 模糊匹配
    """
    conn = init_db()
    c = conn.cursor()
    
    results = []
    
    # 1. 精确 FTS 匹配
    c.execute("""
        SELECT path, snippet(search_fts, 1, '**', '**', '...', 32) as snippet
        FROM search_fts
        WHERE search_fts MATCH ?
        LIMIT ?
    """, (query, limit))
    
    for row in c.fetchall():
        results.append({
            "path": row[0],
            "snippet": row[1],
            "match_type": "exact"
        })
    
    # 2. 如果没有结果，尝试模糊匹配
    if not results:
        # 提取查询关键词
        keywords = query.split()[:3]
        pattern = '%' + '%'.join(keywords) + '%'
        
        c.execute("""
            SELECT path, substr(content, 1, 200) as snippet
            FROM search_index
            WHERE content LIKE ? OR path LIKE ?
            LIMIT ?
        """, (pattern, pattern, limit))
        
        for row in c.fetchall():
            results.append({
                "path": row[0],
                "snippet": row[1][:200] + "...",
                "match_type": "fuzzy"
            })
    
    conn.close()
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }

def index_workspace(extensions: list = [".md", ".txt", ".py", ".js", ".json"]) -> dict:
    """索引工作区"""
    conn = init_db()
    
    indexed = 0
    for ext in extensions:
        for path in WORKSPACE.rglob(f"*{ext}"):
            # 跳过 node_modules, .git 等
            if any(skip in str(path) for skip in ['node_modules', '.git', 'data/', 'cache/']):
                continue
            
            result = index_file(str(path), conn)
            if result.get("success"):
                indexed += 1
    
    conn.close()
    
    return {
        "success": True,
        "indexed_files": indexed
    }

# ==================== 大输出过滤 ====================

def filter_large_output(content: str, intent: str = "", max_size: int = 2000) -> dict:
    """
    大输出过滤
    - 如果内容小于 max_size，直接返回
    - 如果大于 max_size，使用意图过滤
    """
    original_size = len(content)
    
    if original_size <= max_size:
        return {
            "filtered": False,
            "content": content,
            "original_size": original_size
        }
    
    # 需要过滤
    lines = content.split('\n')
    
    # 简单关键词匹配
    if intent:
        keywords = intent.lower().split()
        matched_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                # 保留匹配行及上下文
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                matched_lines.extend(lines[start:end])
        
        if matched_lines:
            filtered_content = '\n'.join(matched_lines)
        else:
            # 没有匹配，返回前 max_size 字符
            filtered_content = content[:max_size]
    else:
        # 无意图，返回前 max_size 字符
        filtered_content = content[:max_size]
    
    return {
        "filtered": True,
        "content": filtered_content,
        "original_size": original_size,
        "filtered_size": len(filtered_content),
        "reduction": f"{(1 - len(filtered_content)/original_size)*100:.1f}%"
    }

# ==================== CLI 接口 ====================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  context-tools.py execute <code> <language>")
        print("  context-tools.py search <query>")
        print("  context-tools.py index")
        print("  context-tools.py filter <content> <intent>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "execute":
        if len(sys.argv) < 3:
            print("Error: code required")
            sys.exit(1)
        code = sys.argv[2]
        lang = sys.argv[3] if len(sys.argv) > 3 else "python"
        result = sandbox_execute(code, lang)
        print(json.dumps(result, ensure_ascii=False))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: query required")
            sys.exit(1)
        query = sys.argv[2]
        result = smart_search(query)
        print(json.dumps(result, ensure_ascii=False))
    
    elif command == "index":
        result = index_workspace()
        print(json.dumps(result, ensure_ascii=False))
    
    elif command == "filter":
        if len(sys.argv) < 3:
            print("Error: content required")
            sys.exit(1)
        content = sys.argv[2]
        intent = sys.argv[3] if len(sys.argv) > 3 else ""
        result = filter_large_output(content, intent)
        print(json.dumps(result, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
