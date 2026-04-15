#!/usr/bin/env python3
"""
link_checker.py — Skill 内链完整性检测器

扫描 skills/*/SKILL.md 中的相对路径引用（./scripts/ ../skills/ 等路径），
验证目标文件/目录是否存在，输出破损链接报告。

支持引用类型：
  - ./scripts/xxx.sh / ./scripts/xxx.py
  - ../skills/xxx/  （跨 skill 引用）
  - ./SKILL.md （自身）
  - 其他相对路径：./xxx ./xxx.md ./xxx/ 等

与 ecology_monitor 的集成：
  被 assess_ecosystem_health() 调用，注入到 metrics['link_health']
  CLI: python3 link_checker.py [--skills-dir DIR] [--json] [--fix]
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


# 匹配 ~ 展开路径 (跨平台 home 目录)
HOME_PATH_RE = re.compile(r'^~/')


def expand_home(path_str: str) -> Path:
    """将 ~ 路径展开为实际 home 目录"""
    if HOME_PATH_RE.match(path_str):
        return Path.home() / path_str[2:]
    return Path(path_str)


# ── 链接提取 ──────────────────────────────────────────────────

def extract_links_from_skill(skill_path: Path) -> list[dict]:
    """
    从单个 SKILL.md 中提取所有相对路径引用
    Returns: [{"ref": str, "context": str, "line": int}, ...]
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return []

    links = []
    text = skill_md.read_text(encoding="utf-8", errors="ignore")

    # 标记代码块区域（排除代码块内的误报）
    in_code_block = False
    # 标记表格行（避免提取列分隔符 | 被误识别）
    in_table = False

    for line_no, line in enumerate(text.splitlines(), 1):
        # 切换代码块状态
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 标记表格行（以 | 开头或包含 | 的行）
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.endswith("|")
        if is_table_row:
            in_table = True

        # ── 1. 行内代码 `path` ──────────────────────────────
        # 匹配 `相对路径`（排除：变量名、单字符、API路径）
        code_refs = re.findall(r'`([^`]+?)`', line)
        for ref in code_refs:
            ref = ref.strip()
            # 过滤误报：单字符、变量名、API路径、空格多的、短变量
            if (not ref
                    or len(ref) < 2
                    or re.match(r'^[a-z_][a-z0-9_]*$', ref)  # snake_case 变量名
                    or ref.startswith(('http://', 'https://', '/', '#', 'mailto:'))
                    or '{' in ref  # 模板变量 {id}
                    or re.match(r'^[A-Z_/{}]+$', ref)  # 大写常量/API路径如 GET /v1/...
                    or re.match(r'^[a-z]\.$', ref)  # 单字母+点
                    or re.match(r'^\w+\([^)]{0,30}\)$', ref)  # 函数调用
                    or ' ' not in ref and len(ref) <= 3 and re.match(r'^[a-z]+$', ref)):
                continue

            # 必须是相对路径特征：./ 或 ../ 或相对文件名
            if (ref.startswith(('./', '../', '~/', '…/'))
                    or (not ref.startswith('/') and '.' in ref)
                    or re.match(r'^[a-z][a-z0-9_-]*\.[a-z]+$', ref)):  # filename.ext
                links.append({
                    "ref": ref,
                    "line": line_no,
                    "context": stripped[:120],
                    "type": "inline"
                })

        # ── 2. Markdown 链接 (text)(path) ──────────────────
        md_link_re = re.compile(r'\[.+?\]\(([^)]+?)\)')
        for match in md_link_re.finditer(line):
            ref = match.group(1).strip()
            if (not ref
                    or len(ref) < 2
                    or ref.startswith(('http://', 'https://', '#', 'mailto:', '/'))
                    or '{' in ref
                    or re.match(r'^[A-Z_/{}]+$', ref)):
                continue
            if (ref.startswith(('./', '../', '~/', '…/'))
                    or (not ref.startswith('/') and '.' in ref)):
                links.append({
                    "ref": ref,
                    "line": line_no,
                    "context": stripped[:120],
                    "type": "md_link"
                })

        # ── 3. 命令行中的 ./scripts/ 引用 ───────────────────
        # 匹配 "run: ./xxx" "cd ./xxx" "python3 ./xxx" 等
        cmd_refs = re.findall(r'(?:^|\s)((?:\./|(?:…)/)[^\s)`"\']+)', line)
        for ref in cmd_refs:
            ref = ref.strip()
            if not ref.startswith(("http://", "https://")):
                links.append({
                    "ref": ref,
                    "line": line_no,
                    "context": stripped[:120],
                    "type": "shell"
                })

    return links


def validate_link(skill_path: Path, ref: str) -> dict:
    """
    验证单个相对路径引用是否存在
    Returns: {"ref": str, "exists": bool, "target": str, "type": "file"|"dir"|"missing"}
    """
    # 清理 ref（去掉尾部符号）
    clean_ref = re.sub(r'[`\)\]\.]+$', '', ref).strip()
    if not clean_ref:
        return {"ref": ref, "exists": False, "target": "", "type": "missing"}

    # 将美化省略号 …/ 转换为 ../
    clean_ref = clean_ref.replace("…/", "../")

    # 解析相对路径基准
    # 支持：./xxx  → skill_path/xxx
    #       ../xxx → skill_path.parent/xxx
    #       scripts/xxx → skill_path/scripts/xxx
    parts = clean_ref.split("/")
    if parts[0] == ".":
        base = skill_path
        parts = parts[1:]
    elif parts[0] == "..":
        base = skill_path.parent
        parts = parts[1:]
    elif clean_ref.startswith("~/"):
        base = Path.home()
        parts = parts[1:]
    else:
        base = skill_path

    target = base.joinpath(*parts) if parts else base

    exists = target.exists()
    link_type = "dir" if exists and target.is_dir() else "file" if exists else "missing"

    return {
        "ref": ref,
        "exists": exists,
        "target": str(target),
        "type": link_type
    }


