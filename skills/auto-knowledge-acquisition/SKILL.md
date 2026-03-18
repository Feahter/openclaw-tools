---
name: auto-knowledge-acquisition
description: |
  自动知识获取系统 - 研究和发现 GitHub 高质量项目，记录学习笔记。
  
  **触发场景**：
  - 用户说"研究GitHub项目"、"发现新工具"、"知识探索"
  - 用户说"最近有什么有趣的开源项目"
  - 用户说"帮我找X领域的优质项目"
  - 定期心跳扫描新项目
  
  **输出**：结构化研究报告 + 评分 + 可操作建议
  
  **不自动生成 Skills**，仅提供研究数据和创建建议。高质量项目建议用 `skill-from-github` 创建。
---

# 自动知识获取系统

发现、研究、记录高质量项目，构建你的技术知识库。

> "站在巨人的肩膀上" —— 这不是抄，是学习

## 🎯 核心定位

这是一个**研究型 Skill**，专注于发现和评估 GitHub 上的高质量项目。它不生成代码或 Skills，只做研究和记录。

**输出价值**：
- 🗂️ 结构化的项目笔记（供后续参考）
- 📊 客观的评分报告（帮助决策）
- 💡 可操作的建议（下一步做什么）

---

## 🔍 研究流程

### 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│                     研究工作流                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣ 搜索    →  2️⃣ 初筛   →  3️⃣ 研究   →  4️⃣ 评分   │
│      关键词过滤        基础指标        深入分析    多维评估  │
│                                                             │
│  5️⃣ 记录    →  6️⃣ 建议                                   │
│      格式输出        行动建议                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 各阶段详解

#### 阶段1：搜索

**搜索策略**：

```bash
# 按领域搜索
gh search repos "topic:AI language:Python stars:>1000 pushed:>2025-01-01"
gh search repos "topic:RAG language:Python stars:>500"
gh search repos "topic:agent framework stars:>1000"

# 按关键词搜索
gh search repos "CLI tool golang stars:>500"
gh search repos "web scraper typescript stars:>300"

# 趋势项目
gh search repos "created:>2025-01-01 stars:>100 --sort stars --order desc"

# 按 license 筛选
gh search repos "stars:>1000 license:mit,apache-2.0"
```

**搜索关键词池**：

| 领域 | 关键词 |
|------|--------|
| AI/LLM | `llm`, `rag`, `agent`, `chatbot`, `embedding`, `vector db` |
| 开发工具 | `cli`, `tool`, `generator`, `scaffolding`, `boilerplate` |
| 前端 | `react`, `vue`, `svelte`, `component library`, `ui framework` |
| 后端 | `api`, `rest`, `graphql`, `server`, `microservice` |
| 数据 | `data pipeline`, `etl`, `data engineering`, `streaming` |
| DevOps | `docker`, `kubernetes`, `ci/cd`, `monitoring`, `deployment` |
| 数据库 | `database`, `orm`, `migrations`, `postgresql`, `mysql` |

#### 阶段2：初筛

**基础指标过滤**：

```yaml
# 最低标准
min_stars: 500           # 至少500 stars
max_age_months: 60      # 不超过5年（避免死项目）
min_weekly_stars: 5     # 近期有活动
has_readme: true        # 必须有README
has_releases: true      # 近期有发布
license_allowed:        # 可接受的license
  - mit
  - apache-2.0
  - bsd-2-clause
  - bsd-3-clause
  - gpl-3.0
```

**快速排除**：

```
❌ 已归档的项目（archived: true）
❌ 没有最近更新的（pushed > 1年前）
❌ 纯文档仓库（docs/）
❌ example/sample 项目
❌ 单文件仓库
```

#### 阶段3：深入研究

**必读内容**：

```
1. README.md
   - 项目做什么？
   - 解决了什么问题？
   - 如何使用？

2. src/ 或 主要代码文件
   - 代码质量如何？
   - 架构设计怎样？
   - 有没有测试？

3. package.json / pyproject.toml / Cargo.toml
   - 依赖管理
   - 版本情况
   - 构建工具

4. issues / discussions
   - 社区活跃度
   - 主要问题类型
   - 开发团队响应

5. CHANGELOG.md 或 releases
   - 版本迭代速度
   - breaking changes 频率
   - 重大功能
```

