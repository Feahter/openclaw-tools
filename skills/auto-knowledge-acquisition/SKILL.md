---
name: auto-knowledge-acquisition
description: 全自动知识获取系统。通过心跳任务触发，自动搜索、评估、研究GitHub项目，无需人工干预生成新Skills。
triggers:
  - "自动获取知识"
  - "auto acquire knowledge"
  - "knowledge pipeline"
---

# 自动知识获取系统

全自动发现并学习GitHub高质量项目，将其方法论编码为新Skills。设计为通过心跳任务触发，零人工干预运行。

## 架构概览

```
心跳触发 → 轮换搜索 → 智能评分 → 自动选择 → 深度研究 → 质量评估 → 生成Skill/记录笔记
```

## 1. 配置管理

### 1.1 搜索轮换配置

`~/.openclaw/config/auto-knowledge.yaml`:

```yaml
search_rotation:
  # 每小时轮换的关键词池
  keywords:
    - category: "开发工具"
      terms: ["cli tool", "developer tools", "git workflow", "code quality"]
    - category: "数据处理"
      terms: ["data processing", "etl pipeline", "data validation", "csv parser"]
    - category: "API集成"
      terms: ["api client", "rest api", "graphql", "webhook"]
    - category: "自动化"
      terms: ["automation", "workflow", "scheduler", "batch processing"]
    - category: "AI应用"
      terms: ["llm tools", "ai automation", "prompt engineering", "rag pipeline"]
    - category: "文档处理"
      terms: ["pdf processing", "markdown tools", "document converter"]
    - category: "系统监控"
      terms: ["system monitoring", "log analysis", "health check"]
    - category: "安全工具"
      terms: ["security scanner", "vulnerability check", "secrets management"]
  
  # 轮换策略
  rotation_strategy: "round_robin"  # round_robin, random, priority
  skip_if_recent: "24h"  # 24小时内搜索过的关键词跳过

quality_thresholds:
  min_score: 3.5        # 最低接受分数 (满分5)
  min_stars: 100        # 最低star数
  max_age_months: 12    # 最大项目年龄
  
generation_criteria:
  min_extracted_methods: 3  # 至少提取3个方法步骤
  complexity_range: [2, 4]  # 复杂度适中 (1=简单, 5=极复杂)
```

### 1.2 状态追踪

`~/.openclaw/state/auto-knowledge-state.json`:

```json
{
  "last_run": "2026-02-07T00:00:00Z",
  "search_history": [
    {
      "timestamp": "2026-02-07T00:00:00Z",
      "keyword": "cli tool",
      "results_count": 15,
      "selected_project": "org/repo",
      "score": 4.2,
      "action": "generated_skill",
      "skill_name": "cli-toolkit"
    }
  ],
  "current_rotation_index": 3,
  "daily_stats": {
    "searches": 5,
    "skills_generated": 1,
    "notes_created": 2,
    "rejected": 2
  }
}
```

## 2. 评分算法

### 2.1 项目质量评分

