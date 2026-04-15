#!/usr/bin/env python3
"""
paradigm_detector.py — 范式跃迁检测器

识别架构瓶颈，判断重构时机，检测范式转移信号。
"""

import json
import sys
from typing import Optional


# ===== 跃迁信号定义 =====

PARADIGM_SIGNALS = {
    "diminishing_returns": {
        "name": "收益递减",
        "weight": 0.2,
        "description": "专家用同样方法，产出递减"
    },
    "complexity_explosion": {
        "name": "复杂度爆炸",
        "weight": 0.2,
        "description": "增加资源反而降低性能"
    },
    "external_disruption": {
        "name": "外部颠覆",
        "weight": 0.2,
        "description": "新范式从边缘崛起"
    },
    "internal_resistance": {
        "name": "内部阻力",
        "weight": 0.15,
        "description": "改进方案越来越多被拒绝"
    },
    "meta_problem_recurrence": {
        "name": "元问题重现",
        "weight": 0.1,
        "description": "同样的根本问题反复出现"
    },
    "paradigm_reference": {
        "name": "范式参照",
        "weight": 0.05,
        "description": "其他领域已发生跃迁"
    },
    "assumption_failure": {
        "name": "假设失效",
        "weight": 0.1,
        "description": "过去有效的假设不再成立"
    }
}


# ===== 范式扫描 =====

def scan_paradigm(
    system: str,
    historical_metrics: list[dict] = None,
    external_signals: list[dict] = None
) -> dict:
    """
    扫描系统的范式状态
    
    Returns:
        {
            system: str,
            paradigm_score: 0-100,
            stage: "optimize" | "prepare" | "transition",
            signals: [{name, intensity, evidence}],
            recommendations: []
        }
    """
    signals = []
    total_score = 0
    
    # 模拟信号评估（实际应用中从metrics分析）
    if historical_metrics:
        # 复杂度爆炸检测
        recent = historical_metrics[-3:] if len(historical_metrics) >= 3 else historical_metrics
        complexity_trend = sum(h.get("complexity", 0) for h in recent) / len(recent) if recent else 0
        
        if complexity_trend > 0.7:
            signals.append({
                "type": "complexity_explosion",
                "name": PARADIGM_SIGNALS["complexity_explosion"]["name"],
                "intensity": min(10, int(complexity_trend * 10)),
                "evidence": f"复杂度指标趋势: {complexity_trend:.2f}"
            })
            total_score += PARADIGM_SIGNALS["complexity_explosion"]["weight"] * complexity_trend * 100
    
    if external_signals:
        for sig in external_signals:
            if sig.get("type") == "disruption":
                signals.append({
                    "type": "external_disruption",
                    "name": PARADIGM_SIGNALS["external_disruption"]["name"],
                    "intensity": sig.get("intensity", 5),
                    "evidence": sig.get("evidence", "检测到外部颠覆信号")
                })
                total_score += PARADIGM_SIGNALS["external_disruption"]["weight"] * sig.get("intensity", 5) / 10 * 100
    
    # 如果没有数据，模拟演示
    if not signals:
        # 演示用模拟信号
        signals = [
            {
                "type": "diminishing_returns",
                "name": "收益递减",
                "intensity": 6,
                "evidence": "优化投入产出比持续下降"
            },
            {
                "type": "complexity_explosion",
                "name": "复杂度爆炸",
                "intensity": 4,
                "evidence": "skill数量增长，但组合效果下降"
            }
        ]
        total_score = 35
    
    # 判断阶段
    if total_score < 30:
        stage = "optimize"
        recommendations = [
            "继续系统思维优化",
            "监控关键指标",
            "识别局部改进机会"
        ]
    elif total_score < 60:
        stage = "prepare"
        recommendations = [
            "启动范式评估",
            "准备重构方案",
            "建立跃迁成本估算"
        ]
    else:
        stage = "transition"
        recommendations = [
            "⚠️ 范式跃迁窗口已打开",
            "评估跃迁收益 vs 成本",
            "制定跃迁路线图"
        ]
    
    return {
        "system": system,
        "paradigm_score": int(total_score),
        "stage": stage,
        "signals": signals,
        "recommendations": recommendations
    }