**研究检查清单**：

```markdown
### 项目基本信息
- [ ] 官方描述（一句话）
- [ ] 核心功能列表
- [ ] 适用场景
- [ ] 对标产品/竞品

### 技术评估
- [ ] 编程语言
- [ ] 主要框架/依赖
- [ ] 代码行数（估算）
- [ ] 测试覆盖率
- [ ] 文档完整性

### 社区评估
- [ ] Stars / Forks 比例
- [ ] 最近更新日期
- [ ] Issue 响应速度
- [ ] PR 合并率
- [ ] 贡献者数量

### 商业/实用评估
- [ ] License 类型
- [ ] 生产可用性
- [ ] 维护活跃度
- [ ] 学习曲线
- [ ] 集成难度
```

#### 阶段4：评分

**多维评分模型**（满分5分）：

```python
def calculate_score(repo):
    scores = {
        # 质量分（40%）
        "code_quality": star_score(repo.stars) * 0.15,
        "documentation": readme_score(repo) * 0.10,
        "test_coverage": test_score(repo) * 0.10,
        "architecture": arch_score(repo) * 0.05,
        
        # 热度分（30%）
        "stars": star_score(repo.stars) * 0.15,
        "recent_activity": activity_score(repo) * 0.10,
        "community": community_score(repo) * 0.05,
        
        # 价值分（30%）
        "uniqueness": unique_score(repo) * 0.10,
        "practicality": practical_score(repo) * 0.10,
        "maintainability": maintain_score(repo) * 0.10,
    }
    
    return sum(scores.values())

def star_score(stars):
    """Stars 评分"""
    if stars >= 10000: return 5.0
    if stars >= 5000: return 4.5
    if stars >= 1000: return 4.0
    if stars >= 500: return 3.5
    if stars >= 100: return 3.0
    return 2.0
```

**评分维度详解**：

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| **代码质量** | 15% | 命名规范、结构清晰、类型提示、代码风格 |
| **文档** | 10% | README完整度、API文档、教程、示例 |
| **测试** | 10% | 测试覆盖、测试质量、CI/CD |
| **架构设计** | 5% | 模块化、可扩展性、设计模式 |
| **Stars** | 15% | 社区认可度 |
| **近期活跃** | 10% | 最近commit、issue响应、版本发布 |
| **社区** | 5% | 贡献者数量、讨论活跃度 |
| **独特性** | 10% | 与现有项目的差异点、创新程度 |
| **实用性** | 10% | 生产可用性、学习曲线、集成难度 |
| **可维护性** | 10% | 依赖健康、版本稳定、迁移难度 |

**评分结果**：

```yaml
评分结果:
  总分: 4.2/5.0
  等级: A（优质项目）
  
  分项得分:
    代码质量: 4.5
    文档: 4.0
    测试: 4.0
    架构: 4.5
    Stars: 4.0
    活跃度: 4.0
    社区: 4.0
    独特性: 4.0
    实用性: 4.5
    可维护性: 4.5

  结论:
    - 值得深入研究
    - 建议作为参考实现
    - 可学习其架构设计
```

---

## 📋 输出格式

### 完整研究报告模板

