# Native SVG Recipes — 各图类型最小可用 JSON 模板

> 配合 `references/style-guides/index.md` 使用。先选 type，再选 style，抄模板。

---

## Agent Architecture（Style 6 Claude Official）

```json
{"style":6,"title":"Title","subtitle":"Subtitle",
 "nodes":[
  {"id":"user","kind":"user_avatar","x":60,"y":220,"width":160,"height":80,"label":"User","sublabel":"Human","type_label":"INPUT","fill":"#fce7d6","stroke":"#d97757"},
  {"id":"gateway","kind":"hexagon","x":280,"y":100,"width":180,"height":60,"label":"Gateway","sublabel":"Channel routing","type_label":"INTERFACE","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"agent","kind":"rect","x":280,"y":220,"width":180,"height":80,"label":"Agent Core","sublabel":"LLM · Memory · Tools","type_label":"CORE","fill":"#e8f5e3","stroke":"#7b8b5c"},
  {"id":"skills","kind":"rect","x":280,"y":360,"width":180,"height":60,"label":"Skills","sublabel":"Tool · Workflow","type_label":"EXTENSION","fill":"#e8f0fc","stroke":"#8c6f5a"},
  {"id":"memory","kind":"cylinder","x":540,"y":200,"width":140,"height":120,"label":"Memory","sublabel":"Context · Sessions","type_label":"STORAGE","fill":"#f4e4c1","stroke":"#d97757"},
  {"id":"tools","kind":"rect","x":540,"y":360,"width":140,"height":60,"label":"Tool Runtime","sublabel":"MCP · Functions","type_label":"EXECUTION","fill":"#fffcf7","stroke":"#ded0c3"},
  {"id":"output","kind":"rect","x":760,"y":220,"width":140,"height":70,"label":"Output","sublabel":"Response","type_label":"OUTPUT","fill":"#fffcf7","stroke":"#ded0c3"}
 ],
 "arrows":[
  {"source":"user","target":"gateway","label":"Request","flow":"control"},
  {"source":"gateway","target":"agent","label":"Route","flow":"control"},
  {"source":"agent","target":"memory","label":"Read","flow":"read"},
  {"source":"agent","target":"skills","label":"Delegate","flow":"control"},
  {"source":"agent","target":"tools","label":"Invoke","flow":"control"},
  {"source":"agent","target":"output","label":"Respond","flow":"data"},
  {"source":"memory","target":"agent","label":"Context","flow":"write"},
  {"source":"skills","target":"agent","label":"Result","flow":"feedback"},
  {"source":"tools","target":"agent","label":"Result","flow":"feedback"}
 ],
 "legend":[{"flow":"control","label":"Control"},{"flow":"read","label":"Read"},{"flow":"write","label":"Write"},{"flow":"feedback","label":"Result"},{"flow":"data","label":"Data"}],
 "legend_position":"bottom-right"}
```

---

## Architecture — Style 3 Blueprint

```json
{"style":3,"title":"System Architecture","subtitle":"Microservices Platform",
 "containers":[
  {"label":"01 // EDGE","x":40,"y":80,"width":880,"height":100,"header_prefix":"01","header_text":"EDGE LAYER"},
  {"label":"02 // APPLICATION","x":40,"y":200,"width":880,"height":160,"header_prefix":"02","header_text":"APPLICATION SERVICES"},
  {"label":"03 // DATA","x":40,"y":380,"width":880,"height":120,"header_prefix":"03","header_text":"DATA + EVENT INFRA"}
 ],
 "nodes":[
  {"id":"client","kind":"rect","x":80,"y":100,"width":120,"height":50,"label":"Client Apps"},
  {"id":"gateway","kind":"rect","x":260,"y":100,"width":140,"height":50,"label":"API Gateway"},
  {"id":"auth","kind":"rect","x":440,"y":100,"width":120,"height":50,"label":"Auth / Policy"},
  {"id":"svc1","kind":"rect","x":100,"y":250,"width":140,"height":60,"label":"User Service"},
  {"id":"svc2","kind":"rect","x":280,"y":250,"width":140,"height":60,"label":"Order Service"},
  {"id":"svc3","kind":"rect","x":460,"y":250,"width":140,"height":60,"label":"Payment Service"},
  {"id":"db","kind":"cylinder","x":100,"y":430,"width":140,"height":50,"label":"PostgreSQL"},
  {"id":"cache","kind":"cylinder","x":300,"y":430,"width":120,"height":50,"label":"Redis Cache"},
  {"id":"warehouse","kind":"rect","x":480,"y":430,"width":140,"height":50,"label":"Data Warehouse"}
 ],
 "arrows":[
  {"source":"client","target":"gateway","label":"HTTPS","flow":"data"},
  {"source":"gateway","target":"auth","label":"Verify","flow":"control"},
  {"source":"gateway","target":"svc1","label":"Route","flow":"control"},
  {"source":"gateway","target":"svc2","label":"Route","flow":"control"},
  {"source":"gateway","target":"svc3","label":"Route","flow":"control"},
  {"source":"svc1","target":"db","label":"Query","flow":"read"},
  {"source":"svc2","target":"cache","label":"Cache","flow":"write"},
  {"source":"svc3","target":"db","label":"TX","flow":"write"},
  {"source":"db","target":"warehouse","label":"Sync","flow":"data"}
 ],
 "legend":[{"flow":"data","label":"Data"},{"flow":"control","label":"Control"},{"flow":"read","label":"Read"},{"flow":"write","label":"Write"}]}
```

