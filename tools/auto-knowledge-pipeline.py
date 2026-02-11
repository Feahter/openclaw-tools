#!/usr/bin/env python3
"""
自动知识获取管道 - 研究模式
只搜索、研究、记录笔记。不自动生成 Skills。
"""

import json
import random
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 路径配置
WORKSPACE = Path.home() / ".openclaw/workspace"
CONFIG_PATH = WORKSPACE / "config/auto-knowledge.yaml"
STATE_PATH = WORKSPACE / "data/auto-knowledge-state.json"
LOG_DIR = WORKSPACE / "data/logs/auto-knowledge"
NOTES_DIR = WORKSPACE / "memory/auto-knowledge-notes"
SUGGESTIONS_FILE = WORKSPACE / "data/sqm/skill-suggestions.json"

# 质量阈值（提高门槛）
MIN_SCORE = 2.5  # 降低阈值，让更多项目进入待创建列表
MIN_STARS = 500   # 原来是 100

def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")
    
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {level}: {message}\n")

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
            "high_score_projects": 0,
            "notes_created": 0,
            "skipped": 0
        }
    }

def save_state(state: dict):
    """保存状态文件"""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def select_next_keyword(state: dict) -> str:
    """选择下一个搜索关键词"""
    pool = [
        {"category": "开发工具", "terms": ["cli tool", "developer tools", "git workflow"]},
        {"category": "数据处理", "terms": ["data processing", "etl pipeline", "data validation"]},
        {"category": "API集成", "terms": ["api client", "rest api", "graphql"]},
        {"category": "自动化", "terms": ["automation", "workflow", "scheduler"]},
        {"category": "AI应用", "terms": ["llm tools", "ai automation", "rag pipeline"]},
        {"category": "文档处理", "terms": ["pdf processing", "markdown tools"]},
        {"category": "系统监控", "terms": ["monitoring", "log analysis", "health check"]},
        {"category": "安全工具", "terms": ["security scanner", "secrets management"]}
    ]
    
    idx = state.get("current_rotation_index", 0)
    category = pool[idx % len(pool)]
    term = random.choice(category["terms"])
    state["current_rotation_index"] = (idx + 1) % len(pool)
    
    return term

def has_recent_search(state: dict, keyword: str, hours: int = 24) -> bool:
    """检查关键词是否在近期搜索过"""
    cutoff = datetime.now().timestamp() - (hours * 3600)
    for entry in state.get("search_history", []):
        if entry.get("keyword") == keyword:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", "2000-01-01")).timestamp()
                if entry_time > cutoff:
                    return True
            except:
                pass
    return False

def calculate_project_score(project: dict) -> float:
    """计算项目质量分数 (0-5)"""
    stars = project.get("stars", 0)
    score = 0
    
    # Stars 评分 (40%)
    if stars >= 10000:
        score += 2.0
    elif stars >= 5000:
        score += 1.8
    elif stars >= 2000:
        score += 1.5
    elif stars >= 1000:
        score += 1.2
    elif stars >= 500:
        score += 1.0
    else:
        score += 0.5
    
    # 活跃度评分 (30%)
    # 假设有 updated_at 字段
    updated_at = project.get("updated_at", "")
    if updated_at:
        try:
            from dateutil import parser
            days_ago = (datetime.now() - parser.parse(updated_at)).days
            if days_ago <= 7:
                score += 1.5
            elif days_ago <= 30:
                score += 1.2
            elif days_ago <= 90:
                score += 0.9
            else:
                score += 0.3
        except:
            score += 0.5
    else:
        score += 0.5
    
    # 许可证友好度 (15%)
    license = project.get("license", "").lower()
    if license in ["mit", "apache-2.0", "bsd", "unlicense"]:
        score += 0.75
    elif license in ["gpl", "lgpl", "agpl"]:
        score += 0.3
    else:
        score += 0.3
    
    # 是否 example 项目 (15%) - 扣分项
    name = project.get("name", "").lower()
    if "example" in name or "demo" in name or "test" in name:
        score -= 0.5
    
    return max(0, min(5, score))

def search_github(keyword: str) -> List[Dict]:
    """搜索GitHub项目（使用 GitHub API）"""
    projects = []
    
    try:
        import subprocess
        import json
        
        # 使用 curl 调用 GitHub API
        query = urllib.parse.quote(f"{keyword} stars:>{MIN_STARS}")
        url = f'https://api.github.com/search/repositories?q={query}&sort=stars&per_page=10'
        
        cmd = f'curl -s "{url}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            items = data.get("items", [])
            
            for p in items:
                projects.append({
                    "name": p.get("name", ""),
                    "url": p.get("html_url", ""),
                    "stars": p.get("stargazers_count", 0),
                    "description": p.get("description", ""),
                    "updated_at": p.get("updated_at", ""),
                    "license": p.get("license", {}).get("spdx_id", "") if p.get("license") else ""
                })
    except Exception as e:
        log(f"搜索失败: {e}", "ERROR")
    
    return projects