```markdown
# 项目研究报告：[项目名]

## 📌 一句话评价
[用一句话描述这个项目是什么、解决什么问题]

## 📊 基本信息

| 字段 | 值 |
|------|-----|
| **GitHub** | [链接] |
| **Stars** | ⭐ X,XXX |
| **语言** | Python / TypeScript / ... |
| **License** | MIT |
| **最后更新** | 2026-01-15 |
| **版本** | v1.2.3 |

## 🎯 项目定位

### 做什么
[详细描述项目功能]

### 解决什么问题
[目标用户 + 痛点 + 解决方案]

### 适用场景
- 场景1
- 场景2
- 场景3

### 竞品对比
| 特性 | 本项目 | 竞品A | 竞品B |
|------|--------|-------|-------|
| 性能 | ✅ 快 | ⚠️ 中 | ✅ 快 |
| 易用性 | ✅ 简单 | ❌ 复杂 | ⚠️ 中 |
| 文档 | ✅ 完善 | ✅ 完善 | ❌ 薄弱 |

## 🔬 深度分析

### 技术架构
[架构图或描述]

**核心模块**：
1. `module_a` - 负责...
2. `module_b` - 负责...

**设计亮点**：
- 🎨 设计1
- 🎨 设计2

### 代码质量
- 命名规范：✅/⚠️/❌
- 类型提示：✅/⚠️/❌
- 测试覆盖：✅/⚠️/❌
- 代码风格：一致/混乱

### 可改进点
[发现的潜在问题]

## 📈 评分报告

### 综合评分
```
总分: X.X / 5.0
等级: S / A / B / C
```

### 分项得分
```
代码质量    ████████░░  4.0
文档完整度  ███████░░░  3.5
架构设计    █████████░  4.5
社区活跃度  ████████░░  4.0
实用价值    █████████░  4.5
```

## 💡 行动建议

### 研究价值
- ✅ 值得深入研究其实现思路
- ✅ 可作为类似项目的参考
- ⚠️ 学习曲线较陡，需要时间

### 可迁移技术
- 架构设计模式
- 某算法实现
- 工具链设计

### 下一步
1. [ ] 克隆项目本地运行
2. [ ] 阅读核心源码
3. [ ] 尝试小功能改造
4. [ ] 撰写学习笔记

## 📚 相关资源

- 官方文档：[链接]
- 视频教程：[链接]
- 相关论文：[链接]

---

*研究日期：2026-03-18*
*研究员：auto-knowledge-acquisition*
```

### 轻量输出模板

```markdown
# [项目名]

**Stars**: ⭐ X,XXX | **语言**: Python | **License**: MIT

**一句话**: [描述]

**评分**: 4.2/5.0 ⭐ (A 级)

**亮点**:
- 亮点1
- 亮点2

**行动**: [深入研究 / 参考架构 / 暂跳过]
```

---

## 🔧 使用场景

### 场景1：心跳定期扫描

配置心跳触发：

```yaml
# ~/.openclaw/config/auto-knowledge.yaml
heartbeat:
  enabled: true
  interval: "3 days"  # 每3天扫描一次
  keywords_rotation:
    - "AI agent framework"
    - "CLI tool generator"
    - "data pipeline python"
```

### 场景2：按需研究

用户发起研究任务：

```
用户: "帮我研究下 RAG 相关的开源项目"
AI: [触发 auto-knowledge-acquisition]
   → 搜索: topic:rag stars:>500 language:python
   → 初筛: 过滤、排序
   → 研究: Top 5 项目深入分析
   → 输出: 结构化报告
```

### 场景3：竞品分析

```
用户: "对比下这几个项目: langchain vs llamaindex vs crewai"
AI: [分别研究每个项目]
   → 统一维度评分
   → 对比表格
   → 结论和建议
```

---

## ⚙️ 配置选项

### 基础配置

```yaml
# ~/.openclaw/config/auto-knowledge.yaml
knowledge:
  # 搜索配置
  search:
    default_stars_threshold: 500
    max_age_months: 60
    max_projects_per_search: 20
    keywords_pools:
      ai: ["llm", "rag", "agent", "chatbot", "embedding"]
      dev: ["cli", "tool", "generator", "boilerplate"]
      data: ["etl", "pipeline", "data engineering"]
  
  # 评分配置
  scoring:
    weights:
      code_quality: 0.15
      documentation: 0.10
      uniqueness: 0.10
      practicality: 0.10
      # ... 其他权重
  
  # 输出配置
  output:
    format: "detailed"  # detailed / brief
    save_to: "memory/auto-knowledge-notes/"
    include_github_links: true
  
  # 过滤配置
  filters:
    exclude_archived: true
    exclude_forks: false
    min_recent_commit_days: 90
    allowed_licenses:
      - mit
      - apache-2.0
      - bsd-3-clause
```

### 高级配置