# ===== 跃迁时机判断 =====

def assess_transition_timing(
    current_state: str,
    metrics: dict = None,
    migration_cost: float = 0,
    opportunity_cost: float = 0
) -> dict:
    """
    判断是否应该跃迁
    
    Returns:
        {
            should_transition: bool,
            confidence: "low" | "medium" | "high",
            transition_cost: {migration, opportunity, total},
            break_even_time: str,
            next_steps: []
        }
    """
    if metrics is None:
        metrics = {}
    
    # 计算跃迁成本
    total_cost = migration_cost + opportunity_cost
    
    # 评估收益（简化：假设跃迁后效率提升30%）
    efficiency_gain = 0.3
    roi = efficiency_gain / (total_cost / 100) if total_cost > 0 else float('inf')
    
    # 判断
    should_transition = roi > 1.5 and metrics.get("paradigm_score", 0) > 50
    
    if roi > 2:
        confidence = "high"
    elif roi > 1:
        confidence = "medium"
    else:
        confidence = "low"
    
    # 下一步
    if should_transition:
        next_steps = [
            "制定详细跃迁计划",
            "建立小范围试点",
            "准备回滚方案"
        ]
    else:
        next_steps = [
            "继续系统优化",
            "积累更多数据",
            "监控跃迁信号"
        ]
    
    return {
        "current_state": current_state,
        "should_transition": should_transition,
        "confidence": confidence,
        "transition_cost": {
            "migration": migration_cost,
            "opportunity": opportunity_cost,
            "total": total_cost
        },
        "estimated_roi": round(roi, 2),
        "break_even_time": f"{12 / roi:.0f}个月" if roi > 0 else "无法估算",
        "next_steps": next_steps
    }


# ===== 架构瓶颈诊断 =====

def diagnose_bottleneck(system_metrics: dict) -> dict:
    """
    诊断架构瓶颈类型
    
    Returns:
        {
            bottleneck_type: str,
            severity: "low" | "medium" | "high" | "critical",
            evidence: [],
            recommendations: []
        }
    """
    if not system_metrics:
        # 演示数据
        system_metrics = {
            "tech_debt_ratio": 0.4,
            "dependency_depth": 8,
            "coordination_cost": 0.3,
            "decision_latency": 0.6,
            "scale_efficiency": 0.5,
            "innovation_gap": 0.4
        }
    
    # 找最严重瓶颈
    bottlenecks = []
    
    if system_metrics.get("tech_debt_ratio", 0) > 0.3:
        bottlenecks.append({
            "type": "tech_debt",
            "name": "技术债型",
            "severity": "high" if system_metrics["tech_debt_ratio"] > 0.5 else "medium",
            "evidence": [f"技术债比例: {system_metrics['tech_debt_ratio']:.0%}"]
        })
    
    if system_metrics.get("dependency_depth", 0) > 7:
        bottlenecks.append({
            "type": "complexity",
            "name": "复杂度型",
            "severity": "critical" if system_metrics["dependency_depth"] > 10 else "high",
            "evidence": [f"依赖深度: {system_metrics['dependency_depth']}层"]
        })
    
    if system_metrics.get("coordination_cost", 0) > 0.4:
        bottlenecks.append({
            "type": "communication",
            "name": "沟通型",
            "severity": "medium",
            "evidence": [f"协调成本占比: {system_metrics['coordination_cost']:.0%}"]
        })
    
    if system_metrics.get("decision_latency", 0) > 0.5:
        bottlenecks.append({
            "type": "decision",
            "name": "决策型",
            "severity": "high",
            "evidence": [f"决策延迟严重: {system_metrics['decision_latency']:.0%}"]
        })
    
    if system_metrics.get("scale_efficiency", 0) < 0.6:
        bottlenecks.append({
            "type": "scale",
            "name": "规模型",
            "severity": "critical" if system_metrics["scale_efficiency"] < 0.3 else "high",
            "evidence": [f"规模效率: {system_metrics['scale_efficiency']:.0%}"]
        })
    
    if system_metrics.get("innovation_gap", 0) > 0.5:
        bottlenecks.append({
            "type": "innovation",
            "name": "创新型",
            "severity": "medium",
            "evidence": [f"创新差距: {system_metrics['innovation_gap']:.0%}"]
        })
    
    # 最严重的瓶颈
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    primary = min(bottlenecks, key=lambda x: severity_order.get(x["severity"], 3)) if bottlenecks else {
        "type": "none",
        "name": "无明显瓶颈",
        "severity": "low",
        "evidence": []
    }
    
    recommendations = {
        "tech_debt": ["优先还债", "建立还债机制", "限制新债累积"],
        "complexity": ["拆分模块", "减少依赖", "简化调用链"],
        "communication": ["扁平化结构", "明确职责", "减少跨团队依赖"],
        "decision": ["决策前移", "授权到一线", "减少审批链路"],
        "scale": ["水平扩展", "无状态设计", "服务拆分"],
        "innovation": ["创新试点", "容错机制", "快速验证"]
    }
    
    return {
        "primary_bottleneck": primary,
        "all_bottlenecks": bottlenecks,
        "recommendations": recommendations.get(primary["type"], [])
    }


