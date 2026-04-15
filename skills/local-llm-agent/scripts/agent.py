#!/usr/bin/env python3
"""
Local LLM Agent - 基于 laconic 架构的本地研究 Agent
轻量级、低成本、可本地运行的研究助手
"""

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional, Protocol
from abc import ABC, abstractmethod


# ============ Data Models ============

@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str


@dataclass
class LLMResponse:
    """LLM 响应"""
    text: str
    cost: float = 0.0
    reasoning: str = ""


@dataclass
class AgentResult:
    """Agent 执行结果"""
    answer: str
    cost: float = 0.0
    knowledge: str = ""
    iterations: int = 0


@dataclass
class Scratchpad:
    """上下文状态管理 - laconic 核心创新"""
    original_question: str
    current_step: str = ""
    knowledge: str = ""
    history: List[str] = field(default_factory=list)
    iteration_count: int = 0
    
    def append_history(self, entry: str):
        if entry:
            self.history.append(entry)
    
    def snapshot(self) -> str:
        """生成当前状态的快照，用于 prompt"""
        lines = [
            f"Question: {self.original_question}",
            f"\nCurrent Step: {self.current_step or '(none yet)'}",
            f"\nKnowledge: {self.knowledge or '(empty)'}",
        ]
        if self.history:
            lines.extend(["\nHistory:", *self.history])
        lines.append(f"\nIteration: {self.iteration_count}")
        return "\n".join(lines)


# ============ Provider Interfaces ============

class SearchProvider(ABC):
    """搜索提供者接口"""
    
    @abstractmethod
    def search(self, query: str) -> List[SearchResult]:
        pass


class LLMProvider(ABC):
    """LLM 提供者接口"""
    
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        pass


# ============ Search Implementations ============

class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo 搜索 - 免费，无需 API key"""
    
    def search(self, query: str) -> List[SearchResult]:
        """使用 ddgr 或 duckduckgo-search 库"""
        try:
            # 尝试使用 duckduckgo-search
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", "")
                    )
                    for r in results
                ]
        except ImportError:
            # 回退到命令行工具
            return self._search_cli(query)
    
    def _search_cli(self, query: str) -> List[SearchResult]:
        """使用 ddgr 命令行工具"""
        try:
            result = subprocess.run(
                ["ddgr", "--json", "-n", "5", query],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return [
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("abstract", "")
                    )
                    for item in data
                ]
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        return []


class BraveProvider(SearchProvider):
    """Brave Search - 需要 API key，质量更高"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str) -> List[SearchResult]:
        import urllib.request
        import urllib.parse
        
        url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count=5"
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                results = data.get("web", {}).get("results", [])
                return [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("description", "")
                    )
                    for r in results[:5]
                ]
        except Exception:
            return []


# ============ LLM Implementations ============

class OllamaProvider(LLMProvider):
    """Ollama 本地模型提供者"""
    
    def __init__(self, model: str = "qwen3:4b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")
    
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        import urllib.request
        
        url = f"{self.host}/api/generate"
        data = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
                return LLMResponse(
                    text=result.get("response", ""),
                    cost=0.0  # 本地模型免费
                )
        except Exception as e:
            return LLMResponse(text=f"Error: {e}", cost=0.0)


