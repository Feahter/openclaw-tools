#!/usr/bin/env python3
"""Resource CLI - Command line interface for resource management"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ResourceManager:
    def __init__(self):
        self.workspace = Path("/Users/fuzhuo/.openclaw/workspace")
        self.data_dir = self.workspace / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.registry_file = self.data_dir / "resource-registry.json"
        self.state_file = self.data_dir / "resource-state.json"
        self.load_registry()
        self.load_state()

    def load_registry(self):
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                self.registry = json.load(f)
        else:
            self.registry = {"version": "1.0", "resources": {}}

    def save_registry(self):
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def register_resource(self, resource_type: str, name: str, **kwargs):
        rid = f"{resource_type}_{name}"
        self.registry["resources"][rid] = {
            "type": resource_type, "name": name,
            "registered_at": datetime.now().isoformat(),
            "status": "active", "config": kwargs
        }
        self.save_registry()
        print(f"Registered: {resource_type}/{name}")
        return rid

    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {"timestamp": datetime.now().isoformat(), "resources": {}}

    def save_state(self):
        self.state["timestamp"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def sense_api_status(self) -> Dict:
        api_status = {
            "minimax": {"priority": "high", "type": "coding_plan", "status": "active"},
            "groq": {"priority": "high", "type": "free_tier", "status": "available"},
            "together_ai": {"priority": "mid", "type": "free_tier", "status": "available"},
            "deepseek": {"priority": "low", "type": "backup", "status": "standby"},
            "siliconflow": {"priority": "low", "type": "backup", "status": "standby"}
        }
        self.state["resources"]["api"] = api_status
        self.save_state()
        return api_status

    def sense_task_progress(self) -> Dict:
        task_board = self.workspace / "task-board.json"
        if task_board.exists():
            with open(task_board) as f:
                tasks = json.load(f)
            completed = sum(1 for t in tasks if t["status"] == "done")
            in_progress = sum(1 for t in tasks if t["status"] in ["progress", "in_progress"])
            progress = {"total": len(tasks), "completed": completed, "in_progress": in_progress,
                       "completion_rate": round(completed/len(tasks)*100, 1) if tasks else 0}
            self.state["resources"]["tasks"] = progress
            self.save_state()
            return progress
        return {"total": 0, "completed": 0, "in_progress": 0}

    def sense_resource_needs(self) -> List:
        needs = []
        api_status = self.state.get("resources", {}).get("api", {})
        for api_name, info in api_status.items():
            if info.get("priority") == "high" and info.get("status") != "active":
                needs.append({"type": "api", "name": api_name, "priority": "high",
                             "action": f"Register {api_name}", "reason": "Not activated"})
        self.state["resources"]["needs"] = needs
        self.save_state()
        return needs

    def get_help_requests(self) -> List:
        requests = []
        requests.append({
            "type": "credential", "priority": "high",
            "message": "Need Minimax API Key for Coding Plan usage query",
            "action": "Provide API Key or visit platform.minimaxi.com/user-center/payment/coding-plan"
        })
        return requests

    def auto_acquire(self) -> List:
        acquired = []
        self.register_resource("api", "groq", url="https://console.groq.com", type="free_tier", cost="free")
        acquired.append({"type": "api", "name": "groq", "action": "registered"})
        return acquired

    def full_status(self):
        self.sense_api_status()
        self.sense_task_progress()
        self.sense_resource_needs()
        return self.state

    def print_status(self):
        self.sense_api_status()
        self.sense_task_progress()
        self.sense_resource_needs()

        print("\n" + "=" * 60)
        print("Resource Status Report")
        print("=" * 60)

        print("\nAPI Resources:")
        for name, info in self.state.get("resources", {}).get("api", {}).items():
            status_icon = "Y" if info.get("status") == "active" else "O"
            print(f"  [{status_icon}] {name}: {info.get('status')} ({info.get('priority')})")

        tasks = self.state.get("resources", {}).get("tasks", {})
        print(f"\nTask Progress: {tasks.get('completed', 0)}/{tasks.get('total', 0)} ({tasks.get('completion_rate', 0)}%)")

        print("\nUser Help Needed:")
        for req in self.get_help_requests():
            print(f"  - {req['message']}")
            print(f"    Action: {req['action']}")

        print("\n" + "=" * 60)


def main():
    manager = ResourceManager()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            manager.print_status()
        elif cmd == "needs":
            for req in manager.get_help_requests():
                print(f"[{req['priority'].upper()}] {req['message']}")
                print(f"  Action: {req['action']}")
        elif cmd == "acquire":
            for item in manager.auto_acquire():
                print(f"Acquired: {item['type']}/{item['name']}")
        elif cmd == "refresh":
            manager.full_status()
            print("Status refreshed")
        else:
            print(f"Unknown command: {cmd}")
    else:
        manager.print_status()


if __name__ == "__main__":
    main()
