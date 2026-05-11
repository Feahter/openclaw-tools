# OpenClaw Architecture Patterns — feZ 本地定制

> 用于 Native SVG 引擎的快速触发模板。

---

## Pattern 1: OpenClaw Agent Architecture（Style 6 · Claude Official）

触发词：OpenClaw 架构 / OpenClaw Agent / 龙虾架构

```json
{"style":6,"title":"OpenClaw Agent Architecture","subtitle":"AI Agent System — Multi-Agent Orchestration",
 "nodes":[
  {"id":"user","kind":"user_avatar","x":60,"y":220,"width":160,"height":80,"label":"User","sublabel":"Human operator","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"gateway","kind":"hexagon","x":280,"y":100,"width":200,"height":70,"label":"Gateway","sublabel":"Channel routing · Auth","type_label":"INTERFACE","fill":"#fffcf7","stroke":"#ded0c3"},
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

## Pattern 2: OpenClaw Dual-Gateway（Style 6 · feZ 定制）

触发词：双 Gateway / 飞书通道 / WeChat 通道

feZ 本地双 Gateway 架构：QClaw Gateway (28789) + npm Gateway (18789)

```json
{"style":6,"title":"OpenClaw Dual-Gateway Architecture","subtitle":"feZ Local Setup — QClaw + npm 双通道",
 "nodes":[
  {"id":"wechat_user","kind":"user_avatar","x":30,"y":80,"width":140,"height":70,"label":"WeChat","sublabel":"用户","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"feishu_user","kind":"user_avatar","x":30,"y":400,"width":140,"height":70,"label":"Feishu","sublabel":"用户","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"qclaw_gw","kind":"hexagon","x":220,"y":60,"width":180,"height":100,"label":"QClaw Gateway","sublabel":"Port 28789 · QClaw Helper · PID 22005","type_label":"INTERFACE","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"npm_gw","kind":"hexagon","x":220,"y":380,"width":180,"height":100,"label":"npm Gateway","sublabel":"Port 18789 · LaunchAgent · PID 22647","type_label":"INTERFACE","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"agent_core","kind":"rect","x":460,"y":210,"width":200,"height":90,"label":"Agent Core","sublabel":"MiniMax-M2.7 · Memory · Skills","type_label":"CORE","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"skills","kind":"rect","x":460,"y":480,"width":200,"height":70,"label":"Skills System","sublabel":"180+ Skills · Tool · Workflow","type_label":"EXTENSION","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"memory","kind":"cylinder","x":720,"y":210,"width":160,"height":110,"label":"Memory","sublabel":"Session · Daily · Long-term","type_label":"STORAGE","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"tools","kind":"rect","x":720,"y":480,"width":160,"height":70,"label":"Tool Runtime","sublabel":"MCP · Functions","type_label":"EXECUTION","fill":"#fffcf7","stroke":"#ded0c3"}
 ],
 "arrows":[
  {"source":"wechat_user","target":"qclaw_gw","label":"消息","flow":"control"},
  {"source":"feishu_user","target":"npm_gw","label":"消息","flow":"control"},
  {"source":"qclaw_gw","target":"agent_core","label":"Route","flow":"control"},
  {"source":"npm_gw","target":"agent_core","label":"Route","flow":"control"},
  {"source":"agent_core","target":"memory","label":"Read","flow":"read"},
  {"source":"agent_core","target":"skills","label":"Delegate","flow":"control"},
  {"source":"agent_core","target":"tools","label":"Invoke","flow":"control"},
  {"source":"memory","target":"agent_core","label":"Context","flow":"write"},
  {"source":"skills","target":"agent_core","label":"Result","flow":"feedback"},
  {"source":"tools","target":"agent_core","label":"Result","flow":"feedback"}
 ],
 "legend":[{"flow":"control","label":"Control"},{"flow":"read","label":"Read"},{"flow":"write","label":"Write"},{"flow":"feedback","label":"Feedback"}],
 "legend_position":"bottom-right"}
```

---

## Pattern 3: Skill System Architecture（Style 5 · Glass）

触发词：Skill 系统 / Skills 架构 / OpenClaw skill 生态

```json
{"style":5,"title":"OpenClaw Skills Ecosystem","subtitle":"Hub + Specialist + Memory 三层架构",
 "nodes":[
  {"id":"user","kind":"user_avatar","x":40,"y":300,"width":140,"height":70,"label":"User","sublabel":"Human","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"orchestrator","kind":"hexagon","x":240,"y":280,"width":180,"height":80,"label":"Skill Orchestrator","sublabel":"Hub · Matcher · Router","type_label":"HUB","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"feishu","kind":"rect","x":480,"y":100,"width":140,"height":65,"label":"Feishu","sublabel":"飞书集成","type_label":"INTEGRATION","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"coding","kind":"rect","x":480,"y":190,"width":140,"height":65,"label":"Coding Agent","sublabel":"代码生成","type_label":"TOOL","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"llm_wiki","kind":"rect","x":480,"y":280,"width":140,"height":65,"label":"LLM Wiki","sublabel":"知识库","type_label":"KNOWLEDGE","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"bazi","kind":"rect","x":480,"y":370,"width":140,"height":65,"label":"Bazi Graph","sublabel":"八字命理","type_label":"KNOWLEDGE","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"memory","kind":"cylinder","x":700,"y":180,"width":160,"height":100,"label":"Memory","sublabel":"Session · Daily · Skill","type_label":"STORAGE","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"tools","kind":"rect","x":700,"y":370,"width":160,"height":65,"label":"Tool Runtime","sublabel":"MCP · Functions","type_label":"EXECUTION","fill":"#fffcf7","stroke":"#ded0c3"}
 ],
 "arrows":[
  {"source":"user","target":"orchestrator","label":"Intent","flow":"control"},
  {"source":"orchestrator","target":"feishu","label":"delegate","flow":"control"},
  {"source":"orchestrator","target":"coding","label":"delegate","flow":"control"},
  {"source":"orchestrator","target":"llm_wiki","label":"delegate","flow":"control"},
  {"source":"orchestrator","target":"bazi","label":"delegate","flow":"control"},
  {"source":"feishu","target":"orchestrator","label":"Result","flow":"feedback"},
  {"source":"coding","target":"orchestrator","label":"Result","flow":"feedback"},
  {"source":"llm_wiki","target":"orchestrator","label":"Result","flow":"feedback"},
  {"source":"bazi","target":"orchestrator","label":"Result","flow":"feedback"},
  {"source":"orchestrator","target":"memory","label":"Context","flow":"read"},
  {"source":"orchestrator","target":"tools","label":"Invoke","flow":"control"}
 ],
 "legend":[{"flow":"control","label":"Delegation"},{"flow":"feedback","label":"Result"},{"flow":"read","label":"Context read"}],
 "legend_position":"bottom-right"}
```

---

## Pattern 4: OpenClaw Memory Architecture（Style 3 · Blueprint）

触发词：OpenClaw Memory / 记忆系统 / Session + Memory

```json
{"style":3,"title":"OpenClaw Memory Architecture","subtitle":"四层记忆体系 + Skill 上下文",
 "nodes":[
  {"id":"input","kind":"user_avatar","x":40,"y":200,"width":120,"height":70,"label":"User Input","sublabel":"消息/命令","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"session_mgr","kind":"rect","x":220,"y":180,"width":180,"height":80,"label":"Session Manager","sublabel":"上下文窗口 · 对话状态","type_label":"MANAGER","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"session","kind":"rect","x":460,"y":80,"width":160,"height":70,"label":"Session Memory","sublabel":"memory/YYYY-MM-DD.md","type_label":"TIER-1","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"daily","kind":"rect","x":460,"y":180,"width":160,"height":70,"label":"Daily Memory","sublabel":"当日工作日志","type_label":"TIER-2","fill":"#fff2cc","stroke":"#d6b656"},
  {"id":"longterm","kind":"cylinder","x":460,"y":280,"width":160,"height":90,"label":"Long-term Memory","sublabel":"MEMORY.md 精选知识","type_label":"TIER-3","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"skill_ctx","kind":"rect","x":460,"y":400,"width":160,"height":70,"label":"Skill Context","sublabel":"memory/skills/{name}/context.md","type_label":"TIER-4","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"context_builder","kind":"rect","x":700,"y":200,"width":180,"height":80,"label":"Context Builder","sublabel":"优先级检索 ·  Ranking","type_label":"OUTPUT","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"agent","kind":"rect","x":920,"y":200,"width":140,"height":70,"label":"Agent Core","sublabel":"LLM 推理","type_label":"CORE","fill":"#e8f5e3","stroke":"#7b8b5c"}
 ],
 "arrows":[
  {"source":"input","target":"session_mgr","label":"消息","flow":"control"},
  {"source":"session_mgr","target":"session","label":"Session","flow":"read"},
  {"source":"session_mgr","target":"daily","label":"Daily","flow":"read"},
  {"source":"session_mgr","target":"longterm","label":"Long-term","flow":"read"},
  {"source":"session_mgr","target":"skill_ctx","label":"Skill","flow":"read"},
  {"source":"session","target":"context_builder","label":"Context","flow":"write"},
  {"source":"daily","target":"context_builder","label":"Context","flow":"write"},
  {"source":"longterm","target":"context_builder","label":"Context","flow":"write"},
  {"source":"skill_ctx","target":"context_builder","label":"Context","flow":"write"},
  {"source":"context_builder","target":"agent","label":"Context","flow":"write"}
 ],
 "legend":[{"flow":"control","label":"Input"},{"flow":"read","label":"Memory read"},{"flow":"write","label":"Context write"}],
 "legend_position":"bottom-right"}
```

---

## Pattern 5: OpenClaw Tool Call Flow（Style 2 · Dark Terminal）

触发词：OpenClaw Tool / MCP / 工具调用

```json
{"style":2,"title":"OpenClaw Tool Call Flow","subtitle":"LLM → Tool → LLM 循环",
 "nodes":[
  {"id":"user","kind":"user_avatar","x":40,"y":200,"width":120,"height":70,"label":"User","sublabel":"Query","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"llm","kind":"rect","x":220,"y":190,"width":160,"height":80,"label":"LLM (MiniMax-M2.7)","sublabel":"推理 + 工具决策","type_label":"CORE","fill":"#1e293b","stroke":"#38bdf8"},
  {"id":"selector","kind":"rect","x":440,"y":190,"width":150,"height":70,"label":"Tool Selector","sublabel":"路由到 MCP Server","type_label":"SELECTOR","fill":"#1e293b","stroke":"#a78bfa"},
  {"id":"mcp_feishu","kind":"rect","x":660,"y":80,"width":140,"height":65,"label":"Feishu MCP","sublabel":"飞书 API","type_label":"MCP","fill":"#1e293b","stroke":"#34d399"},
  {"id":"mcp_browser","kind":"rect","x":660,"y":190,"width":140,"height":65,"label":"Browser CDP","sublabel":"bb-browser","type_label":"MCP","fill":"#1e293b","stroke":"#34d399"},
  {"id":"mcp_files","kind":"rect","x":660,"y":300,"width":140,"height":65,"label":"File System","sublabel":"read/write/exec","type_label":"MCP","fill":"#1e293b","stroke":"#34d399"},
  {"id":"result","kind":"rect","x":860,"y":190,"width":140,"height":70,"label":"Result Parser","sublabel":"结构化结果 → LLM","type_label":"OUTPUT","fill":"#1e293b","stroke":"#f59e0b"},
  {"id":"output","kind":"rect","x":1050,"y":190,"width":120,"height":60,"label":"Response","sublabel":"最终回复","type_label":"FINAL","fill":"#1e293b","stroke":"#ded0c3"}
 ],
 "arrows":[
  {"source":"user","target":"llm","label":"Query","flow":"control"},
  {"source":"llm","target":"selector","label":"Tool call JSON","flow":"control"},
  {"source":"selector","target":"mcp_feishu","label":"Invoke","flow":"control"},
  {"source":"selector","target":"mcp_browser","label":"Invoke","flow":"control"},
  {"source":"selector","target":"mcp_files","label":"Invoke","flow":"control"},
  {"source":"mcp_feishu","target":"result","label":"Result","flow":"feedback"},
  {"source":"mcp_browser","target":"result","label":"Result","flow":"feedback"},
  {"source":"mcp_files","target":"result","label":"Result","flow":"feedback"},
  {"source":"result","target":"llm","label":"Context","flow":"write"},
  {"source":"llm","target":"output","label":"Respond","flow":"data"}
 ],
 "legend":[{"flow":"control","label":"Control"},{"flow":"feedback","label":"Result"},{"flow":"write","label":"Context write"},{"flow":"data","label":"Output"}],
 "legend_position":"bottom-right"}
```

---

## Pattern 6: OpenClaw 定制化差异图（Style 6 · 官方 vs feZ 定制）

触发词：OpenClaw 差异 / 定制点 / vs 官方

灰色节点 = 官方默认，绿色/橙色节点 = feZ 定制差异点

```json
{"style":6,"title":"OpenClaw 定制化差异图","subtitle":"灰色=官方默认 · 绿色/橙色=feZ定制节点",
 "nodes":[
  {"id":"stock","kind":"rect","x":30,"y":100,"width":160,"height":60,"label":"官方默认","sublabel":"单Gateway · 默认模型","type_label":"STOCK","fill":"#f5f5f5","stroke":"#999999"},
  {"id":"custom","kind":"rect","x":30,"y":400,"width":160,"height":60,"label":"feZ 定制","sublabel":"双Gateway · MiniMax","type_label":"CUSTOM","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"gw_stock","kind":"hexagon","x":240,"y":100,"width":140,"height":60,"label":"Gateway (单一)","sublabel":"单端口","type_label":"STOCK","fill":"#f5f5f5","stroke":"#999999"},
  {"id":"gw_qclaw","kind":"hexagon","x":240,"y":380,"width":140,"height":60,"label":"QClaw Gateway","sublabel":"Port 28789 · PID 22005","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"gw_npm","kind":"hexagon","x":240,"y":460,"width":140,"height":60,"label":"npm Gateway","sublabel":"Port 18789 · PID 22647","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"model_stock","kind":"rect","x":240,"y":200,"width":140,"height":55,"label":"默认模型","sublabel":"OpenAI/Claude","type_label":"STOCK","fill":"#f5f5f5","stroke":"#999999"},
  {"id":"model_minimax","kind":"rect","x":240,"y":560,"width":140,"height":55,"label":"MiniMax-M2.7","sublabel":"主模型 · M2.5/M2.1 兜底","type_label":"DIFF","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"ch_wechat","kind":"rect","x":440,"y":380,"width":120,"height":60,"label":"WeChat","sublabel":"QClaw Helper","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"ch_feishu","kind":"rect","x":440,"y":460,"width":120,"height":60,"label":"Feishu","sublabel":"tenant_access_token","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"ch_stock","kind":"rect","x":440,"y":100,"width":120,"height":55,"label":"默认 Channel","sublabel":"单一通道","type_label":"STOCK","fill":"#f5f5f5","stroke":"#999999"},
  {"id":"cron_stock","kind":"rect","x":440,"y":200,"width":120,"height":55,"label":"Cron (默认)","sublabel":"5 分钟间隔","type_label":"STOCK","fill":"#f5f5f5","stroke":"#999999"},
  {"id":"cron_custom","kind":"rect","x":440,"y":560,"width":120,"height":55,"label":"Cron (定制)","sublabel":"60 分钟间隔","type_label":"DIFF","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"agent_core","kind":"rect","x":620,"y":260,"width":180,"height":80,"label":"Agent Core","sublabel":"Skills 180+ · MCP","type_label":"CORE","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"memory","kind":"cylinder","x":620,"y":440,"width":140,"height":100,"label":"Memory","sublabel":"Session · Daily · Long-term","type_label":"STORAGE","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"health","kind":"rect","x":860,"y":260,"width":140,"height":55,"label":"Health Monitor","sublabel":"reply_rate <50% 告警","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"builderpulse","kind":"rect","x":860,"y":340,"width":140,"height":55,"label":"BuilderPulse","sublabel":"cron 推送飞书","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"cf_proxy","kind":"rect","x":860,"y":420,"width":140,"height":55,"label":"CF Proxy","sublabel":"墙内访问 GitHub/HF","type_label":"DIFF","fill":"#fce7d6","stroke":"#d97757"}
 ],
 "arrows":[
  {"source":"stock","target":"gw_stock","label":"默认","flow":"control"},
  {"source":"stock","target":"model_stock","label":"默认","flow":"control"},
  {"source":"stock","target":"ch_stock","label":"默认","flow":"control"},
  {"source":"stock","target":"cron_stock","label":"默认","flow":"control"},
  {"source":"custom","target":"gw_qclaw","label":"Diff","flow":"control"},
  {"source":"custom","target":"gw_npm","label":"Diff","flow":"control"},
  {"source":"custom","target":"model_minimax","label":"Diff","flow":"control"},
  {"source":"custom","target":"cron_custom","label":"Diff","flow":"control"},
  {"source":"gw_qclaw","target":"ch_wechat","label":"WeChat","flow":"control"},
  {"source":"gw_npm","target":"ch_feishu","label":"Feishu","flow":"control"},
  {"source":"ch_wechat","target":"agent_core","label":"消息","flow":"control"},
  {"source":"ch_feishu","target":"agent_core","label":"消息","flow":"control"},
  {"source":"model_minimax","target":"agent_core","label":"推理","flow":"control"},
  {"source":"agent_core","target":"memory","label":"Context","flow":"read"},
  {"source":"agent_core","target":"health","label":"监控","flow":"control"},
  {"source":"agent_core","target":"builderpulse","label":"推送","flow":"data"},
  {"source":"builderpulse","target":"ch_feishu","label":"飞书通知","flow":"data"},
  {"source":"agent_core","target":"cf_proxy","label":"GitHub/HF","flow":"control"}
 ],
 "legend":[{"flow":"control","label":"官方默认"},{"flow":"control","label":"feZ定制"},{"flow":"data","label":"数据流"}],
 "legend_position":"bottom-right"}
```