def generate_note_content(project: dict, score: float) -> str:
    """生成学习笔记内容"""
    name = project.get("name", "unknown").replace("-", " ").replace("_", " ").title()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
title: "{name}"
source_url: "{project.get('url', '')}"
stars: {project.get('stars', 0)}
score: {score:.2f}/5.0
researched_at: {timestamp}
tags: ["research", "auto-knowledge"]
---

# {name}

## 项目信息

- **URL**: [{project.get('url', 'N/A')}]({project.get('url', 'N/A')})
- **Stars**: {project.get('stars', 0)}
- **License**: {project.get('license', 'Unknown')}
- **评分**: {score:.2f}/5.0

## 研究摘要

### 核心功能

（此处记录项目核心功能）

### 使用场景

（此处记录适用场景）

### 优缺点

**优点**:
- 

**缺点**:
- 

## 创建建议

"""
    
    # 根据评分添加建议
    if score >= 4.5:
        content += "## ⭐⭐⭐ 强烈建议创建 Skill\n\n这是一个高质量项目，建议使用 `skill-from-github` 创建完整 Skill。\n"
    elif score >= 4.0:
        content += "## ⭐⭐ 建议创建 Skill\n\n项目质量不错，可以考虑创建 Skill。\n"
    else:
        content += "## ⭐ 可选\n\n项目一般，仅作为学习参考。\n"
    
    content += f"""
---

*研究时间: {timestamp}*
*来源: auto-knowledge-acquisition*
"""
    
    return content

def add_suggestion(project: dict, score: float):
    """添加创建建议"""
    suggestions = []
    if SUGGESTIONS_FILE.exists():
        try:
            with open(SUGGESTIONS_FILE) as f:
                suggestions = json.load(f)
        except:
            suggestions = []
    
    # 检查是否已存在
    for s in suggestions:
        if s.get("url") == project.get("url"):
            return  # 已存在
    
    if score >= MIN_SCORE:
        suggestions.append({
            "name": project.get("name", ""),
            "url": project.get("url", ""),
            "stars": project.get("stars", 0),
            "score": score,
            "added_at": datetime.now().isoformat(),
            "reason": "高分项目，建议创建 Skill"
        })
        
        # 保存
        SUGGESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SUGGESTIONS_FILE, "w") as f:
            json.dump(suggestions, f, indent=2)
        
        log(f"📝 添加建议: {project.get('name')} (分数: {score:.2f})")
    else:
        log(f"  ⏭️ 分数不足，跳过: {project.get('name')} ({score:.2f})")

def main():
    """主执行流程"""
    log("=" * 50)
    log("启动自动知识获取管道（研究模式）")
    
    state = load_state()
    
    # 1. 选择关键词
    keyword = select_next_keyword(state)
    log(f"搜索关键词: {keyword}")
    
    # 检查近期搜索
    if has_recent_search(state, keyword):
        log(f"跳过: {keyword} 在24小时内已搜索", "WARNING")
        if "skipped" not in state["daily_stats"]:
            state["daily_stats"]["skipped"] = 0
        state["daily_stats"]["skipped"] += 1
        save_state(state)
        return
    
    # 2. 搜索 GitHub
    log("搜索 GitHub...")
    projects = search_github(keyword)
    log(f"找到 {len(projects)} 个项目")
    
    if not projects:
        log("无结果，跳过")
        return
    
    # 3. 评分并选择
    high_score_count = 0
    
    for project in projects[:5]:  # 只处理前5个
        score = calculate_project_score(project)
        project["score"] = score
        
        log(f"  {project.get('name', 'N/A')}: {score:.2f}/5.0 ({project.get('stars', 0)} ⭐)")
        
        # 高分项目
        if score >= MIN_SCORE:
            high_score_count += 1
            
            # 4. 保存笔记
            note_content = generate_note_content(project, score)
            note_name = f"{project.get('name', 'unknown')}.md"
            note_path = NOTES_DIR / f"{datetime.now().strftime('%Y-%m-%d')}"
            note_path.mkdir(parents=True, exist_ok=True)
            note_path = note_path / note_name
            
            with open(note_path, "w") as f:
                f.write(note_content)
            
            log(f"  ✅ 保存笔记: {note_path.name}")
            
            # 5. 添加创建建议
            add_suggestion(project, score)
            
            state["daily_stats"]["notes_created"] += 1
    
    # 记录历史
    state["search_history"].append({
        "timestamp": datetime.now().isoformat(),
        "keyword": keyword,
        "projects_found": len(projects),
        "high_score": high_score_count
    })
    
    # 更新统计
    state["daily_stats"]["searches"] += 1
    state["daily_stats"]["high_score_projects"] += high_score_count
    
    save_state(state)
    
    # 6. 打印统计
    stats = state["daily_stats"]
    log(f"今日统计: 搜索{stats['searches']}次, 高分{stats['high_score_projects']}个, "
        f"笔记{stats['notes_created']}个")
    
    log("完成")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 测试模式
        print("测试模式运行...")
        state = load_state()
        keyword = select_next_keyword(state)
        print(f"选择的关键词: {keyword}")
    else:
        main()
