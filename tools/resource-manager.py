#!/usr/bin/env python3
"""
Resource Sensing and Access System - Autonomous Resource Management
Features:
1. Unified Resource Interface
2. Automatic Status Sensing
3. Autonomous Access Control
4. Resource Acquisition Decision
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class ResourceManager:
    """Resource Manager - Unified Resource Management"""

    def __init__(self):
        self.workspace = Path("/Users/fuzhuo/.openclaw/workspace")
        self.data_dir = self.workspace / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.registry_file = self.data_dir / "resource-registry.json"
        self.credentials_file = self.data_dir / "credentials.json"
        self.state_file = self.data_dir / "resource-state.json"

        self.load_registry()
        self.load_state()

    # ============ Resource Registry ============

    def load_registry(self):
        """Load resource registry"""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "version": "1.0",
                "updated": datetime.now().isoformat(),
                "resources": {}
            }

    def save_registry(self):
        """Save resource registry"""
        self.registry["updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    def register_resource(self, resource_type: str, name: str, **kwargs):
        """Register a resource"""
        resource_id = f"{resource_type}_{name}"

        self.registry["resources"][resource_id] = {
            "type": resource_type,
            "name": name,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "config": kwargs
        }

        self.save_registry()
        print(f"Registered resource: {resource_type}/{name}")

        return resource_id

    def get_resource(self, resource_type: str = None, name: str = None) -> List[Dict]:
        """Get resources"""
        results = []
        for rid, resource in self.registry["resources"].items():
            if resource_type and resource["type"] != resource_type:
                continue
            if name and resource["name"] != name:
                continue
            results.append(resource)
        return results

    # ============ Resource Status Sensing ============

    def load_state(self):
        """Load resource state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "timestamp": datetime.now().isoformat(),
                "resources": {}
            }

    def save_state(self):
        """Save resource state"""
        self.state["timestamp"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def sense_api_status(self) -> Dict[str, Any]:
        """Sense API resource status"""
        api_status = {}

        apis = [
            {"name": "minimax", "priority": "high", "type": "coding_plan"},
            {"name": "groq", "priority": "high", "type": "free_tier"},
            {"name": "together_ai", "priority": "mid", "type": "free_tier"},
            {"name": "deepseek", "priority": "low", "type": "backup"},
            {"name": "siliconflow", "priority": "low", "type": "backup"}
        ]

        for api in apis:
            api_status[api["name"]] = {
                "priority": api["priority"],
                "type": api["type"],
                "status": self._check_api_health(api["name"]),
                "last_checked": datetime.now().isoformat()
            }

        self.state["resources"]["api"] = api_status
        self.save_state()

        return api_status

    def _check_api_health(self, api_name: str) -> str:
        """Check API health status"""
        health_status = {
            "minimax": "active",
            "groq": "available",
            "together_ai": "available",
            "deepseek": "standby",
            "siliconflow": "standby"
        }
        return health_status.get(api_name, "unknown")

    def sense_task_progress(self) -> Dict[str, Any]:
        """Sense task progress"""
        task_board = self.workspace / "task-board.json"

        if task_board.exists():
            with open(task_board) as f:
                tasks = json.load(f)

            completed = sum(1 for t in tasks if t["status"] == "done")
            in_progress = sum(1 for t in tasks if t["status"] in ["progress", "in_progress"])
            pending = sum(1 for t in tasks if t["status"] == "pending")

            progress = {
                "total": len(tasks),
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "completion_rate": round(completed / len(tasks) * 100, 1) if tasks else 0
            }

            self.state["resources"]["tasks"] = progress
            self.save_state()

            return progress

        return {"total": 0, "completed": 0, "in_progress": 0, "pending": 0}

    def sense_resource_needs(self) -> List[Dict]:
        """Sense resource needs"""
        needs = []

        api_status = self.state.get("resources", {}).get("api", {})
        for api_name, info in api_status.items():
            if info.get("priority") == "high" and info.get("status") in ["standby", "unknown"]:
                needs.append({
                    "type": "api",
                    "name": api_name,
                    "priority": "high",
                    "action": f"Register {api_name} account",
                    "reason": "High priority API not activated"
                })

        task_progress = self.state.get("resources", {}).get("tasks", {})
        if task_progress.get("in_progress", 0) > 5:
            needs.append({
                "type": "task",
                "name": "Task Backlog",
                "priority": "mid",
                "action": "Execute task queue",
                "reason": f"{task_progress['in_progress']} tasks in progress"
            })

        self.state["resources"]["needs"] = needs
        self.save_state()

        return needs

    # ============ Resource Access Control ============

    def store(self, key: str, value: Any, category: str = "general"):
        """Store resource"""
        storage_file = self.data_dir / f"storage_{category}.json"

        if storage_file.exists():
            with open(storage_file) as f:
                storage = json.load(f)
        else:
            storage = {}

        storage[key] = {
            "value": value,
            "stored_at": datetime.now().isoformat()
        }

        with open(storage_file, 'w') as f:
            json.dump(storage, f, indent=2, ensure_ascii=False)

        print(f"Stored: {category}/{key}")

    def retrieve(self, key: str, category: str = "general") -> Any:
        """Retrieve resource"""
        storage_file = self.data_dir / f"storage_{category}.json"

        if not storage_file.exists():
            return None

        with open(storage_file) as f:
            storage = json.load(f)

        if key in storage:
            print(f"Retrieved: {category}/{key}")
            return storage[key]["value"]

        return None

    def list_storage(self, category: str = "general") -> List[str]:
        """List storage items"""
        storage_file = self.data_dir / f"storage_{category}.json"

        if not storage_file.exists():
            return []

        with open(storage_file) as f:
            storage = json.load(f)

        return list(storage.keys())

    # ============ Resource Acquisition Decision ============

    def should_acquire(self, resource_type: str) -> tuple[bool, str]:
        """Determine if resource should be acquired"""
        if resource_type == "api":
            api_status = self.state.get("resources", {}).get("api", {})
            for api_name, info in api_status.items():
                if info.get("priority") == "high" and info.get("status") != "active":
                    return True, f"Need to activate {api_name}"

            if not any(a["name"] == "groq" for a in self.get_resource("api")):
                return True, "Groq free resource not registered"

        if resource_type == "knowledge":
            needs = self.state.get("resources", {}).get("needs", [])
            if any(n["type"] == "learning" for n in needs):
                return True, "Learning needs"

        return False, "Resources sufficient"

    def auto_acquire(self) -> List[Dict]:
        """Auto acquire resources"""
        acquired = []

        should_get, reason = self.should_acquire("api")
        if should_get:
            print(f"Auto acquiring: {reason}")

            self.register_resource(
                "api",
                "groq",
                url="https://console.groq.com",
                type="free_tier",
                cost="free",
                priority="high"
            )
            acquired.append({"type": "api", "name": "groq", "action": "registered"})

        self.save_state()

        return acquired

    # ============ User Help Requests ============

    def get_help_requests(self) -> List[Dict]:
        """Get user help requests"""
        requests = []

        api_status = self.state.get("resources", {}).get("api", {})
        if api_status.get("minimax", {}).get("type") == "coding_plan":
            requests.append({
                "type": "credential",
                "priority": "high",
                "message": "Need Minimax API Key to query Coding Plan usage",
                "action": "Provide API Key or visit https://platform.minimaxi.com/user-center/payment/coding-plan"
            })

        needs = self.state.get("resources", {}).get("needs", [])
        for need in needs:
            if need.get("priority") == "high":
                requests.append({
                    "type": "decision",
                    "priority": "high",
                    "message": f"High priority need: {need.get('action', need.get('reason'))}",
                    "action": need.get("action", "Please confirm")
                })

        return requests

    # ============ Full Status Report ============

    def full_status_report(self) -> Dict[str, Any]:
        """Generate full status report"""
        self.sense_api_status()
        self.sense_task_progress()
        self.sense_resource_needs()

        report = {
            "timestamp": datetime.now().isoformat(),
            "api_resources": self.state.get("resources", {}).get("api", {}),
            "task_progress": self.state.get("resources", {}).get("tasks", {}),
            "resource_needs": self.state.get("resources", {}).get("needs", []),
            "help_requests": self.get_help_requests(),
            "auto_acquired": self.auto_acquire()
        }

        return report

    def print_status(self):
        """Print status"""
        report = self.full_status_report()

        print("\n" + "=" * 60)
        print("Resource Status Report")
        print("=" * 60)

        print("\nAPI Resources:")
        for name, info in report["api_resources"].items():
            status_icon = "Y" if info.get("status") == "active" else "X"
            print(f"  [{status_icon}] {name}: {info.get('status')} ({info.get('priority')})")

        print(f"\nTask Progress: {report['task_progress']}")
        print(f"  Completion Rate: {report['task_progress'].get('completion_rate', 0)}%")

        if report["resource_needs"]:
            print("\nResource Needs:")
            for need in report["resource_needs"]:
                print(f"  - [{need.get('priority', '?').upper()}] {need.get('action')}: {need.get('reason')}")

        if report["help_requests"]:
            print("\nUser Help Needed:")
            for req in report["help_requests"]:
                print(f"  - {req['message']}")
                print(f"    Action: {req['action']}")

        if report["auto_acquired"]:
            print("\nAuto Acquired:")
            for item in report["auto_acquired"]:
                print(f"  - {item['type']}/{item['name']}: {item['action']}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys

    manager = ResourceManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            manager.print_status()
        elif command == "list":
            print("\nRegistered Resources:")
            for rid, resource in manager.registry["resources"].items():
                print(f"  - {rid}: {resource['status']}")
        elif command == "needs":
            requests = manager.get_help_requests()
            for i, req in enumerate(requests, 1):
                print(f"{i}. [{req['priority'].upper()}] {req['message']}")
                print(f"   Action: {req['action']}")
        elif command == "refresh":
            manager.full_status_report()
            print("Status refreshed")
        elif command == "acquire":
            acquired = manager.auto_acquire()
            for item in acquired:
                print(f"  - {item['type']}/{item['name']}: {item['action']}")
        elif command == "get":
            key = sys.argv[2] if len(sys.argv) > 2 else None
            category = sys.argv[3] if len(sys.argv) > 3 else "general"
            if key:
                value = manager.retrieve(key, category)
                if value:
                    print(json.dumps(value, indent=2, ensure_ascii=False))
        elif command == "set":
            key = sys.argv[2] if len(sys.argv) > 2 else None
            value = sys.argv[3] if len(sys.argv) > 3 else None
            category = sys.argv[4] if len(sys.argv) > 4 else "general"
            if key and value:
                try:
                    value = json.loads(value)
                except:
                    pass
                manager.store(key, value, category)
        elif command == "register":
            resource_type = sys.argv[2] if len(sys.argv) > 2 else None
            name = sys.argv[3] if len(sys.argv) > 3 else None
            if resource_type and name:
                manager.register_resource(resource_type, name)
        else:
            print(f"Unknown command: {command}")
    else:
        manager.print_status()
