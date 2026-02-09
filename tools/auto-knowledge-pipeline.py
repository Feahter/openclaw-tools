#!/usr/bin/env python3
"""
自动知识获取管道 - 心跳任务执行脚本
每小时自动搜索、评估、生成Skills，无需人工干预
"""

import asyncio
import json
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 路径配置
WORKSPACE = Path.home() / ".openclaw/workspace"
CONFIG_PATH = WORKSPACE / "config/auto-knowledge.yaml"
STATE_PATH = WORKSPACE / "data/auto-knowledge-state.json"
SKILLS_DIR = WORKSPACE / "skills"
LOG_DIR = WORKSPACE / "data/logs/auto-knowledge"
NOTES_DIR = WORKSPACE / "memory/auto-knowledge-notes"

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {level}: {message}"
    print(log_line)
    
    # 写入日志文件
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def load_state() -> dict:
    """加载状态文件"""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {
        "last_run": None,
        "search_history": [],
        "current_rotation_index": 0,
        "daily_stats": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "searches": 0,
            "skills_generated": 0,
            "notes_created": 0,
            "rejected": 0
        },
        "keyword_pool": [
            {"category": "开发工具", "terms": ["cli tool", "developer tools", "git workflow"]},
            {"category": "数据处理", "terms": ["data processing", "etl pipeline", "data validation"]},
            {"category": "API集成", "terms": ["api client", "rest api", "graphql"]},
            {"category": "自动化", "terms": ["automation", "workflow", "scheduler"]},
            {"category": "AI应用", "terms": ["llm tools", "ai automation", "rag pipeline"]},
            {"category": "文档处理", "terms": ["pdf processing", "markdown tools"]},
            {"category": "系统监控", "terms": ["monitoring", "log analysis", "health check"]},
            {"category": "安全工具", "terms": ["security scanner", "secrets management"]}
        ]
    }

def save_state(state: dict):
    """保存状态文件"""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def select_next_keyword(state: dict) -> str:
    """选择下一个搜索关键词（轮换）"""
    pool = state.get("keyword_pool", [])
    if not pool:
        return "automation tools"
    
    idx = state.get("current_rotation_index", 0)
    category = pool[idx % len(pool)]
    term = random.choice(category["terms"])
    
    # 更新索引
    state["current_rotation_index"] = (idx + 1) % len(pool)
    
    return term

def has_recent_search(state: dict, keyword: str, hours: int = 24) -> bool:
    """检查关键词是否在近期搜索过"""
    cutoff = datetime.now() - timedelta(hours=hours)
    for entry in state.get("search_history", []):
        if entry.get("keyword") == keyword:
            entry_time = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
            if entry_time > cutoff:
                return True
    return False

async def search_github(keyword: str, min_stars: int = 100) -> List[Dict]:
    """搜索GitHub项目（使用web_fetch）"""
    import urllib.parse
    
    query = urllib.parse.quote(f"{keyword} stars:>{min_stars}")
    url = f"https://github.com/search?q={query}&type=repositories&s=stars&o=desc"
    
    log(f"搜索GitHub: {keyword}")
    
    # 这里实际应该调用 web_fetch，但在心跳脚本中我们通过系统调用
    # 简化版本：返回模拟数据用于测试
    # 实际部署时应该调用 openclaw 的 web_fetch 工具
    
    # 返回示例结构
    return [
        {
            "name": f"example-{keyword.replace(' ', '-')}",
            "url": f"https://github.com/example/{keyword.replace(' ', '-')}",
            "stars": random.randint(500, 15000),
            "last_update": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
            "license": random.choice(["MIT", "Apache-2.0", "GPL", ""]),
            "description": f"A tool for {keyword}"
        }
    ]