class OpenRouterProvider(LLMProvider):
    """OpenRouter 提供者 - 统一入口，自动 fallback"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
    
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        import urllib.request
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())
                content = result["choices"][0]["message"]["content"]
                # 估算成本
                tokens = result.get("usage", {}).get("total_tokens", 0)
                cost = tokens * 0.000003  # 粗略估算 $3/MTok
                return LLMResponse(text=content, cost=cost)
        except Exception as e:
            return LLMResponse(text=f"Error: {e}", cost=0.0)


# ============ Agent Core ============

class LocalLLMAgent:
    """本地 LLM 研究 Agent - laconic 架构实现"""
    
    # Prompts
    PLANNER_SYSTEM = """You are a focused research planner. You must gather evidence from web searches before answering. Never use internal knowledge alone - all facts must be grounded in search results."""
    
    SYNTHESIZER_SYSTEM = """You compress search findings into a concise, plain-text knowledge state. ONLY include facts that appear in the search results provided. Never add information from internal knowledge. If information is missing, leave a placeholder like [NOT YET SEARCHED]."""
    
    FINALIZER_SYSTEM = """You write the final answer using the knowledge state. If information is insufficient, say so clearly."""
    
    def __init__(
        self,
        planner: LLMProvider,
        synthesizer: LLMProvider,
        searcher: SearchProvider,
        finalizer: Optional[LLMProvider] = None,
        max_iterations: int = 5,
        search_cost: float = 0.0,
        debug: bool = False
    ):
        self.planner = planner
        self.synthesizer = synthesizer
        self.finalizer = finalizer or synthesizer
        self.searcher = searcher
        self.max_iterations = max_iterations
        self.search_cost = search_cost
        self.debug = debug
    
    def research(self, question: str, prior_knowledge: str = "") -> AgentResult:
        """执行研究循环"""
        pad = Scratchpad(original_question=question)
        if prior_knowledge:
            pad.knowledge = prior_knowledge
        
        total_cost = 0.0
        
        for i in range(self.max_iterations):
            pad.iteration_count = i + 1
            
            # 1. Planner: 决定下一步行动
            decision, cost = self._plan(pad)
            total_cost += cost
            
            if decision == "answer":
                # 检查是否有知识（强制 grounding）
                if not pad.knowledge.strip():
                    # 强制搜索一次
                    results = self.searcher.search(question)
                    total_cost += self.search_cost
                    pad.append_history(f"search[{pad.iteration_count}]: {question} (forced)")
                    cost = self._synthesize(pad, question, results)
                    total_cost += cost
                    continue
                
                # 生成最终答案
                answer, cost = self._finalize(pad)
                total_cost += cost
                return AgentResult(
                    answer=answer,
                    cost=total_cost,
                    knowledge=pad.knowledge,
                    iterations=pad.iteration_count
                )
            
            elif decision.startswith("search:"):
                query = decision[7:].strip()
                results = self.searcher.search(query)
                total_cost += self.search_cost
                pad.append_history(f"search[{pad.iteration_count}]: {query}")
                cost = self._synthesize(pad, query, results)
                total_cost += cost
        
        # 达到最大迭代次数，尽力生成答案
        answer, cost = self._finalize(pad)
        total_cost += cost
        return AgentResult(
            answer=answer + "\n\n[Note: Max iterations reached]",
            cost=total_cost,
            knowledge=pad.knowledge,
            iterations=pad.iteration_count
        )
    
    def _plan(self, pad: Scratchpad) -> tuple:
        """Planner: 决定搜索还是回答"""
        user_prompt = self._build_planner_prompt(pad)
        
        if self.debug:
            print(f"[DEBUG] Planner prompt:\n{user_prompt}\n")
        
        resp = self.planner.generate(self.PLANNER_SYSTEM, user_prompt)
        raw = resp.text.strip().lower()
        
        if self.debug:
            print(f"[DEBUG] Planner response: {raw}\n")
        
        # 解析决策
        if "action: answer" in raw or raw.startswith("answer"):
            return "answer", resp.cost
        
        # 提取搜索查询
        match = re.search(r'query\s*[:\-]\s*(.+)', raw, re.IGNORECASE)
        if match:
            return f"search: {match.group(1).strip()}", resp.cost
        
        # 默认搜索
        if "search" in raw:
            # 尝试提取查询
            lines = raw.split('\n')
            for line in lines:
                if line.strip() and not line.lower().startswith("action"):
                    return f"search: {line.strip()}", resp.cost
        
        # 如果有知识就回答，否则搜索
        if pad.knowledge.strip():
            return "answer", resp.cost
        return f"search: {pad.original_question}", resp.cost
    
    def _synthesize(self, pad: Scratchpad, query: str, results: List[SearchResult]) -> float:
        """Synthesizer: 压缩搜索结果到知识"""
        user_prompt = self._build_synthesizer_prompt(pad, query, results)
        
        if self.debug:
            print(f"[DEBUG] Synthesizer prompt:\n{user_prompt[:500]}...\n")
        
        resp = self.synthesizer.generate(self.SYNTHESIZER_SYSTEM, user_prompt)
        pad.knowledge = resp.text.strip()
        pad.current_step = f"Last query: {query}"
        
        if self.debug:
            print(f"[DEBUG] Updated knowledge: {pad.knowledge[:200]}...\n")
        
        return resp.cost
    
    def _finalize(self, pad: Scratchpad) -> tuple:
        """Finalizer: 生成最终答案"""
        user_prompt = self._build_finalizer_prompt(pad)
        resp = self.finalizer.generate(self.FINALIZER_SYSTEM, user_prompt)
        return resp.text.strip(), resp.cost
    
    def _build_planner_prompt(self, pad: Scratchpad) -> str:
        """构建 Planner prompt"""
        lines = [
            "Review the scratchpad and choose an action.",
            "IMPORTANT: You must search for evidence before answering. Do NOT answer using internal knowledge.",
            "Output exactly:",
            "Action: Search",
            "Query: <your search query>",
            "",
            "Or if you have enough information:",
            "Action: Answer",
            "",
            "Scratchpad:",
            pad.snapshot()
        ]
        return "\n".join(lines)
    
    def _build_synthesizer_prompt(self, pad: Scratchpad, query: str, results: List[SearchResult]) -> str:
        """构建 Synthesizer prompt"""
        lines = [
            f"Question: {pad.original_question}",
            f"\nExisting Knowledge: {pad.knowledge or '(empty)'}",
            f"\nNew Search Query: {query}",
            "\nNew Search Results:"
        ]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.title} | {r.url} | {r.snippet}")
        lines.append("\nTask: Update the knowledge section with concise, relevant facts in PLAIN TEXT.")
        return "\n".join(lines)
    
    def _build_finalizer_prompt(self, pad: Scratchpad) -> str:
        """构建 Finalizer prompt"""
        return f"User Question: {pad.original_question}\n\nKnowledge: {pad.knowledge}\n\nWrite a direct answer."


# ============ CLI ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Local LLM Research Agent")
    parser.add_argument("question", help="Research question")
    parser.add_argument("--model", default="qwen3:4b", help="Ollama model name")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama host")
    parser.add_argument("--max-iter", type=int, default=5, help="Max iterations")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--knowledge", help="Prior knowledge from previous run")
    
    args = parser.parse_args()
    
    # 初始化 providers
    llm = OllamaProvider(model=args.model, host=args.host)
    searcher = DuckDuckGoProvider()
    
    # 创建 agent
    agent = LocalLLMAgent(
        planner=llm,
        synthesizer=llm,
        searcher=searcher,
        max_iterations=args.max_iter,
        debug=args.debug
    )
    
    print(f"🔍 Researching: {args.question}\n")
    start = time.time()
    
    result = agent.research(args.question, prior_knowledge=args.knowledge or "")
    
    elapsed = time.time() - start
    
    print(f"\n{'='*50}")
    print(f"📊 Answer (after {result.iterations} iterations, {elapsed:.1f}s):")
    print(f"{'='*50}")
    print(result.answer)
    print(f"\n💰 Cost: ${result.cost:.4f}")
    print(f"📝 Knowledge:\n{result.knowledge[:500]}...")


if __name__ == "__main__":
    main()
