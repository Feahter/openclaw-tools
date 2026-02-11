# HEARTBEAT.md

## 🫀 统一心跳任务（每小时）

**Cron 任务**: `87cece86-7125-424d-8d20-ed8c5981298e`
- **频率**: 每小时整点
- **目标**: 系统自主维护与持续进化
- **脚本**: `/Users/fuzhuo/.openclaw/workspace/tools/unified-heartbeat.py`

**整合模块**:
1. 🔋 **资源优化** - 检查API状态、任务统计、**自动化机会扫描**
2. 🛠️ **Skills 维护** - 检查更新、发现新 skills、轮换搜索
3. 📚 **自动知识获取** - `auto-knowledge-acquisition` 全自动生成新 Skills
4. 🧬 **进化分析** - 记录成功模式、追踪改进项

**进化增强 Skills**（已纳入心跳 SOP）:
- `autonomous-brain` - 主动监控、自主决策、持续运行
- `reflect-learn` - 从对话中学习，持续改进
- `basal-ganglia-memory` - 习惯形成，自动化常用操作
- `agent-autonomy-kit` - 任务队列，主动工作
- `para-second-brain` - 知识管理，语义搜索
- `ai-rag-pipeline` - 检索增强生成，知识获取

**日志位置**: `data/heartbeat-report-YYYYMMDD-HHMM.json`

---

## 📚 自动知识获取管道（每小时）

**Skill**: `auto-knowledge-acquisition`  
**脚本**: `/Users/fuzhuo/.openclaw/workspace/tools/auto-knowledge-pipeline.py`  
**触发**: 每小时心跳自动执行  
**人工干预**: 无需

### 执行流程

```
心跳触发 → 轮换关键词 → 搜索GitHub → 智能评分 → 自动选择 
→ 生成Skill/记录笔记 → 更新状态
```

### 自动决策策略

| 条件 | 自动操作 |
|------|---------|
| 项目评分 ≥ 4.0 | 自动选择，高置信度 |
| 项目评分 3.5-4.0 | 自动选择，中置信度 |
| 项目评分 < 3.5 | 拒绝，记录原因 |
| 生成价值评估通过 | 自动生成Skill |
| 生成价值评估部分通过 | 保存为学习笔记 |
| Skill已存在 | 跳过，避免重复 |

### 配置位置

- **轮换关键词**: `skills/auto-knowledge-acquisition/SKILL.md`
- **执行状态**: `data/auto-knowledge-state.json`
- **执行日志**: `data/logs/auto-knowledge/YYYY-MM-DD.log`
- **学习笔记**: `memory/auto-knowledge-notes/`

### 手动测试

```bash
# 手动运行一次
python tools/auto-knowledge-pipeline.py
```

---

## 🧠 进化增强 SOP（纳入心跳）

### 模块1: 资源优化 + 自动化机会
- 扫描心跳日志中的错误模式
- 识别可自动化的重复操作
- 触发 `automation-workflows` 分析

### 模块2: Skills 维护 + 自主学习
- 使用 `autonomous-brain` 主动监控 Skills 健康度
- 每周使用 `find-skills` 搜索进化相关 Skills
- 识别 `basal-ganglia-memory` 可记录的操作习惯

### 模块3: 自动知识获取 + RAG
- `ai-rag-pipeline` 增强搜索质量
- 每周深度搜索高价值项目
- 知识自动存入 `para-second-brain`

### 模块4: 进化分析 + 自我反思
- 使用 `reflect-learn` 分析心跳执行日志
- 识别成功模式（写入 `success-patterns.json`）
- 追踪待改进项（写入 `improvements.json`）
- 生成进化建议

---

## ✅ 已整合的持续进化流程

*记录于 memory/evolution-workflows-2026-02-07.md*

### 已整合到心跳

| 流程 | 整合模块 | 触发时机 |
|------|---------|---------|
| **自动化知识获取** | Skills 维护 | 每日凌晨3点深度搜索 |
| **自动化机会扫描** | 资源优化 | 每小时扫描执行日志 |
| **自主决策增强** | 全模块 | 持续运行（autonomous-brain） |
| **习惯形成追踪** | 资源优化 | 每周分析常用操作 |
| **RAG知识获取** | 知识模块 | 每周深度搜索（ai-rag-pipeline） |

### 按需触发

| 流程 | 触发方式 | Skills |
|------|---------|--------|
| **对话复盘优化** | 用户主动 `/evolve` | `reflect-learn` |
| **多代理分工** | 复杂任务自动识别 | `agent-commander` |
| **知识库构建** | 每日一次 | `para-second-brain` |
| **性能优化分析** | 每周一次 | `perf-profiler`, `macbook-optimizer` |
| **系统健康检查** | 每日一次 | `system-monitor`, `server-health` |

---

## 📊 本地 Skills 进化分类

### 核心进化 Skills（Critical）

| Skill | 功能 | 整合模块 |
|-------|------|---------|
| `autonomous-brain` | 自主思考、主动监控 | 全模块 |
| `reflect-learn` | 从错误中学习、持续改进 | 进化分析 |
| `basal-ganglia-memory` | 习惯形成、操作自动化 | 资源优化 |
| `agent-autonomy-kit` | 任务队列、持续工作 | 任务执行 |

### 知识管理 Skills

| Skill | 功能 | 整合模块 |
|-------|------|---------|
| `para-second-brain` | PARA知识组织、语义搜索 | 自动知识获取 |
| `ai-rag-pipeline` | RAG管道、检索增强生成 | 自动知识获取 |
| `auto-knowledge-acquisition` | 自动发现和生成Skills | Skills维护 |

### 自动化 Skills

| Skill | 功能 | 整合模块 |
|-------|------|---------|
| `automation-workflows-0-1-0` | 自动化工作流设计 | 资源优化 |
| `workflow-automation` | ETL管道、DAG工作流 | 资源优化 |
| `cron-scheduling` | 定时任务管理 | 任务执行 |
| `openclaw-auto-updater` | 自动更新 | 任务执行 |

### 监控 Skills

| Skill | 功能 | 整合模块 |
|-------|------|---------|
| `system-monitor` | CPU/RAM/GPU监控 | 资源优化 |
| `process-monitor` | 进程监控、告警 | 资源优化 |
| `server-health` | 服务健康检查 | 资源优化 |
| `perf-profiler` | 性能分析 | 资源优化 |

### 数据分析 Skills

| Skill | 功能 | 整合模块 |
|-------|------|---------|
| `data-analyst` | 数据分析、报表生成 | 进化分析 |
| `data-visualization` | 可视化 | 进化分析 |
| `big-data-analysis` | 大规模数据分析 | 进化分析 |

---

## 🔄 进化工作流状态

### 本周进化目标
- [ ] 整合 `autonomous-brain` 到心跳执行
- [ ] 建立 `reflect-learn` 自动触发机制
- [ ] 完善 `para-second-brain` 知识索引
- [ ] 启用 `ai-rag-pipeline` 增强搜索

### 已完成
- ✅ 统一心跳任务框架
- ✅ 自动知识获取管道
- ✅ Skills 自动安装机制
- ✅ 进化分析日志系统

### 待处理
- ⏳ `basal-ganglia-memory` 习惯追踪配置
- ⏳ `agent-autonomy-kit` 任务队列集成
- ⏳ RAG管道与知识库联动

---

## 历史任务（已合并）

之前的独立任务已合并为统一心跳：
- ❌ ~~进化分析-每小时~~ → 合并到模块4
- ❌ ~~Skills Discovery & Maintenance~~ → 合并到模块2
