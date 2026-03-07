#!/usr/bin/env python3
"""
OpenClaw RPA Runner - 基于 browser-use 的浏览器自动化
用法:
  python3 browser_rpa_runner.py "访问https://example.com并截图"
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 配置路径
WORKSPACE = Path.home() / "rpa-workspace"
SCREENSHOTS_DIR = WORKSPACE / "screenshots"
LOGS_DIR = WORKSPACE / "logs"

# 确保目录存在
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


async def run_rpa_task(task: str, headless: bool = True):
    """执行 RPA 任务"""
    from browser_use import Agent, BrowserConfig, BrowserContextConfig
    
    # 配置浏览器
    browser_config = BrowserConfig(
        headless=headless,
        disable_security=False,
    )
    
    context_config = BrowserContextConfig(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    )
    
    # 创建 Agent
    agent = Agent(
        task=task,
        browser_config=browser_config,
        browser_context_config=context_config,
    )
    
    # 执行任务
    print(f"🤖 开始执行: {task}")
    result = await agent.run()
    
    return result


def save_screenshot(history: list, step: int):
    """保存截图"""
    if history and hasattr(history[step], 'screenshot'):
        screenshot_path = SCREENSHOTS_DIR / f"step_{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(screenshot_path, 'wb') as f:
            f.write(history[step].screenshot)
        return screenshot_path
    return None


def log_result(task: str, result: dict, success: bool):
    """记录执行日志"""
    log_file = LOGS_DIR / f"rpa_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "success": success,
        "result": result,
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


async def main():
    parser = argparse.ArgumentParser(description="OpenClaw RPA Runner")
    parser.add_argument("task", help="要执行的任务描述")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    try:
        # 执行任务
        result = await run_rpa_task(args.task, headless=not args.headed)
        
        # 记录结果
        success = result.is_done() if hasattr(result, 'is_done') else True
        log_result(args.task, {"steps": len(result.history) if hasattr(result, 'history') else 0}, success)
        
        print(f"\n✅ 任务完成!")
        print(f"   步骤数: {len(result.history) if hasattr(result, 'history') else 'N/A'}")
        
        return 0
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 任务失败: {error_msg}")
        log_result(args.task, {"error": error_msg}, False)
        
        # 保存失败截图
        if 'history' in locals():
            save_screenshot(result.history, -1)
        
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
