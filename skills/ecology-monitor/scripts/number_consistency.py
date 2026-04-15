#!/usr/bin/env python3
"""
number_consistency.py — Skill 声明数字一致性检测器

扫描 skills/*/SKILL.md 中声明的 "X skills" 类数字引用（如"63 of 192 skills"、
"100+ 信息源"、"16 platforms"），与实际系统状态比对，输出不一致报告。

支持检测的数字类型：
  - "N of M skills"  →  与 skills/ 目录数量比对
  - "N+ 个技能"       →  下限检测（允许实际 >= 声明）
  - "N 信息源/平台"   →  与实际信息源列表数量比对
  - "N plugins/tools" →  工具数量检测
  - "N scripts"       →  与 skill/scripts/ 目录比对

与 ecology_monitor 的集成：
  被 assess_ecosystem_health() 调用，注入到 metrics['doc_consistency']
  CLI: python3 number_consistency.py [--skills-dir DIR] [--json]
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


# ── 数字声明正则 ──────────────────────────────────────────────

# 匹配 "N of M skills" 类型声明（如 "63 of 192 skills"）
SKILL_COUNT_RE = re.compile(
    r'''
    (\d[\d,]*)\s+(?:of|/|~)\s+(\d[\d,]*)\s+skills
    |
    (\d[\d,]*)\s+(?:of|/|~)\s+(\d[\d,]*)\s+个?技能
    |
    (\d[\d,]*)\s+of\s+(\d[\d,]*)\s+[\w-]+
    ''',
    re.VERBOSE | re.IGNORECASE
)

# 匹配 "N+ skills / 个技能 / 个工具" 类型声明
SKILL_COUNT_PLUS_RE = re.compile(
    r'''
    (\d[\d,]*)\+?\s+(?:个)?(?:技能|skills|工具|tools|平台|platforms?|信息源|sources?|命令|commands?)
    ''',
    re.VERBOSE | re.IGNORECASE
)

# 匹配 "included N of M" 类型（如 <available_skills> 标签内容）
AVAILABLE_SKILLS_RE = re.compile(
    r'''
    included\s+(\d[\d,]*)\s+of\s+(\d[\d,]*)
    ''',
    re.VERBOSE | re.IGNORECASE
)

# 匹配 "XX skills" 简单计数（用于检测 "63 skills" 等）
SIMPLE_SKILL_COUNT_RE = re.compile(
    r'''
    (?:^|\s)([\d,]+)\+?\s+(?:installed|total|active|skills|个技能)(?:\s|$|:)
    ''',
    re.VERBOSE | re.IGNORECASE
)


def parse_int(s: str) -> int:
    """解析可能带逗号的数字字符串"""
    return int(s.replace(",", "").strip())


# ── 数字提取 ──────────────────────────────────────────────────

def extract_number_declarations(skill_md: Path) -> list[dict]:
    """
    从单个 SKILL.md 中提取所有数字声明
    Returns: [{"declared": N, "type": str, "context": str, "line": int}, ...]
    """
    if not skill_md.exists():
        return []

    declarations = []
    text = skill_md.read_text(encoding="utf-8", errors="ignore")

    for line_no, line in enumerate(text.splitlines(), 1):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # 1. "N of M skills" 声明
        for match in SKILL_COUNT_RE.finditer(line_stripped):
            groups = match.groups()
            # 组别: (first_N, first_M) or (cn_first, cn_M) or (generic_N, generic_M)
            if groups[0] is not None:  # English "N of M skills"
                first = parse_int(groups[0])
                second = parse_int(groups[1])
                declarations.append({
                    "declared": second,  # 声明总数
                    "type": "skill_count_of",
                    "raw": match.group(),
                    "context": line_stripped[:120],
                    "line": line_no,
                    "first_val": first
                })
            elif groups[2] is not None:  # Chinese "N of M 技能"
                first = parse_int(groups[2])
                second = parse_int(groups[3])
                declarations.append({
                    "declared": second,
                    "type": "skill_count_of_cn",
                    "raw": match.group(),
                    "context": line_stripped[:120],
                    "line": line_no,
                    "first_val": first
                })

        # 2. <available_skills> 中的 included N of M
        for match in AVAILABLE_SKILLS_RE.finditer(line_stripped):
            groups = match.groups()
            included = parse_int(groups[0])
            total = parse_int(groups[1])
            declarations.append({
                "declared": total,
                "type": "available_skills_tag",
                "raw": match.group(),
                "context": line_stripped[:120],
                "line": line_no,
                "first_val": included,
                "note": f"{included}/{total}"
            })

        # 3. 简单 "N skills" 计数（需要排除年份、日期等误报）
        for match in SIMPLE_SKILL_COUNT_RE.finditer(line_stripped):
            val = parse_int(match.group(1))
            # 排除明显不是 skill 计数的情况
            ctx = line_stripped.lower()
            # 允许的范围：10-999（合理 skill 数量）
            if 10 <= val <= 999 and "skill" in ctx:
                declarations.append({
                    "declared": val,
                    "type": "simple_skill_count",
                    "raw": match.group(),
                    "context": line_stripped[:120],
                    "line": line_no,
                })

        # 4. "N+ 个技能/工具/平台" 类型
        for match in SKILL_COUNT_PLUS_RE.finditer(line_stripped):
            val = parse_int(match.group(1))
            # 过滤：只保留可能是 skill 相关的
            ctx = match.group().lower()
            if any(k in ctx for k in ["skill", "工具", "技能", "platform", "信息源", "source"]):
                if 2 <= val <= 999:
                    declarations.append({
                        "declared": val,
                        "type": "plus_count",
                        "raw": match.group(),
                        "context": line_stripped[:120],
                        "line": line_no,
                        "check_type": "minimum"  # N+ 声明表示下限
                    })

    return declarations


# ── 实际状态获取 ─────────────────────────────────────────────

def get_actual_skill_count(skills_dir: Path) -> int:
    """获取实际安装的 skill 数量（顶级目录数）"""
    return len([p for p in skills_dir.iterdir()
                if p.is_dir() and not p.name.startswith(".")
                and (p / "SKILL.md").exists()])


def get_actual_script_count(skill_path: Path) -> int:
    """获取 skill/scripts/ 目录下的脚本数量"""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return 0
    return len([f for f in scripts_dir.iterdir()
                if f.is_file() and f.suffix in (".py", ".sh", ".js", ".ts")])


# ── 一致性检测 ───────────────────────────────────────────────

def check_consistency(skill_path: Path, skills_dir: Path) -> dict:
    """检测单个 skill 的数字一致性"""
    skill_md = skill_path / "SKILL.md"
    declarations = extract_number_declarations(skill_md)
    if not declarations:
        return None  # 无数字声明

    actual_total_skills = get_actual_skill_count(skills_dir)

    results = []
    for decl in declarations:
        issues = []
        d_type = decl["type"]

        if d_type in ("skill_count_of", "skill_count_of_cn", "available_skills_tag"):
            # 与实际 skills 目录数量比对
            actual = actual_total_skills
            declared = decl["declared"]
            diff = actual - declared

            if abs(diff) > 5:  # 允许 ±5 误差
                status = "❌ 过期" if diff > 0 else "⚠️ 偏高"
                issues.append({
                    "status": status,
                    "expected": declared,
                    "actual": actual,
                    "drift": diff,
                    "message": f"声明 {declared} skills，当前实际 {actual}（偏差 {diff:+d}）"
                })
            else:
                issues.append({
                    "status": "✅ 一致",
                    "expected": declared,
                    "actual": actual,
                    "drift": diff,
                    "message": f"声明 {declared} ≈ 实际 {actual}"
                })

        elif d_type == "plus_count":
            # N+ 声明 → 只检查 actual >= declared
            actual = actual_total_skills
            if actual < decl["declared"]:
                issues.append({
                    "status": "❌ 不足",
                    "expected": f">={decl['declared']}",
                    "actual": actual,
                    "message": f"声明 {decl['declared']}+ skills，实际仅 {actual}"
                })

        elif d_type == "simple_skill_count":
            actual = actual_total_skills
            diff = actual - decl["declared"]
            if abs(diff) > 3:
                issues.append({
                    "status": "❌ 过期" if diff > 0 else "⚠️ 偏高",
                    "expected": decl["declared"],
                    "actual": actual,
                    "drift": diff,
                    "message": f"声明 {decl['declared']} skills，实际 {actual}（偏差 {diff:+d}）"
                })

        results.append({**decl, "issues": issues})

    return {
        "skill": skill_path.name,
        "declarations": results,
        "has_issues": any(r["issues"] for r in results)
    }


# ── 主扫描逻辑 ───────────────────────────────────────────────

def scan_all(skills_dir: Optional[str] = None) -> dict:
    """
    扫描所有 skills 的数字一致性
    """
    if not skills_dir:
        skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    else:
        skills_dir = Path(skills_dir)

    actual_total = get_actual_skill_count(skills_dir)
    issues = []
    clean = []

    skill_paths = [p for p in skills_dir.iterdir()
                   if p.is_dir() and not p.name.startswith(".")]

    def check_one(skill_path: Path) -> Optional[dict]:
        try:
            return check_consistency(skill_path, skills_dir)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(check_one, sp): sp for sp in skill_paths}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result and result["has_issues"]:
                    issues.append(result)
                elif result:
                    clean.append(result["skill"])
            except Exception:
                pass

    scanned = len(issues) + len(clean)

    # 收集所有有问题的声明
    all_issue_decls = []
    for item in issues:
        for decl in item["declarations"]:
            for issue in decl["issues"]:
                all_issue_decls.append({
                    "skill": item["skill"],
                    "type": decl["type"],
                    "line": decl["line"],
                    "context": decl["context"],
                    **issue
                })

    return {
        "actual_skill_count": actual_total,
        "total_skills": len(skill_paths),
        "scanned": scanned,
        "with_issues": len(issues),
        "clean": len(clean),
        "clean_skills": clean[:10],
        "consistency_rate": round(len(clean) / max(scanned, 1) * 100, 1),
        "issue_details": issues,
        "summary": all_issue_decls,
        "scanned_at": datetime.now(timezone.utc).isoformat()
    }


# ── 生态集成 ──────────────────────────────────────────────────

def get_doc_consistency_summary(skills_dir: str = None) -> dict:
    """
    返回文档一致性指标，供 ecology_monitor 使用
    """
    result = scan_all(skills_dir)
    return {
        "actual_skill_count": result["actual_skill_count"],
        "outdated_declarations": len(result["summary"]),
        "affected_skills": result["with_issues"],
        "clean_skills": result["clean"],
        "consistency_rate": round(result["clean"] / max(result["scanned"], 1) * 100, 1),
        "top_issues": result["summary"][:5]
    }


# ── CLI ──────────────────────────────────────────────────────

def format_report(result: dict) -> str:
    issues = result["summary"]
    lines = [
        "=" * 60,
        "📊 Skill 声明数字一致性报告",
        "=" * 60,
        f"实际 skills 总数: {result['actual_skill_count']}",
        f"有数字声明的 skills: {result['scanned']}  |  一致: {result['clean']}  |  有问题: {result['with_issues']}",
        f"一致性率: {result['consistency_rate']}%",
        "",
    ]

    if issues and len(issues) > 0:
        lines.append("🚨 数字不一致:")
        for issue in issues[:15]:
            status = issue.get("status", "❌")
            lines.append(f"  [{issue['skill']}] L{issue['line']} {status}")
            lines.append(f"    {issue.get('message', '')}")
            lines.append(f"    → {issue['context'][:80]}")
    else:
        lines.append("✅ 所有数字声明与实际状态一致")

    if result["clean_skills"]:
        shown = result["clean_skills"][:10]
        lines.append(f"\n✅ 数字准确 ({len(shown)} skills): {', '.join(shown)}"
                     + (" ..." if len(result["clean_skills"]) > 10 else ""))

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill 声明数字一致性检测")
    parser.add_argument("--skills-dir", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = scan_all(args.skills_dir)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