```python
def calculate_project_score(project) -> float:
    """
    计算项目质量分数 (0-5)
    """
    scores = {}
    
    # Stars 评分 (25%)
    stars = project.get('stars', 0)
    if stars >= 10000: scores['stars'] = 5.0
    elif stars >= 5000: scores['stars'] = 4.5
    elif stars >= 2000: scores['stars'] = 4.0
    elif stars >= 1000: scores['stars'] = 3.5
    elif stars >= 500: scores['stars'] = 3.0
    elif stars >= 100: scores['stars'] = 2.0
    else: scores['stars'] = 1.0
    
    # 活跃度评分 (25%)
    last_update = project.get('last_update')
    days_ago = (now - last_update).days
    if days_ago <= 7: scores['activity'] = 5.0
    elif days_ago <= 30: scores['activity'] = 4.5
    elif days_ago <= 90: scores['activity'] = 4.0
    elif days_ago <= 180: scores['activity'] = 3.0
    elif days_ago <= 365: scores['activity'] = 2.0
    else: scores['activity'] = 1.0
    
    # 文档完整性 (20%)
    readme_length = project.get('readme_length', 0)
    has_examples = project.get('has_examples', False)
    has_api_doc = project.get('has_api_doc', False)
    doc_score = 0
    if readme_length > 5000: doc_score += 2
    elif readme_length > 2000: doc_score += 1.5
    if has_examples: doc_score += 1.5
    if has_api_doc: doc_score += 1.5
    scores['documentation'] = min(5, doc_score)
    
    # 社区健康 (15%)
    issue_response_time = project.get('avg_issue_response_days', 999)
    pr_count = project.get('recent_prs', 0)
    health_score = 0
    if issue_response_time <= 7: health_score += 2.5
    elif issue_response_time <= 30: health_score += 2
    if pr_count >= 10: health_score += 2.5
    elif pr_count >= 5: health_score += 2
    scores['community'] = min(5, health_score)
    
    # 许可证友好度 (15%)
    license = project.get('license', '').lower()
    if license in ['mit', 'apache-2.0', 'bsd']: scores['license'] = 5.0
    elif license in ['gpl', 'lgpl']: scores['license'] = 3.0
    elif license: scores['license'] = 2.0
    else: scores['license'] = 1.0
    
    # 加权计算
    weights = {
        'stars': 0.25,
        'activity': 0.25,
        'documentation': 0.20,
        'community': 0.15,
        'license': 0.15
    }
    
    final_score = sum(scores[k] * weights[k] for k in weights)
    return round(final_score, 2), scores
```

### 2.2 自动选择策略

```python
def auto_select_project(projects: list, min_score: float = 3.5) -> dict:
    """
    自动选择最佳项目，无需人工确认
    """
    # 过滤低于阈值的
    qualified = [p for p in projects if p['score'] >= min_score]
    
    if not qualified:
        return {
            'action': 'reject',
            'reason': 'no_qualified_projects',
            'max_score': max(p['score'] for p in projects) if projects else 0
        }
    
    # 按分数排序
    qualified.sort(key=lambda x: x['score'], reverse=True)
    
    # 选择策略
    best = qualified[0]
    
    # 如果最高分 >= 4.0，直接选择
    if best['score'] >= 4.0:
        return {
            'action': 'select',
            'project': best,
            'confidence': 'high',
            'reason': f"高分项目 ({best['score']}/5)"
        }
    
    # 如果 3.5-4.0，检查是否有明显更好的
    if len(qualified) >= 2:
        second = qualified[1]
        if best['score'] - second['score'] >= 0.5:
            return {
                'action': 'select',
                'project': best,
                'confidence': 'medium',
                'reason': f"明显优于备选 ({best['score']} vs {second['score']})"
            }
        else:
            # 分数接近，选择stars更高的
            if best['stars'] >= second['stars']:
                selected = best
            else:
                selected = second
            return {
                'action': 'select',
                'project': selected,
                'confidence': 'medium',
                'reason': f"社区规模更大 ({selected['stars']} stars)"
            }
    
    # 只有一个合格项目
    return {
        'action': 'select',
        'project': best,
        'confidence': 'low',
        'reason': '唯一合格选项'
    }
```

## 3. 深度研究流程

### 3.1 自动文档提取

```python
async def deep_research_project(repo_url: str) -> dict:
    """
    自动深入研究项目，提取核心方法论
    """
    research = {
        'source_url': repo_url,
        'timestamp': datetime.now().isoformat(),
        'extracted_data': {}
    }
    
    # 1. 获取README
    readme = await fetch_readme(repo_url)
    research['extracted_data']['readme'] = {
        'length': len(readme),
        'sections': extract_sections(readme),
        'installation': extract_installation(readme),
        'usage_examples': extract_usage(readme)
    }
    
    # 2. 获取核心源码结构
    structure = await analyze_code_structure(repo_url)
    research['extracted_data']['code_structure'] = {
        'main_modules': structure['modules'],
        'entry_points': structure['entry_points'],
        'core_algorithms': structure['algorithms']
    }
    
    # 3. 提取关键概念
    concepts = extract_key_concepts(readme, structure)
    research['extracted_data']['key_concepts'] = concepts
    
    # 4. 识别最佳实践
    practices = extract_best_practices(readme, structure)
    research['extracted_data']['best_practices'] = practices
    
    # 5. 常见陷阱
    pitfalls = extract_pitfalls(readme, await fetch_issues(repo_url))
    research['extracted_data']['common_pitfalls'] = pitfalls
    
    return research
```

