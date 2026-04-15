#!/usr/bin/env python3
"""
Skill Health Monitor - 技能健康度监测
跟踪skill使用频率，识别废弃技能
"""
import json, subprocess
from pathlib import Path
from datetime import datetime, timedelta
import re

SKILLS_DIR = Path.home() / ".openclaw/workspace/skills"
STATE_FILE = Path.home() / ".openclaw/workspace/.state/evolution/skill-health.json"
MINING_REPORT = Path.home() / ".openclaw/workspace/.state/evolution/daily-mining.md"

def get_skill_last_used(skill_name):
    """检查skill在挖掘报告中出现频率"""
    if not MINING_REPORT.exists():
        return 0
    
    content = MINING_REPORT.read_text(encoding='utf-8')
    # 简单计数（实际应该用向量相似度）
    skill_short = skill_name.replace('-', ' ').replace('_', ' ')
    count = content.lower().count(skill_short.lower())
    return min(count, 10)  # 封顶

def scan_skills():
    """扫描skills目录，收集基本信息"""
    skills = []
    for d in SKILLS_DIR.iterdir():
        if not d.is_dir() or d.name.startswith('.'):
            continue
        skill_file = d / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            # 提取description前100字
            desc_match = re.search(r'description:\s*>[^\n]*\n\s*(.+?)(?:\n|---\n)', content, re.DOTALL)
            desc = desc_match.group(1).strip()[:80] if desc_match else ''
            
            # 尝试获取mtime
            mtime = d.stat().st_mtime
            
            skills.append({
                'name': d.name,
                'description': desc,
                'last_modified': datetime.fromtimestamp(mtime).isoformat(),
                'health_score': 5,  # 默认5分
                'mention_freq': get_skill_last_used(d.name),
            })
    return skills

def score_skills(skills):
    """为技能打分"""
    for s in skills:
        score = 5  # 基础分
        # 提及频率加分
        score += min(s['mention_freq'], 5)
        # 最近修改时间（30天内+2分）
        try:
            last_mod = datetime.fromisoformat(s['last_modified'])
            if (datetime.now() - last_mod).days < 30:
                score += 2
        except:
            pass
        s['health_score'] = min(score, 10)
    
    return sorted(skills, key=lambda x: -x['health_score'])

def main():
    skills = scan_skills()
    scored = score_skills(skills)
    
    # 找出健康度低的（<4分且mention_freq=0）
    low_health = [s for s in scored if s['health_score'] < 4]
    
    result = {
        'checked_at': datetime.now().isoformat(),
        'total_skills': len(skills),
        'skills': scored,
        'low_health_warnings': [
            {
                'name': s['name'],
                'reason': f"health={s['health_score']}, mentions={s['mention_freq']}",
                'suggestion': '考虑合并到通用技能或卸载'
            }
            for s in low_health
        ]
    }
    
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"# 技能健康度报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print(f"总技能数：{len(skills)}")
    print(f"\n🏥 健康度TOP10：")
    for s in scored[:10]:
        bar = "█" * s['health_score'] + "░" * (10 - s['health_score'])
        print(f"  {s['name']:<35} {bar} {s['health_score']}/10  (提及{s['mention_freq']}次)")
    
    if low_health:
        print(f"\n⚠️ 低健康度技能（需关注）：")
        for s in low_health:
            print(f"  - {s['name']}: {s['description'][:40]}")
    
    print(f"\n📄 详细报告：{STATE_FILE}")

if __name__ == '__main__':
    main()
