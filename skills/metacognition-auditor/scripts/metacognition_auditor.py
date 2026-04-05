#!/usr/bin/env python3
"""
metacognition_auditor.py — 元认知审计器

二阶思维执行、预验尸分析、认知盲区识别。
"""

import json
import sys
from datetime import datetime
from typing import Optional


# ===== 认知偏见库 =====

COGNITIVE_BIASES = {
    "confirmation": {
        "name": "确认偏误",
        "description": "只搜索支持当前观点的信息，忽略反例",
        "mitigation": "强制为对立观点辩护，列出3个反例"
    },
    "overconfidence": {
        "name": "过度自信",
        "description": "低估风险，高估成功率",
        "mitigation": "预验尸 + 历史数据对比 + 悲观预期"
    },
    "sunk_cost": {
        "name": "沉没成本谬误",
        "description": "不愿放弃已投入大量资源的失败决策",
        "mitigation": "问：'如果没有这项投入，现在还会继续吗？'"
    },
    "recency": {
        "name": "近期偏差",
        "description": "过度重视最新信息，忽略长期趋势",
        "mitigation": "加权历史数据，建立长周期指标"
    },
    "groupthink": {
        "name": "群体思维",
        "description": "团队内不愿反对主流意见",
        "mitigation": "匿名意见收集，指定魔鬼代言人"
    },
    "anchoring": {
        "name": "锚定效应",
        "description": "第一个数字/信息影响后续判断",
        "mitigation": "独立评估，避免先入为主"
    },
    "availability": {
        "name": "可得性启发",
        "description": "最近/印象深刻的事件被高估概率",
        "mitigation": "数据驱动，统计基础概率"
    }
}


# ===== 预验尸分析 =====

def pre_mortem(
    decision: str,
    timeline: str = "6个月后",
    participants: list[str] = None
) -> dict:
    """
    预验尸分析
    
    Args:
        decision: 要分析的决策
        timeline: 假设的时间点
        participants: 参与者列表
    
    Returns:
        {
            decision: str,
            timeline: str,
            failure_modes: [失败模式],
            cognitive_blindspots: [认知盲区],
            prevention_measures: [预防措施],
            signals_to_monitor: [监控信号]
        }
    """
    # 基于决策类型生成典型失败模式
    failure_templates = {
        "技术选型": [
            "技术债累积速度超预期",
            "团队学习曲线比预估长",
            "供应商锁定风险实现",
            "社区活跃度下降"
        ],
        "架构决策": [
            "微服务复杂度超出运维能力",
            "过度设计导致开发效率下降",
            "技术选型在3年后成为负债"
        ],
        "产品决策": [
            "用户需求假设错误",
            "竞争对手抢先发布",
            "监管环境变化"
        ],
        "团队决策": [
            "关键人员离职",
            "团队协作摩擦超预期",
            "招聘困难导致进度延误"
        ],
        "default": [
            "执行速度低于预期",
            "资源不足",
            "外部环境变化"
        ]
    }
    
    # 识别决策类型
    decision_lower = decision.lower()
    matched_type = "default"
    for key in failure_templates:
        if key.lower() in decision_lower:
            matched_type = key
            break
    
    failure_modes = failure_templates[matched_type]
    
    # 生成典型盲区
    cognitive_blindspots = [
        {
            "type": "未知的未知",
            "description": "完全没考虑到的风险因素",
            "risk_level": "high"
        },
        {
            "type": "假设过于乐观",
            "description": "基于最好情况的假设，而非最可能的情况",
            "risk_level": "medium"
        },
        {
            "type": "能力高估",
            "description": "低估执行难度，高估团队能力",
            "risk_level": "medium"
        }
    ]
    
    # 预防措施
    prevention_measures = [
        {
            "measure": "建立决策日志",
            "action": "记录每个关键假设，定期复核"
        },
        {
            "measure": "设定检查点",
            "action": f"在{timeline}前设置决策复核点"
        },
        {
            "measure": "预警指标",
            "action": "建立早期预警信号"
        }
    ]
    
    # 监控信号
    signals_to_monitor = [
        "进度偏差 > 20%",
        "团队士下降",
        "外部环境重大变化"
    ]
    
    return {
        "decision": decision,
        "timeline": timeline,
        "matched_type": matched_type,
        "failure_modes": failure_modes,
        "cognitive_blindspots": cognitive_blindspots,
        "prevention_measures": prevention_measures,
        "signals_to_monitor": signals_to_monitor
    }


# ===== 认知偏见检测 =====

def detect_bias(
    decision: str,
    evidence: list[str],
    opposing_view: list[str] = None
) -> dict:
    """
    检测决策中的认知偏见
    
    Returns:
        {
            decision: str,
            detected_biases: [{type, name, description, mitigation}],
            risk_level: "low" | "medium" | "high",
            recommendation: str
        }
    """
    detected_biases = []
    risk_level = "low"
    
    # 检查确认偏误
    if len(evidence) > 0 and (not opposing_view or len(opposing_view) == 0):
        detected_biases.append(COGNITIVE_BIASES["confirmation"])
        risk_level = "medium"
    
    # 检查近期偏差（证据都来自最近）
    # 简化：假设只有证据=可能有近期偏差
    if len(evidence) >= 3:
        detected_biases.append(COGNITIVE_BIASES["recency"])
    
    # 检查群体思维（没有对立意见）
    if not opposing_view:
        detected_biases.append(COGNITIVE_BIASES["groupthink"])
        risk_level = max(risk_level, "medium")
    
    # 生成建议
    if detected_biases:
        bias_names = [b["name"] for b in detected_biases]
        recommendation = f"检测到认知偏见：{', '.join(bias_names)}。建议为对立观点辩护。"
    else:
        recommendation = "暂未检测到明显认知偏见"
    
    return {
        "decision": decision,
        "evidence_count": len(evidence),
        "opposing_view_count": len(opposing_view) if opposing_view else 0,
        "detected_biases": detected_biases,
        "risk_level": risk_level,
        "recommendation": recommendation
    }


