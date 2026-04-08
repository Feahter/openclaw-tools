#!/usr/bin/env python3
"""
wiki-query — Search the llm-wiki-agent wiki
Usage: python wiki_query.py <query> [--limit 3]
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Wiki is at skills/llm-wiki-agent/wiki/ (sibling to wiki-query/)
WIKI_DIR = Path(__file__).parent.parent.parent / "llm-wiki-agent" / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"


def search_wiki(query: str, limit: int = 3) -> list[dict]:
    """Simple keyword search across wiki titles and content."""
    results = []
    query_words = query.lower().split()

    # Search index titles
    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        # Extract wiki links from index
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for match in link_pattern.finditer(index_content):
            title, link = match.group(1), match.group(2)
            # Search in title
            if any(w.lower() in title.lower() for w in query_words):
                results.append({
                    "title": title,
                    "path": WIKI_DIR / link if not link.startswith("http") else link,
                    "match_type": "title",
                    "path_str": link
                })

    # Search concept/entity files
    search_dirs = [WIKI_DIR / "concepts", WIKI_DIR / "entities", WIKI_DIR / "sources"]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for md_file in search_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].lstrip("# ").strip()
            content_lower = content.lower()

            # Count query word matches
            match_count = sum(1 for w in query_words if w in content_lower)
            title_match = any(w.lower() in first_line.lower() for w in query_words)

            if match_count > 0 or title_match:
                # Score by match count + title bonus
                score = match_count + (2 if title_match else 0)
                results.append({
                    "title": first_line,
                    "path": md_file,
                    "match_type": "title" if title_match else "content",
                    "score": score,
                    "path_str": str(md_file.relative_to(WIKI_DIR.parent.parent))
                })

    # Dedupe by path, sort by score
    seen = set()
    deduped = []
    for r in sorted(results, key=lambda x: -x.get("score", 0)):
        key = str(r["path"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped[:limit]


def format_result(result: dict, content_preview: str = "") -> str:
    """Format a search result."""
    path_str = result.get("path_str", str(result["path"]))
    title = result.get("title", "Untitled")
    match_type = result.get("match_type", "content")

    lines = [f"## {title}", f"**来源**: `{path_str}` | **匹配**: {match_type}", ""]
    if content_preview:
        lines.append(content_preview[:200] + ("..." if len(content_preview) > 200 else ""))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search the llm-wiki-agent wiki")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=3, help="Max results (default: 3)")
    args = parser.parse_args()

    results = search_wiki(args.query, args.limit)

    if not results:
        print(f"No results for: {args.query}")
        print(f"Tried wiki at: {WIKI_DIR}")
        sys.exit(0)

    print(f"\n🔍 Wiki search: {args.query}\n")
    print(f"Found {len(results)} result(s):\n")

    for i, r in enumerate(results, 1):
        path = r["path"]
        content = ""
        if hasattr(path, "read_text"):
            content = path.read_text(encoding="utf-8")
            # Get relevant snippet
            lines = content.split("\n")
            # Skip first heading
            snippet_lines = []
            in_section = False
            for line in lines[1:]:
                if line.startswith("## "):
                    if snippet_lines:
                        break
                    in_section = True
                    continue
                if in_section and line.strip():
                    snippet_lines.append(line.strip())

            content = " ".join(snippet_lines[:3])

        print(format_result(r, content))
        print()


if __name__ == "__main__":
    main()
