#!/usr/bin/env python3
"""
记忆管理系统 - 三层架构自动分类
Session → State → Memory 自动升级
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = MEMORY_DIR / "task-state.md"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

# 重要关键词
IMPORTANT_KEYWORDS = [
    "决策", "决定", "原则", "偏好", "约定", "规则",
    "记住", "不要", "必须", "一定要",
    "important", "remember", "never", "always"
]

# 任务关键词
TASK_KEYWORDS = [
    "任务", "待办", "进度", "完成", "进行中",
    "task", "todo", "progress", "doing"
]


class MemoryManager:
    """三层记忆管理系统"""
    
    def __init__(self):
        self.session_memory = []
        self.state_data = {}
        self.memory_data = []
    
    def classify(self, content: str) -> str:
        """自动分类记忆"""
        content_lower = content.lower()
        
        # L3: 重要决策 → Memory (长期)
        for kw in IMPORTANT_KEYWORDS:
            if kw in content_lower:
                return "memory"
        
        # L2: 任务相关 → State (状态)
        for kw in TASK_KEYWORDS:
            if kw in content_lower:
                return "state"
        
        # L1: 其他 → Session (会话)
        return "session"
    
    def remember(self, content: str, category: str = None, auto: bool = True) -> str:
        """记忆入口"""
        if auto:
            category = category or self.classify(content)
        
        timestamp = datetime.now().isoformat()
        
        if category == "memory":
            self._write_memory(content, timestamp)
            return "memory"
        elif category == "state":
            self._write_state(content, timestamp)
            return "state"
        else:
            self.session_memory.append({"content": content, "time": timestamp})
            return "session"
    
    def _write_memory(self, content: str, timestamp: str):
        """写入长期记忆"""
        entry = f"- **{timestamp[:10]}**: {content}\n"
        
        # 追加到 MEMORY.md 或 memory/ai/
        memory_path = MEMORY_DIR / "ai" / "自动记忆.md"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(memory_path, "a") as f:
            f.write(entry)
    
    def _write_state(self, content: str, timestamp: str):
        """写入状态"""
        state_path = MEMORY_DIR / "auto-state.md"
        
        content = f"\n## {timestamp[:19]}\n{content}\n"
        
        with open(state_path, "a") as f:
            f.write(content)
    
    def retrieve(self, query: str) -> Dict:
        """检索记忆（自动匹配层级）"""
        results = {"session": [], "state": [], "memory": []}
        
        # L1: Session
        results["session"] = [m for m in self.session_memory if query in m["content"]]
        
        # L2: State
        state_path = MEMORY_DIR / "auto-state.md"
        if state_path.exists():
            with open(state_path) as f:
                content = f.read()
                if query in content:
                    results["state"] = [query]
        
        # L3: Memory
        memory_path = MEMORY_DIR / "ai" / "自动记忆.md"
        if memory_path.exists():
            with open(memory_path) as f:
                content = f.read()
                if query in content:
                    results["memory"] = [query]
        
        return results
    
    def upgrade(self, content: str) -> str:
        """手动升级记忆层级"""
        return self.remember(content, auto=True)


def main():
    """测试"""
    mm = MemoryManager()
    
    # 测试分类
    test_cases = [
        "记住不要用var要用const",  # memory
        "今天要完成第5章",  # state
        "天气不错",  # session
        "重要决策: 每周一9点执行研究",  # memory
    ]
    
    print("🧠 记忆分类测试:")
    for content in test_cases:
        category = mm.classify(content)
        print(f"  [{category}] {content}")


if __name__ == "__main__":
    main()
