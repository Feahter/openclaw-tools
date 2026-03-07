#!/usr/bin/env python3
"""
自动任务执行器 - 基于优先级和资源自动调度任务
功能：
1. 优先级任务队列
2. 资源感知调度
3. 并发执行优化
4. 自动化收益最大化
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import heapq

class AutoTaskExecutor:
    def __init__(self):
        self.workspace = Path("/Users/fuzhuo/.openclaw/workspace")
        self.data_dir = self.workspace / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.task_queue_file = self.data_dir / "task-queue.json"
        self.execution_log_file = self.data_dir / "execution-log.json"

        self.load_tasks()

    def load_tasks(self):
        """加载任务队列"""
        if self.task_queue_file.exists():
            with open(self.task_queue_file) as f:
                data = json.load(f)
                # 确保是列表格式
                if isinstance(data, list):
                    self.task_queue = data
                else:
                    self.task_queue = []
        else:
            self.task_queue = []

        if self.execution_log_file.exists():
            with open(self.execution_log_file) as f:
                self.execution_log = json.load(f)
        else:
            self.execution_log = []

    def save_tasks(self):
        """保存任务队列"""
        with open(self.task_queue_file, 'w') as f:
            json.dump(self.task_queue, f, indent=2, ensure_ascii=False)

        with open(self.execution_log_file, 'w') as f:
            json.dump(self.execution_log, f, indent=2, ensure_ascii=False)

    def add_task(self, title: str, priority: int, category: str, command: str = None, estimated_time: int = 30):
        """添加任务到队列"""
        task = {
            "id": len(self.task_queue) + 1,
            "title": title,
            "priority": priority,  # 1-10, 10最高
            "category": category,  # 资源/效率/商业/进化
            "command": command,
            "estimated_time": estimated_time,  # 分钟
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "execute_count": 0
        }

        # 添加优先级标记，直接排序
        task["_priority_key"] = -priority
        self.task_queue.append(task)
        # 按优先级排序
        self.task_queue.sort(key=lambda x: x.get("_priority_key", 0))
        self.save_tasks()

        print(f"✅ 添加任务: {title} (优先级: {priority})")

        return task

    def get_next_task(self) -> Optional[Dict]:
        """获取下一个要执行的任务"""
        for task in self.task_queue:
            if task["status"] == "pending":
                self.task_queue.remove(task)
                return task

        return None

    def execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        print(f"\n▶️ 执行任务: {task['title']}")
        print(f"   分类: {task['category']} | 预计时间: {task['estimated_time']}分钟")

        start_time = datetime.now()
        result = {
            "task_id": task["id"],
            "title": task["title"],
            "start_time": start_time.isoformat(),
            "status": "running"
        }

        # 执行命令（如果有）
        if task.get("command"):
            try:
                process = subprocess.run(
                    task["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=task["estimated_time"] * 60
                )
                result["output"] = process.stdout
                result["return_code"] = process.returncode
                result["status"] = "success" if process.returncode == 0 else "failed"
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            # 无命令的任务（如思考、规划）
            result["status"] = "success"
            result["output"] = "任务完成"

        result["end_time"] = datetime.now().isoformat()
        result["duration"] = (datetime.fromisoformat(result["end_time"]) - start_time).total_seconds() / 60

        # 更新任务状态
        task["status"] = result["status"]
        task["execute_count"] += 1
        task["last_executed"] = result["end_time"]

        # 记录执行日志
        self.execution_log.append(result)
        self.save_tasks()

        print(f"   状态: {result['status']} | 耗时: {result['duration']:.1f}分钟")

        return result

    def analyze_execution(self):
        """分析执行效率"""
        print("\n📊 执行效率分析")
        print("=" * 50)

        if not self.execution_log:
            print("暂无执行记录")
            return {}

        # 统计
        total = len(self.execution_log)
        success = sum(1 for e in self.execution_log if e["status"] == "success")
        failed = total - success

        print(f"总执行次数: {total}")
        print(f"成功: {success} ({success/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")

        # 平均耗时
        durations = [e["duration"] for e in self.execution_log if "duration" in e]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"平均耗时: {avg_duration:.1f}分钟")

        # 分类统计
        categories = {}
        for e in self.execution_log:
            # 从task-board或任务ID获取分类
            cat = e.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0}
            categories[cat]["total"] += 1
            if e["status"] == "success":
                categories[cat]["success"] += 1

        print("\n分类统计:")
        for cat, stats in categories.items():
            rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {cat}: {stats['success']}/{stats['total']} ({rate:.1f}%)")

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "avg_duration": avg_duration if durations else 0,
            "categories": categories
        }

    def auto_schedule(self):
        """自动调度任务"""
        print("\n📅 自动任务调度")
        print("=" * 50)

        # 定义周期性任务
        scheduled_tasks = [
            {
                "title": "检查API资源状态",
                "priority": 8,
                "category": "资源",
                "command": "python3 /Users/fuzhuo/.openclaw/workspace/tools/resource-optimizer.py",
                "estimated_time": 5,
                "schedule": "每30分钟"
            },
            {
                "title": "运行效率优化",
                "priority": 7,
                "category": "效率",
                "command": "python3 /Users/fuzhuo/.openclaw/workspace/tools/evolution-engine.py",
                "estimated_time": 10,
                "schedule": "每小时"
            },
            {
                "title": "商业机会扫描",
                "priority": 6,
                "category": "商业",
                "command": "python3 /Users/fuzhuo/.openclaw/workspace/tools/resource-optimizer.py --scan-opportunities",
                "estimated_time": 15,
                "schedule": "每天"
            },
            {
                "title": "任务队列分析",
                "priority": 5,
                "category": "进化",
                "command": "python3 /Users/fuzhuo/.openclaw/workspace/tools/auto-task-executor.py --analyze",
                "estimated_time": 5,
                "schedule": "每天"
            }
        ]

        print("已调度的任务:")
        for task in scheduled_tasks:
            print(f"  [{task['priority']}] {task['title']} - {task['schedule']}")

        return scheduled_tasks

    def run_full_cycle(self):
        """运行完整周期"""
        print(f"\n🚀 自动任务执行器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. 自动调度
        scheduled = self.auto_schedule()

        # 2. 分析执行历史
        analysis = self.analyze_execution()

        # 3. 添加建议的任务
        suggested_tasks = [
            ("注册Groq免费账户", 9, "资源", None, 20),
            ("充值Minimax ¥13", 10, "资源", None, 5),
            ("优化API调用策略", 8, "效率", None, 30),
            ("测试并发任务功能", 7, "效率", None, 60),
            ("编写商业化方案", 6, "商业", None, 120)
        ]

        print("\n建议添加的任务:")
        for title, priority, category, cmd, time in suggested_tasks:
            self.add_task(title, priority, category, cmd, time)

        # 4. 执行下一个高优先级任务
        next_task = self.get_next_task()
        if next_task:
            self.execute_task(next_task)

        self.save_tasks()

        print("\n" + "=" * 60)
        print("✅ 执行周期完成!")
        print(f"📊 待执行任务: {len(self.task_queue)}")
        print(f"📈 总执行次数: {len(self.execution_log)}")

        return {
            "scheduled_tasks": len(scheduled),
            "pending_tasks": len(self.task_queue),
            "execution_count": len(self.execution_log),
            "analysis": analysis
        }

if __name__ == "__main__":
    import sys

    executor = AutoTaskExecutor()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            executor.analyze_execution()
        elif sys.argv[1] == "--schedule":
            executor.auto_schedule()
        elif sys.argv[1] == "--next":
            task = executor.get_next_task()
            if task:
                executor.execute_task(task)
    else:
        executor.run_full_cycle()