### 3.2 方法论提取

```python
def extract_methodology(research_data: dict) -> dict:
    """
    从研究数据中提取可编码的方法论
    """
    methodology = {
        'purpose': '',           # Skill用途
        'core_method': [],       # 核心方法步骤
        'input_output': {},      # 输入输出定义
        'decision_points': [],   # 关键决策点
        'quality_criteria': [],  # 质量标准
        'variations': []         # 常见变体
    }
    
    # 从README提取目的
    methodology['purpose'] = extract_purpose(research_data['readme'])
    
    # 从代码和文档提取核心方法
    methodology['core_method'] = extract_steps(
        research_data['usage_examples'],
        research_data['code_structure']
    )
    
    # 提取输入输出
    methodology['input_output'] = {
        'inputs': extract_inputs(research_data),
        'outputs': extract_outputs(research_data),
        'optional_params': extract_options(research_data)
    }
    
    # 提取质量标准
    methodology['quality_criteria'] = extract_quality_standards(
        research_data['best_practices']
    )
    
    return methodology
```

## 4. 质量评估

### 4.1 生成价值评估

```python
def evaluate_generation_worth(methodology: dict) -> dict:
    """
    评估是否值得生成Skill
    """
    checks = {
        'method_extractable': len(methodology['core_method']) >= 3,
        'complexity_appropriate': 2 <= estimate_complexity(methodology) <= 4,
        'reproducible': has_clear_io(methodology['input_output']),
        'valuable': solves_common_problem(methodology['purpose']),
        'novel': not_duplicate_existing(methodology['purpose'])
    }
    
    pass_rate = sum(checks.values()) / len(checks)
    
    if pass_rate == 1.0:
        return {
            'action': 'generate_skill',
            'confidence': 'high',
            'checks': checks
        }
    elif pass_rate >= 0.8:
        return {
            'action': 'generate_skill',
            'confidence': 'medium',
            'checks': checks,
            'warnings': [k for k, v in checks.items() if not v]
        }
    elif pass_rate >= 0.6:
        return {
            'action': 'create_note',
            'confidence': 'low',
            'checks': checks,
            'reason': '质量勉强，保存为学习笔记'
        }
    else:
        return {
            'action': 'reject',
            'reason': '质量不足',
            'failed_checks': [k for k, v in checks.items() if not v]
        }
```

## 5. 自动生成Skill

### 5.1 Skill模板生成

```python
def generate_skill_file(methodology: dict, project_info: dict) -> str:
    """
    自动生成SKILL.md文件内容
    """
    skill_content = f"""---
name: {generate_skill_name(methodology['purpose'])}
description: {generate_description(methodology['purpose'])}
triggers:
{generate_triggers(methodology['purpose'])}
source:
  project: {project_info['name']}
  url: {project_info['url']}
  license: {project_info['license']}
  auto_generated: true
  generated_at: {datetime.now().isoformat()}
---

# {methodology['purpose']}

自动生成的Skill，基于 [{project_info['name']}]({project_info['url']}) 项目的方法论。

## 核心方法

{format_core_method(methodology['core_method'])}

## 输入与输出

### 输入
{format_io(methodology['input_output']['inputs'])}

### 输出
{format_io(methodology['input_output']['outputs'])}

### 可选参数
{format_options(methodology['input_output']['optional_params'])}

## 质量标准

{format_quality_criteria(methodology['quality_criteria'])}

## 常见变体

{format_variations(methodology['variations'])}

## 最佳实践

{format_best_practices(project_info.get('best_practices', []))}

## 常见陷阱

{format_pitfalls(project_info.get('common_pitfalls', []))}

---

*本Skill由 auto-knowledge-acquisition 系统自动生成*
*来源: {project_info['url']}*
*生成时间: {datetime.now().isoformat()}*
"""
    return skill_content
```

