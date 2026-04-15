#!/usr/bin/env python3
"""
组合模式注册器 - 固化高频组合为模板
用法: python3 pattern_registry.py add <skill-a> <skill-b> [--name NAME] [--emergence DESC]
"""
import json
import sys
from pathlib import Path
from datetime import datetime

PATTERNS_DIR = Path(__file__).parent
REGISTRY_FILE = PATTERNS_DIR / "registry.json"

def load_registry():
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {"patterns": [], "last_updated": None}

def save_registry(data):
    data["last_updated"] = datetime.now().isoformat()
    REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def add_pattern(skill_a, skill_b, name=None, emergence="", trigger=""):
    data = load_registry()
    
    # 检查是否已存在
    for p in data["patterns"]:
        if set(p["skills"]) == {skill_a, skill_b}:
            print(f"Pattern already exists: {p['name']}")
            return
    
    pattern = {
        "name": name or f"{skill_a}-{skill_b}",
        "skills": [skill_a, skill_b],
        "emergence": emergence,
        "trigger": trigger,
        "added_at": datetime.now().isoformat(),
        "usage_count": 1
    }
    data["patterns"].append(pattern)
    save_registry(data)
    print(f"Added: {pattern['name']}")

def list_patterns():
    data = load_registry()
    if not data["patterns"]:
        print("No patterns registered yet.")
        return
    for p in data["patterns"]:
        print(f"- {p['name']}: {', '.join(p['skills'])} ({p['usage_count']} uses)")

def increment_usage(pattern_name):
    data = load_registry()
    for p in data["patterns"]:
        if p["name"] == pattern_name:
            p["usage_count"] = p.get("usage_count", 0) + 1
            save_registry(data)
            return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 4:
        add_pattern(sys.argv[2], sys.argv[3], 
                    name=sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "list":
        list_patterns()
    else:
        print(__doc__)
