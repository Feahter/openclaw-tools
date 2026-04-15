#!/usr/bin/env python3
"""
涌现检测器 - 监控skill组合，评估涌现价值，固化高分组合
用法: python3 emergence_detector.py scan [--min-uses 3] [--threshold 0.7]
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PATTERNS_DIR = Path(__file__).parent
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

def get_skill_descriptions():
    """获取所有skill的描述"""
    descriptions = {}
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                # 提取description
                for line in content.split('\n'):
                    if line.startswith('description'):
                        descriptions[skill_dir.name] = line.replace('description:', '').strip().strip('>').strip()
                        break
    return descriptions

def detect_combinations_from_sessions(days=7):
    """从最近session中发现skill组合"""
    # 使用session-miner的能力
    result = subprocess.run(
        ["python3", str(Path.home() / ".openclaw" / "workspace" / "scripts" / "evolution" / "session-miner.py"),
         "--days", str(days), "--format", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return defaultdict(int)
    
    try:
        data = json.loads(result.stdout)
    except:
        return defaultdict(int)
    
    combinations = defaultdict(int)
    
    # 分析每个session中的skill使用模式
    for session in data.get("sessions", []):
        skills_used = set()
        for msg in session.get("messages", []):
            # 检测skill调用模式
            content = msg.get("content", "")
            if "skill" in content.lower():
                # 简单模式匹配
                for skill_dir in SKILLS_DIR.iterdir():
                    if skill_dir.is_dir() and skill_dir.name in content:
                        skills_used.add(skill_dir.name)
        
        # 记录skill对
        skills_list = sorted(skills_used)
        for i in range(len(skills_list)):
            for j in range(i+1, len(skills_list)):
                combo = f"{skills_list[i]}+{skills_list[j]}"
                combinations[combo] += 1
    
    return combinations

def calculate_emergence_score(combo, skill_descriptions):
    """计算涌现分数"""
    skills = combo.split("+")
    if len(skills) < 2:
        return 0.0
    
    # 简化：基于描述重叠度计算互补性
    desc_a = skill_descriptions.get(skills[0], "")
    desc_b = skill_descriptions.get(skills[1], "")
    
    # 互补指标：描述不完全重叠
    overlap = len(set(desc_a.split()) & set(desc_b.split()))
    total = len(set(desc_a.split()) | set(desc_b.split()))
    
    if total == 0:
        return 0.5  # 默认
    
    # 互补性高（重叠少）= 涌现潜力高
    complementarity = 1 - (overlap / total) if total > 0 else 0.5
    
    return complementarity

def scan_and_report(min_uses=3, threshold=0.6):
    """扫描并生成报告"""
    print(f"🔍 Scanning for skill combinations (min {min_uses} uses, threshold {threshold})...")
    
    skill_descriptions = get_skill_descriptions()
    combinations = detect_combinations_from_sessions()
    
    # 过滤低频
    significant = {k: v for k, v in combinations.items() if v >= min_uses}
    
    if not significant:
        print("No significant combinations found.")
        return
    
    # 计算涌现分数
    scored = []
    for combo, uses in significant.items():
        score = calculate_emergence_score(combo, skill_descriptions)
        scored.append((combo, uses, score, uses * score))
    
    # 按综合分数排序
    scored.sort(key=lambda x: x[3], reverse=True)
    
    print(f"\n📊 Found {len(scored)} significant combinations:\n")
    print(f"{'Combination':<50} {'Uses':>6} {'Score':>7} {'Total':>7}")
    print("-" * 72)
    
    for combo, uses, score, total in scored[:20]:
        badge = "🏆" if score >= threshold else "  "
        print(f"{badge} {combo:<48} {uses:>6} {score:>7.2f} {total:>7.2f}")
    
    # 高分组合（建议固化）
    high_score = [x for x in scored if x[2] >= threshold]
    if high_score:
        print(f"\n✨ {len(high_score)} patterns above threshold - consider adding to registry:")
        for combo, uses, score, total in high_score[:5]:
            print(f"  python3 pattern_registry.py add {combo.replace('+', ' ')}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-uses", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.6)
    args = parser.parse_args()
    
    scan_and_report(args.min_uses, args.threshold)