---

## Memory Architecture — Style 3 Blueprint

```json
{"style":3,"title":"Memory Architecture","subtitle":"Mem0-style Layered Memory",
 "nodes":[
  {"id":"input","kind":"rect","x":80,"y":100,"width":160,"height":60,"label":"User Input","sublabel":"Query / Event","type_label":"INPUT"},
  {"id":"manager","kind":"hexagon","x":300,"y":80,"width":200,"height":80,"label":"Memory Manager","sublabel":"store · retrieve · forget","type_label":"CORE"},
  {"id":"working","kind":"rect","x":560,"y":40,"width":160,"height":60,"label":"Working Memory","sublabel":"context window","type_label":"TIER-1"},
  {"id":"shortterm","kind":"rect","x":560,"y":120,"width":160,"height":60,"label":"Short-term","sublabel":"session cache","type_label":"TIER-2"},
  {"id":"vector","kind":"cylinder","x":560,"y":220,"width":160,"height":80,"label":"Vector Store","sublabel":"embeddings","type_label":"TIER-3"},
  {"id":"graph","kind":"circle_cluster","x":560,"y":330,"width":160,"height":80,"label":"Graph DB","sublabel":"relationships","type_label":"TIER-3"},
  {"id":"kv","kind":"cylinder","x":760,"y":220,"width":140,"height":70,"label":"Key-Value","sublabel":"raw facts","type_label":"TIER-3"},
  {"id":"output","kind":"rect","x":300,"y":460,"width":200,"height":60,"label":"Context Builder","sublabel":"Ranked retrieval","type_label":"OUTPUT"}
 ],
 "arrows":[
  {"source":"input","target":"manager","label":"raw","flow":"control"},
  {"source":"manager","target":"working","label":"write(WM)","flow":"write"},
  {"source":"manager","target":"shortterm","label":"cache","flow":"write"},
  {"source":"manager","target":"vector","label":"embed","flow":"write"},
  {"source":"manager","target":"graph","label":"store facts","flow":"write"},
  {"source":"manager","target":"kv","label":"put","flow":"write"},
  {"source":"manager","target":"output","label":"retrieve","flow":"read"},
  {"source":"vector","target":"output","label":"chunks","flow":"read"},
  {"source":"graph","target":"output","label":"facts","flow":"read"},
  {"source":"working","target":"output","label":"context","flow":"read"}
 ],
 "legend":[{"flow":"control","label":"Control"},{"flow":"write","label":"Memory write"},{"flow":"read","label":"Memory read"}]}
```

---

## Multi-Agent — Style 5 Glassmorphism