# ── 主扫描逻辑 ───────────────────────────────────────────────

def scan_skills(skills_dir: Optional[str] = None, max_workers: int = 8) -> dict:
    """
    扫描所有 skills，返回破损链接报告

    Returns:
        {
            "total_skills": int,
            "scanned_skills": int,
            "total_links": int,
            "broken_links": [{"skill": str, "ref": str, "target": str, "line": int, "context": str}, ...],
            "healthy_skills": [str, ...],
            "skill_detail": {skill_name: {"total": N, "broken": N, "links": [...]}}
        }
    """
    if not skills_dir:
        skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    else:
        skills_dir = Path(skills_dir)

    broken = []
    healthy = []
    skill_detail = {}
    total_links = 0

    # 收集所有 skill 路径
    skill_paths = [p for p in skills_dir.iterdir()
                   if p.is_dir() and not p.name.startswith(".")]

    def scan_skill(skill_path: Path) -> dict:
        links = extract_links_from_skill(skill_path)
        validated = []
        skill_broken = []

        for link in links:
            result = validate_link(skill_path, link["ref"])
            validated.append({**link, **result})
            if not result["exists"]:
                skill_broken.append({**link, **result})

        return skill_path.name, links, validated, skill_broken

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scan_skill, sp): sp for sp in skill_paths}
        for future in as_completed(futures):
            try:
                name, links, validated, skill_broken = future.result()
                skill_detail[name] = {
                    "total": len(links),
                    "broken": len(skill_broken),
                    "links": validated
                }
                total_links += len(links)
                broken.extend([{**b, "skill": name} for b in skill_broken])
                if not skill_broken and links:
                    healthy.append(name)
            except Exception as e:
                pass  # 忽略扫描失败的 skill

    # 按破损严重程度排序
    broken.sort(key=lambda x: (x["skill"], x["line"]))

    return {
        "total_skills": len(skill_paths),
        "scanned_skills": len(skill_detail),
        "total_links": total_links,
        "broken_links": broken,
        "healthy_skills": healthy,
        "skill_detail": skill_detail,
        "scanned_at": datetime.now(timezone.utc).isoformat()
    }


# ── 生态集成：注入到 ecology_monitor ─────────────────────────

def get_link_health_summary(skills_dir: str = None) -> dict:
    """
    返回 link health 指标，供 ecology_monitor 使用
    结构与 existing metrics 保持一致
    """
    result = scan_skills(skills_dir)
    total = result["total_links"]
    broken = len(result["broken_links"])
    healthy = result["scanned_skills"] - len({b["skill"] for b in result["broken_links"]})

    return {
        "total_links": total,
        "broken_links": broken,
        "healthy_links": total - broken,
        "link_integrity_rate": round((total - broken) / max(total, 1) * 100, 1),
        "healthy_skills_count": healthy,
        "broken_skills_count": len({b["skill"] for b in result["broken_links"]}),
        "top_broken": [
            {
                "skill": b["skill"],
                "ref": b["ref"],
                "target": b["target"],
                "line": b["line"]
            }
            for b in result["broken_links"][:5]
        ]
    }


# ── CLI ──────────────────────────────────────────────────────

def format_report(result: dict) -> str:
    broken = result["broken_links"]
    lines = [
        "=" * 60,
        "🔗 Skill 内链完整性报告",
        "=" * 60,
        f"扫描: {result['scanned_skills']}/{result['total_skills']} skills",
        f"总链接数: {result['total_links']}  |  破损: {len(broken)}  |  完整: {result['total_links'] - len(broken)}",
        f"链接完好率: {round((result['total_links'] - len(broken)) / max(result['total_links'], 1) * 100, 1)}%",
        "",
    ]

    if broken:
        lines.append("🚨 破损链接:")
        current_skill = None
        for b in broken:
            if b["skill"] != current_skill:
                lines.append(f"\n  [{b['skill']}]")
                current_skill = b["skill"]
            lines.append(f"    L{b['line']}: {b['ref']}  →  ❌ {b['target']}")
            if b.get("context"):
                lines.append(f"         {b['context'][:80]}")
    else:
        lines.append("✅ 所有链接完整，无破损引用")

    # 健康 skill
    if result["healthy_skills"]:
        lines.append(f"\n✅ 链接健康 ({len(result['healthy_skills'])} skills): "
                     f"{', '.join(result['healthy_skills'][:10])}"
                     + (" ..." if len(result['healthy_skills']) > 10 else ""))

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill 内链完整性检测")
    parser.add_argument("--skills-dir", default=None, help="skills 根目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--limit", type=int, default=0, help="限制扫描 skill 数量（调试用）")
    args = parser.parse_args()

    result = scan_skills(args.skills_dir)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
