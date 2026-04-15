#!/usr/bin/env python3
"""
wiki-query — Search the llm-wiki-agent wiki

【算法优化 v2】预计算Snippet缓存：
- 旧：每次搜索全读文件取snippet，O(n)文件IO
- 新：Snippet预计算+缓存，只读变化的文件，O(变化文件数)
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Wiki is at skills/llm-wiki-agent/wiki/ (sibling to wiki-query/)
WIKI_DIR = Path(__file__).parent.parent.parent / "llm-wiki-agent" / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
CACHE_FILE = Path(__file__).parent / "snippets_cache.json"

# ── Snippet预计算缓存 ───────────────────────────────────────

def get_mtime_key(path: Path) -> str:
    """获取文件的mtime+size作为缓存key"""
    try:
        stat = path.stat()
        return f"{stat.st_mtime:.0f}_{stat.st_size}"
    except:
        return ""


def load_snippets_cache() -> dict:
    """加载snippet缓存"""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except:
        return {}


def save_snippets_cache(cache: dict) -> None:
    """保存snippet缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))


def extract_snippet(content: str) -> str:
    """从文件内容提取snippet（前3行正文）"""
    lines = content.split("\n")
    snippet_lines = []
    in_section = False
    for line in lines[1:]:  # skip first heading
        if line.startswith("## "):
            if snippet_lines:
                break
            in_section = True
            continue
        if in_section and line.strip():
            snippet_lines.append(line.strip())
    return " ".join(snippet_lines[:3])


def build_snippets_cache(force: bool = False) -> dict:
    """
    构建/更新snippet缓存。
    【算法优化v2核心】：
    - 只读 mtime 变化的文件（增量更新）
    - 已缓存且文件未变 → 直接用缓存值
    """
    cache = load_snippets_cache()
    search_dirs = [
        WIKI_DIR / "concepts",
        WIKI_DIR / "entities",
        WIKI_DIR / "sources",
    ]

    updated = 0
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for md_file in search_dir.glob("*.md"):
            key = get_mtime_key(md_file)
            file_id = str(md_file)
            # 增量：文件未变，直接用缓存
            if not force and cache.get(file_id, {}).get("_key") == key:
                continue
            # 文件变化或新文件 → 重新计算snippet
            try:
                content = md_file.read_text(encoding="utf-8")
                first_line = content.split("\n")[0].lstrip("# ").strip()
                snippet = extract_snippet(content)
                cache[file_id] = {
                    "_key": key,
                    "_mtime": key.split("_")[0] if key else "",
                    "title": first_line,
                    "snippet": snippet,
                    "content_lower": content.lower(),
                }
                updated += 1
            except Exception:
                pass

    if updated > 0:
        save_snippets_cache(cache)
    return cache


def invalidate_cache(md_file: Path) -> None:
    """单文件缓存失效"""
    cache = load_snippets_cache()
    file_id = str(md_file)
    if file_id in cache:
        del cache[file_id]
        save_snippets_cache(cache)


# ── 搜索 ───────────────────────────────────────────────

def search_wiki(query: str, limit: int = 3, use_cache: bool = True) -> list[dict]:
    """
    【算法优化v2】：
    - 构建/更新snippet缓存（增量）
    - 在缓存中搜索，不需要每次读文件
    """
    cache = build_snippets_cache() if use_cache else {}
    query_words = query.lower().split()
    results = []

    # 1. Index标题搜索（仍然读index文件，很小）
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for match in link_pattern.finditer(index_content):
            title, link = match.group(1), match.group(2)
            if any(w.lower() in title.lower() for w in query_words):
                results.append({
                    "title": title,
                    "path": WIKI_DIR / link if not link.startswith("http") else link,
                    "match_type": "title",
                    "path_str": link,
                    "score": 3,  # title match bonus
                    "cached": False,
                })

    # 2. 在缓存中搜索（不再读文件）
    for file_id, data in cache.items():
        content_lower = data.get("content_lower", "")
        title = data.get("title", "")
        match_count = sum(1 for w in query_words if w in content_lower)
        title_match = any(w.lower() in title.lower() for w in query_words)

        if match_count > 0 or title_match:
            score = match_count + (3 if title_match else 0)
            md_path = Path(file_id)
            results.append({
                "title": title,
                "path": md_path,
                "match_type": "title" if title_match else "content",
                "score": score,
                "snippet": data.get("snippet", ""),
                "path_str": str(md_path.relative_to(WIKI_DIR.parent.parent)),
                "cached": True,
            })

    # 去重 + 排序
    seen = set()
    deduped = []
    for r in sorted(results, key=lambda x: -x.get("score", 0)):
        key = str(r["path"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped[:limit]


def format_result(result: dict) -> str:
    """Format a search result."""
    path_str = result.get("path_str", str(result.get("path", "")))
    title = result.get("title", "Untitled")
    match_type = result.get("match_type", "content")
    snippet = result.get("snippet", "")

    lines = [
        f"## {title}",
        f"**来源**: `{path_str}` | **匹配**: {match_type}{" | 💾" if result.get("cached") else ""}",
        "",
    ]
    if snippet:
        lines.append(snippet[:200] + ("..." if len(snippet) > 200 else ""))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search the llm-wiki-agent wiki")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=3, help="Max results (default: 3)")
    parser.add_argument("--no-cache", action="store_true", help="Disable snippet cache")
    parser.add_argument("--rebuild-cache", action="store_true", help="Force rebuild snippet cache")
    args = parser.parse_args()

    if args.rebuild_cache:
        build_snippets_cache(force=True)
        print("✅ Snippet cache rebuilt")

    results = search_wiki(
        args.query, args.limit,
        use_cache=not args.no_cache
    )

    if not results:
        print(f"No results for: {args.query}")
        sys.exit(0)

    print(f"\n🔍 Wiki search: {args.query}\n")
    print(f"Found {len(results)} result(s):\n")

    for r in results:
        print(format_result(r))
        print()


if __name__ == "__main__":
    main()
