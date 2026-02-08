---
name: skill-orchestrator
description: |
  技能编排器 - 自动发现、安装并使用最适合的技能来完成任务。
  
  **核心能力:**
  1. **需求解析** - 分析用户描述，识别需要的技能组合
  2. **自动发现** - 搜索技能生态，找到最佳匹配
  3. **自动安装** - 无缝安装缺失的技能
  4. **智能执行** - 调用合适的技能完成任务
  5. **模型调度** - 当前模型受限时，自动切换可用模型
  
  **触发场景:**
  - 用户描述任务但不确定用什么技能
  - "帮我处理这个PDF并生成报告"
  - "分析这些数据并可视化"
  - "优化这段代码并生成文档"
  - 任何需要多技能协作的复杂任务
  
  **使用方式:** 直接描述你的需求，系统自动编排最优技能组合并执行。
---

# 技能编排器 (Skill Orchestrator)

## 工作流

```
用户需求
    ↓
[1] 需求解析 - 拆解为子任务
    ↓
[2] 技能匹配 - 发现/确认所需技能
    ↓
[3] 自动安装 - 安装缺失技能
    ↓
[4] 模型选择 - 选择最佳执行模型
    ↓
[5] 任务分发 - 执行子任务
    ↓
[6] 结果整合 - 合并输出
```

## 步骤详解

### 1. 需求解析

将用户描述拆解为原子任务：

| 用户描述 | 拆解为子任务 | 所需技能 |
|---------|------------|---------|
| "分析CSV并生成PDF报告" | 1. 读取CSV<br>2. 数据分析<br>3. 生成图表<br>4. 导出PDF | xlsx, canvas-design, pdf |
| "优化代码并写测试" | 1. 代码分析<br>2. 性能优化<br>3. 生成测试 | performance-optimizer, test-driven-development |
| "爬取网页并存数据库" | 1. 网页抓取<br>2. 数据清洗<br>3. 数据库操作 | browser, database |

### 2. 技能匹配

检查本地已安装技能：
```bash
# 列出所有可用技能
ls skills/
```

发现缺失技能：
```bash
# 搜索技能
npx skills find [关键词]
```

### 3. 自动安装

无缝安装：
```bash
npx skills add [owner/repo@skill] -g -y
```

### 4. 模型选择

**调度策略:**

| 场景 | 选择模型 | 原因 |
|------|---------|------|
| 当前模型正常 | 当前模型 | 保持上下文连续 |
| 当前模型限速 | 备用模型 | 避免等待 |
| 复杂推理任务 | kimi-coding/k2p5 | 强推理能力 |
| 简单任务 | 轻量模型 | 成本低 |
| 代码生成 | kimi-coding/k2p5 | 代码能力强 |
| 多语言混合 | kimi-coding/k2p5 | 多语言支持好 |

**检测限速:**
- 监控 API 响应时间
- 检查 rate limit 错误
- 自动降级到备用模型

### 5. 任务分发

**并行执行:**
```python
# 独立子任务并行处理
tasks = [
    ("分析数据", "kimi-coding/k2p5"),
    ("生成图表", "kimi-coding/k2p5"),
]
```

**串行执行:**
```python
# 依赖子任务串行处理
pipeline = [
    ("读取文件", "current"),
    ("处理数据", "current"),  # 依赖上一步
    ("生成输出", "current"),  # 依赖上一步
]
```

### 6. 结果整合

合并各子任务输出，生成最终结果。

## 使用示例

### 示例 1: 完整自动化

**用户输入:**
> "帮我分析这个 sales.csv，生成趋势图，并导出为 PDF 报告"

**系统自动执行:**
1. **解析需求:**
   - 读取 CSV → 需要 `xlsx` skill
   - 数据分析 → 内置能力
   - 生成图表 → 需要 `canvas-design` skill
   - 导出 PDF → 需要 `pdf` skill

2. **检查技能:**
   ```bash
   ls skills/ | grep -E "xlsx|canvas|pdf"
   # 发现 xlsx 已安装
   # 发现 canvas-design 缺失
   # 发现 pdf 缺失
   ```

3. **自动安装:**
   ```bash
   npx skills find canvas-design
   npx skills add [匹配结果] -g -y
   
   npx skills find pdf
   npx skills add [匹配结果] -g -y
   ```

4. **选择模型:**
   - 当前模型: kimi-coding/k2p5 ✓ 正常
   - 决策: 使用当前模型

5. **执行子任务:**
   - 使用 `xlsx` 读取 CSV
   - 使用 `canvas-design` 生成图表
   - 使用 `pdf` 导出报告

6. **输出结果:**
   - 返回 PDF 文件路径
   - 提供数据分析摘要

### 示例 2: 模型降级

**场景:** 当前模型限速

**系统自动处理:**
```python
# 检测到限速
if rate_limited(current_model):
    # 切换到备用模型
    fallback_model = get_available_model()
    spawn_task(task, model=fallback_model)
```

## 核心脚本

### auto-orchestrate.py