### 5.2 命名规范

```python
def generate_skill_name(purpose: str) -> str:
    """
    生成规范的skill名称
    """
    # 提取关键词
    keywords = extract_keywords(purpose)
    
    # 命名规则: 功能-领域
    # 例如: "pdf-processing", "api-testing", "data-validation"
    
    name = '-'.join(keywords[:3])  # 最多3个词
    name = name.lower()
    name = re.sub(r'[^a-z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name)  # 合并连续横线
    name = name.strip('-')
    
    return name
```

## 6. 心跳集成

### 6.1 心跳任务配置

在 `HEARTBEAT.md` 中添加：

```yaml
knowledge_acquisition:
  enabled: true
  schedule: "0 * * * *"  # 每小时执行
  max_runtime_minutes: 15
  
  steps:
    - name: "select_keyword"
      action: "rotate_search_keyword"
      
    - name: "search_github"
      action: "search_projects"
      timeout: 120
      
    - name: "score_projects"
      action: "calculate_scores"
      
    - name: "auto_select"
      action: "select_best_project"
      
    - name: "deep_research"
      action: "research_project"
      timeout: 300
      condition: "selection_confidence >= medium"
      
    - name: "evaluate_worth"
      action: "evaluate_generation"
      
    - name: "generate_skill"
      action: "create_skill_file"
      condition: "action == generate_skill"
      
    - name: "record_note"
      action: "create_learning_note"
      condition: "action == create_note"
      
    - name: "update_state"
      action: "persist_state"
```

### 6.2 执行脚本

`tools/auto-knowledge-pipeline.py`:

```python
#!/usr/bin/env python3
"""
自动知识获取管道 - 心跳任务执行脚本
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# 加载配置
CONFIG_PATH = Path.home() / ".openclaw/config/auto-knowledge.yaml"
STATE_PATH = Path.home() / ".openclaw/state/auto-knowledge-state.json"
SKILLS_DIR = Path.home() / ".openclaw/workspace/skills"

async def main():
    """主执行流程"""
    print(f"[{datetime.now()}] 启动自动知识获取管道")
    
    # 1. 加载配置和状态
    config = load_config(CONFIG_PATH)
    state = load_state(STATE_PATH)
    
    # 2. 选择搜索关键词
    keyword = select_next_keyword(config, state)
    print(f"当前关键词: {keyword}")
    
    # 3. 搜索GitHub
    projects = await search_github(keyword, min_stars=config['quality_thresholds']['min_stars'])
    print(f"找到 {len(projects)} 个项目")
    
    if not projects:
        record_skip(state, keyword, "no_results")
        return
    
    # 4. 评分
    for project in projects:
        score, details = calculate_project_score(project)
        project['score'] = score
        project['score_details'] = details
    
    # 5. 自动选择
    decision = auto_select_project(projects, config['quality_thresholds']['min_score'])
    print(f"决策: {decision['action']}")
    
    if decision['action'] == 'reject':
        record_skip(state, keyword, decision['reason'])
        return
    
    # 6. 深入研究
    project = decision['project']
    print(f"深入研究: {project['name']} (分数: {project['score']})")
    
    research = await deep_research_project(project['url'])
    methodology = extract_methodology(research)
    
    # 7. 评估生成价值
    evaluation = evaluate_generation_worth(methodology)
    print(f"评估结果: {evaluation['action']} (置信度: {evaluation.get('confidence', 'N/A')})")
    
    # 8. 执行生成或记录
    if evaluation['action'] == 'generate_skill':
        skill_content = generate_skill_file(methodology, project)
        skill_name = generate_skill_name(methodology['purpose'])
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        
        # 保存Skill
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(skill_content)
        print(f"✅ 生成Skill: {skill_path}")
        
        record_success(state, keyword, project, skill_name, "skill")
        
    elif evaluation['action'] == 'create_note':
        note_path = save_learning_note(project, methodology, research)
        print(f"📝 保存学习笔记: {note_path}")
        record_success(state, keyword, project, None, "note")
        
    else:
        record_skip(state, keyword, evaluation['reason'])
    
    # 9. 保存状态
    save_state(STATE_PATH, state)
    print(f"[{datetime.now()}] 完成")

if __name__ == "__main__":
    asyncio.run(main())
```

