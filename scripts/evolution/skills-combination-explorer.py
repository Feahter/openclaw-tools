#!/usr/bin/env python3
"""
主动探索循环 - 扫描高频组合，提取模式
用法: python3 skills-combination-explorer.py [--days 7] [--min-uses 2]
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
PATTERNS_DIR = WORKSPACE / "skills" / "skill-orchestrator" / "patterns"
LCM_DB = Path.home() / ".qclaw/memory/lossless/lcm.db"
REPORT_FILE = WORKSPACE / ".state" / "combination-explorer-report.json"

# Skills 目录
SKILLS_DIR = WORKSPACE / "skills"

def get_all_skill_names():
    """获取所有skill名称"""
    skills = set()
    for d in SKILLS_DIR.iterdir():
        if d.is_dir():
            skills.add(d.name)
            # 也添加简称
            skills.add(d.name.replace("skill-", ""))
    return skills

def query_sessions_from_db(days=7):
    """直接从LCM DB查询sessions"""
    import sqlite3
    
    if not LCM_DB.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(LCM_DB))
        cursor = conn.cursor()
        
        # 获取最近N天的conversation_id
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT conversation_id, created_at 
            FROM conversations 
            WHERE created_at > ? 
            ORDER BY created_at DESC
        """, (cutoff.isoformat(),))
        
        convos = cursor.fetchall()
        
        # 获取每个convo的消息
        patterns_found = []
        
        for conv_id, created_at in convos:
            cursor.execute("""
                SELECT role, content FROM messages 
                WHERE conversation_id = ? AND role = 'user'
                ORDER BY created_at ASC
            """, (conv_id,))
            
            messages = cursor.fetchall()
            skills_in_convo = set()
            
            all_skills = get_all_skill_names()
            
            for role, content in messages:
                if not content:
                    continue
                # 简单字符串匹配
                for skill in all_skills:
                    if skill in content:
                        skills_in_convo.add(skill)
            
            # 记录共现
            skills_list = sorted(skills_in_convo)
            for i in range(len(skills_list)):
                for j in range(i+1, len(skills_list)):
                    patterns_found.append((skills_list[i], skills_list[j]))
        
        conn.close()
        return patterns_found
        
    except Exception as e:
        print(f"DB error: {e}")
        return []

def run_session_miner(days=7):
    """运行session-miner获取文本报告"""
    result = subprocess.run(
        ["python3", str(WORKSPACE / "scripts" / "evolution" / "session-miner.py"), str(days)],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return ""
    return result.stdout

def parse_patterns_from_report(report_text):
    """从session-miner报告文本中提Skill组合"""
    patterns = []
    
    # 从文本中提取skill名称
    all_skills = list(get_all_skill_names())
    
    # 查找报告中提到的skill
    mentioned = set()
    for skill in all_skills:
        if skill in report_text:
            mentioned.add(skill)
    
    # 如果在同一次运行中提到多个skill，记录为组合
    # 按段落分组
    sections = report_text.split("###")
    
    for section in sections:
        skills_in_section = set()
        for skill in all_skills:
            if skill in section:
                skills_in_section.add(skill)
        
        if len(skills_in_section) >= 2:
            for s1 in skills_in_section:
                for s2 in skills_in_section:
                    if s1 != s2:
                        patterns.append((s1, s2))
    
    return patterns

def count_patterns(patterns):
    """统计组合频率"""
    counter = {}
    for p in patterns:
        key = tuple(sorted(p))
        counter[key] = counter.get(key, 0) + 1
    
    # 转为排序列表
    result = []
    for (a, b), count in counter.items():
        result.append({
            "skills": [a, b],
            "combo": f"{a}+{b}",
            "count": count
        })
    
    return sorted(result, key=lambda x: x["count"], reverse=True)

def update_pattern_registry(high_freq_patterns):
    """更新模式注册表"""
    registry_file = PATTERNS_DIR / "registry.json"
    
    if registry_file.exists():
        registry = json.loads(registry_file.read_text())
    else:
        registry = {"patterns": [], "last_updated": None}
    
    existing_names = {p["name"] for p in registry["patterns"]}
    existing_combos = {tuple(sorted(p["skills"])) for p in registry["patterns"]}
    
    added = 0
    for p in high_freq_patterns:
        combo_key = tuple(sorted(p["skills"]))
        if combo_key in existing_combos:
            continue
        
        suggested_name = f"{p['skills'][0]}-{p['skills'][1]}"
        if suggested_name in existing_names:
            suggested_name = f"{p['skills'][0]}-{p['skills'][1]}-{p['count']}"
        
        registry["patterns"].append({
            "name": suggested_name,
            "skills": p["skills"],
            "trigger": "auto-detected",
            "emergence": "needs manual description",
            "usage_count": p["count"],
            "auto_detected": True,
            "added_at": datetime.now().isoformat()
        })
        existing_names.add(suggested_name)
        existing_combos.add(combo_key)
        added += 1
    
    registry["last_updated"] = datetime.now().isoformat()
    registry_file.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
    
    return added

def main():
    days = 7
    min_uses = 2
    
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        days = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else days
    
    if "--min-uses" in sys.argv:
        idx = sys.argv.index("--min-uses")
        min_uses = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else min_uses
    
    print("🔄 Skills Combination Explorer")
    print("=" * 40)
    print(f"   Period: {days} days, Min uses: {min_uses}")
    
    # 方法1: 直接查LCM DB
    print("\n📡 Querying LCM database...")
    db_patterns = query_sessions_from_db(days)
    print(f"   Found {len(db_patterns)} co-occurrence records from DB")
    
    # 方法2: 解析session-miner报告
    print("\n📡 Running session-miner report...")
    report_text = run_session_miner(days)
    report_patterns = parse_patterns_from_report(report_text)
    print(f"   Found {len(report_patterns)} patterns from report")
    
    # 合并
    all_patterns = db_patterns + report_patterns
    print(f"   Total: {len(all_patterns)} patterns")
    
    # 统计频率
    patterns = count_patterns(all_patterns)
    
    if not patterns:
        print("\n⚠️ No skill combinations found.")
        print("   This is normal if you haven't used multiple skills together recently.")
        return
    
    # 过滤低频
    significant = [p for p in patterns if p["count"] >= min_uses]
    print(f"\n📊 Significant patterns (≥{min_uses} uses): {len(significant)}")
    
    print("\n   Top patterns:")
    for p in patterns[:10]:
        print(f"   - {p['combo']}: {p['count']} times")
    
    # 更新注册表
    print("\n💾 Updating pattern registry...")
    added = update_pattern_registry(significant)
    print(f"   Added {added} new patterns")
    
    # 生成报告
    report = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "total_patterns_found": len(patterns),
        "significant_patterns": len(significant),
        "top_patterns": patterns[:10],
        "next_steps": [
            "Review patterns in skill-orchestrator/patterns/registry.json",
            "Add emergence descriptions for auto-detected patterns",
            "Consider creating meta-skills for top combinations"
        ]
    }
    
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 40)
    print(f"📊 Report: {REPORT_FILE}")
    print(f"📈 Total: {len(patterns)} patterns, {len(significant)} significant")

if __name__ == "__main__":
    main()
