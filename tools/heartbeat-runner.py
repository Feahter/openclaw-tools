#!/usr/bin/env python3
"""
进化心跳任务 - 定时执行自我优化和资源获取
配置方式：通过cron任务定时调用此脚本
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_heartbeat_task(task_type: str = "all"):
    """运行心跳任务"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tools_dir = Path(__file__).parent

    print(f"\n{'='*60}")
    print(f"🫀 进化心跳任务 - {timestamp}")
    print(f"类型: {task_type}")
    print(f"{'='*60}\n")

    results = {}

    # 1. 资源优化任务
    if task_type in ["all", "resources"]:
        print("📊 步骤1: 资源优化")
        try:
            result = subprocess.run(
                ["python3", str(tools_dir / "resource-optimizer.py")],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["resources"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout[-500:] if result.stdout else "",
                "timestamp": timestamp
            }
            print(f"   结果: {results['resources']['status']}")
        except Exception as e:
            results["resources"] = {"status": "error", "message": str(e)}

    # 2. 进化引擎任务
    if task_type in ["all", "evolution"]:
        print("\n🧬 步骤2: 进化分析")
        try:
            result = subprocess.run(
                ["python3", str(tools_dir / "evolution-engine.py")],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["evolution"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout[-500:] if result.stdout else "",
                "timestamp": timestamp
            }
            print(f"   结果: {results['evolution']['status']}")
        except Exception as e:
            results["evolution"] = {"status": "error", "message": str(e)}

    # 3. 任务执行任务
    if task_type in ["all", "tasks"]:
        print("\n🚀 步骤3: 任务调度")
        try:
            result = subprocess.run(
                ["python3", str(tools_dir / "auto-task-executor.py")],
                capture_output=True,
                text=True,
                timeout=120
            )
            results["tasks"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout[-500:] if result.stdout else "",
                "timestamp": timestamp
            }
            print(f"   结果: {results['tasks']['status']}")
        except Exception as e:
            results["tasks"] = {"status": "error", "message": str(e)}

    # 4. 综合报告
    print(f"\n{'='*60}")
    print("📋 心跳任务完成报告")
    print(f"{'='*60}")

    for task_name, result in results.items():
        status_icon = "✅" if result.get("status") == "success" else "❌"
        print(f"{status_icon} {task_name}: {result.get('status', 'unknown')}")

    # 保存执行记录
    workspace = Path("/Users/fuzhuo/.openclaw/workspace")
    log_file = workspace / "data/heartbeat-log.json"
    log_file.parent.mkdir(exist_ok=True)

    if log_file.exists():
        with open(log_file) as f:
            heartbeat_log = json.load(f)
    else:
        heartbeat_log = {"executions": []}

    heartbeat_log["executions"].append({
        "timestamp": timestamp,
        "task_type": task_type,
        "results": results
    })

    # 只保留最近100条记录
    heartbeat_log["executions"] = heartbeat_log["executions"][-100:]

    with open(log_file, 'w') as f:
        json.dump(heartbeat_log, f, indent=2, ensure_ascii=False)

    print(f"\n💾 执行记录已保存到 {log_file}")

    return results

if __name__ == "__main__":
    task_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_heartbeat_task(task_type)