```python
#!/usr/bin/env python3
"""
自动技能编排脚本
用法: python auto-orchestrate.py "需求描述"
"""

import sys
import subprocess
import json
from pathlib import Path

class SkillOrchestrator:
    def __init__(self):
        self.skills_dir = Path("skills")
        self.model_priority = [
            "kimi-coding/k2p5",
            "kimi-k2p5",
            "claude-sonnet",
        ]
    
    def parse_requirement(self, description: str) -> list:
        """解析需求为子任务"""
        # 关键词匹配
        keywords = {
            "csv|excel|xlsx": "xlsx",
            "pdf": "pdf",
            "chart|graph|visual": "canvas-design",
            "image|photo": "canvas-design",
            "ppt|slide|presentation": "pptx",
            "doc|word|document": "docx",
            "test|spec": "test-driven-development",
            "optimize|performance": "performance-optimizer",
            "database|sql|db": "database",
            "github|git|pr": "github",
            "web|browser|scrape": "browser",
            "cron|schedule|timer": "cron-mastery",
        }
        
        tasks = []
        desc_lower = description.lower()
        
        for pattern, skill in keywords.items():
            if any(p in desc_lower for p in pattern.split("|")):
                tasks.append({
                    "skill": skill,
                    "action": "auto",
                })
        
        return tasks
    
    def check_skill_installed(self, skill_name: str) -> bool:
        """检查技能是否已安装"""
        return (self.skills_dir / skill_name).exists()
    
    def find_skill(self, keyword: str) -> list:
        """搜索技能"""
        result = subprocess.run(
            ["npx", "skills", "find", keyword],
            capture_output=True,
            text=True
        )
        # 解析输出...
        return []
    
    def install_skill(self, skill_ref: str) -> bool:
        """安装技能"""
        result = subprocess.run(
            ["npx", "skills", "add", skill_ref, "-g", "-y"],
            capture_output=True
        )
        return result.returncode == 0
    
    def select_model(self, task_complexity: str = "medium") -> str:
        """选择执行模型"""
        # 检查当前模型状态
        for model in self.model_priority:
            if self.is_model_available(model):
                return model
        return self.model_priority[0]
    
    def is_model_available(self, model: str) -> bool:
        """检查模型是否可用"""
        # 通过轻量请求检测
        return True
    
    def execute_subtask(self, task: dict, model: str) -> str:
        """执行子任务"""
        # 调用 sessions_spawn 或其他方式
        return ""
    
    def orchestrate(self, description: str) -> dict:
        """主编排流程"""
        # 1. 解析需求
        tasks = self.parse_requirement(description)
        
        # 2. 确保技能安装
        for task in tasks:
            skill = task["skill"]
            if not self.check_skill_installed(skill):
                print(f"发现缺失技能: {skill}")
                # 自动安装
        
        # 3. 选择模型
        model = self.select_model()
        
        # 4. 执行任务
        results = []
        for task in tasks:
            result = self.execute_subtask(task, model)
            results.append(result)
        
        # 5. 整合结果
        return {
            "tasks": tasks,
            "model_used": model,
            "results": results,
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python auto-orchestrate.py '需求描述'")
        sys.exit(1)
    
    description = sys.argv[1]
    orchestrator = SkillOrchestrator()
    result = orchestrator.orchestrate(description)
    print(json.dumps(result, indent=2))
```

## 配置

### 模型优先级配置

```json
{
  "model_priority": {
    "coding": ["kimi-coding/k2p5", "claude-sonnet"],
    "analysis": ["kimi-k2p5", "claude-opus"],
    "creative": ["claude-opus", "kimi-k2p5"],
    "fallback": "kimi-k2p5"
  },
  "auto_fallback": true,
  "fallback_threshold": 5.0
}
```

### 技能仓库源

```json
{
  "sources": [
    "https://skills.sh",
    "https://clawhub.com",
    "github:openclaw/skills"
  ]
}
```

## 使用模式

### 模式 1: 全自动 (推荐)

用户只描述需求，系统自动完成所有步骤。

**示例:**
> "把这个 Excel 里的数据分析一下，出几个图表，然后做成 PPT"

**系统自动:**
1. 发现需要 xlsx + canvas-design + pptx
2. 检查并安装缺失技能
3. 选择最佳模型
4. 执行完整流程
5. 返回 PPT 文件

### 模式 2: 半自动

用户确认后再执行关键步骤。

**示例:**
> "我想处理一些数据"

**系统响应:**
> "检测到可能需要的技能: xlsx (数据处理), canvas-design (可视化)
> 是否自动安装并执行?"

### 模式 3: 仅发现

只推荐技能，不自动安装。

**示例:**
> "有什么技能可以帮我做数据分析?"

**系统响应:**
> "找到以下技能:
> - xlsx: Excel/CSV 处理
> - canvas-design: 图表生成
> - algorithm-toolkit: 数据分析算法
> 使用 `npx skills add [技能名]` 安装"

## 注意事项

1. **权限:** 自动安装需要确认或配置免确认
2. **成本:** 多模型调用可能增加成本
3. **隐私:** 任务分发时注意数据安全
4. **回退:** 编排失败时回退到基础能力
