#!/usr/bin/env python3
"""
Musk 第一性原理商业框架 - 执行脚本

用法：
    python framework.py analyze "你的商业问题"

示例：
    python framework.py analyze "火箭发射太贵"
    python framework.py cost "电池成本分析"
    python framework.py goal "10年殖民火星"
"""

import sys
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_section(title):
    print(f"\n📌 {title}")
    print("-" * 40)

def print_question(q):
    print(f"\n❓ {q}")

def print_answer(a):
    print(f"   {a}")

def print_tip(t):
    print(f"\n💡 {t}")

def analyze_problem(problem):
    """第一性原理分析"""
    print_header(f"第一性原理分析: {problem}")
    
    # 1. 陈述问题
    print_section("1. 问题陈述")
    print(f"原始问题: {problem}")
    
    # 2. 剥离表象
    print_section("2. 剥离表象")
    print_question("这个问题背后有哪些'行业惯例'？")
    print_answer("  - [写下你知道的惯例]")
    
    print_question("'别人一直这么做'的因素？")
    print_answer("  - [写下别人怎么做]")
    
    print_question("有哪些'因为一直这样'的假设？")
    print_answer("  - [写下这些假设]")
    
    # 3. 本质分析
    print_section("3. 本质分析")
    print_question("这个问题最底层要解决什么？")
    print_answer("  [第一层本质]")
    
    print_question("物理/数学上是怎么实现的？")
    print_answer("  [第二层本质]")
    
    print_question("如果完全不考虑现有方案，从零开始怎么做？")
    print_answer("  [第三层本质 - 重新定义]")
    
    # 4. 假设暴露
    print_section("4. 假设暴露与验证")
    print("常见隐藏假设:")
    print("  □ 客户不会接受 [验证：是/否]")
    print("  □ 成本不能降 [验证：是/否]")
    print("  □ 必须用这个技术 [验证：是/否]")
    print("  □ 市场不够大 [验证：是/否]")
    
    # 5. 重新定义
    print_section("5. 重新定义问题")
    print("如果不考虑以上假设，问题可以重新定义为：")
    print("  [新问题定义]")
    
    # 6. 结论
    print_section("6. 结论")
    print("✅ 可行性: [高/中/低]")
    print("🔴 核心障碍: [列出来]")
    print("➡️  下一步: [行动建议]")

def analyze_cost(subject):
    """10% 法则成本分析"""
    print_header(f"10% 法则分析: {subject}")
    
    print_section("当前成本结构")
    print(f"分析对象: {subject}")
    print()
    print("  当前成本: [XXX]")
    print("  年降幅: [0% 或 XX%]")
    print()
    print("  溢价分解:")
    print("    - 供应链溢价: [XX%]")
    print("    - 规模不足: [XX%]")
    print("    - 效率损失: [XX%]")
    print("    - 垄断利润: [XX%]")
    print()
    print("  本质成本: [原材料 + 基础劳动 + 必要设备]")
    
    print_section("10% 路径")
    print("  第1年: -10% → [新成本]")
    print("  第2年: -19% → [新成本]")
    print("  第3年: -27% → [新成本]")
    print("  第5年: -41% → [新成本]")
    
    print_section("结论")
    print("  可持续: [是/否]")
    print("  瓶颈: [列出来]")
    print("  建议: [下一步]")

def verify_goal(goal):
    """目标倒推验证"""
    print_header(f"目标倒推验证: {goal}")
    
    print_section("目标陈述")
    print(f"目标: {goal}")
    
    print_section("倒推分解")
    print("从目标倒推到起点：")
    print()
    print("  目标 → 需要什么？")
    print("  → 需要的资源？")
    print("  → 需要的团队？")
    print("  → 需要的资金？")
    print("  → 需要的技能？")
    print()
    print("  起点 ← 有什么？")
    print("  ← 现有资源？")
    print("  ← 现有团队？")
    print("  ← 现有资金？")
    print("  ← 现有技能？")
    
    print_section("差距分析")
    print("  时间差距: [需要多久 / 有多久]")
    print("  资金差距: [需要多少 / 有多少]")
    print("  人才差距: [需要什么 / 有什么]")
    
    print_section("可行性判断")
    print("  🟢 可达成的路径清晰")
    print("  🟡 某些路径不清晰，需要验证")
    print("  🔴 某些假设不成立，需要重新思考")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    
    command = sys.argv[1]
    arg = " ".join(sys.argv[2:])
    
    if command == "analyze":
        analyze_problem(arg)
    elif command == "cost":
        analyze_cost(arg)
    elif command == "goal":
        verify_goal(arg)
    else:
        print(f"未知命令: {command}")
        print("可用命令: analyze, cost, goal")

if __name__ == "__main__":
    main()
