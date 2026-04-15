#!/usr/bin/env python3
"""
User Preference Profile - 用户行为偏好提取
从 .learnings/LEARNINGS.md 提取用户偏好，生成 profile
"""
import re, json
from pathlib import Path
from datetime import datetime
from collections import Counter

LEARNINGS_DIR = Path.home() / ".openclaw/workspace/.learnings"
OUTPUT_DIR = Path.home() / ".openclaw/workspace/.state/evolution"
PROFILE_PATH = OUTPUT_DIR / 'user-preferences.json'

def extract_preferences():
    learn_path = LEARNINGS_DIR / "LEARNINGS.md"
    if not learn_path.exists():
        return {}
    
    content = learn_path.read_text(encoding='utf-8')
    entries = re.split(r'^## ', content, flags=re.MULTILINE)
    
    corrections = []
    best_practices = []
    
    for entry in entries[1:]:
        cat_match = re.search(r'\*\*Category\*\*:\s*(\w+)', entry)
        if not cat_match: continue
        cat = cat_match.group(1)
        
        summary_match = re.search(r'### Summary\n(.+)', entry)
        details_match = re.search(r'### Details\n(.+)', entry, re.DOTALL)
        
        item = {
            'title': entry.split('\n')[0].strip(),
            'summary': summary_match.group(1).strip() if summary_match else '',
            'details': details_match.group(1).strip()[:300] if details_match else '',
        }
        
        if cat == 'correction':
            corrections.append(item)
        elif cat == 'best_practice':
            best_practices.append(item)
    
    return {'corrections': corrections, 'best_practices': best_practices}

def build_profile(data):
    profile = {
        'last_updated': datetime.now().isoformat(),
        'total_corrections': len(data['corrections']),
        'total_best_practices': len(data['best_practices']),
        'patterns': {
            'concise': 0,
            'technical': 0,
            'creative': 0,
            'direct': 0,
        },
        'top_corrections': [],
        'top_practices': [],
    }
    
    # 简单模式识别（关键词推断）
    correction_texts = ' '.join(c['summary'] for c in data['corrections'])
    
    if '太长' in correction_texts or '简洁' in correction_texts:
        profile['patterns']['concise'] = 1
    if '代码' in correction_texts or '技术' in correction_texts:
        profile['patterns']['technical'] = 1
    if '创意' in correction_texts or '有趣' in correction_texts:
        profile['patterns']['creative'] = 1
    if '直接' in correction_texts or '不要' in correction_texts:
        profile['patterns']['direct'] = 1
    
    profile['top_corrections'] = data['corrections'][-5:]  # 最近5条
    profile['top_practices'] = data['best_practices'][-5:]
    
    return profile

def main():
    data = extract_preferences()
    profile = build_profile(data)
    
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    
    print(f"# 用户偏好画像\n")
    print(f"更新时间：{profile['last_updated']}")
    print(f"累计纠正：{profile['total_corrections']}次")
    print(f"累计最佳实践：{profile['total_best_practices']}次")
    print(f"\n行为模式：")
    for p, v in profile['patterns'].items():
        if v:
            print(f"  ✅ {p}")
    
    print(f"\n📄 Profile: {PROFILE_PATH}")

if __name__ == '__main__':
    main()
