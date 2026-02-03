#!/usr/bin/env python3
"""
心跳进化器 - 心跳任务自主更新能力
自动检查、更新和优化心跳任务配置
"""

import json, subprocess, os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

CONFIG_DIR = Path.home() / ".openclaw"
HEARTBEAT_CONFIG = CONFIG_DIR / "heartbeat-config.json"
HEARTBEAT_LOG = CONFIG_DIR / "heartbeat-log.json"

# 核心心跳任务定义
CORE_TASKS = {
    "resources": {
        "name": "资源监控",
        "script": "resource-monitor.py",
        "schedule": "*/30 * * * *",
        "description": "监控 API 资源状态并优化",
        "priority": "high",
        "health_check": lambda: True
    },
    "evolution": {
        "name": "进化分析",
        "script": "evolution-agent.py",
        "schedule": "0 * * * *",
        "description": "分析系统状态并生成进化建议",
        "priority": "medium",
        "health_check": lambda: True
    },
    "skills-check": {
        "name": "Skills 更新检查",
        "script": "skill-manager.py",
        "schedule": "0 6 * * *",
        "description": "检查 skills 更新并自动更新",
        "priority": "medium",
        "health_check": lambda: True
    },
    "agent-evolution": {
        "name": "Agent 能力进化",
        "script": "agent-evolution-manager.py",
        "schedule": "0 0 * * 0",
        "description": "执行 agent 能力评估和进化",
        "priority": "low",
        "health_check": lambda: True
    }
}


def get_cron_jobs() -> List[str]:
    """获取当前 cron 任务"""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    except Exception:
        pass
    return []


def is_task_configured(task_id: str) -> bool:
    """检查任务是否已配置"""
    script = CORE_TASKS.get(task_id, {}).get("script", "")
    if not script:
        return False
    
    cron_jobs = get_cron_jobs()
    return any(script in job for job in cron_jobs)


def sync_tasks() -> Dict:
    """同步所有心跳任务"""
    results = {}
    tools_dir = Path("/Users/fuzhuo/.openclaw/workspace/tools")
    
    for task_id, config in CORE_TASKS.items():
        script = config.get("script", "")
        schedule = config.get("schedule", "")
        
        # 构建 cron 命令
        script_path = tools_dir / script
        cron_line = f"{schedule} python3 {script_path}"
        
        # 检查是否已存在
        cron_jobs = get_cron_jobs()
        is_configured = any(script in job for job in cron_jobs)
        
        if not is_configured:
            # 添加任务
            new_cron = cron_jobs + [f"# {config['name']}", cron_line]
            try:
                subprocess.run(["crontab", "-"], input='\n'.join(new_cron), text=True)
                results[task_id] = {"status": "added", "config": config}
            except Exception:
                results[task_id] = {"status": "failed", "config": config}
        else:
            results[task_id] = {"status": "ok", "config": config}
    
    return results


def check_health() -> Dict:
    """健康检查"""
    health = {}
    for task_id, config in CORE_TASKS.items():
        configured = is_task_configured(task_id)
        health[task_id] = {
            "name": config["name"],
            "configured": configured,
            "healthy": configured
        }
    return health


def evolve() -> Dict:
    """执行进化分析"""
    health = check_health()
    suggestions = []
    
    # 检查需要修复的任务
    for task_id, status in health.items():
        if not status["healthy"]:
            suggestions.append(f"建议修复: {status['name']}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "health": health,
        "suggestions": suggestions,
        "total_tasks": len(CORE_TASKS),
        "healthy_count": sum(1 for h in health.values() if h["healthy"])
    }


def report() -> str:
    """生成报告"""
    evo = evolve()
    health = evo["health"]
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║               💓 心跳任务自主进化报告                          ║
╠══════════════════════════════════════════════════════════════╣
║ 时间: {evo['timestamp'][:19]:<47}║
╠══════════════════════════════════════════════════════════════╣
║ 任务状态                                                      ║
"""
    for task_id, status in health.items():
        icon = "✅" if status["healthy"] else "❌"
        report += f"║ {icon} {status['name']:<48}║\n"
    
    report += f"""╠══════════════════════════════════════════════════════════════╣
║ 统计: {evo['healthy_count']}/{evo['total_tasks']} 健康                                         ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    if evo["suggestions"]:
        report += "\n建议:\n" + "\n".join(f"  • {s}" for s in evo["suggestions"])
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print(report())
    elif sys.argv[1] == "--sync":
        results = sync_tasks()
        for task_id, result in results.items():
            icon = "✅" if result["status"] == "ok" else "➕"
            print(f"{icon} {result['config']['name']}: {result['status']}")
    elif sys.argv[1] == "--health":
        health = check_health()
        for task_id, status in health.items():
            print(f"{'✅' if status['healthy'] else '❌'} {task_id}")
    elif sys.argv[1] == "--evolve":
        evo = evolve()
        print(f"健康: {evo['healthy_count']}/{evo['total_tasks']}")
        for s in evo["suggestions"]:
            print(f"  → {s}")
    elif sys.argv[1] == "--help":
        print("""
💓 心跳进化器

用法:
  python3 heartbeat-evolution.py          # 显示报告
  python3 heartbeat-evolution.py --sync   # 同步任务
  python3 heartbeat-evolution.py --health # 健康检查
  python3 heartbeat-evolution.py --evolve # 进化分析
        """)
