#!/usr/bin/env python3
"""
事件驱动心跳 - 简化版
保留事件分析能力，但直接执行
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def main():
    print("=" * 50)
    print(f"🫀 事件驱动心跳 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 获取决策
    result = subprocess.run(
        ['python3', '/Users/fuzhuo/.openclaw/workspace/tools/event-scheduler.py'],
        capture_output=True, text=True
    )
    
    # 解析决策
    decisions = []
    for line in result.stdout.split('\n'):
        if '决策:' in line:
            import re
            match = re.search(r'决策:\s*\[(.*?)\]', line)
            if match:
                decisions = [d.strip().strip("'\"") for d in match.group(1).split(',')]
    
    print(f"\n📋 决策结果: {decisions}")
    
    if not decisions or decisions == ['none'] or decisions == []:
        print("⏭️  跳过执行 - 无需运行的任务")
        sys.exit(0)
    
    # 总是运行统一心跳（它内部会智能调度模块）
    print("\n🚀 执行统一心跳任务...")
    
    result = subprocess.run(
        ['python3', '/Users/fuzhuo/.openclaw/workspace/tools/unified-heartbeat.py'],
        capture_output=True, text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("⚠️", result.stderr[:500])
    
    # 更新任务状态
    TASK_STATE = Path("/Users/fuzhuo/.openclaw/workspace/memory/task-state.md")
    if TASK_STATE.exists():
        content = TASK_STATE.read_text()
        
        # 更新每个任务的时间
        for task in decisions:
            if f'## {task}:' in content:
                content = content.replace(
                    f'## {task}:',
                    f'## {task}: {datetime.now().isoformat()}'
                )
            else:
                content += f'\n## {task}: {datetime.now().isoformat()}'
        
        TASK_STATE.write_text(content)
        print("\n✅ 任务完成，已更新状态")

if __name__ == "__main__":
    main()
