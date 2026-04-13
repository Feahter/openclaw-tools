#!/usr/bin/env python3
"""
Deep Research Agent - 融合卡兹克横纵分析法与 laconic 架构
"""

import argparse
import json
import os
import sys
import textwrap
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import subprocess
import urllib.request
import urllib.parse
import re
import tempfile

# ============================================================
# 数据结构
# ============================================================

@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    source_type: str = "unknown"  # official|media|academic|community|unknown
    access_time: str = ""

    def to_dict(self):
        return asdict(self)

@dataclass
class KnowledgeItem:
    """知识笔记本中的单个知识点"""
    topic: str
    source_url: str
    source_type: str
    access_time: str
    summary: str
    details: str
    credibility: str = "medium"  # high|medium|low

    def to_markdown(self) -> str:
        stars = {"high": "★★★★★", "medium": "★★★", "low": "★"}
        return textwrap.dedent(f"""\
        ### {self.topic}

        **来源**：[{self.source_url}]({self.source_url})（{self.access_time}）
        **来源质量**：{stars.get(self.credibility, '?')}
        
        **一句话概括**：{self.summary}
        
        **细节**：{self.details}
        """)

@dataclass
class KnowledgeNotebook:
    """知识笔记本 - 存储所有压缩后的知识"""
    vertical_knowledge: List[KnowledgeItem] = field(default_factory=list)
    horizontal_knowledge: List[KnowledgeItem] = field(default_factory=list)
    cross_knowledge: List[KnowledgeItem] = field(default_factory=list)

    def add(self, item: KnowledgeItem, category: str = "vertical"):
        if category == "vertical":
            self.vertical_knowledge.append(item)
        elif category == "horizontal":
            self.horizontal_knowledge.append(item)
        else:
            self.cross_knowledge.append(item)

    def to_markdown(self) -> str:
        sections = []
        if self.vertical_knowledge:
            sections.append("## 纵向知识\n")
            for k in self.vertical_knowledge:
                sections.append(k.to_markdown())
        if self.horizontal_knowledge:
            sections.append("\n## 横向知识\n")
            for k in self.horizontal_knowledge:
                sections.append(k.to_markdown())
        if self.cross_knowledge:
            sections.append("\n## 交汇知识\n")
            for k in self.cross_knowledge:
                sections.append(k.to_markdown())
        return "\n".join(sections)

    def to_json(self) -> str:
        return json.dumps({
            "vertical": [k.to_dict() for k in self.vertical_knowledge],
            "horizontal": [k.to_dict() for k in self.horizontal_knowledge],
            "cross": [k.to_dict() for k in self.cross_knowledge]
        }, ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "KnowledgeNotebook":
        data = json.loads(json_str)
        kb = KnowledgeNotebook()
        for k in data.get("vertical", []):
            kb.vertical_knowledge.append(KnowledgeItem(**k))
        for k in data.get("horizontal", []):
            kb.horizontal_knowledge.append(KnowledgeItem(**k))
        for k in data.get("cross", []):
            kb.cross_knowledge.append(KnowledgeItem(**k))
        return kb

@dataclass
class ResearchResult:
    """研究结果"""
    topic: str
    knowledge: KnowledgeNotebook
    markdown_report: str
    pdf_path: Optional[str] = None
    cost: float = 0.0
    iterations: int = 0

    def save_knowledge(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.knowledge.to_json())

    def save_markdown(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.markdown_report)

# ============================================================
# LLM Provider 接口
# ============================================================

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

    def get_cost(self) -> float:
        return 0.0

class OllamaProvider(LLMProvider):
    """Ollama 本地模型"""
    def __init__(self, model: str = "qwen3:4b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except Exception as e:
            return f"[Ollama Error: {e}]"

    def get_cost(self) -> float:
        return 0.0  # 本地模型成本为 0

# ============================================================
# Search Provider 接口
# ============================================================

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        pass

class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo 搜索"""
    def __init__(self):
        self.ddgr_available = self._check_ddgr()

    def _check_ddgr(self) -> bool:
        try:
            subprocess.run(["ddgr", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False

    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if self.ddgr_available:
            return self._search_ddgr(query, max_results)
        else:
            return self._search_ddg_html(query, max_results)

    def _search_ddgr(self, query: str, max_results: int) -> List[SearchResult]:
        try:
            cmd = ["ddgr", "--json", "-n", str(max_results), query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            results = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("abstract", ""),
                        source_type=self._classify_url(item.get("url", "")),
                        access_time=datetime.now().strftime("%Y-%m-%d")
                    ))
                except:
                    pass
            return results
        except Exception as e:
            return [SearchResult(title=f"Error: {e}", url="", snippet="")]

    def _search_ddg_html(self, query: str, max_results: int) -> List[SearchResult]:
        """简单的 HTML 解析方式（备选）"""
        url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            results = []
            # 简单正则提取（简化版）
            pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.DOTALL)
            for url, title, snippet in matches[:max_results]:
                snippet = re.sub(r'<[^>]+>', '', snippet)
                results.append(SearchResult(
                    title=title.strip(),
                    url=url,
                    snippet=snippet.strip(),
                    source_type=self._classify_url(url),
                    access_time=datetime.now().strftime("%Y-%m-%d")
                ))
            return results
        except Exception as e:
            return [SearchResult(title=f"Search Error: {e}", url="", snippet="")]

    def _classify_url(self, url: str) -> str:
        if not url:
            return "unknown"
        if any(x in url for x in ["github.com", "arxiv.org", "官方", "official"]):
            return "official"
        elif any(x in url for x in ["reddit.com", "twitter.com", "x.com", "zhihu.com"]):
            return "community"
        elif any(x in url for x in ["arxiv.org"]):
            return "academic"
        elif any(x in url for x in ["techcrunch.com", "theinformation.com", "verge.com"]):
            return "media"
        return "unknown"

# ============================================================
# 核心 Agent 组件
# ============================================================

class Planner:
    """Planner - 决定下一步行动：搜索 / 分析 / 回答"""

    SYSTEM_PROMPT = """你是一个研究助手。你的任务是决定下一步该做什么。

可选行动：
1. search - 需要更多搜索结果来回答问题
2. analyze - 有足够信息，可以开始分析了
3. answer - 有足够信息，可以直接给出答案

判断规则：
- 如果研究对象的基本信息（是什么、谁做的、什么时候诞生的）还不清楚 → search
- 如果需要了解竞品、横向对比信息 → search
- 如果纵向和横向的基本信息都已收集充分 → analyze
- 如果用户问题可以直接回答（简单事实型问题）→ answer

输出一行，格式：ACTION: search|analyze|answer
理由：[简短说明]
"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def decide(self, question: str, knowledge: KnowledgeNotebook) -> str:
        prompt = f"""研究问题：{question}

当前已收集的知识：
{self._summarize_knowledge(knowledge)}

请决定下一步行动。"""
        response = self.llm.generate(self.SYSTEM_PROMPT, prompt)
        # 解析响应
        for line in response.strip().split("\n"):
            if line.startswith("ACTION:"):
                action = line.split(":")[1].strip().lower()
                if action in ["search", "analyze", "answer"]:
                    return action
        return "search"  # 默认搜索

    def _summarize_knowledge(self, knowledge: KnowledgeNotebook) -> str:
        v_count = len(knowledge.vertical_knowledge)
        h_count = len(knowledge.horizontal_knowledge)
        c_count = len(knowledge.cross_knowledge)
        return f"纵向知识点：{v_count}个，横向知识点：{h_count}个，交汇知识点：{c_count}个"


class Synthesizer:
    """Synthesizer - 将搜索结果压缩为结构化知识"""

    SYSTEM_PROMPT = """你是一个知识压缩专家。你的任务是将搜索结果压缩为结构化的知识点。

来源优先级：
- ★★★★★ 官方一手：官方博客、GitHub Release、创始人推文、公司公告
- ★★★★ 权威媒体原创：TechCrunch、The Information 等原创报道
- ★★★★ 学术论文：arXiv、Google Scholar
- ★★★ 社区讨论：Reddit、GitHub Issues、知乎
- ★★ 聚合/转载：多数媒体转载版
- ★ 未知来源

输出格式（严格遵循）：
```
知识点：[主题标题，一句话]

来源：[URL]
来源质量：[高/中/低]
访问时间：[YYYY-MM-DD]

一句话概括：[用一句话说明这个知识点的核心内容]

细节：
[可供写作使用的具体信息，包括数据、引用、具体描述]
```

规则：
1. 每个搜索结果提炼为一个知识点
2. "一句话概括"要能直接用于报告
3. "细节"要包含可用于写作的具体信息
4. 来源质量根据来源优先级判断
5. 如果搜索结果质量太低（来源不明、内容模糊），跳过该结果
"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def synthesize(self, results: List[SearchResult], category: str = "vertical") -> List[KnowledgeItem]:
        if not results:
            return []

        # 构建搜索结果文本
        results_text = "\n\n".join([
            f"--- 搜索结果 {i+1} ---\n标题：{r.title}\nURL：{r.url}\n摘要：{r.snippet}"
            for i, r in enumerate(results) if r.url
        ])

        prompt = f"""请将以下搜索结果压缩为结构化知识点。

搜索结果：
{results_text}

类别：{"纵向（时间线/发展历程）" if category == "vertical" else "横向（竞品对比/当前状态）" if category == "horizontal" else "交汇（洞察/判断）"}

输出尽可能多的知识点，每个搜索结果一个知识点。"""
        
        response = self.llm.generate(self.SYSTEM_PROMPT, prompt)
        return self._parse_response(response, results)

    def _parse_response(self, response: str, results: List[SearchResult]) -> List[KnowledgeItem]:
        items = []
        current_item = {}
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("知识点："):
                if current_item and "topic" in current_item:
                    try:
                        items.append(KnowledgeItem(**current_item))
                    except:
                        pass
                current_item = {"topic": line[4:].strip()}
            elif line.startswith("来源："):
                current_item["source_url"] = line[3:].strip()
            elif line.startswith("来源质量："):
                cred = line[5:].strip()
                current_item["credibility"] = "high" if "高" in cred else "low" if "低" in cred else "medium"
            elif line.startswith("访问时间："):
                current_item["access_time"] = line[5:].strip()
            elif line.startswith("一句话概括："):
                current_item["summary"] = line[6:].strip()
            elif line.startswith("细节："):
                current_item["details"] = ""
            elif "details" in current_item and line and not line.startswith("---"):
                current_item["details"] += line + " "

        if current_item and "topic" in current_item:
            try:
                items.append(KnowledgeItem(**current_item))
            except:
                pass

        # 如果解析失败，尝试用原始结果
        if not items and results:
            for r in results:
                if r.url and r.snippet:
                    items.append(KnowledgeItem(
                        topic=r.title,
                        source_url=r.url,
                        source_type=r.source_type,
                        access_time=r.access_time or datetime.now().strftime("%Y-%m-%d"),
                        summary=r.snippet[:200],
                        details=r.snippet,
                        credibility="medium"
                    ))

        return items


class Analyzer:
    """Analyzer - 横纵分析"""

    SYSTEM_PROMPT = """你是一个深度研究分析师，使用"横纵分析法"对研究对象进行系统性分析。

横纵分析法包含两个维度：
1. 纵向分析（Diachronic）：沿时间轴还原发展全貌
   - 起源追溯：诞生背景、技术/理念/需求、创始人背景、行业环境
   - 诞生节点：首次发布时间、最早形态和定位
   - 演进历程：关键节点（版本更新、融资、团队变动、战略转向、危机）
   - 决策逻辑：每个节点的"为什么选A而不是B"、约束条件、锁定效应
   - 阶段划分：萌芽期、快速增长期、转型期等

2. 横向分析（Synchronic）：以当前时间点为切面与竞品对比
   - 竞品识别：根据纵向信息判断场景（A无竞品/B少竞品/C多竞品）
   - 核心差异对比：技术路线、商业模式、目标用户、优劣势
   - 用户口碑：社区评价、真实使用体验
   - 生态位分析：在整个赛道版图中的位置

3. 横纵交汇洞察：
   - 历史如何塑造了今天的竞争位置
   - 优势/劣势的历史根源
   - 未来推演：最可能的、最危险的、最乐观的三个剧本

写作风格：
- 叙事驱动，有故事弧线，不是流水账
- 句子时长时短，有节奏感
- 敢下判断，用"我的判断是"承认主观性
- 层层剥开：现象→表面解释→更深的追问→核心洞察
- 绝对禁区：赋能、抓手、首先...其次...最后、说白了、本质上

输出格式：完整的 Markdown 报告，包含：
1. 一句话定义
2. 纵向分析（完整的叙事故事）
3. 横向分析（竞品对比）
4. 横纵交汇洞察
5. 信息来源
"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def analyze(self, topic: str, knowledge: KnowledgeNotebook) -> str:
        knowledge_text = knowledge.to_markdown()
        
        prompt = f"""请使用横纵分析法对"{topic}"进行深度研究分析。

已收集的知识：
{knowledge_text}

请生成完整的 Markdown 研究报告。报告要：
1. 有叙事感和故事弧线，不是流水账
2. 敢下判断，每个判断有事实支撑
3. 纵向部分要讲清楚"为什么"
4. 横向部分要讲清楚"凭什么"
5. 交汇洞察要有新的判断，不是前面内容的缩写

字数要求：10000-30000字
"""
        return self.llm.generate(self.SYSTEM_PROMPT, prompt)


class Finalizer:
    """Finalizer - 生成最终报告"""

    SYSTEM_PROMPT = """你是一个报告格式化专家。你需要将研究报告优化为可读性更强的版本。

要求：
1. 确保结构清晰，有明确的小标题
2. 确保段落之间有过渡句
3. 确保开头有吸引力
4. 确保结尾有升华或回扣
5. 确保没有语法错误和事实矛盾

绝对禁止：
- 首先...其次...最后
- 综上所述
- 不难发现
- 值得注意的是
- 赋能、抓手、打通闭环
- 在当今AI快速发展的时代
"""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def finalize(self, report: str, topic: str) -> str:
        prompt = f"""请优化以下研究报告的写作质量。

研究主题：{topic}

原始报告：
{report}

请进行以下优化：
1. 检查并修正语法错误
2. 添加过渡句使段落更连贯
3. 优化开头使其更有吸引力
4. 检查结尾是否有升华
5. 确保没有触犯绝对禁区
"""
        return self.llm.generate(self.SYSTEM_PROMPT, prompt)


# ============================================================
# 主 Agent
# ============================================================

class DeepResearchAgent:
    """深度研究 Agent"""

    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        searcher: Optional[SearchProvider] = None,
        max_iterations: int = 5
    ):
        self.llm = llm or OllamaProvider()
        self.searcher = searcher or DuckDuckGoProvider()
        self.max_iterations = max_iterations
        
        self.planner = Planner(self.llm)
        self.synthesizer = Synthesizer(self.llm)
        self.analyzer = Analyzer(self.llm)
        self.finalizer = Finalizer(self.llm)
        
        self.total_cost = 0.0

    def research(self, topic: str, prior_knowledge: Optional[KnowledgeNotebook] = None) -> ResearchResult:
        """执行深度研究"""
        knowledge = prior_knowledge or KnowledgeNotebook()
        
        # 生成初始搜索查询
        search_queries = self._generate_search_queries(topic)
        
        # 收集信息循环
        for iteration in range(self.max_iterations):
            action = self.planner.decide(topic, knowledge)
            
            if action == "search":
                # 并行搜索纵向和横向信息
                new_knowledge = self._collect_information(topic, search_queries, knowledge)
                knowledge = self._merge_knowledge(knowledge, new_knowledge)
            elif action == "analyze":
                break
            else:
                break
        
        # 生成分析报告
        report = self.analyzer.analyze(topic, knowledge)
        final_report = self.finalizer.finalize(report, topic)
        
        return ResearchResult(
            topic=topic,
            knowledge=knowledge,
            markdown_report=final_report,
            cost=self.total_cost,
            iterations=iteration + 1
        )

    def _generate_search_queries(self, topic: str) -> Dict[str, List[str]]:
        """生成搜索查询"""
        prompt = f"""为研究"{topic}"生成搜索查询。

请生成以下类别的搜索查询：
1. 纵向（历史、起源、发展）：3-5个查询
2. 横向（竞品、对比、现状）：3-5个查询

输出格式：
```
纵向查询：
- 查询1
- 查询2
...

横向查询：
- 查询1
- 查询2
...
```"""
        
        response = self.llm.generate(
            "你是一个搜索策略专家，擅长生成有效的搜索查询。",
            prompt
        )
        
        # 简单解析
        vertical = []
        horizontal = []
        current_section = None
        
        for line in response.split("\n"):
            line = line.strip()
            if "纵向" in line:
                current_section = "vertical"
            elif "横向" in line:
                current_section = "horizontal"
            elif line.startswith("-"):
                query = line[1:].strip()
                if query:
                    if current_section == "vertical":
                        vertical.append(query)
                    elif current_section == "horizontal":
                        horizontal.append(query)
        
        # 默认查询（如果解析失败）
        if not vertical:
            vertical = [f"{topic} 发展历史", f"{topic} 创始人 背景", f"{topic} 诞生 起源"]
        if not horizontal:
            horizontal = [f"{topic} 竞品 对比", f"{topic} 评测 用户口碑", f"{topic} 市场 现状"]
        
        return {"vertical": vertical, "horizontal": horizontal}

    def _collect_information(
        self, 
        topic: str, 
        queries: Dict[str, List[str]], 
        knowledge: KnowledgeNotebook
    ) -> KnowledgeNotebook:
        """收集信息"""
        new_knowledge = KnowledgeNotebook()
        
        # 收集纵向信息
        for query in queries.get("vertical", []):
            results = self.searcher.search(query)
            items = self.synthesizer.synthesize(results, "vertical")
            for item in items:
                new_knowledge.add(item, "vertical")
        
        # 收集横向信息
        for query in queries.get("horizontal", []):
            results = self.searcher.search(query)
            items = self.synthesizer.synthesize(results, "horizontal")
            for item in items:
                new_knowledge.add(item, "horizontal")
        
        return new_knowledge

    def _merge_knowledge(
        self, 
        existing: KnowledgeNotebook, 
        new: KnowledgeNotebook
    ) -> KnowledgeNotebook:
        """合并知识（去重）"""
        merged = KnowledgeNotebook()
        
        # 合并纵向知识
        existing_urls = {k.source_url for k in existing.vertical_knowledge}
        for item in new.vertical_knowledge:
            if item.source_url not in existing_urls:
                merged.add(item, "vertical")
        for item in existing.vertical_knowledge:
            merged.add(item, "vertical")
        
        # 合并横向知识
        existing_urls = {k.source_url for k in existing.horizontal_knowledge}
        for item in new.horizontal_knowledge:
            if item.source_url not in existing_urls:
                merged.add(item, "horizontal")
        for item in existing.horizontal_knowledge:
            merged.add(item, "horizontal")
        
        return merged


# ============================================================
# PDF 转换
# ============================================================

def convert_to_pdf(markdown_path: str, output_path: str, title: str):
    """使用 md_to_pdf.py 转换"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(skill_dir, "scripts", "md_to_pdf.py")
    
    if os.path.exists(script_path):
        cmd = f"python3 {script_path} {markdown_path} {output_path} --title '{title}'"
        os.system(cmd)
    else:
        print(f"[Warning] md_to_pdf.py not found at {script_path}")
        print(f"[Info] Markdown saved at: {markdown_path}")


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Deep Research Agent")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("--output", "-o", help="输出 PDF 文件名")
    parser.add_argument("--format", "-f", choices=["pdf", "markdown", "json"], default="pdf", help="输出格式")
    parser.add_argument("--model", "-m", default="qwen3:4b", help="Ollama 模型")
    parser.add_argument("--max-iter", "-n", type=int, default=5, help="最大迭代次数")
    parser.add_argument("--knowledge", "-k", help="前置知识 JSON 文件")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 加载前置知识
    prior_knowledge = None
    if args.knowledge:
        try:
            with open(args.knowledge, "r", encoding="utf-8") as f:
                prior_knowledge = KnowledgeNotebook.from_json(f.read())
        except Exception as e:
            print(f"[Warning] Failed to load knowledge: {e}")
    
    # 创建 Agent
    agent = DeepResearchAgent(
        llm=OllamaProvider(model=args.model),
        max_iterations=args.max_iter
    )
    
    # 执行研究
    print(f"🔍 开始研究：{args.topic}")
    result = agent.research(args.topic, prior_knowledge)
    
    # 生成文件名
    safe_topic = re.sub(r'[^\w\s-]', '', args.topic).strip()[:30]
    timestamp = datetime.now().strftime("%Y%m%d")
    
    if args.format == "markdown":
        output_path = args.output or f"{safe_topic}_深度报告_{timestamp}.md"
        result.save_markdown(output_path)
        print(f"✅ Markdown 报告已保存：{output_path}")
    elif args.format == "json":
        output_path = args.output or f"{safe_topic}_知识笔记本_{timestamp}.json"
        result.save_knowledge(output_path)
        print(f"✅ 知识笔记本已保存：{output_path}")
    else:
        md_path = f"/tmp/{safe_topic}_报告_{timestamp}.md"
        result.save_markdown(md_path)
        
        output_path = args.output or f"{safe_topic}_深度报告_{timestamp}.pdf"
        convert_to_pdf(md_path, output_path, args.topic)
        print(f"✅ PDF 报告已保存：{output_path}")
    
    # 打印统计
    print(f"\n📊 统计：")
    print(f"  - 迭代次数：{result.iterations}")
    print(f"  - 纵向知识：{len(result.knowledge.vertical_knowledge)} 个")
    print(f"  - 横向知识：{len(result.knowledge.horizontal_knowledge)} 个")
    print(f"  - 成本：${result.cost:.4f}")

if __name__ == "__main__":
    main()
