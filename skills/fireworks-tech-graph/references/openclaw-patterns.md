# OpenClaw Architecture Patterns

> OpenClaw 专属图类型，基于实际系统架构总结。

---

## Pattern 1: OpenClaw Agent Architecture（Style 6）

**触发词**：OpenClaw 架构 / OpenClaw Agent / 龙虾架构

** Tested prompt（直接可用）**：
```
Draw OpenClaw Agent architecture diagram, Style 6 (Claude Official).

Use three layers with left-side labels:
- Interface Layer: Gateway (channel routing · auth)
- Core Layer: Agent Core (LLM · Memory · Skills System)
- Foundation Layer: Tool Runtime + Memory Store

Include: User → Gateway → Agent Core → [Skills / Memory / Tools] → Output.

Use warm cream background (#f8f6f3), teal-green for agent core,
warm beige for infrastructure, gray for storage.

Include semantic arrows: control (Gateway→Agent), read (Agent→Memory),
invoke (Agent→Tools), feedback (Tools/Skills→Agent).
```

** JSON（直接可执行）**：
```json
{"style":6,"title":"OpenClaw Agent Architecture","subtitle":"AI Agent System — Multi-Agent Orchestration",
 "nodes":[
  {"id":"user","kind":"user_avatar","x":60,"y":220,"width":160,"height":80,"label":"User","sublabel":"Human operator","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"gateway","kind":"rect","x":280,"y":100,"width":200,"height":70,"label":"Gateway","sublabel":"Channel routing · Auth","type_label":"INTERFACE","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"agent","kind":"rect","x":280,"y":220,"width":200,"height":80,"label":"Agent Core","sublabel":"LLM · Memory · Skills","type_label":"CORE","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"skills","kind":"rect","x":280,"y":360,"width":200,"height":70,"label":"Skills System","sublabel":"Tool · Workflow · Memory","type_label":"EXTENSION","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"memory","kind":"cylinder","x":540,"y":200,"width":160,"height":120,"label":"Memory","sublabel":"Context · Sessions","type_label":"STORAGE","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"tools","kind":"rect","x":540,"y":360,"width":160,"height":70,"label":"Tool Runtime","sublabel":"MCP · Functions","type_label":"EXECUTION","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"output","kind":"rect","x":760,"y":220,"width":160,"height":70,"label":"Output","sublabel":"Response · Action","type_label":"OUTPUT","fill":"#fffcf7","stroke":"#ded0c3"}
 ],
 "arrows":[
  {"source":"user","target":"gateway","label":"Request","flow":"control"},
  {"source":"gateway","target":"agent","label":"Route","flow":"control"},
  {"source":"gateway","target":"skills","label":"Skill trigger","flow":"control"},
  {"source":"agent","target":"memory","label":"Read","flow":"read"},
  {"source":"agent","target":"skills","label":"Delegate","flow":"control"},
  {"source":"agent","target":"tools","label":"Invoke","flow":"control"},
  {"source":"agent","target":"output","label":"Respond","flow":"data"},
  {"source":"memory","target":"agent","label":"Context","flow":"write"},
  {"source":"skills","target":"agent","label":"Result","flow":"feedback"},
  {"source":"tools","target":"agent","label":"Result","flow":"feedback"}
 ],
 "legend":[{"flow":"control","label":"Control flow"},{"flow":"read","label":"Memory read"},{"flow":"write","label":"Memory write"},{"flow":"feedback","label":"Result feedback"},{"flow":"data","label":"Data output"}],
 "legend_position":"bottom-right"}
```

---

## Pattern 2: OpenClaw Dual-Gateway（Style 6）

**触发词**：双 Gateway / 飞书通道 / WeChat 通道

**说明**：feZ 的双 Gateway 架构（QClaw 内置 28789 + npm 全局 18789）

```
Draw OpenClaw dual-gateway architecture, Style 6.

Two parallel gateway instances:
- QClaw Gateway (port 28789): WeChat channel via QClaw Helper
- npm Gateway (port 18789): Feishu channel via LaunchAgent

Both connect to the same Agent Core. Show:
User → WeChat → QClaw Gateway → Agent Core
User → Feishu → npm Gateway → Agent Core
Agent Core → Skills/Memory/Tools
Agent Core → WeChat Response / Feishu Response
```

---

## Pattern 3: Skill System Architecture（Style 5 Glass）

**触发词**：Skill 系统 / Skills 架构 / OpenClaw skill 生态

```
Draw OpenClaw Skills ecosystem, Style 5 (Glassmorphism).

Three layers:
1. Trigger Layer: User intent → Skill matcher
2. Skill Layer: Individual skills (feishu, coding-agent, llm-wiki, etc.)
3. Execution Layer: Tool runtime, memory, session manager

Show skill orchestration: skill-orchestrator as coordinator,
individual skills as specialists, memory as shared state.

Use frosted glass cards for each skill box.
Color code by domain: blue for integrations, green for tools,
purple for knowledge, orange for creative.
```

---

## Pattern 4: OpenClaw Memory Architecture（Style 3 Blueprint）

**触发词**：OpenClaw Memory / 记忆系统 / Session + Memory

```
Draw OpenClaw memory architecture, Style 3 (Blueprint).

Four memory tiers:
1. Session Memory (Working): current conversation context
2. Daily Memory: memory/YYYY-MM-DD.md files
3. Long-term Memory: MEMORY.md curated knowledge
4. Skill Memory: memory/skills/{skill}/context.md

Show the memory hierarchy:
Input → Session Manager → [Daily Memory / Long-term Memory / Skill Memory]
                          → Context Builder → Agent Core

Use blueprint style with cyan strokes, grid background.
Label each tier with its file path pattern.
```

---

## Pattern 5: OpenClaw Tool Call Flow（Style 2 Dark Terminal）

**触发词**：OpenClaw Tool / MCP / 工具调用

```
Draw OpenClaw tool call execution flow, Style 2 (Dark Terminal).

Flow: LLM decides → Tool Selector → MCP Server → Execution → Parser → LLM

Components:
- User query enters Agent Core
- LLM (MiniMax-M2.7) generates tool call JSON
- Tool Selector routes to correct MCP server
- Execution returns structured result
- Result Parser feeds back to LLM
- LLM generates final response

Use dark terminal style with neon accent arrows.
Monospace font. Show the loop: LLM → Tools → LLM (iterative).
```
