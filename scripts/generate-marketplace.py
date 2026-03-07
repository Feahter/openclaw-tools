#!/usr/bin/env python3
"""扫描 skills/ 目录，生成 marketplace.json"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
OUTPUT = REPO_ROOT / "marketplace.json"


def parse_frontmatter(skill_md: Path) -> dict:
    """从 SKILL.md 提取 YAML frontmatter 中的 name 和 description"""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    fm = text[3:end].strip()
    result = {}
    for key in ("name", "description", "version"):
        match = re.search(rf'^{key}:\s*(.+)$', fm, re.MULTILINE)
        if match:
            val = match.group(1).strip().strip('"').strip("'")
            result[key] = val
    return result


def parse_meta(meta_path: Path) -> dict:
    """从 _meta.json 提取 slug 和 version"""
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return {k: data[k] for k in ("slug", "version") if k in data}
    except Exception:
        return {}


def main():
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        dir_name = skill_dir.name
        fm = parse_frontmatter(skill_md)
        meta = parse_meta(skill_dir / "_meta.json") if (skill_dir / "_meta.json").exists() else {}

        entry = {
            "name": fm.get("name", dir_name),
            "slug": meta.get("slug", dir_name),
            "description": fm.get("description", ""),
            "version": meta.get("version", fm.get("version", "")),
            "path": f"skills/{dir_name}",
        }
        skills.append(entry)

    marketplace = {
        "version": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(skills),
        "skills": skills,
    }

    OUTPUT.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {OUTPUT} with {len(skills)} skills")


if __name__ == "__main__":
    main()
