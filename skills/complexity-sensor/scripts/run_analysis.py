#!/usr/bin/env python3
"""
run_analysis.py — 四层大脑联合分析

一次性执行四层分析，输出完整报告。
"""

import subprocess
from pathlib import Path

SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"
SCRIPT_DIR = Path(__file__).parent

SCRIPT_PATHS = {
    "complexity": SCRIPT_DIR / "complexity_sensor.py",
    "metacognition": SKILLS_DIR / "metacognition-auditor" / "scripts" / "metacognition_auditor.py",
    "paradigm": SKILLS_DIR / "paradigm-detector" / "scripts" / "paradigm_detector.py",
    "ecology": SKILLS_DIR / "ecology-monitor" / "scripts" / "ecology_monitor.py",
}


def run_python(key: str) -> dict:
    script_path = SCRIPT_PATHS.get(key)
    if not script_path or not script_path.exists():
        return {"error": f"Script not found: {key}"}
    try:
        result = subprocess.run(["python3", str(script_path)], capture_output=True, text=True, timeout=60)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}


def filter_lines(stdout: str, keywords: list) -> list:
    return [l for l in stdout.split("n") if any(k in l for k in keywords)]


def main():
    print("=" * 60)
    print(" OpenClaw 最强大脑 — 四层联合分析")
    print("=" * 60)

    layers = [
        ("1", "Complexity Sensor", "complexity", ["复杂度", "等级", "相变", "涌现", "critical", "high", "low"]),
        ("2", "Metacognition Auditor", "metacognition", ["预验尸", "偏见", "审计", "风险", "decision"]),
        ("3", "Paradigm Detector", "paradigm", ["范式", "瓶颈", "跃迁", "重构", "stage"]),
        ("4", "Ecology Monitor", "ecology", ["生态", "濒危", "入侵", "共生", "健康", "评分"]),
    ]

    all_outputs = {}
    for num, name, key, keywords in layers:
        print(f"\n[Layer {num}] {name}")
        print("-" * 40)
        r = run_python(key)
        if "error" in r:
            print(f"Error: {r['error']}")
            all_outputs[key] = None
        else:
            lines = filter_lines(r["stdout"], keywords)
            for l in lines[:8]:
                print(l)
            all_outputs[key] = r["stdout"]

    print("\n" + "=" * 60)
    print(" 综合建议")
    print("-" * 40)

    # 从输出中提取关键发现
    if all_outputs.get("complexity") and "critical" in all_outputs["complexity"].lower():
        print(" 1. 复杂度Critical — 解除循环依赖")
    if all_outputs.get("ecology"):
        if "17" in all_outputs["ecology"] or "入侵" in all_outputs["ecology"]:
            print(" 2. 入侵Skills — 拆分或限制")
        if "濒危" in all_outputs["ecology"]:
            print(" 3. 濒危Skills — 评估归档或合并")

    print("\n使用说明:")
    print("  详细报告: python3 <各层脚本路径>")
    print("  查看统计: python3 ecology_monitor.py")


if __name__ == "__main__":
    main()
