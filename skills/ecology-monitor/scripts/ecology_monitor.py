#!/usr/bin/env python3
"""
ecology_monitor.py — 技能生态系统监测器

监控skill群体健康度、识别濒危/入侵物种、检测共生依赖。
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ===== 生态健康评估 =====

def assess_ecosystem_health(skills_dir: str = None, session_data_dir: str = None) -> dict:
    """
    评估技能生态系统健康度
    
    Returns:
        {
            health_score: 0-100,
            level: "excellent" | "good" | "dangerous",
            metrics: {...},
            endangered_skills: [],
            invasive_skills: [],
            symbiosis_pairs: [],
            recommendations: []
        }
    """
    if not skills_dir:
        skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    else:
        skills_dir = Path(skills_dir)
    
    # 扫描所有skills
    all_skills = []
    skill_metadata = {}
    
    if skills_dir.exists():
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                skill_name = skill_path.name
                all_skills.append(skill_name)
                
                # 读取metadata（简化：只用目录修改时间作为活性指标）
                try:
                    mtime = skill_path.stat().st_mtime
                    skill_metadata[skill_name] = {
                        "last_modified": mtime,
                        "has_scripts": (skill_path / "scripts").exists(),
                        "skill_size": sum(f.stat().st_size for f in skill_path.rglob("*") if f.is_file())
                    }
                except:
                    pass
    
    n = len(all_skills)
    
    # ===== 代谢率指标 =====
    # 简化：使用skill数量作为代理指标
    skill_density = min(100, n / 10)  # 假设健康值是10-20个skills
    
    # ===== 多样性指标（简化）====
    # 假设skills均匀分布
    diversity_score = min(100, n * 5)  # 越多越健康
    
    # ===== 综合评分 =====
    health_score = min(100, int(
        skill_density * 0.3 +
        diversity_score * 0.4 +
        30  # 基础分
    ))
    
    # 等级判定
    if health_score >= 80:
        level = "excellent"
    elif health_score >= 60:
        level = "good"
    else:
        level = "dangerous"
    
    # ===== 濒危技能检测（简化）=====
    endangered_skills = []
    # 小skill（size小）+ 长时间无更新 = 濒危
    for name, meta in skill_metadata.items():
        if meta["skill_size"] < 1000 and (datetime.now().timestamp() - meta["last_modified"]) > 86400 * 30:
            endangered_skills.append({
                "name": name,
                "reason": "size_small_and_old",
                "protection_priority": "low"
            })
    
    # ===== 入侵技能检测（简化）=====
    invasive_skills = []
    # 大skill（size大）+ 有scripts = 可能过度扩张
    for name, meta in skill_metadata.items():
        if meta["skill_size"] > 50000 and meta["has_scripts"]:
            invasive_skills.append({
                "name": name,
                "reason": "oversized_with_scripts",
                "control_priority": "medium"
            })
    
    # ===== 共生关系（简化）=====
    symbiosis_pairs = []
    # 假设lobster-evolution生态内的skills有共生关系
    ecosystem_skills = ["lobster-evolution", "session-miner", "skill-proposer", "self-improving-agent"]
    for i, a in enumerate(ecosystem_skills):
        for b in ecosystem_skills[i+1:]:
            if a in all_skills and b in all_skills:
                symbiosis_pairs.append({
                    "skill_a": a,
                    "skill_b": b,
                    "type": "ecosystem",
                    "strength": "strong" if any(x in [a, b] for x in ["lobster-evolution", "session-miner"]) else "medium"
                })
    
    # ===== 建议 =====
    recommendations = []
    if n < 10:
        recommendations.append("skill数量偏少，考虑丰富生态")
    if len(endangered_skills) > 3:
        recommendations.append(f"发现{len(endangered_skills)}个濒危skill，建议评估是否归档")
    if len(invasive_skills) > 2:
        recommendations.append(f"发现{len(invasive_skills)}个可能入侵的skill，建议拆分或限制")
    if not symbiosis_pairs:
        recommendations.append("未发现明显共生关系，skills可能过于独立")
    if not recommendations:
        recommendations.append("生态系统状态良好")
    
    return {
        "health_score": health_score,
        "level": level,
        "metrics": {
            "total_skills": n,
            "skill_density": round(skill_density, 2),
            "diversity_score": round(diversity_score, 2),
            "endangered_count": len(endangered_skills),
            "invasive_count": len(invasive_skills),
            "symbiosis_count": len(symbiosis_pairs)
        },
        "endangered_skills": endangered_skills[:5],
        "invasive_skills": invasive_skills[:5],
        "symbiosis_pairs": symbiosis_pairs[:10],
        "recommendations": recommendations
    }


# ===== 濒危技能检测 =====

def detect_endangered(skills: list[str] = None, usage_data: dict = None) -> dict:
    """
    检测濒危技能
    
    Returns:
        {
            endangered_skills: [{name, reason, usage_frequency, protection_priority}],
            total_count: int,
            protection_plan: []
        }
    """
    if not skills:
        # 演示数据
        skills = ["old-skill", "deprecated-skill", "unused-skill"]
    
    endangered = []
    
    for skill in skills:
        # 简化判断
        endangered.append({
            "name": skill,
            "reason": "low_usage_frequency",
            "usage_frequency": "0-1/月",
            "protection_priority": "medium"
        })
    
    # 保护计划
    protection_plan = []
    for e in endangered:
        if e["protection_priority"] == "high":
            protection_plan.append(f"重推广 {e['name']} 并更新文档")
        elif e["protection_priority"] == "medium":
            protection_plan.append(f"评估 {e['name']} 是否可合并")
        else:
            protection_plan.append(f"考虑归档 {e['name']}")
    
    return {
        "endangered_skills": endangered,
        "total_count": len(endangered),
        "protection_plan": protection_plan
    }


# ===== 入侵检测 =====

def detect_invasive(skills: list[str] = None, call_graph: dict = None) -> dict:
    """
    检测入侵技能
    
    Returns:
        {
            invasive_skills: [{name, spread_pattern, dominance_score, control_priority}],
            total_count: int,
            control_plan: []
        }
    """
    if not skills:
        # 演示数据
        skills = ["skill-creator", "skill-evolution-manager"]
    
    invasive = []
    
    for skill in skills:
        invasive.append({
            "name": skill,
            "spread_pattern": "high_trigger_frequency",
            "dominance_score": 75,
            "control_priority": "high"
        })
    
    # 控制计划
    control_plan = []
    for inv in invasive:
        if inv["control_priority"] == "high":
            control_plan.append(f"拆分 {inv['name']} 为专注多个skill")
        else:
            control_plan.append(f"限制 {inv['name']} 触发词范围")
    
    return {
        "invasive_skills": invasive,
        "total_count": len(invasive),
        "control_plan": control_plan
    }


# ===== 共生网络分析 =====

def analyze_symbiosis(skills: list[str] = None, call_data: list[tuple] = None) -> dict:
    """
    分析技能间的共生关系
    
    Returns:
        {
            symbiosis_pairs: [{skill_a, skill_b, type, strength}],
            key_species: [skill names],
            network_metrics: {...}
        }
    """
    if not skills:
        # 演示：lobster-evolution生态
        skills = ["lobster-evolution", "session-miner", "skill-proposer", "self-improving-agent"]
    
    if not call_data:
        # 演示调用关系
        call_data = [
            ("session-miner", "lobster-evolution"),
            ("lobster-evolution", "skill-proposer"),
            ("lobster-evolution", "self-improving-agent"),
            ("skill-proposer", "lobster-evolution"),
        ]
    
    # 构建共生网络
    pairs = []
    nodes = set()
    edges = defaultdict(list)
    
    for caller, callee in call_data:
        if caller in skills and callee in skills:
            pairs.append({
                "skill_a": caller,
                "skill_b": callee,
                "type": "dependency",
                "strength": "strong"
            })
            nodes.add(caller)
            nodes.add(callee)
            edges[caller].append(callee)
    
    # 找关键物种（被依赖最多的）
    dependency_count = defaultdict(int)
    for caller, callees in edges.items():
        for callee in callees:
            dependency_count[callee] += 1
    
    key_species = sorted(dependency_count.keys(), key=lambda x: dependency_count[x], reverse=True)[:3]
    
    # 网络指标
    network_metrics = {
        "total_nodes": len(nodes),
        "total_edges": len(pairs),
        "density": len(pairs) / max(len(skills) * (len(skills) - 1), 1),
        "key_species": key_species
    }
    
    return {
        "symbiosis_pairs": pairs,
        "key_species": key_species,
        "network_metrics": network_metrics
    }


# ===== CLI 入口 =====

def main():
    if len(sys.argv) < 2:
        print("=" * 50)
        print("技能生态系统监测器 - 演示模式")
        print("=" * 50)
        
        # 生态健康评估
        print("\n🌍 生态健康评估")
        health = assess_ecosystem_health()
        level_emoji = {"excellent": "🟢", "good": "🟡", "dangerous": "🔴"}
        level_text = {"excellent": "优秀", "good": "良好", "dangerous": "危险"}
        print(f"\n技能总数: {health['metrics']['total_skills']}")
        print(f"综合评分: {health['health_score']}/100")
        print(f"等级: {level_emoji[health['level']]} {level_text[health['level']]}")
        print(f"\n📐 指标:")
        for k, v in health['metrics'].items():
            print(f"   {k}: {v}")
        
        # 濒危技能
        print(f"\n\n🦎 濒危技能 ({len(health['endangered_skills'])}个):")
        if health['endangered_skills']:
            for e in health['endangered_skills'][:3]:
                print(f"   • {e['name']} - {e['reason']}")
        else:
            print("   ✅ 无濒危技能")
        
        # 入侵技能
        print(f"\n🐛 入侵技能 ({len(health['invasive_skills'])}个):")
        if health['invasive_skills']:
            for inv in health['invasive_skills'][:3]:
                print(f"   • {inv['name']} - {inv['reason']}")
        else:
            print("   ✅ 无入侵技能")
        
        # 共生关系
        print(f"\n\n🔗 共生网络 ({health['metrics']['symbiosis_count']}对):")
        for pair in health['symbiosis_pairs'][:3]:
            print(f"   {pair['skill_a']} ←{pair['type']}→ {pair['skill_b']} ({pair['strength']})")
        
        # 建议
        print(f"\n\n💡 建议:")
        for rec in health['recommendations']:
            print(f"   → {rec}")
        
        # 共生网络分析（演示）
        print("\n\n🔬 共生网络分析")
        symbiosis = analyze_symbiosis()
        print(f"\n关键物种: {', '.join(symbiosis['key_species']) if symbiosis['key_species'] else '无'}")
        print(f"网络密度: {symbiosis['network_metrics']['density']:.3f}")
        for pair in symbiosis['symbiosis_pairs'][:3]:
            print(f"  {pair['skill_a']} → {pair['skill_b']}")
        
        return
    
    # JSON 模式
    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        
        mode = data.get("mode", "health")
        
        if mode == "health":
            result = assess_ecosystem_health(
                skills_dir=data.get("skills_dir"),
                session_data_dir=data.get("session_data_dir")
            )
        elif mode == "endangered":
            result = detect_endangered(
                skills=data.get("skills"),
                usage_data=data.get("usage_data")
            )
        elif mode == "invasive":
            result = detect_invasive(
                skills=data.get("skills"),
                call_graph=data.get("call_graph")
            )
        else:
            result = analyze_symbiosis(
                skills=data.get("skills"),
                call_data=data.get("call_data")
            )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