def calculate_project_score(project: dict) -> tuple:
    """计算项目质量分数"""
    scores = {}
    
    # Stars (25%)
    stars = project.get("stars", 0)
    if stars >= 10000: scores["stars"] = 5.0
    elif stars >= 5000: scores["stars"] = 4.5
    elif stars >= 2000: scores["stars"] = 4.0
    elif stars >= 1000: scores["stars"] = 3.5
    elif stars >= 500: scores["stars"] = 3.0
    elif stars >= 100: scores["stars"] = 2.0
    else: scores["stars"] = 1.0
    
    # Activity (25%)
    last_update = datetime.fromisoformat(project.get("last_update", "2000-01-01"))
    days_ago = (datetime.now() - last_update).days
    if days_ago <= 7: scores["activity"] = 5.0
    elif days_ago <= 30: scores["activity"] = 4.5
    elif days_ago <= 90: scores["activity"] = 4.0
    elif days_ago <= 180: scores["activity"] = 3.0
    elif days_ago <= 365: scores["activity"] = 2.0
    else: scores["activity"] = 1.0
    
    # Documentation (20%) - 简化估计
    scores["documentation"] = 3.5  # 默认中等
    
    # Community (15%) - 简化估计
    scores["community"] = 3.5  # 默认中等
    
    # License (15%)
    license = project.get("license", "").lower()
    if license in ["mit", "apache-2.0", "bsd"]: scores["license"] = 5.0
    elif license in ["gpl", "lgpl"]: scores["license"] = 3.0
    elif license: scores["license"] = 2.0
    else: scores["license"] = 1.0
    
    # 加权计算
    weights = {"stars": 0.25, "activity": 0.25, "documentation": 0.20, 
               "community": 0.15, "license": 0.15}
    final_score = sum(scores[k] * weights[k] for k in weights)
    
    return round(final_score, 2), scores

def auto_select_project(projects: List[Dict], min_score: float = 3.5) -> Dict:
    """自动选择最佳项目"""
    qualified = [p for p in projects if p.get("score", 0) >= min_score]
    
    if not qualified:
        max_score = max((p.get("score", 0) for p in projects), default=0)
        return {
            "action": "reject",
            "reason": "no_qualified_projects",
            "max_score": max_score
        }
    
    qualified.sort(key=lambda x: x.get("score", 0), reverse=True)
    best = qualified[0]
    
    if best["score"] >= 4.0:
        return {
            "action": "select",
            "project": best,
            "confidence": "high",
            "reason": f"高分项目 ({best['score']}/5)"
        }
    elif len(qualified) >= 2:
        second = qualified[1]
        if best["score"] - second["score"] >= 0.5:
            return {
                "action": "select",
                "project": best,
                "confidence": "medium",
                "reason": f"明显优于备选"
            }
        else:
            selected = best if best["stars"] >= second["stars"] else second
            return {
                "action": "select",
                "project": selected,
                "confidence": "medium",
                "reason": "社区规模更大"
            }
    else:
        return {
            "action": "select",
            "project": best,
            "confidence": "low",
            "reason": "唯一合格选项"
        }

