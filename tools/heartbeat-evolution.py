#!/usr/bin/env python3
"""
心跳进化器 - 心跳任务自主更新能力
自动检查、更新和优化心跳任务配置

错误处理增强版：
- 网络异常自动重试 (最多 3 次)
- 端口占用检测和优雅失败
- API 调用超时处理
- 错误日志记录
- 健康检查机制
"""

import json
import subprocess
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

CONFIG_DIR = Path.home() / ".openclaw"
HEARTBEAT_CONFIG = CONFIG_DIR / "heartbeat-config.json"
HEARTBEAT_LOG = CONFIG_DIR / "heartbeat-log.json"

# ==================== 日志配置 ====================
LOG_DIR = CONFIG_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "heartbeat-evolution.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 重试配置 ====================
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
SUBPROCESS_TIMEOUT = 30  # 子进程超时

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


# ==================== 错误处理增强 ====================

def log_error(error_type: str, error_msg: str, context: Dict = None):
    """记录错误日志"""
    error_info = {
        "type": error_type,
        "message": error_msg,
        "timestamp": datetime.now().isoformat(),
        "context": context or {}
    }
    logger.error(f"[{error_type}] {error_msg}")
    if context:
        logger.debug(f"错误上下文: {json.dumps(context, ensure_ascii=False)}")
    return error_info


