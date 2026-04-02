#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# talent-mind.py — 天才思维三层操作系统（AI 增强版）
# 用法: python3 talent-mind.py
# 交互式问答，驱动三层思考协议

import sys
from datetime import datetime

def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

def ask(prompt, multiline=False):
    if multiline:
        print(f"\n{prompt}")
        print("(输入空行结束)")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)
    else:
        return input(f"\n{prompt} > ").strip()

def run():
    print("""
╔══════════════════════════════════════════════╗
║    天才思维三层操作系统                      ║
║    认知架构 → 表征方式 → 元认知协议          ║
╚══════════════════════════════════════════════╝
    """.center(60))

    problem = ask("你要思考的问题是什么？", multiline=True)
    if not problem:
        print("没有输入问题，退出。")
        return

    print(f"\n问题：{problem}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # ──────────────────────────────────────────
    # 第一层：认知架构（系统A/B双轨）
    # ──────────────────────────────────────────
    section("第一层：认知架构 — 系统A/B双轨")

    print("【系统A：直觉模式】")
    intuition = ask("直觉告诉你什么？（第一反应，不评判）")
    print(f"  → {intuition}")

    print("\n【系统B：反例验证】")
    print("系统A的直觉在什么条件下失效？")
    counter1 = ask("  反例1（最可能的失效情况）")
    counter2 = ask("  反例2（极端情况）")
    counter3 = ask("  反例3（看起来最荒谬但可能的情况）")

    print("\n【系统张力结论】")
    print("当系统A（直觉）和系统B（反例）冲突时：")
    tension = ask("  这个张力暴露了什么？")
    insight1 = ask("  新认知是什么？")

    # ──────────────────────────────────────────
    # 第二层：表征方式（多模态转换）
    # ──────────────────────────────────────────
    section("第二层：表征方式 — 三种语言重述")

    print("【表征1：数学/精确语言】")
    math_repr = ask("用精确语言定义变量和关系")
    print(f"  → {math_repr}")

    print("\n【表征2：几何/视觉语言】")
    visual_repr = ask("用空间/图形/结构描述（想象画面）")
    print(f"  → {visual_repr}")

    print("\n【表征3：隐喻/叙事语言】")
    story_repr = ask("用一个日常故事或类比来说明")
    print(f"  → {story_repr}")

    print("\n【表征发现】")
    blindspot = ask("哪个表征暴露了其他表征没有发现的盲区？")
    print(f"  → {blindspot}")

    # ──────────────────────────────────────────
    # 第三层：元认知协议（递归循环）
    # ──────────────────────────────────────────
    section("第三层：元认知协议 — 递归审视")

    print("【对象层：答案是什么】")
    answer = ask("你的结论是什么？")
    print(f"  → {answer}")

    print("\n【过程层：为什么这样思考】")
    path = ask("你的思考路径是什么？")
    assumption = ask("用了什么隐含假设？")
    print(f"  路径：{path}")
    print(f"  假设：{assumption}")

    print("\n【元层：推翻思考框架】")
    if_wrong = ask("如果推翻自己的核心假设，会怎样？")
    framework = ask("你用的分类标准本身是否有问题？")
    print(f"  推翻假设：{if_wrong}")
    print(f"  标准问题：{framework}")

    # ──────────────────────────────────────────
    # 四组对立统一
    # ──────────────────────────────────────────
    section("四组对立统一审视")

    print("快速填写（跳过直接写'跳过'）：")
    pairs = [
        ("分解↔综合", "分解视角", "综合视角"),
        ("抽象↔具体", "抽象视角", "具体视角"),
        ("怀疑↔确信", "怀疑视角", "确信视角"),
        ("自我↔无我", "自我视角", "他者视角"),
    ]
    pair_results = []
    for name, left, right in pairs:
        val = input(f"  {name}：{left}？") or "跳过"
        val2 = input(f"          {right}？") or "跳过"
        discovery = input(f"          发现？") or "跳过"
        pair_results.append((name, val, val2, discovery))
        print()

    # ──────────────────────────────────────────
    # 负空间意识
    # ──────────────────────────────────────────
    section("负空间意识 — 没思考什么")

    excluded = ask("问题中默认排除了什么？")
    new_problems = ask("你的解决方案可能创造什么新问题？")
    if_wrong_world = ask("如果核心假设是错的，世界会是什么样？")

    # ──────────────────────────────────────────
    # 输出总结
    # ──────────────────────────────────────────
    section("天才思维 — 最终洞察")

    print("\n三层分析后，最突破性的三个发现：\n")
    for i in range(1, 4):
        finding = input(f"  发现{i}：").strip()
        if finding:
            print(f"    {i}. {finding}")

    print("""
╔══════════════════════════════════════════════╗
║  执行口诀：                                   ║
║  直觉来 → 找反例                            ║
║  单一视角 → 切三种                          ║
║  沉浸思考 → 跳出来                          ║
║  理所当然 → 问负空间                        ║
╚══════════════════════════════════════════════╝
    """)

    # 保存到 state
    from pathlib import Path
    state_dir = Path(__file__).parent.parent / ".state"
    state_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = state_dir / f"talent-session-{ts}.md"

    with open(out_file, "w") as f:
        f.write(f"# 天才思维 session\n\n")
        f.write(f"**问题**: {problem}\n\n")
        f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        f.write(f"## 第一层：系统A/B\n\n")
        f.write(f"**直觉**: {intuition}\n\n")
        f.write(f"**反例**: {counter1} / {counter2} / {counter3}\n\n")
        f.write(f"**张力结论**: {tension} → {insight1}\n\n")
        f.write(f"## 第二层：表征方式\n\n")
        f.write(f"**数学**: {math_repr}\n\n")
        f.write(f"**视觉**: {visual_repr}\n\n")
        f.write(f"**隐喻**: {story_repr}\n\n")
        f.write(f"**盲区**: {blindspot}\n\n")
        f.write(f"## 第三层：元认知\n\n")
        f.write(f"**答案**: {answer}\n\n")
        f.write(f"**路径**: {path}\n\n")
        f.write(f"**假设**: {assumption}\n\n")
        f.write(f"**推翻假设**: {if_wrong}\n\n")
        f.write(f"**框架问题**: {framework}\n\n")
        f.write(f"## 负空间\n\n")
        f.write(f"**排除**: {excluded}\n\n")
        f.write(f"**新问题**: {new_problems}\n\n")
        f.write(f"**假设错的世界**: {if_wrong_world}\n\n")

    print(f"\n→ 已保存到 {out_file}")

if __name__ == "__main__":
    run()