def generate_skill_name(project_name: str) -> str:
    """生成skill名称 - 从项目名提取"""
    # 从项目名提取，如 "example-data-processing" → "data-processing"
    name = project_name.lower()
    # 移除 "example-" 前缀
    if name.startswith("example-"):
        name = name[8:]
    # 只保留字母和连字符
    name = re.sub(r'[^a-z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name or "auto-generated-skill"

def generate_skill_content(project: dict, methodology: dict) -> str:
    """生成SKILL.md内容"""
    skill_name = generate_skill_name(project.get("name", "auto-skill"))
    timestamp = datetime.now().isoformat()
    
    # 从项目名生成描述
    project_name = project.get("name", "auto-skill")
    description = project_name.replace("-", " ").replace("_", " ").title()
    
    content = f"""---
name: {skill_name}
description: {description} - {project.get('license', 'Open Source')}
triggers:
  - "{skill_name}"
  - "{project_name}"
source:
  project: {project.get("name")}
  url: {project.get("url")}
  license: {project.get("license", "Unknown")}
  auto_generated: true
  generated_at: {timestamp}
  score: {project.get("score", 0)}
---

# {description}

自动生成的Skill，基于 [{project.get("name")}]({project.get("url")}) 的方法论。

## 核心方法

1. 分析需求
2. 提取关键参数
3. 执行核心逻辑
4. 验证输出

## 使用场景

- {description} 相关任务

## 质量标准

- 输入清晰明确
- 输出可验证
- 过程可追溯

## 注意事项

*本Skill由 auto-knowledge-acquisition 系统自动生成*
*来源: {project.get('url')}*
*生成时间: {timestamp}*
*项目评分: {project.get('score', 0)}/5*
"""
    return content

def record_history(state: dict, keyword: str, result: dict):
    """记录搜索历史"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "keyword": keyword,
        "result": result
    }
    state["search_history"].append(entry)
    
    # 只保留最近100条
    if len(state["search_history"]) > 100:
        state["search_history"] = state["search_history"][-100:]

def update_daily_stats(state: dict, action: str):
    """更新每日统计"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = state.get("daily_stats", {})
    
    if stats.get("date") != today:
        stats = {"date": today, "searches": 0, "skills_generated": 0, 
                "notes_created": 0, "rejected": 0}
    
    stats["searches"] = stats.get("searches", 0) + 1
    
    if action == "skill":
        stats["skills_generated"] = stats.get("skills_generated", 0) + 1
    elif action == "note":
        stats["notes_created"] = stats.get("notes_created", 0) + 1
    elif action == "reject":
        stats["rejected"] = stats.get("rejected", 0) + 1
    
    state["daily_stats"] = stats

async def main():
    """主执行流程"""
    log("=" * 50)
    log("启动自动知识获取管道")
    
    try:
        # 1. 加载状态
        state = load_state()
        
        # 2. 选择关键词
        keyword = select_next_keyword(state)
        
        # 检查是否近期搜索过
        if has_recent_search(state, keyword):
            log(f"关键词 '{keyword}' 24小时内已搜索，跳过", "SKIP")
            return
        
        log(f"当前关键词: {keyword}")
        
        # 3. 搜索项目（模拟）
        projects = await search_github(keyword)
        log(f"找到 {len(projects)} 个项目")
        
        if not projects:
            record_history(state, keyword, {"action": "skip", "reason": "no_results"})
            update_daily_stats(state, "reject")
            save_state(state)
            return
        
        # 4. 评分
        for project in projects:
            score, details = calculate_project_score(project)
            project["score"] = score
            project["score_details"] = details
            log(f"项目评分: {project['name']} = {score}/5")
        
        # 5. 自动选择
        decision = auto_select_project(projects)
        log(f"决策: {decision['action']} - {decision.get('reason', '')}")
        
        if decision["action"] == "reject":
            record_history(state, keyword, decision)
            update_daily_stats(state, "reject")
            save_state(state)
            return
        
        # 6. 生成Skill（简化版，实际应深入研究）
        project = decision["project"]
        
        # 检查是否已存在同名Skill
        skill_name = generate_skill_name(project.get("name", ""))
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        
        if skill_path.exists():
            log(f"Skill '{skill_name}' 已存在，跳过", "SKIP")
            record_history(state, keyword, {"action": "skip", "reason": "already_exists"})
            save_state(state)
            return
        
        # 生成内容
        skill_content = generate_skill_content(project, {})
        
        # 保存
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(skill_content)
        log(f"✅ 生成Skill: {skill_path}")
        
        # 记录
        record_history(state, keyword, {
            "action": "generated_skill",
            "project": project["name"],
            "score": project["score"],
            "skill_name": skill_name
        })
        update_daily_stats(state, "skill")
        
        # 7. 保存状态
        save_state(state)
        
        # 8. 打印统计
        stats = state["daily_stats"]
        log(f"今日统计: 搜索{stats['searches']}次, 生成{stats['skills_generated']}个Skill, "
            f"笔记{stats['notes_created']}个, 跳过{stats['rejected']}次")
        
    except Exception as e:
        log(f"执行出错: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
    
    log("完成")
    log("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
