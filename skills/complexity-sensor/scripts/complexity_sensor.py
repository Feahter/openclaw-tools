#!/usr/bin/env python3
"""
complexity_sensor.py — 复杂性思维传感器

检测 skill 组合的复杂度、相变临界点、涌现信号。
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


# ===== 复杂度评估 =====

def assess_complexity(skills: list[str], calls: list[tuple] = None) -> dict:
    """
    评估 skill 组合的复杂度
    
    Args:
        skills: 涉及的 skill 列表
        calls: 调用关系 [(caller, callee), ...]
    
    Returns:
        {
            score: 0-100,
            level: "low" | "medium" | "high" | "critical",
            factors: [贡献因素],
            warnings: [警告信号],
            recommendations: [建议]
        }
    """
    if not skills:
        return _empty_result()
    
    n = len(skills)
    
    # 1. 连接密度
    if calls:
        actual_connections = len(calls)
        possible_connections = n * (n - 1)
        connection_density = actual_connections / max(possible_connections, 1)
    else:
        # 无调用数据，假设线性关系
        connection_density = 0.1 * n
    
    # 2. 非线性项检测（循环依赖）
    has_cycles = _has_cycle(calls) if calls else False
    
    # 3. 依赖深度（简化：按调用链计算）
    depth = _calc_depth(calls) if calls else 1
    
    # 4. 复杂度评分
    score = min(100, int(
        connection_density * 40 +
        depth * 15 +
        (20 if has_cycles else 0) +
        (n - 1) * 10
    ))
    
    # 5. 等级判定
    if score >= 80:
        level = "critical"
    elif score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"
    
    # 6. 风险因素
    factors = []
    warnings = []
    recommendations = []
    
    if connection_density > 0.3:
        factors.append(f"连接密度过高: {connection_density:.2f}")
        warnings.append("🔴 连接密度 > 0.3，接近相变临界点")
        recommendations.append("考虑拆分高连接密度的 skill 组合")
    
    if has_cycles:
        factors.append("存在循环依赖")
        warnings.append("⚠️ 反馈回路存在，可能导致系统震荡")
        recommendations.append("解除循环依赖，改为单向调用")
    
    if depth > 5:
        factors.append(f"依赖深度过深: {depth}层")
        warnings.append("🟡 依赖链过长，调试困难")
        recommendations.append("考虑提取公共模块，减少调用深度")
    
    if n > 7:
        factors.append(f"Skill 数量较多: {n}个")
        warnings.append("🟡 组合规模大，涌现概率增加")
        recommendations.append("评估是否可以拆分任务")
    
    return {
        "score": score,
        "level": level,
        "metrics": {
            "connection_density": round(connection_density, 3),
            "dependency_depth": depth,
            "has_cycles": has_cycles,
            "skill_count": n
        },
        "factors": factors or ["无显著风险因素"],
        "warnings": warnings or ["✅ 复杂度在可接受范围内"],
        "recommendations": recommendations or ["持续监控即可"]
    }


def _has_cycle(calls: list[tuple]) -> bool:
    """检测是否存在循环依赖（简化的环检测）"""
    if not calls:
        return False
    
    # 构建邻接表
    adj = {}
    for caller, callee in calls:
        adj.setdefault(caller, []).append(callee)
    
    # DFS 检测环
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False
    
    for node in adj:
        if node not in visited:
            if dfs(node):
                return True
    return False


def _calc_depth(calls: list[tuple]) -> int:
    """计算最大依赖深度"""
    if not calls:
        return 1
    
    # 构建调用图
    adj = {}
    for caller, callee in calls:
        adj.setdefault(caller, []).append(callee)
    
    # BFS 计算从根节点到叶子的最大深度
    max_depth = 0
    
    def bfs(start):
        visited = {start}
        queue = [(start, 1)]
        max_d = 1
        while queue:
            node, depth = queue.pop(0)
            max_d = max(max_d, depth)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        return max_d
    
    roots = set(adj.keys()) - {c for _, c in calls}
    for root in roots or adj.keys():
        max_depth = max(max_depth, bfs(root))
    
    return max_depth


def _empty_result():
    return {
        "score": 0,
        "level": "low",
        "metrics": {"connection_density": 0, "dependency_depth": 0, "has_cycles": False, "skill_count": 0},
        "factors": [],
        "warnings": ["✅ 无 skill 数据"],
        "recommendations": ["无需干预"]
    }


# ===== 相变检测 =====

def detect_phase_transition(
    current_metrics: dict,
    historical_metrics: list[dict] = None,
    threshold: float = 0.3
) -> dict:
    """
    检测是否接近相变临界点
    
    Args:
        current_metrics: 当前指标 {connection_density, dependency_depth, ...}
        historical_metrics: 历史指标列表
        threshold: 相变阈值
    
    Returns:
        {is_near_transition, risk_level, triggering_factors}
    """
    cd = current_metrics.get("connection_density", 0)
    has_cycles = current_metrics.get("has_cycles", False)
    
    # 接近临界点的条件
    near_transition = (cd > threshold) or (has_cycles and cd > threshold * 0.7)
    
    if near_transition:
        risk_level = "high"
        triggering_factors = []
        if cd > threshold:
            triggering_factors.append(f"连接密度 {cd:.2f} 超过阈值 {threshold}")
        if has_cycles:
            triggering_factors.append("存在反馈回路 + 高连接密度")
    else:
        risk_level = "low"
        triggering_factors = []
    
    return {
        "is_near_transition": near_transition,
        "risk_level": risk_level,
        "triggering_factors": triggering_factors or ["无显著触发因素"]
    }


# ===== 涌现检测 =====

def detect_emergence(
    skills: list[str],
    calls: list[tuple],
    historical_calls: list[dict] = None
) -> dict:
    """
    检测潜在的涌现行为
    
    Returns:
        {emergence_signals: [], novel_combinations: [], assessment: str}
    """
    n = len(skills)
    emergence_signals = []
    novel_combinations = []
    
    # 1. 顺序涌现：组合效果 > 各部分之和
    # 简化判断：skill 数量 > 5 且有深度调用链
    if n >= 5:
        depth = _calc_depth(calls)
        if depth >= 3:
            emergence_signals.append({
                "type": "顺序涌现",
                "signal": f"多个skills({n}个)深度组合，可能产生组合效应",
                "confidence": "medium"
            })
    
    # 2. 跨域涌现：不同领域 skill 组合
    domains = _infer_domains(skills)
    if len(domains) >= 3:
        emergence_signals.append({
            "type": "跨域涌现",
            "signal": f"跨{len(domains)}个领域skills组合，可能产生跨域新能力",
            "confidence": "low"
        })
    
    # 3. novel 组合检测（与历史对比）
    if historical_calls:
        new_combos = _find_novel_combinations(calls, historical_calls)
        if new_combos:
            novel_combinations = new_combos
            emergence_signals.append({
                "type": "新组合",
                "signal": f"发现{len(new_combos)}个从未出现的skill组合",
                "confidence": "high"
            })
    
    # 评估
    if emergence_signals:
        assessment = f"检测到{len(emergence_signals)}个涌现信号，关注组合效应"
    else:
        assessment = "未检测到明显涌现信号"
    
    return {
        "emergence_signals": emergence_signals,
        "novel_combinations": novel_combinations,
        "assessment": assessment
    }


def _infer_domains(skills: list[str]) -> set:
    """推断 skill 所属领域（简化版）"""
    # 已知领域映射
    domain_keywords = {
        "browser": ["browser", "web", "chrome", "playwright"],
        "coding": ["code", "git", "programming", "coder"],
        "memory": ["memory", "learn", "evolution"],
        "research": ["search", "research", "analyze"],
        "creative": ["write", "novel", "creative"],
        "data": ["data", "analytics", "sql"],
    }
    
    domains = set()
    for skill in skills:
        for domain, keywords in domain_keywords.items():
            if any(k in skill.lower() for k in keywords):
                domains.add(domain)
    
    if not domains:
        domains.add("general")
    
    return domains


def _find_novel_combinations(calls: list[tuple], historical: list[dict]) -> list:
    """找出与历史记录相比新出现的组合"""
    known = set()
    for h in historical:
        if "calls" in h:
            for c in h["calls"]:
                known.add(tuple(sorted(c)) if isinstance(c, (list, tuple)) else c)
    
    novel = []
    for c in calls:
        key = tuple(sorted(c)) if isinstance(c, (list, tuple)) else c
        if key not in known:
            novel.append(c)
    
    return novel


# ===== CLI 入口 =====

def main():
    if len(sys.argv) < 2:
        # 无参数：演示模式
        demo_skills = ["lobster-evolution", "session-miner", "skill-proposer", "self-improving-agent"]
        demo_calls = [
            ("session-miner", "lobster-evolution"),
            ("lobster-evolution", "skill-proposer"),
            ("skill-proposer", "lobster-evolution"),  # 反向，形成回路
        ]
        
        print("=" * 50)
        print("复杂度传感器 - 演示模式")
        print("=" * 50)
        print(f"\n📊 Skill组合: {', '.join(demo_skills)}")
        
        result = assess_complexity(demo_skills, demo_calls)
        print(f"\n🧮 复杂度评分: {result['score']}/100")
        print(f"📈 等级: {result['level']}")
        print(f"\n📐 关键指标:")
        for k, v in result['metrics'].items():
            print(f"   {k}: {v}")
        print(f"\n⚠️ 警告信号:")
        for w in result['warnings']:
            print(f"   {w}")
        print(f"\n💡 建议:")
        for r in result['recommendations']:
            print(f"   {r}")
        
        # 相变检测
        phase = detect_phase_transition(result['metrics'])
        print(f"\n🔄 相变风险: {phase['risk_level']}")
        
        # 涌现检测
        emergence = detect_emergence(demo_skills, demo_calls)
        print(f"\n✨ 涌现评估: {emergence['assessment']}")
        
        return
    
    # 从 JSON 文件读取
    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        
        skills = data.get("skills", [])
        calls = data.get("calls", [])
        
        result = assess_complexity(skills, calls)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
