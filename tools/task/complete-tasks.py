#!/usr/bin/env python3
"""更新任务看板状态"""

import json

TASKS_FILE = "/Users/fuzhuo/.openclaw/workspace/task-board.json"

with open(TASKS_FILE) as f:
    tasks = json.load(f)

# 需要标记完成的任务
to_complete = [
    "增加本地化的语音能力",
    "增加视觉能力"
]

updated = 0
for task in tasks:
    if task["title"] in to_complete and task["status"] in ["todo", "progress"]:
        task["status"] = "done"
        task["progress"] = 100
        task["updated"] = "2026-02-01T16:08:00.000Z"
        print(f"✅ 标记完成: {task['title']}")
        updated += 1

with open(TASKS_FILE, "w") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print(f"\n已更新 {updated} 个任务")