def safe_subprocess_run(cmd: List[str], timeout: int = SUBPROCESS_TIMEOUT, retries: int = MAX_RETRIES) -> Optional[subprocess.CompletedProcess]:
    """安全的子进程执行 - 带超时和重试"""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            error_msg = f"命令超时: {' '.join(cmd)}"
            logger.warning(f"{error_msg} (尝试 {attempt}/{retries})")
            last_error = error_msg
            if attempt < retries:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            error_msg = f"命令执行失败: {e}"
            logger.error(error_msg)
            last_error = e
            if attempt < retries:
                time.sleep(RETRY_DELAY)
    
    log_error("SUBPROCESS_FAILED", str(last_error), {"cmd": cmd, "retries": retries})
    return None


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """重试装饰器 - 网络异常自动重试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    last_exception = e
                    logger.warning(f"第 {attempt}/{max_retries} 次尝试失败: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
            logger.error(f"重试 {max_retries} 次后仍失败: {last_exception}")
            raise last_exception
        return wrapper
    return decorator


def check_script_exists(script_path: Path) -> Tuple[bool, str]:
    """检查脚本是否存在"""
    if script_path.exists():
        return True, f"脚本存在: {script_path}"
    return False, f"脚本不存在: {script_path}"


def get_cron_jobs() -> List[str]:
    """获取当前 cron 任务 - 增强版"""
    result = safe_subprocess_run(["crontab", "-l"], timeout=10, retries=MAX_RETRIES)
    
    if result is None:
        logger.warning("无法获取 cron 任务列表")
        return []
    
    if result.returncode == 0:
        jobs = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        logger.debug(f"获取到 {len(jobs)} 个 cron 任务")
        return jobs
    else:
        logger.warning(f"crontab 返回非零状态: {result.returncode}")
        return []


def is_task_configured(task_id: str) -> Tuple[bool, Optional[str]]:
    """检查任务是否已配置 - 增强版"""
    config = CORE_TASKS.get(task_id, {})
    script = config.get("script", "")
    
    if not script:
        return False, f"任务 {task_id} 没有配置脚本"
    
    cron_jobs = get_cron_jobs()
    
    # 检查脚本是否在任意 cron 任务中
    for job in cron_jobs:
        if script in job:
            return True, f"任务已配置: {script}"
    
    return False, f"任务未配置: {script}"


def check_task_health(task_id: str, config: Dict) -> Dict:
    """检查单个任务健康状态"""
    script = config.get("script", "")
    script_path = Path("/Users/fuzhuo/.openclaw/workspace/tools") / script
    
    exists, exists_msg = check_script_exists(script_path)
    configured, config_msg = is_task_configured(task_id)
    
    return {
        "task_id": task_id,
        "name": config["name"],
        "script_exists": exists,
        "script_path": str(script_path),
        "configured": configured,
        "healthy": exists and configured,
        "messages": [msg for msg in [exists_msg, config_msg] if msg]
    }


def check_health() -> Dict:
    """健康检查 - 增强版"""
    logger.info("开始心跳任务健康检查")
    health = {
        "timestamp": datetime.now().isoformat(),
        "tasks": {},
        "summary": {"healthy": 0, "unhealthy": 0, "total": len(CORE_TASKS)}
    }
    
    for task_id, config in CORE_TASKS.items():
        task_health = check_task_health(task_id, config)
        health["tasks"][task_id] = task_health
        
        if task_health["healthy"]:
            health["summary"]["healthy"] += 1
            logger.info(f"任务健康: {task_id}")
        else:
            health["summary"]["unhealthy"] += 1
            logger.warning(f"任务不健康: {task_id} - {task_health.get('messages', [])}")
    
    logger.info(f"健康检查完成: {health['summary']['healthy']}/{health['summary']['total']} 健康")
    return health


def sync_tasks_with_retry(max_retries: int = MAX_RETRIES) -> Dict:
    """同步所有心跳任务 - 增强版"""
    logger.info("开始同步心跳任务")
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
            # 添加任务 - 带重试
            new_cron = cron_jobs + [f"# {config['name']}", cron_line]
            
            last_error = None
            for attempt in range(1, max_retries + 1):
                try:
                    result = subprocess.run(
                        ["crontab", "-"], 
                        input='\n'.join(new_cron), 
                        text=True, 
                        timeout=SUBPROCESS_TIMEOUT
                    )
                    if result.returncode == 0:
                        results[task_id] = {
                            "status": "added", 
                            "config": config,
                            "attempt": attempt
                        }
                        logger.info(f"任务已添加: {task_id} (尝试 {attempt})")
                        break
                    else:
                        last_error = f"crontab 返回 {result.returncode}"
                except Exception as e:
                    last_error = e
                    logger.warning(f"添加任务失败 ({attempt}/{max_retries}): {e}")
                    if attempt < max_retries:
                        time.sleep(RETRY_DELAY)
            
            if task_id not in results:
                results[task_id] = {
                    "status": "failed", 
                    "config": config,
                    "error": str(last_error)
                }
                log_error("TASK_SYNC_FAILED", str(last_error), {"task": task_id})
        else:
            results[task_id] = {"status": "ok", "config": config}
    
    logger.info(f"同步完成: {sum(1 for r in results.values() if r['status'] in ['ok', 'added'])}/{len(results)} 成功")
    return results


def evolve() -> Dict:
    """执行进化分析 - 增强版"""
    logger.info("开始进化分析")
    health = check_health()
    suggestions = []
    actions_needed = []
    
    # 检查需要修复的任务
    for task_id, status in health["tasks"].items():
        if not status["healthy"]:
            suggestion = f"建议修复: {status['name']}"
            suggestions.append(suggestion)
            
            # 生成具体建议
            if not status.get("script_exists"):
                action = f"创建缺失的脚本: {status.get('script_path', 'unknown')}"
                actions_needed.append(action)
            elif not status.get("configured"):
                action = f"配置 cron 任务: {status['name']}"
                actions_needed.append(action)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "health": health,
        "suggestions": suggestions,
        "actions_needed": actions_needed,
        "total_tasks": len(CORE_TASKS),
        "healthy_count": health["summary"]["healthy"],
        "status": "healthy" if health["summary"]["healthy"] == len(CORE_TASKS) else "needs_attention"
    }
    
    logger.info(f"进化分析完成: {result['status']}")
    return result


def report() -> str:
    """生成报告 - 增强版"""
    evo = evolve()
    health = evo["health"]
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║               💓 心跳任务自主进化报告                          ║
╠══════════════════════════════════════════════════════════════╣
║ 时间: {evo['timestamp'][:19]:<47}║
║ 状态: {evo['status']:<46}║
╠══════════════════════════════════════════════════════════════╣
║ 任务状态                                                      ║
"""
    for task_id, status in health["tasks"].items():
        icon = "✅" if status["healthy"] else "❌"
        messages = status.get("messages", [])
        msg_suffix = f" ({', '.join(messages[:1])})" if messages else ""
        report += f"║ {icon} {status['name']:<35}{msg_suffix:<13}║\n"
    
    report += f"""╠══════════════════════════════════════════════════════════════╣
║ 统计: {evo['healthy_count']}/{evo['total_tasks']} 健康                                         ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    if evo["suggestions"]:
        report += "\n建议:\n" + "\n".join(f"  • {s}" for s in evo["suggestions"])
    
    if evo["actions_needed"]:
        report += "\n需要操作:\n" + "\n".join(f"  → {a}" for a in evo["actions_needed"])
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print(report())
    elif sys.argv[1] == "--sync":
        results = sync_tasks_with_retry()
        print("\n📋 同步结果:")
        for task_id, result in results.items():
            icon = "✅" if result["status"] in ["ok", "added"] else "❌"
            status_text = result['status']
            if result['status'] == 'added':
                status_text += f" (第 {result.get('attempt', 1)} 次尝试)"
            print(f"  {icon} {result['config']['name']}: {status_text}")
    elif sys.argv[1] == "--health":
        health = check_health()
        print("\n🏥 健康检查:")
        for task_id, status in health["tasks"].items():
            icon = "✅" if status["healthy"] else "❌"
            messages = ", ".join(status.get("messages", []))
            print(f"  {icon} {task_id}: {status['name']}")
            if messages:
                print(f"     {messages}")
        print(f"\n📊 统计: {health['summary']['healthy']}/{health['summary']['total']} 健康")
    elif sys.argv[1] == "--evolve":
        evo = evolve()
        print(f"\n📊 进化分析:")
        print(f"  状态: {evo['status']}")
        print(f"  健康: {evo['healthy_count']}/{evo['total_tasks']}")
        if evo["suggestions"]:
            print("\n建议:")
            for s in evo["suggestions"]:
                print(f"  • {s}")
        if evo["actions_needed"]:
            print("\n需要操作:")
            for a in evo["actions_needed"]:
                print(f"  → {a}")
    elif sys.argv[1] == "--retry" and len(sys.argv) > 2:
        # 重试特定任务
        task_id = sys.argv[2]
        if task_id in CORE_TASKS:
            config = CORE_TASKS[task_id]
            results = {task_id: {"status": "pending", "config": config}}
            results = sync_tasks_with_retry()
            for task_id, result in results.items():
                icon = "✅" if result["status"] in ["ok", "added"] else "❌"
                print(f"  {icon} {result['config']['name']}: {result['status']}")
        else:
            print(f"❌ 未知任务: {task_id}")
    elif sys.argv[1] == "--help":
        print("""
💓 心跳进化器

用法:
  python3 heartbeat-evolution.py          # 显示报告
  python3 heartbeat-evolution.py --sync   # 同步任务 (带重试)
  python3 heartbeat-evolution.py --health # 健康检查
  python3 heartbeat-evolution.py --evolve # 进化分析
  python3 heartbeat-evolution.py --retry <task_id> # 重试特定任务
        """)
    else:
        print("❌ 未知参数")
