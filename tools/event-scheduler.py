#!/usr/bin/env python3
"""
事件驱动调度器 - 智能决策版本
根据事件队列和任务状态，智能决定执行哪些任务
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

MEMORY_DIR = Path("/Users/fuzhuo/.openclaw/workspace/memory")
EVENT_QUEUE = MEMORY_DIR / "event-queue.md"
TASK_STATE = MEMORY_DIR / "task-state.md"

# 任务执行间隔（分钟）
TASK_INTERVALS = {
    'heartbeat': 60,
    'research': 60,
    'skills_maintenance': 180,
    'knowledge': 180,
    'evolution': 1440,
    'sqm': 180,
    'aqa': 180,
}


def read_event_queue() -> List[Dict]:
    """读取事件队列"""
    if not EVENT_QUEUE.exists():
        return []

    events = []
    content = EVENT_QUEUE.read_text()

    in_pending = False
    for line in content.split('\n'):
        if '## 待处理事件' in line:
            in_pending = True
            continue
        if '## ' in line and in_pending:
            break
        if in_pending and '- [' in line:
            match = re.search(r'\[(\w+)\]\s*(\w+):\s*(.+?)\s*@(\S+)', line)
            if match:
                priority, event_type, payload, timestamp = match.groups()
                events.append({
                    'priority': priority,
                    'type': event_type,
                    'payload': payload,
                    'timestamp': timestamp
                })

    return events


def get_last_run(task: str) -> Optional[datetime]:
    """获取任务上次执行时间"""
    if not TASK_STATE.exists():
        return None

    content = TASK_STATE.read_text()

    for line in content.split('\n'):
        if f'## {task}:' in line:
            parts = line.split(': ', 1)
            if len(parts) == 2:
                try:
                    return datetime.fromisoformat(parts[1].strip())
                except:
                    pass
    return None


def should_run(task: str) -> bool:
    """判断任务是否应该执行（基于间隔）"""
    last_run = get_last_run(task)
    if last_run is None:
        return True

    now = datetime.now()
    interval = TASK_INTERVALS.get(task, 60)
    return (now - last_run).total_seconds() > interval * 60


def analyze_events(events: List[Dict]) -> Dict[str, any]:
    """分析事件队列，返回需要触发的任务"""
    triggered = {
        'tasks': set(),
        'high_priority': False,
        'event_summary': []
    }

    if not events:
        triggered['event_summary'] = ['无待处理事件']
        return triggered

    # 按优先级分类事件
    priority_events = {'P0': [], 'P1': [], 'P2': [], 'P3': []}
    for event in events:
        p = event.get('priority', 'P3')
        if p in priority_events:
            priority_events[p].append(event)

    # P0/P1 事件触发高优先级
    high_priority_count = len(priority_events['P0']) + len(priority_events['P1'])
    if high_priority_count > 0:
        triggered['high_priority'] = True

    # 根据事件类型触发对应任务
    event_type_to_task = {
        'skill_gap': 'skills_maintenance',
        'knowledge_gap': 'knowledge',
        'error': 'heartbeat',
        'task_completed': 'evolution',
        'api_error': 'resources',
    }

    for event in events:
        event_type = event.get('type', '')
        if event_type in event_type_to_task:
            task = event_type_to_task[event_type]
            if should_run(task):
                triggered['tasks'].add(task)

    # 生成摘要
    for priority, evts in priority_events.items():
        if evts:
            triggered['event_summary'].append(f'{priority}: {len(evts)} 个')

    return triggered


def get_time_based_tasks(hour: int, triggered_tasks: set) -> List[str]:
    """基于时间的任务调度"""
    tasks = []

    # 核心任务：每小时
    if should_run('heartbeat'):
        tasks.append('heartbeat')

    # 每天 3 点：深度知识获取
    if hour == 3:
        if should_run('skills_maintenance'):
            tasks.append('skills_maintenance')
        if should_run('knowledge'):
            tasks.append('knowledge')

    # 每天 5 点：进化分析
    if hour == 5:
        if should_run('evolution'):
            tasks.append('evolution')

    # 每 3 小时：SQM + AQA
    if hour % 3 == 0:
        if should_run('sqm'):
            tasks.append('sqm')
        if should_run('aqa'):
            tasks.append('aqa')

    return tasks


def main():
    """主决策逻辑"""
    now = datetime.now()
    hour = now.hour

    # 读取事件
    events = read_event_queue()

    # 分析事件
    event_analysis = analyze_events(events)

    # 事件驱动的任务
    event_tasks = event_analysis['tasks']

    # 时间驱动的任务
    time_tasks = get_time_based_tasks(hour, event_tasks)

    # 合并任务（去重）
    all_tasks = list(set(event_tasks) | set(time_tasks))

    # 总是包含 heartbeat（如果需要）
    if should_run('heartbeat') and 'heartbeat' not in all_tasks:
        all_tasks.append('heartbeat')

    # 输出决策
    print(f"时间: {now.isoformat()}")
    print(f"当前小时: {hour}")
    print(f"事件数: {len(events)}")
    print(f"事件摘要: {', '.join(event_analysis['event_summary'])}")
    print(f"高优先级: {'是' if event_analysis['high_priority'] else '否'}")
    print(f"决策: {all_tasks}")

    # 输出可执行命令（供外部调用）
    if all_tasks:
        print(f"\n# 可选: 直接运行特定模块")
        for task in all_tasks:
            print(f"# {task}")

    return all_tasks


if __name__ == "__main__":
    main()