```yaml
# 针对特定领域的评分调整
scoring_overrides:
  # 快速演进的领域，降低文档权重
  ai_ml:
    documentation: 0.05
    practicality: 0.15
  
  # 基础设施类，提高稳定性权重
  infrastructure:
    maintainability: 0.15
    stability: 0.15
```

---

## 📁 输出管理

### 存储结构

```
memory/auto-knowledge-notes/
├── YYYY-MM/
│   ├── project-name-1.md      # 完整报告
│   ├── project-name-2.md
│   └── ...
├── weekly-digest-YYYY-WXX.md  # 周报摘要
├── monthly-report-YYYY-MM.md   # 月报
└── index.json                  # 索引文件
```

### 索引文件格式

```json
{
  "last_updated": "2026-03-18",
  "total_projects": 42,
  "by_category": {
    "ai_ml": 15,
    "dev_tools": 12,
    "data": 8,
    "other": 7
  },
  "top_rated": [
    {"name": "project-a", "score": 4.8, "date": "2026-03-15"},
    {"name": "project-b", "score": 4.6, "date": "2026-03-12"}
  ],
  "projects": [
    {
      "name": "project-a",
      "path": "2026-03/project-a.md",
      "stars": 12500,
      "score": 4.8,
      "tags": ["ai", "rag", "python"],
      "research_date": "2026-03-15"
    }
  ]
}
```

---

## 🤝 与其他 Skills 配合

| 场景 | 使用流程 |
|------|---------|
| **发现项目** | `auto-knowledge-acquisition` → 研究评分 → 记录 |
| **创建Skill** | `auto-knowledge-acquisition` 发现高分项目 → `skill-from-github` 创建 |
| **深度学习** | `auto-knowledge-acquisition` → `oss-code-analysis` 深入源码 |
| **竞品分析** | `auto-knowledge-acquisition` × 多项目 → 对比报告 |
| **技术选型** | `auto-knowledge-acquisition` → 评分 → `decision-matrix` 决策 |

---

## 🎓 研究方法论

### 高效研究技巧

1. **先广后深**
   ```
   第一轮：快速扫描20个项目 → 筛选5个有潜力的
   第二轮：深入研究5个项目 → 确定2个值得细看的
   ```

2. **对比学习**
   ```
   选择3个同类项目
   统一维度对比
   找出各自优势
   ```

3. **源码为王**
   ```
   README 是门面
   源码是内核
   真正理解靠读代码
   ```

4. **实践验证**
   ```
   克隆下来跑一跑
   尝试小功能改造
   真正用过才算研究完
   ```

### 常见陷阱

```
❌ 只看 Stars，不看质量
   → 大项目不一定值得学

❌ 只看文档，不读代码
   → 文档可能吹牛，代码才见真章

❌ 收藏癖
   → 研究10个不如精通2个

❌ 只研究热门项目
   → 冷门领域可能有宝藏
```

---

## ✅ 快速参考

### 命令速查

```bash
# 搜索高星项目
gh search repos "topic:XX stars:>1000" --limit 10

# 搜索近期活跃项目
gh search repos "created:>2025-01-01 stars:>100" --sort stars --limit 10

# 获取项目详情
gh repo view owner/repo

# 查看项目语言分布
gh repo view owner/repo --json languages
```

### 决策树

```
发现项目
    ↓
满足基础条件？(stars>500, 最近更新, 有文档)
    ↓ 是
深入研究
    ↓
评分 >= 4.0?
    ↓ 是
记录笔记 + 标记"建议创建Skill"
    ↓ 否
仅记录笔记
```

---

## 📝 研究日记模板

```markdown
# 研究日记 - YYYY-MM-DD

## 今日研究主题
[研究了什么领域/什么问题]

## 发现的项目

### 项目A
- 评分: 4.5/5.0
- 亮点: ...
- 收获: ...

### 项目B
- 评分: 3.8/5.0  
- 亮点: ...
- 收获: ...

## 今日总结
- 学到了什么
- 下次研究重点
- 需要深入的项目
```

---

*本 Skill 专注于研究和发现，不直接生成 Skills*
*高分项目建议使用 `skill-from-github` 创建完整实现*
*配合 `oss-code-analysis` 进行源码级深度学习*