```json
{"style":5,"title":"Multi-Agent Collaboration","subtitle":"Orchestrated Sub-Agent System",
 "containers":[
  {"label":"Mission Control","x":40,"y":80,"width":880,"height":80},
  {"label":"Specialist Agents","x":40,"y":200,"width":880,"height":200},
  {"label":"Synthesis","x":40,"y":440,"width":880,"height":80}
 ],
 "nodes":[
  {"id":"user","kind":"user_avatar","x":60,"y":90,"width":160,"height":60,"label":"User Brief"},
  {"id":"coordinator","kind":"hexagon","x":300,"y":80,"width":200,"height":70,"label":"Coordinator Agent","sublabel":"Task planning"},
  {"id":"researcher","kind":"hexagon","x":100,"y":260,"width":180,"height":70,"label":"Research Agent","sublabel":"Web search · RAG"},
  {"id":"coder","kind":"hexagon","x":380,"y":260,"width":180,"height":70,"label":"Coding Agent","sublabel":"Code generation"},
  {"id":"reviewer","kind":"hexagon","x":660,"y":260,"width":180,"height":70,"label":"Review Agent","sublabel":"Quality check"},
  {"id":"memory","kind":"cylinder","x":100,"y":450,"width":180,"height":60,"label":"Shared Memory"},
  {"id":"synth","kind":"rect","x":380,"y":450,"width":200,"height":60,"label":"Synthesis Engine"},
  {"id":"output","kind":"rect","x":660,"y":450,"width":160,"height":60,"label":"Final Response"}
 ],
 "arrows":[
  {"source":"user","target":"coordinator","label":"brief","flow":"control"},
  {"source":"coordinator","target":"researcher","label":"delegate","flow":"control"},
  {"source":"coordinator","target":"coder","label":"delegate","flow":"control"},
  {"source":"coordinator","target":"reviewer","label":"delegate","flow":"control"},
  {"source":"researcher","target":"memory","label":"write","flow":"write"},
  {"source":"coder","target":"memory","label":"write","flow":"write"},
  {"source":"reviewer","target":"memory","label":"write","flow":"write"},
  {"source":"memory","target":"synth","label":"read","flow":"read"},
  {"source":"synth","target":"output","label":"response","flow":"data"}
 ],
 "legend":[{"flow":"control","label":"Delegation"},{"flow":"write","label":"Memory write"},{"flow":"read","label":"Memory read"},{"flow":"data","label":"Output"}]}
```

---

## Comparison Matrix — Style 4 Notion Clean

```json
{"style":4,"title":"Comparison","subtitle":"System A vs System B",
 "headers":["Feature","System A","System B"],
 "rows":[
  ["Performance","✅ Fast","⚠️ Medium"],
  ["Scalability","✅ Horizontal","✅ Horizontal"],
  ["Ease of Use","✅ GUI","❌ CLI only"],
  ["Cost","💰 High","🆓 Free"]
 ],
 "nodes":[],
 "arrows":[]}
```

---

## Timeline / Gantt — Style 3 Blueprint

```json
{"style":3,"title":"Project Timeline","subtitle":"Q1-Q2 2026 Milestones",
 "milestones":[
  {"id":"m1","x":120,"y":150,"label":"Kickoff","date":"Week 1"},
  {"id":"m2","x":300,"y":150,"label":"Alpha","date":"Week 6"},
  {"id":"m3","x":500,"y":150,"label":"Beta","date":"Week 12"},
  {"id":"m4","x":700,"y":150,"label":"GA","date":"Week 18"}
 ],
 "bars":[
  {"id":"b1","x":120,"y":200,"width":180,"label":"Phase 1","color":"#6c8ebf"},
  {"id":"b2","x":300,"y":280,"width":200,"label":"Phase 2","color":"#82b366"},
  {"id":"b3","x":500,"y":360,"width":200,"label":"Phase 3","color":"#d6b656"}
 ],
 "nodes":[],
 "arrows":[
  {"source":"m1","target":"m2","label":"6 weeks","flow":"data"},
  {"source":"m2","target":"m3","label":"6 weeks","flow":"data"},
  {"source":"m3","target":"m4","label":"6 weeks","flow":"data"}
 ]}
```

---

## Mind Map — Style 1 Flat Icon

```json
{"style":1,"title":"Mind Map","subtitle":"Central Topic",
 "nodes":[
  {"id":"center","kind":"circle","x":420,"y":250,"width":120,"height":120,"label":"Central Topic"},
  {"id":"n1","kind":"rect","x":60,"y":100,"width":140,"height":60,"label":"Branch 1"},
  {"id":"n2","kind":"rect","x":60,"y":220,"width":140,"height":60,"label":"Branch 2"},
  {"id":"n3","kind":"rect","x":60,"y":340,"width":140,"height":60,"label":"Branch 3"},
  {"id":"n4","kind":"rect","x":700,"y":100,"width":140,"height":60,"label":"Branch 4"},
  {"id":"n5","kind":"rect","x":700,"y":220,"width":140,"height":60,"label":"Branch 5"},
  {"id":"n6","kind":"rect","x":700,"y":340,"width":140,"height":60,"label":"Branch 6"}
 ],
 "arrows":[
  {"source":"center","target":"n1","label":"","flow":"control"},
  {"source":"center","target":"n2","label":"","flow":"control"},
  {"source":"center","target":"n3","label":"","flow":"control"},
  {"source":"center","target":"n4","label":"","flow":"control"},
  {"source":"center","target":"n5","label":"","flow":"control"},
  {"source":"center","target":"n6","label":"","flow":"control"}
 ],
 "legend":[],
 "legend_position":""}
```
