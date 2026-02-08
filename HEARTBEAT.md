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

## 已整合的持续进化流程

*记录于 memory/evolution-workflows-2026-02-07.md*

### ✅ 已整合到心跳

| 流程 | 整合模块 | 触发时机 |
|------|---------|---------|
| **自动化知识获取** | Skills 维护 | 每日凌晨3点深度搜索 |
| **自动化机会扫描** | 资源优化 | 每小时扫描执行日志 |

### ❌ 按需触发（不适合定时）

| 流程 | 触发方式 | Skills |
|------|---------|--------|
| **对话复盘优化** | 用户主动 `/evolve` | `skill-evolution-manager` |
| **多代理分工** | 复杂任务自动识别 | `agent-commander` |

---

## 历史任务（已合并）

之前的独立任务已合并为统一心跳：
- ❌ ~~进化分析-每小时~~ → 合并到模块3
- ❌ ~~Skills Discovery & Maintenance~~ → 合并到模块2
