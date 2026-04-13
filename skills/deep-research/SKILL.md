---
name: deep-research
description: |
  深度研究 Agent — 融合卡兹克横纵分析法与 laconic 架构的本地研究助手。
  
  触发词：深度研究、横纵分析、研究一下、帮我分析、调研一下、竞品分析、deep research。
  
  核心能力：
  - 双轴分析：纵轴（时间深度）+ 横轴（竞争广度）
  - laconic 架构：上下文压缩 + 知识传承 + 成本追踪
  - 强制 grounding：所有事实必须来自搜索结果
  - 输出：排版精美 PDF 研究报告
  
  对比普通 Agent：不是无限追加历史，而是结构化压缩知识 + 强制来源标注
  对比 hv-analysis：更轻量（本地运行 $0）+ 支持 follow-up + 知识传承
---

# Deep Research Agent

> 融合了：
> - **卡兹克横纵分析法**（hv-analysis）：历时-共时分析框架、来源优先级体系、可读性写作风格
> - **laconic 架构**：上下文压缩、Planner/Synthesizer/Finalizer 三组件、知识传承

## 5秒上手

```bash
# 前提：Ollama 已安装
ollama serve && ollama pull qwen3:4b

# 执行深度研究
python3 ~/.openclaw/workspace/skills/deep-research/scripts/agent.py \
  "Claude Code 深度研究" \
  --output claude_code_report.pdf
```

## 核心设计理念

**不是无限追加历史，而是结构化压缩知识。**

普通 Agent 的问题是：上下文无限膨胀，导致模型在冗余历史中迷失、推理成本爆炸、质量下降。

本 skill 的解决方案：
1. **每步压缩**：Synthesizer 将搜索结果压缩为结构化知识，丢弃原始冗余
2. **强制 grounding**：每个知识点必须标注来源，不允许内部幻觉
3. **双轴分析框架**：保证研究有结构、有深度、有可读性
4. **知识传承**：follow-up 问题复用已有知识，无需重新搜索

## 架构

```
User Question
    ↓
┌─────────────────────────────────────────────┐
│                  Planner                      │
│  决定：搜索 / 分析 / 回答                     │
└──────┬──────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────┐
│              Searcher (可选)                  │
│  DuckDuckGo / Brave / arxiv                 │
└──────┬──────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────┐
│           Synthesizer                        │
│  压缩为结构化知识 + 来源标注                  │
│  知识存入 KnowledgeNotebook                  │
└──────┬──────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────┐
│              Analyzer                        │
│  横纵分析：纵向叙事 + 横向对比 + 交汇洞察     │
└──────┬──────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────┐
│             Finalizer                        │
│  生成可读报告 + PDF 导出                      │
└─────────────────────────────────────────────┘
```

## 知识笔记本格式

每次搜索结果压缩后存入 KnowledgeNotebook，格式：

```markdown
## 知识点：[主题]

**来源**：[URL]（访问时间）
**核心内容**：一句话概括
**细节**：[具体信息，可用于写作]
**可信度**：高/中/低（根据来源质量）
```

**来源优先级**（Synthesizer 必须遵循）：
| 类型 | 优先级 | 示例 |
|------|--------|------|
| 官方一手 | ★★★★★ | 官方博客、GitHub Release、创始人推文 |
| 权威媒体原创 | ★★★★ | TechCrunch 原创、The Information |
| 学术论文 | ★★★★ | arXiv、Google Scholar |
| 社区讨论 | ★★★ | Reddit、GitHub Issues、知乎 |
| 聚合/转载 | ★★ | 多数媒体转载版 |
| 未知来源 | ★ | 无法验证的博客 |

---

## 横纵分析法模块

### 纵向分析（Diachronic）

沿时间轴还原研究对象从诞生到现在的发展全貌。

**必须覆盖**：
1. **起源**：诞生的背景、技术/理念/需求、创始人背景、当时的行业环境
2. **诞生节点**：首次发布/成立时间、最早的形态和定位
3. **演进历程**：按时间顺序梳理所有关键节点（版本更新、融资、团队变动、战略转向、危机）
4. **决策逻辑**：每个关键节点的「为什么选A而不是B」、约束条件、锁定效应
5. **阶段划分**：萌芽期、快速增长期、转型期等，每个阶段有核心特征和核心矛盾

### 横向分析（Synchronic）

以当前时间点为切面，与竞品进行全面对比。

**竞品场景判断**：
- **场景A（无竞品）**：分析为什么没有竞品、未来从哪冒出竞争者
- **场景B（1-2个竞品）**：逐一深入对比
- **场景C（3+竞品）**：选取3-5个代表性竞品深入分析，其余简要提及

**对比维度**：
- 核心差异：技术路线、商业模式、目标用户、核心优势与短板
- 用户口碑：社区评价、真实使用体验
- 生态位：在整个赛道版图中的位置

### 横纵交汇洞察

把纵向和横向结合起来，给出新判断：

1. **历史如何塑造了今天的竞争位置**
2. **优势的历史根源**：追溯到哪个节点/决策
3. **劣势的历史根源**：当初的「好决策」是否变成了包袱
4. **未来推演**：最可能的、最危险的、最乐观的三个剧本

---

## 写作风格

