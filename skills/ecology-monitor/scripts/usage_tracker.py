#!/usr/bin/env python3
"""
usage_tracker.py — Skill 使用频率追踪器

轻量级使用记录，每次 skill 被加载时追加到 usage.jsonl。
可被 OpenClaw hook 或心跳任务调用。
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


USAGE_DIR = Path.home() / ".openclaw" / "workspace" / ".state" / "skill-usage"
USAGE_DIR.mkdir(parents=True, exist_ok=True)
USAGE_FILE = USAGE_DIR / "usage.jsonl"


def record_usage(skill_name: str, trigger: str = None, session_id: str = None) -> dict:
    """
    记录一次 skill 使用
    
    Returns:
        {"recorded": True, "skill": skill_name, "timestamp": iso}
    """
    entry = {
        "skill": skill_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trigger": trigger,
        "session_id": session_id
    }
    
    with open(USAGE_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return {"recorded": True, **entry}


def get_skill_usage(days: int = 30) -> dict:
    """
    获取 skill 使用统计
    
    Returns:
        {skill_name: {"count": N, "last_used": iso, "triggers": [trigger1, trigger2, ...]}}
    """
    if not USAGE_FILE.exists():
        return {}
    
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    stats = {}
    
    with open(USAGE_FILE) as f:
        for line in f:
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp"]).timestamp()
                if ts < cutoff:
                    continue
                
                skill = entry["skill"]
                if skill not in stats:
                    stats[skill] = {"count": 0, "last_used": None, "triggers": set()}
                
                stats[skill]["count"] += 1
                stats[skill]["last_used"] = entry["timestamp"]
                if entry.get("trigger"):
                    stats[skill]["triggers"].add(entry["trigger"])
            except:
                continue
    
    # 转换 set 为 list
    for skill in stats:
        stats[skill]["triggers"] = list(stats[skill]["triggers"])
    
    return stats


def get_top_skills(n: int = 20, days: int = 30) -> list:
    """获取使用最频繁的 N 个 skills"""
    stats = get_skill_usage(days)
    sorted_skills = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
    return sorted_skills[:n]


def get_neglected_skills(all_skills: list, days: int = 30, min_usage: int = 1) -> list:
    """获取被忽视的 skills（使用次数 < min_usage）"""
    stats = get_skill_usage(days)
    used = set(stats.keys())
    neglected = [s for s in all_skills if s not in used]
    return neglected


def main():
    if len(sys.argv) < 2:
        # 统计模式
        print("=" * 50)
        print("Skill 使用统计")
        print("=" * 50)
        
        top = get_top_skills(10, days=30)
        if top:
            print(f"\n📊 Top 10 Skills (近30天):")
            for i, (skill, data) in enumerate(top, 1):
                print(f"  {i}. {skill}: {data['count']}次")
                if data['triggers']:
                    print(f"      触发: {', '.join(data['triggers'][:3])}")
        else:
            print("\n暂无使用记录")
            print(f"使用以下命令记录: usage_tracker.py record <skill-name>")
        
        return
    
    cmd = sys.argv[1]
    
    if cmd == "record" and len(sys.argv) >= 3:
        skill = sys.argv[2]
        trigger = sys.argv[3] if len(sys.argv) >= 4 else None
        result = record_usage(skill, trigger)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "stats":
        days = int(sys.argv[2]) if len(sys.argv) >= 3 else 30
        top = get_top_skills(20, days)
        print(json.dumps(top, ensure_ascii=False, indent=2))
    
    elif cmd == "neglected" and len(sys.argv) >= 3:
        all_skills_path = sys.argv[2]
        try:
            import yaml
            with open(all_skills_path) as f:
                data = yaml.safe_load(f)
                all_skills = [s for s in data.keys()]
        except:
            all_skills = sys.argv[3].split(",") if len(sys.argv) >= 4 else []
        
        neglected = get_neglected_skills(all_skills)
        print(f"被忽视的 skills ({len(neglected)}):")
        for s in neglected:
            print(f"  - {s}")
    
    else:
        print("Usage:")
        print("  usage_tracker.py                    # 显示统计")
        print("  usage_tracker.py record <skill> [trigger]  # 记录使用")
        print("  usage_tracker.py stats [days=30]      # JSON 统计")


if __name__ == "__main__":
    main()
