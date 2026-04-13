---
name: local-llm-agent
description: 本地 LLM 研究 Agent - 基于 laconic 架构的轻量级研究助手。在本地 Ollama 上运行，无需 API 费用，支持搜索→合成→回答的完整研究循环。触发：本地研究、ollama agent、离线研究、低成本 research agent、laconic python。
---

# Local LLM Agent - 本地研究助手

## 5秒上手

```bash
# 前提：Ollama 已安装并运行
ollama pull qwen3:4b

# 执行研究
python3 ~/.openclaw/workspace/skills/local-llm-agent/scripts/agent.py "2024年诺贝尔化学奖得主是谁"
```

## 概述

基于 [laconic](https://github.com/smhanov/laconic) 架构的 Python 实现，专为本地 LLM 优化：

- **上下文压缩**：不像普通 Agent 那样无限追加历史，而是每步压缩为结构化知识
- **强制 grounding**：所有事实必须来自搜索结果，不用内部知识幻觉
- **成本追踪**：精确计算 API 调用费用（本地模型为 $0）
- **知识传承**：支持 follow-up 问题，无需重新搜索

## 架构

```
User Question
    ↓
┌─────────────┐
│   Planner   │ ← 决定：搜索 / 回答
└──────┬──────┘
       ↓ (搜索)
┌─────────────┐
│   Searcher  │ ← DuckDuckGo / Brave
└──────┬──────┘
       ↓ (结果)
┌─────────────┐
│ Synthesizer │ ← 压缩为知识
└──────┬──────┘
       ↓ (循环或结束)
┌─────────────┐
│  Finalizer  │ ← 生成答案
└─────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
# 可选：duckduckgo-search 库（比命令行更快）
pip3 install duckduckgo-search

# 或安装 ddgr 命令行工具
brew install ddgr  # macOS
```

### 2. 启动 Ollama

```bash
ollama serve        # 后台运行
ollama pull qwen3:4b  # 或 qwen3:8b, llama3.2 等
```

### 3. 运行研究

```bash
python3 ~/.openclaw/workspace/skills/local-llm-agent/scripts/agent.py \
  "量子计算的最新进展"
```

## 高级用法

### 使用 Brave Search（更高质量）

编辑脚本，替换 searcher：

```python
from agent import BraveProvider

searcher = BraveProvider(api_key="your-brave-api-key")
```

### 使用 OpenRouter（云端模型 fallback）

```python
from agent import OpenRouterProvider

llm = OpenRouterProvider(
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"
)
```

### Follow-up 问题（知识传承）

```python
# 第一次研究
result1 = agent.research("2024诺贝尔化学奖得主")

# 后续问题，携带已有知识
result2 = agent.research(
    "他们获得了多少奖金",
    prior_knowledge=result1.knowledge
)
```

## 命令行参数

```
python3 agent.py [question] [options]

Options:
  --model TEXT       Ollama 模型名 (默认: qwen3:4b)
  --host TEXT        Ollama 地址 (默认: http://localhost:11434)
  --max-iter INT     最大迭代次数 (默认: 5)
  --debug            调试模式，显示完整 prompt
  --knowledge TEXT   前置知识（用于 follow-up）
```

## 性能对比

| 指标 | GPT-4 + 搜索 | Local LLM + laconic |
|------|-------------|---------------------|
| 单次成本 | $0.05-0.20 | $0.00 |
| 延迟 | 5-15s | 10-60s（取决于本地 GPU）|
| 隐私 | 数据出境 | 本地处理 |
| 可用性 | 需要 API key | 离线可用 |

## 模型推荐

| 模型 | 参数 | 显存需求 | 适合场景 |
|------|------|---------|---------|
| qwen3:4b | 4B | 3GB | 快速测试、简单问答 |
| qwen3:8b | 8B | 6GB | 平衡速度和质量 |
| qwen3:32b | 32B | 20GB | 复杂推理、高质量研究 |
| llama3.2 | 3B | 2GB | 超低资源环境 |

## 故障排查

### Ollama 连接失败

```bash
# 检查服务是否运行
curl http://localhost:11434/api/tags

# 手动启动
ollama serve
```

### 搜索无结果

```bash
# 检查网络连接
ping duckduckgo.com

# 使用 Brave 替代（需要 API key）
```

### 模型输出格式错误

- 较小模型（<4B）可能无法遵循指令格式
- 建议：使用 qwen3:4b 或更大模型

## 与 laconic 的差异

| 特性 | laconic (Go) | local-llm-agent (Python) |
|------|-------------|-------------------------|
| 语言 | Go | Python |
| 搜索 | DuckDuckGo, Brave, Tavily | DuckDuckGo, Brave |
| LLM | 任意（通过接口） | Ollama, OpenRouter |
| 策略 | Scratchpad, Graph Reader | Scratchpad |
| 依赖 | 纯标准库 | 可选外部库 |

## 扩展开发

### 添加新的 SearchProvider

```python
from agent import SearchProvider, SearchResult

class MySearcher(SearchProvider):
    def search(self, query: str) -> List[SearchResult]:
        # 实现搜索逻辑
        return [SearchResult(title="...", url="...", snippet="...")]
```

### 添加新的 LLMProvider

```python
from agent import LLMProvider, LLMResponse

class MyLLM(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        # 调用模型 API
        return LLMResponse(text="...", cost=0.0)
```

## 参考

- [laconic](https://github.com/smhanov/laconic) - 原版 Go 实现
- [llmhub](https://github.com/smhanov/llmhub) - 统一 LLM 客户端
- [HN 原文](https://news.ycombinator.com/item?id=47738094) - 架构灵感来源