# ===== 决策审计 =====

def audit_decision(
    decision: str,
    alternatives: list[str] = None,
    criteria: list[str] = None
) -> dict:
    """
    决策审计
    
    Returns:
        {
            decision: str,
            first_order_analysis: {},
            second_order_analysis: {},
            cognitive_blindspots: [],
            overall_assessment: str,
            recommendations: []
        }
    """
    if criteria is None:
        criteria = ["收益", "风险", "成本", "时间"]
    
    if alternatives is None:
        alternatives = []
    
    # 一阶分析
    first_order_analysis = {
        "goal": f"通过 {decision} 达成什么",
        "evidence": "基于现有信息的评估",
        "confidence": "中等"  # 简化
    }
    
    # 二阶审视
    second_order_analysis = {
        "boundary_conditions": [
            "决策的有效性依赖于哪些假设",
            "这些假设成立的条件是什么"
        ],
        "risk_assumptions": [
            "假设1：情况不会剧烈变化",
            "假设2：执行能力足够",
            "假设3：资源充足"
        ],
        "opposing_evidence": []
    }
    
    # 盲区检测
    blindspots = detect_bias(decision, [decision], alternatives)
    
    # 综合评估
    if blindspots["risk_level"] == "high":
        overall = "⚠️ 高风险决策，检测到多个认知偏见"
    elif blindspots["risk_level"] == "medium":
        overall = "🟡 中等风险，建议增加对立分析"
    else:
        overall = "✅ 暂未检测到明显风险"
    
    # 建议
    recommendations = []
    if alternatives:
        recommendations.append({
            "type": "比较分析",
            "action": f"对比 {len(alternatives)} 个替代方案"
        })
    if blindspots["detected_biases"]:
        recommendations.append({
            "type": "偏见缓解",
            "action": blindspots["recommendation"]
        })
    recommendations.append({
        "type": "决策日志",
        "action": "记录假设和预期结果"
    })
    
    return {
        "decision": decision,
        "alternatives": alternatives or [],
        "first_order_analysis": first_order_analysis,
        "second_order_analysis": second_order_analysis,
        "cognitive_blindspots": blindspots,
        "overall_assessment": overall,
        "recommendations": recommendations
    }


# ===== CLI 入口 =====

def main():
    if len(sys.argv) < 2:
        # 演示模式
        print("=" * 50)
        print("元认知审计器 - 演示模式")
        print("=" * 50)
        
        # 预验尸演示
        print("\n📋 预验尸分析")
        result = pre_mortem(
            decision="迁移到微服务架构",
            timeline="12个月后"
        )
        print(f"\n决策: {result['decision']}")
        print(f"时间: {result['timeline']}")
        print(f"类型: {result['matched_type']}")
        print(f"\n失败模式:")
        for i, mode in enumerate(result['failure_modes'], 1):
            print(f"  {i}. {mode}")
        print(f"\n认知盲区:")
        for bs in result['cognitive_blindspots']:
            print(f"  - [{bs['risk_level']}] {bs['type']}: {bs['description']}")
        print(f"\n预防措施:")
        for pm in result['prevention_measures']:
            print(f"  • {pm['measure']}: {pm['action']}")
        
        # 偏见检测演示
        print("\n\n🔍 认知偏见检测")
        bias_result = detect_bias(
            decision="继续使用现有技术栈",
            evidence=["团队熟悉", "性能足够", "稳定性好"],
            opposing_view=["技术债会累积", "招人困难"]
        )
        print(f"\n决策: {bias_result['decision']}")
        print(f"风险等级: {bias_result['risk_level']}")
        print(f"建议: {bias_result['recommendation']}")
        
        # 决策审计演示
        print("\n\n📊 决策审计")
        audit = audit_decision(
            decision="选择方案A",
            alternatives=["方案B", "方案C"],
            criteria=["成本", "风险", "收益"]
        )
        print(f"\n决策: {audit['decision']}")
        print(f"综合评估: {audit['overall_assessment']}")
        for rec in audit['recommendations']:
            print(f"  • {rec['type']}: {rec['action']}")
        
        return
    
    # JSON 模式
    try:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        
        mode = data.get("mode", "audit")
        
        if mode == "premortem":
            result = pre_mortem(
                decision=data["decision"],
                timeline=data.get("timeline", "6个月后"),
                participants=data.get("participants")
            )
        elif mode == "bias":
            result = detect_bias(
                decision=data["decision"],
                evidence=data.get("evidence", []),
                opposing_view=data.get("opposing_view")
            )
        else:
            result = audit_decision(
                decision=data["decision"],
                alternatives=data.get("alternatives"),
                criteria=data.get("criteria")
            )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
