#!/usr/bin/env python3
"""
连接密度指标 - 衡量skill之间的输入输出重叠度
用法: python3 connection_density.py [--skills SKILL_A,SKILL_B]
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"

def parse_skill_io(skill_name):
    """解析skill的输入输出"""
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    
    if not skill_md.exists():
        return {"inputs": set(), "outputs": set(), "keywords": set()}
    
    content = skill_md.read_text()
    lines = content.split('\n')
    
    inputs = set()
    outputs = set()
    keywords = set()
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # 提取触发关键词
        if 'trigger' in line_lower or 'keyword' in line_lower:
            # 提取引号内的词
            words = line.split('"')
            for w in words:
                w = w.strip()
                if w and len(w) > 2:
                    keywords.add(w)
        
        # 提取输入模式
        if any(x in line_lower for x in ['input', 'receive', 'accept']):
            words = line.replace(',', ' ').split()
            for w in words:
                w = w.strip().lower()
                if len(w) > 3:
                    keywords.add(w)
        
        # 提取输出模式
        if any(x in line_lower for x in ['output', 'produce', 'return', 'generate']):
            words = line.replace(',', ' ').split()
            for w in words:
                w = w.strip().lower()
                if len(w) > 3:
                    keywords.add(w)
    
    return {"inputs": inputs, "outputs": outputs, "keywords": keywords}

def calculate_connection_density(skill_pairs=None):
    """计算skill之间的连接密度"""
    
    # 获取所有skill
    all_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    
    # 如果指定了pairs，只计算这些
    if skill_pairs:
        pairs_to_check = []
        for pair in skill_pairs:
            skills = pair.split(',')
            if len(skills) == 2:
                pairs_to_check.append(tuple(sorted(skills)))
    else:
        # 生成所有可能的pairs
        pairs_to_check = []
        for i, s1 in enumerate(all_skills):
            for s2 in all_skills[i+1:]:
                pairs_to_check.append((s1, s2))
    
    results = []
    
    # 解析每个skill的IO
    skill_io = {}
    for skill in all_skills:
        skill_io[skill] = parse_skill_io(skill)
    
    # 计算每对的连接密度
    for (s1, s2) in pairs_to_check:
        io1 = skill_io.get(s1, {"keywords": set()})
        io2 = skill_io.get(s2, {"keywords": set()})
        
        kw1 = io1.get("keywords", set())
        kw2 = io2.get("keywords", set())
        
        if not kw1 or not kw2:
            continue
        
        intersection = kw1 & kw2
        union = kw1 | kw2
        
        # 连接密度：重叠程度
        density = len(intersection) / len(union) if union else 0
        
        # 互补性：并集大小
        complementarity = len(union) / (len(kw1) + len(kw2)) if (len(kw1) + len(kw2)) > 0 else 0
        
        # 高价值连接：高互补 + 有一定重叠（不是完全无关）
        if density > 0.05 and density < 0.8:
            value_score = complementarity * (1 - abs(0.3 - density) * 2)
        else:
            value_score = 0
        
        results.append({
            "pair": f"{s1}+{s2}",
            "density": round(density, 3),
            "complementarity": round(complementarity, 3),
            "value_score": round(value_score, 3),
            "overlap": len(intersection),
            "total_keywords": len(union)
        })
    
    # 按value_score排序
    results.sort(key=lambda x: x["value_score"], reverse=True)
    
    return results

def report(results, top_n=20):
    """生成连接密度报告"""
    
    print("🔗 Skills Connection Density Report")
    print("=" * 70)
    
    if not results:
        print("No connections found.")
        return
    
    print(f"\n📊 Top {top_n} High-Value Skill Connections:\n")
    print(f"{'Rank':<5} {'Pair':<45} {'Density':>8} {'Value':>8}")
    print("-" * 70)
    
    for i, r in enumerate(results[:top_n]):
        badge = "🏆" if r["value_score"] > 0.5 else "  "
        print(f"{badge}{i+1:<4} {r['pair']:<45} {r['density']:>8.3f} {r['value_score']:>8.3f}")
    
    # 统计
    high_value = [r for r in results if r["value_score"] > 0.5]
    medium_value = [r for r in results if 0.3 < r["value_score"] <= 0.5]
    
    print(f"\n📈 Summary:")
    print(f"   Total pairs analyzed: {len(results)}")
    print(f"   🏆 High value (score > 0.5): {len(high_value)}")
    print(f"   📦 Medium value (0.3 - 0.5): {len(medium_value)}")
    
    return results

def main():
    # 解析参数
    skills_arg = None
    if "--skills" in sys.argv:
        idx = sys.argv.index("--skills")
        if idx + 1 < len(sys.argv):
            skills_arg = sys.argv[idx + 1].split(',')
    
    print("🔄 Calculating connection density...")
    
    results = calculate_connection_density(skills_arg)
    report(results)
    
    # 保存结果
    output_file = WORKSPACE / ".state" / "connection-density.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(results[:50], indent=2))
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