## 7. 监控与报告

### 7.1 执行日志

`~/.openclaw/logs/auto-knowledge/YYYY-MM-DD.log`:

```
[2026-02-07 00:00:01] INFO: 启动自动知识获取
[2026-02-07 00:00:02] INFO: 关键词: "cli tool"
[2026-02-07 00:00:05] INFO: 找到 23 个项目
[2026-02-07 00:00:06] INFO: 最高分: cli-enhancer (4.3/5)
[2026-02-07 00:00:06] INFO: 决策: select (confidence: high)
[2026-02-07 00:00:15] INFO: 深入研究完成
[2026-02-07 00:00:16] INFO: 评估: generate_skill (confidence: high)
[2026-02-07 00:00:18] INFO: ✅ 生成Skill: cli-tool-enhancer
[2026-02-07 00:00:18] INFO: 完成
```

### 7.2 统计报告

每日生成报告：`~/.openclaw/reports/auto-knowledge-daily.json`

```json
{
  "date": "2026-02-07",
  "summary": {
    "total_runs": 24,
    "searches": 24,
    "projects_found": 412,
    "qualified_projects": 89,
    "skills_generated": 3,
    "notes_created": 5,
    "rejected": 16
  },
  "top_skills": [
    {
      "name": "cli-tool-enhancer",
      "source": "org/cli-enhancer",
      "score": 4.3,
      "source_stars": 5234
    }
  ],
  "rejection_reasons": {
    "no_qualified_projects": 8,
    "quality_insufficient": 5,
    "duplicate_existing": 3
  }
}
```

## 8. 安全与边界

### 8.1 自动决策边界

| 场景 | 自动处理 | 需要人工 |
|------|---------|---------|
| 项目选择 (score >= 4.0) | ✅ 自动 | ❌ |
| 项目选择 (3.5 <= score < 4.0) | ✅ 自动+标记 | ❌ |
| 项目选择 (score < 3.5) | ✅ 拒绝 | ❌ |
| Skill生成 (所有检查通过) | ✅ 自动 | ❌ |
| Skill生成 (部分检查失败) | ✅ 保存为笔记 | ❌ |
| 覆盖现有Skill | ❌ 跳过 | ✅ 需要确认 |
| 检测到潜在安全风险 | ❌ 暂停 | ✅ 需要审查 |

### 8.2 质量保证

自动生成的Skills会：
1. 包含 `auto_generated: true` 标记
2. 记录来源和生成时间
3. 定期评估使用率
4. 低使用率Skills自动归档

## 9. 持续改进

系统会自动优化自身：

- **关键词效果追踪**: 记录哪些关键词产生高质量Skills
- **评分算法校准**: 根据生成的Skills实际质量调整权重
- **研究深度自适应**: 根据项目复杂度调整研究时间
- **生成模板迭代**: 根据反馈优化Skill模板

---

## 快速启动

```bash
# 1. 创建配置目录
mkdir -p ~/.openclaw/config ~/.openclaw/state ~/.openclaw/logs/auto-knowledge

# 2. 复制默认配置
cp skills/auto-knowledge-acquisition/config-template.yaml ~/.openclaw/config/auto-knowledge.yaml

# 3. 手动测试运行
python tools/auto-knowledge-pipeline.py --dry-run

# 4. 配置心跳任务（由HEARTBEAT.md管理）
```

---

*本Skill定义了完整的自动知识获取系统架构*
