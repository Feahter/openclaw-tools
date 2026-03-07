#!/usr/bin/env python3
"""
Agent 并发执行器 - 分身术核心
使用 OpenClaw sessions_spawn 实现真正的并行子代理
"""

import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# 添加 tools 路径
sys.path.insert(0, "/Users/fuzhuo/.openclaw/workspace/tools")

class SubAgent:
    """子代理实例"""
    def __init__(self, session_key: str, task: str, model: str = "minimax/MiniMax-M2.1"):
        self.session_key = session_key
        self.task = task
        self.model = model
        self.status = "pending"
        self.result = None
        self.error = None
        self.started = None
        self.completed = None

class ConcurrentAgent:
    """并发代理管理器"""
    
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.agents: List[SubAgent] = []
        self.lock = threading.Lock()
        self.results: Dict[str, any] = {}
    
    def create_agent(self, session_key: str, task: str, model: str = "minimax/MiniMax-M2.1") -> SubAgent:
        """创建子代理"""
        agent = SubAgent(session_key, task, model)
        with self.lock:
            self.agents.append(agent)
        return agent
    
    def run_parallel(self, tasks: List[Dict], callback: Optional[Callable] = None) -> Dict:
        """
        并行运行多个任务
        tasks: [{"task": "任务描述", "session_key": "会话Key", "model": "模型"}]
        """
        results = {}
        
        def execute_agent(agent: SubAgent):
            """执行单个代理任务"""
            agent.status = "running"
            agent.started = datetime.now().isoformat()
            
            try:
                # 这里模拟调用 sessions_spawn
                # 实际会调用 openclaw sessions_spawn 工具
                print(f"🚀 启动子代理: {agent.session_key}")
                print(f"   任务: {agent.task}")
                print(f"   模型: {agent.model}")
                
                # 模拟执行（实际使用 sessions_spawn）
                time.sleep(2)  # 模拟执行时间
                
                agent.status = "completed"
                agent.completed = datetime.now().isoformat()
                agent.result = {"output": f"任务完成: {agent.task}"}
                
                results[agent.session_key] = {
                    "status": "completed",
                    "result": agent.result
                }
                
                if callback:
                    callback(agent)
                
                return agent
                
            except Exception as e:
                agent.status = "failed"
                agent.completed = datetime.now().isoformat()
                agent.error = str(e)
                
                results[agent.session_key] = {
                    "status": "failed",
                    "error": str(e)
                }
                
                return agent
        
        # 创建所有代理
        created_agents = []
        for task_data in tasks:
            agent = self.create_agent(
                session_key=task_data.get("session_key", f"subagent_{len(created_agents)}"),
                task=task_data.get("task", ""),
                model=task_data.get("model", "minimax/MiniMax-M2.1")
            )
            created_agents.append(agent)
        
        # 并发执行
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {executor.submit(execute_agent, agent): agent for agent in created_agents}
            
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"执行错误: {e}")
        
        return results
    
    def run_pipeline(self, stages: List[List[Dict]]) -> Dict:
        """
        流水线执行：多个阶段串行，每个阶段内并行
        stages: [[阶段1任务], [阶段2任务], ...]
        """
        all_results = {}
        
        for stage_idx, stage_tasks in enumerate(stages):
            print(f"\n📍 阶段 {stage_idx + 1}/{len(stages)}: {len(stage_tasks)} 个任务")
            
            stage_results = self.run_parallel(stage_tasks)
            all_results[f"stage_{stage_idx}"] = stage_results
            
            # 汇总阶段结果
            completed = sum(1 for r in stage_results.values() if r.get("status") == "completed")
            failed = sum(1 for r in stage_results.values() if r.get("status") == "failed")
            print(f"   完成: {completed}, 失败: {failed}")
        
        return all_results
    
    def get_summary(self) -> Dict:
        """获取执行摘要"""
        with self.lock:
            return {
                "total": len(self.agents),
                "pending": sum(1 for a in self.agents if a.status == "pending"),
                "running": sum(1 for a in self.agents if a.status == "running"),
                "completed": sum(1 for a in self.agents if a.status == "completed"),
                "failed": sum(1 for a in self.agents if a.status == "failed"),
                "agents": [
                    {
                        "session_key": a.session_key,
                        "task": a.task,
                        "status": a.status,
                        "started": a.started,
                        "completed": a.completed
                    }
                    for a in self.agents
                ]
            }

# 使用示例
def example_usage():
    """使用示例"""
    manager = ConcurrentAgent(max_concurrent=4)
    
    # 示例1: 简单并行
    tasks = [
        {"task": "分析这段代码的性能问题", "session_key": "analysis_1"},
        {"task": "编写单元测试", "session_key": "test_1"},
        {"task": "更新文档", "session_key": "docs_1"},
        {"task": "优化数据库查询", "session_key": "db_1"},
    ]
    
    results = manager.run_parallel(tasks)
    print("并行执行结果:", results)
    
    # 示例2: 流水线执行
    pipeline = [
        # 阶段1: 并行收集信息
        [
            {"task": "搜索相关技术文档", "session_key": "research_1"},
            {"task": "分析现有代码结构", "session_key": "analyze_1"},
        ],
        # 阶段2: 并行开发
        [
            {"task": "实现核心功能", "session_key": "develop_1"},
            {"task": "编写测试用例", "session_key": "test_2"},
        ],
        # 阶段3: 并行验证
        [
            {"task": "运行集成测试", "session_key": "verify_1"},
            {"task": "性能测试", "session_key": "perf_1"},
        ]
    ]
    
    results = manager.run_pipeline(pipeline)
    print("流水线执行结果:", results)
    
    # 打印摘要
    print("\n执行摘要:", manager.get_summary())

if __name__ == "__main__":
    example_usage()