# ===== CLI 入口 =====

def main():
    if len(sys.argv) < 2:
        print("=" * 50)
        print("范式跃迁检测器 - 演示模式")
        print("=" * 50)
        
        # 范式扫描
        print("\n📊 范式扫描")
        scan = scan_paradigm("OpenClaw架构")
        stage_emoji = {"optimize": "🟢", "prepare": "🟡", "transition": "🔴"}
        print(f"\n系统: {scan['system']}")
        print(f"范式评分: {scan['paradigm_score']}/100")
        print(f"阶段: {stage_emoji[scan['stage']]} {'系统优化' if scan['stage'] == 'optimize' else '准备重构' if scan['stage'] == 'prepare' else '范式跃迁窗口'}")
        print(f"\n跃迁信号:")
        for sig in scan['signals']:
            print(f"  • {sig['name']} (强度: {sig['intensity']}/10)")
            print(f"    {sig['evidence']}")
        print(f"\n建议:")
        for rec in scan['recommendations']:
            print(f"  → {rec}")
        
        # 瓶颈诊断
        print("\n\n🔍 架构瓶颈诊断")
        diag = diagnose_bottleneck({})
        severity_emoji = {"critical": "⚫", "high": "🔴", "medium": "🟡", "low": "🟢", "none": "✅"}
        print(f"\n主要瓶颈: {severity_emoji[diag['primary_bottleneck']['severity']]} {diag['primary_bottleneck']['name']}")
        if diag['primary_bottleneck']['evidence']:
            for ev in diag['primary_bottleneck']['evidence']:
                print(f"  证据: {ev}")
        print(f"\n建议:")
        for rec in diag['recommendations']:
            print(f"  → {rec}")
        
        # 跃迁时机
        print("\n\n⏰ 跃迁时机判断")
        timing = assess_transition_timing(
            current_state="单体架构",
            migration_cost=100,
            opportunity_cost=30
        )
        print(f"\n当前状态: {timing['current_state']}")
        print(f"跃迁成本: {timing['transition_cost']['total']} (迁移:{timing['transition_cost']['migration']} + 机会:{timing['transition_cost']['opportunity']})")
        print(f"预计ROI: {timing['estimated_roi']:.2f}")
        print(f"置信度: {timing['confidence']}")
        print(f"\n{'✅ 建议跃迁' if timing['should_transition'] else '❌ 建议继续优化'}")
        for step in timing['next_steps']:
            print(f"  → {step}")
        
        return
    
    # JSON 模式
    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        
        mode = data.get("mode", "scan")
        
        if mode == "scan":
            result = scan_paradigm(
                system=data["system"],
                historical_metrics=data.get("historical_metrics"),
                external_signals=data.get("external_signals")
            )
        elif mode == "timing":
            result = assess_transition_timing(
                current_state=data.get("current_state", ""),
                metrics=data.get("metrics"),
                migration_cost=data.get("migration_cost", 0),
                opportunity_cost=data.get("opportunity_cost", 0)
            )
        else:
            result = diagnose_bottleneck(data.get("metrics", {}))
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