借鉴卡兹克文风，让研究报告可读。

### 可用元素
- **节奏感**：句子时长时短，段落跳跃自然，一句话自成一段
- **叙事驱动**：有故事弧线，不写流水账
- **知识自然带出**：在讲述过程中自然引出背景知识
- **敢下判断**：用「我的判断是」承认主观性，每个判断有事实支撑
- **层层剥开**：现象→表面解释→更深的追问→核心洞察
- **回环呼应**：开头埋的钩子在结尾 callback

### 绝对禁区
```
❌ 套话：首先...其次...最后、综上所述、值得注意的是
❌ 空洞形容词：赋能、抓手、打通闭环
❌ 教科书开头：在当今AI快速发展的时代...
❌ 高频踩雷词：说白了、意味着什么？、本质上...
❌ 空泛工具名：不说"AI工具"，要说具体名字
❌ 编造：搜不到的信息诚实标注「暂缺」，绝不编造
```

---

## 命令行接口

```bash
python3 scripts/agent.py "研究对象" [options]

Options:
  --output FILE          输出 PDF 文件名（默认：研究对象_深度报告.pdf）
  --format TYPE          输出格式：pdf / markdown / json（默认：pdf）
  --max-iter N           最大搜索迭代次数（默认：5）
  --model MODEL          Ollama 模型名（默认：qwen3:4b）
  --knowledge JSON       前置知识（用于 follow-up，可从上一次输出获取）
  --sources-only        只收集信息，不生成报告（用于快速调研）
  --debug               调试模式，显示中间状态

# 示例
python3 scripts/agent.py "Claude Code"
python3 scripts/agent.py "Claude Code" --output report.pdf --format pdf
python3 scripts/agent.py "它支持 Windows 吗" --knowledge "$(cat last_knowledge.json)"
```

## Follow-up 用法

```python
# 第一次研究
result = agent.research("Claude Code 深度研究")
print(result.knowledge)  # 知识笔记本（用于下次 follow-up）
print(result.pdf_path)    # PDF 路径

# 后续问题（携带已有知识，无需重新搜索）
result2 = agent.research(
    "它的定价策略是什么",
    prior_knowledge=result.knowledge
)
```

---

## PDF 输出

使用内置的 md_to_pdf.py（来自 hv-analysis）生成排版精美的 PDF。

```bash
# 自动调用
python3 scripts/agent.py "Claude Code" --output report.pdf
```

**排版规范**：
- A4 页面，页边距上25mm/左右20mm/下20mm
- 封面页：标题（28pt深蓝）+ 副标题 + 作者信息
- 配色：H1=#1a5276深蓝、H2=#1e8449绿、H3=#2e86c1浅蓝
- 正文：10.5pt，行距1.75，两端对齐
- 引用块：左侧3pt竖线 + 浅灰背景
- 表格：斑马纹，深蓝表头

---

## 与 hv-analysis 的区别

| 维度 | hv-analysis | deep-research（本 skill） |
|------|-------------|--------------------------|
| **运行方式** | 子Agent并行搜索（云端模型） | 本地 Ollama（$0成本） |
| **上下文** | 每次重新搜索 | 知识传承，follow-up 不重复搜索 |
| **架构** | 多子Agent协作 | Planner/Synthesizer/Analyzer/Finalizer 单体 |
| **报告生成** | 直接生成 | 先压缩知识，再生成（质量更稳定） |
| **成本** | API 费用 | $0（本地模型） |
| **离线可用** | 否 | 是（搜索除外） |

---

## 与 local-llm-agent 的区别

| 维度 | local-llm-agent | deep-research（本 skill） |
|------|-----------------|--------------------------|
| **分析框架** | 无（直接回答） | 横纵分析法（结构化） |
| **报告输出** | JSON 结构化答案 | 可读性 PDF 报告 |
| **写作风格** | 无 | 卡兹克风格（可读性强） |
| **来源标注** | 简单 | 严格来源优先级体系 |
| **适用场景** | 快速问答 | 深度研究（1-3万字） |

---

## 依赖

```bash
# 核心依赖
pip3 install duckduckgo-search  # 搜索（可选 ddgr 命令行）

# PDF 输出
pip3 install weasyprint markdown

# Ollama（必须）
# 安装：https://ollama.com
# 模型：ollama pull qwen3:4b
```

## 扩展开发

### 添加搜索 Provider

```python
from agent import SearchProvider, SearchResult

class MySearcher(SearchProvider):
    def search(self, query: str) -> List[SearchResult]:
        # 实现搜索逻辑
        return [SearchResult(
            title="...",
            url="...",
            snippet="...",
            source_type="official|media|academic|community",
            access_time=datetime.now().isoformat()
        )]
```

### 添加 LLM Provider

```python
from agent import LLMProvider, LLMResponse

class MyLLM(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        # 调用模型 API
        return LLMResponse(
            text="...",
            cost=0.0,
            tokens_used=0
        )
```

---

## 参考

- [khazix-skills/hv-analysis](https://github.com/KKKKhazix/khazix-skills) - 横纵分析法
- [laconic](https://github.com/smhanov/laconic) - laconic 研究架构
- [llmhub](https://github.com/smhanov/llmhub) - 统一 LLM 客户端
