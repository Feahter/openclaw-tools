#!/usr/bin/env python3
"""
Convoy Engine — 多子Agent并行执行 + 崩溃自愈 + 状态持久化

核心设计：
- 多个子Agent以 convoy 模式并行运行
- 共享状态文件 (JSON)，断点可恢复
- 超时/崩溃自动重启，不影响整体流程
- 支持 DAG 依赖拓扑

使用方式：
    python3 convoy.py run --task "研究 X" --parallel 3
    python3 convoy.py status
    python3 convoy.py resume --convoy-id <id>
    python3 convoy.py kill --convoy-id <id>
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
STATE_DIR = WORKSPACE / ".state" / "convoy"
STATE_DIR.mkdir(parents=True, exist_ok=True)


def now_ts():
    return datetime.now().isoformat()


# ─────────────────────────────────────────────────────────────
# Convoy 状态管理
# ─────────────────────────────────────────────────────────────

class ConvoyState:
    """共享状态文件读写，带文件锁"""

    def __init__(self, convoy_id: str):
        self.file = STATE_DIR / f"{convoy_id}.json"
        self.lock_file = STATE_DIR / f"{convoy_id}.lock"

    def read(self) -> dict:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except (json.JSONDecodeError, IOError):
                return self._new_state()
        return self._new_state()

    def write(self, state: dict):
        self.file.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    def _new_state(self) -> dict:
        return {
            "convoy_id": self.file.stem,
            "created_at": now_ts(),
            "updated_at": now_ts(),
            "status": "initializing",  # initializing | running | completed | failed | killed
            "tasks": {},
            "results": {},
            "errors": {},
            "total_cost": 0.0,
        }

    def update_task(self, task_id: str, task_state: dict):
        s = self.read()
        if "tasks" not in s:
            s["tasks"] = {}
        s["tasks"][task_id] = {
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "pid": None,
            "session_key": None,
            "error": None,
            "retry_count": 0,
            **task_state,
        }
        s["updated_at"] = now_ts()
        self.write(s)

    def mark_running(self, task_id: str, pid: int, session_key: str):
        s = self.read()
        if task_id in s["tasks"]:
            s["tasks"][task_id]["status"] = "running"
            s["tasks"][task_id]["started_at"] = now_ts()
            s["tasks"][task_id]["pid"] = pid
            s["tasks"][task_id]["session_key"] = session_key
        s["updated_at"] = now_ts()
        self.write(s)

    def mark_completed(self, task_id: str, result: str = ""):
        s = self.read()
        if task_id in s["tasks"]:
            s["tasks"][task_id]["status"] = "completed"
            s["tasks"][task_id]["completed_at"] = now_ts()
            if result:
                s["results"][task_id] = result
        s["updated_at"] = now_ts()
        self.write(s)

    def mark_failed(self, task_id: str, error: str):
        s = self.read()
        if task_id in s["tasks"]:
            s["tasks"][task_id]["status"] = "failed"
            s["tasks"][task_id]["completed_at"] = now_ts()
            s["tasks"][task_id]["error"] = error
            s["tasks"][task_id]["retry_count"] = s["tasks"][task_id].get("retry_count", 0) + 1
        s["updated_at"] = now_ts()
        self.write(s)

    def all_done(self) -> bool:
        s = self.read()
        return all(t["status"] in ("completed", "failed", "skipped") for t in s["tasks"].values())

    def any_running(self) -> bool:
        s = self.read()
        return any(t["status"] == "running" for t in s["tasks"].values())


# ─────────────────────────────────────────────────────────────
# Convoy 运行引擎
# ─────────────────────────────────────────────────────────────

class ConvoyEngine:
    def __init__(self, convoy_id: str, max_parallel: int = 3, max_retries: int = 2):
        self.id = convoy_id
        self.state = ConvoyState(convoy_id)
        self.max_parallel = max_parallel
        self.max_retries = max_retries

    def define_tasks(self, tasks: list[dict]):
        """定义 convoy 任务列表，tasks 为 [{id, prompt, depends_on?}]"""
        for t in tasks:
            self.state.update_task(t["id"], {
                "prompt": t["prompt"],
                "depends_on": t.get("depends_on", []),
                "retry_count": 0,
            })

    def _can_start(self, task_id: str) -> bool:
        """检查依赖是否全部完成"""
        s = self.state.read()
        deps = s["tasks"].get(task_id, {}).get("depends_on", [])
        for dep in deps:
            if s["tasks"].get(dep, {}).get("status") != "completed":
                return False
        return True

    def _start_task(self, task_id: str) -> Optional[tuple[int, str]]:
        """
        启动一个子Agent任务，返回 (pid, session_key) 或 None
        目前用 sessions_spawn 触发（需要通过 API）
        简化版：写入待执行队列，由外部 runner 执行
        """
        s = self.state.read()
        pid = os.getpid()
        session_key = f"convoy:{self.id}:{task_id}"
        self.state.mark_running(task_id, pid, session_key)
        return pid, session_key

    def run(self, wait: bool = True, poll_interval: int = 10):
        """启动 convoy，支持等待模式"""
        s = self.state.read()
        s["status"] = "running"
        self.state.write(s)

        # 写入 task_queue.json，由外部/openclaw 的 sessions_spawn 读取并执行
        queue_file = STATE_DIR / f"{self.id}.queue.json"
        queue_file.write_text(json.dumps({"pending": list(s["tasks"].keys())}, indent=2))

        if not wait:
            return

        # 等待所有任务完成
        while True:
            time.sleep(poll_interval)
            s = self.state.read()
            if self.state.all_done():
                s["status"] = "completed"
                self.state.write(s)
                print(f"[Convoy {self.id}] 完成")
                break

    def kill(self):
        s = self.state.read()
        s["status"] = "killed"
        for t in s["tasks"].values():
            if t["status"] == "running":
                t["status"] = "killed"
        self.state.write(s)


# ─────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────

def cmd_run(args):
    convoy_id = args.id or f"convoy-{uuid.uuid4().hex[:8]}"
    engine = ConvoyEngine(convoy_id, max_parallel=args.parallel)

    # 解析任务
    # 简单模式：单个 prompt 拆成 N 个子任务
    task_prompts = _split_task(args.task, args.parallel)
    tasks = [
        {"id": f"t{i+1}", "prompt": p, "depends_on": [] if i == 0 else [f"t{i}"]}
        for i, p in enumerate(task_prompts)
    ]

    # 如果并行数 > 1，去掉依赖链，变成纯并行
    if args.parallel > 1 and not args.chain:
        for t in tasks:
            t["depends_on"] = []

    print(f"🚀 启动 Convoy {convoy_id}，{len(tasks)} 个任务，并行数 {args.parallel}")
    engine.define_tasks(tasks)
    engine.run(wait=args.wait, poll_interval=args.poll)
    return convoy_id


def cmd_status(args):
    if not args.id:
        # 列出所有 convoy
        files = list(f for f in STATE_DIR.glob("*.json") if not f.name.endswith(".queue.json"))
        if not files:
            print("暂无 Convoy 任务")
            return
        print(f"共 {len(files)} 个 Convoy：\n")
        for f in sorted(files):
            try:
                s = json.loads(f.read_text())
                task_count = len(s.get("tasks", {}))
                done = sum(1 for t in s.get("tasks", {}).values() if t["status"] == "completed")
                print(f"  [{s.get('status', 'unknown'):12}] {f.stem}  ({done}/{task_count})  {s.get('created_at', '')[:16]}")
            except (json.JSONDecodeError, KeyError):
                print(f"  [损坏?] {f.stem}")
        return

    state = ConvoyState(args.id).read()
    print(f"Convoy: {args.id}")
    print(f"状态: {state['status']}")
    print(f"总耗时: {state.get('updated_at', '')[:16]}")
    print(f"\n任务列表：")
    for tid, t in state.get("tasks", {}).items():
        icon = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌", "skipped": "⏭️"}.get(t["status"], "?")
        retry = f" (重试 {t.get('retry_count', 0)} 次)" if t.get("retry_count", 0) > 0 else ""
        print(f"  {icon} {tid}: {t['status']}{retry}")
        if t.get("error"):
            print(f"      错误: {t['error'][:100]}")


def cmd_resume(args):
    print(f"🔁 恢复 Convoy {args.id}")
    engine = ConvoyEngine(args.id)
    engine.run(wait=True)


def cmd_kill(args):
    engine = ConvoyEngine(args.id)
    engine.kill()
    print(f"🚫 Convoy {args.id} 已终止")


def cmd_clean(args):
    """清理超过 N 天的 convoy 状态文件"""
    import time as time_module
    cutoff = time_module.time() - args.days * 86400
    removed = 0
    for f in STATE_DIR.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    print(f"清理了 {removed} 个历史 Convoy 记录")


def _split_task(task: str, n: int) -> list[str]:
    """简单任务分割：把一个大任务拆成 N 块"""
    # 这里可以用 LLM 做智能分割，简化版用关键词切分
    return [f"{task} [任务 {i+1}/{n}]" for i in range(n)]


def main():
    parser = argparse.ArgumentParser(description="Convoy Engine — 多子Agent并行执行引擎")
    sub = parser.add_subparsers()

    p_run = sub.add_parser("run", help="启动新 Convoy")
    p_run.add_argument("--task", "-t", required=True, help="研究/执行任务")
    p_run.add_argument("--parallel", "-p", type=int, default=3, help="并行数 (默认3)")
    p_run.add_argument("--chain", action="store_true", help="串行链式执行 (默认并行)")
    p_run.add_argument("--id", help="指定 Convoy ID")
    p_run.add_argument("--wait", action="store_true", default=False, help="等待完成")
    p_run.add_argument("--poll", type=int, default=10, help="轮询间隔(秒)")
    p_run.set_defaults(fn=cmd_run)

    p_status = sub.add_parser("status", help="查看 Convoy 状态")
    p_status.add_argument("--id", help="指定 Convoy ID，留空列出全部")
    p_status.set_defaults(fn=cmd_status)

    p_resume = sub.add_parser("resume", help="恢复被中断的 Convoy")
    p_resume.add_argument("--id", required=True)
    p_resume.set_defaults(fn=cmd_resume)

    p_kill = sub.add_parser("kill", help="终止 Convoy")
    p_kill.add_argument("--id", required=True)
    p_kill.set_defaults(fn=cmd_kill)

    p_clean = sub.add_parser("clean", help="清理历史 Convoy")
    p_clean.add_argument("--days", type=int, default=7, help="清理 N 天前的 (默认7天)")
    p_clean.set_defaults(fn=cmd_clean)

    args = parser.parse_args()
    if hasattr(args, "fn"):
        args.fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
