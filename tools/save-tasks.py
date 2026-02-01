#!/usr/bin/env python3
"""保存更新后的任务到任务看板"""

import json

# 读取更新后的任务
with open("/tmp/tasks_updated.json") as f:
    tasks = json.load(f)

# 保存到任务看板文件
with open("/Users/fuzhuo/.openclaw/workspace/task-board.json", "w") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print(f"已保存 {len(tasks)} 个任务到任务看板")
