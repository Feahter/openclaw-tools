#!/usr/bin/env python3
"""
AQA 自动决策器 - 我来决定是否创建 Skills

工作流程：
1. 加载 AQA 发现的高分项目
2. 我评估并决定是否创建
3. 直接创建 Skills
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
SUGGESTIONS_FILE = WORKSPACE / "data" / "sqm" / "skill-suggestions.json"
SKILLS_DIR = WORKSPACE / "skills"

# 我的判断标准
MY_MIN_SCORE = 3.0  # 我创建分数 >= 3.0 的项目
MY_MIN_STARS = 1000  # 至少 1000 stars


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def load_suggestions():
    """加载创建建议"""
    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE) as f:
            return json.load(f)
    return []


def get_github_info(url: str) -> dict:
    """获取 GitHub 项目详细信息"""
    # 从 URL 提取 owner/repo
    parts = url.rstrip("/").split("/")
    repo = parts[-1] if parts else ""
    owner = parts[-2] if len(parts) >= 2 else ""
    
    # 调用 GitHub API
    cmd = f'curl -s "https://api.github.com/repos/{owner}/{repo}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        try:
            import json
            data = json.loads(result.stdout)
            return {
                "name": data.get("name", repo),
                "full_name": data.get("full_name", f"{owner}/{repo}"),
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language", ""),
                "license": data.get("license", {}).get("spdx_id", "") if data.get("license") else "",
                "updated_at": data.get("updated_at", ""),
                "html_url": data.get("html_url", url),
            }
        except:
            pass
    
    return {"name": repo, "html_url": url}


def skill_exists(name: str) -> bool:
    """检查 Skill 是否已存在"""
    return (SKILLS_DIR / name).exists()


def create_skill(name: str, info: dict) -> bool:
    """创建 Skill"""
    skill_dir = SKILLS_DIR / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成 SKILL.md
    description = info.get("description", "").replace('"', "'")[:200]
    license = info.get("license", "Unknown")
    stars = info.get("stars", 0)
    url = info.get("html_url", "")
    
    skill_md = f"""---
name: {name}
description: "{description}"
triggers:
  - "{name}"
  - "{info.get('full_name', '').split('/')[-1] if '/' in info.get('full_name', '') else name}"
source:
  project: {info.get('full_name', '')}
  url: {url}
  license: {license}
  auto_generated: true
  generated_at: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
  score: {info.get('score', 0)}
---

# {info.get('name', name).replace('-', ' ').replace('_', ' ').title()}

基于 [{info.get('full_name', '项目')}]({url}) 创建的 Skill。

## 项目信息

- **Stars**: {stars}
- **License**: {license}
- **语言**: {info.get('language', 'N/A')}

## 描述

{description}

## 使用方式

（请根据项目 README 补充使用方式）

## 注意事项

*本 Skill 由 AQA 自动创建*
*创建时间: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    # 写入文件
    (skill_dir / "SKILL.md").write_text(skill_md)
    
    # 生成 _meta.json
    import json
    meta = {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": "AQA-Auto",
        "category": "auto-generated",
        "tags": ["auto-generated", info.get("language", "").lower()],
        "capabilities": ["待补充"],
        "scripts": [],
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "source_url": url,
        "stars": stars,
    }
    
    (skill_dir / "_meta.json").write_text(json.dumps(meta, indent=2))
    
    return True


def evaluate_project(project: dict) -> tuple:
    """
    我来评估项目是否值得创建 Skill
    
    返回: (是否创建, 原因)
    """
    name = project.get("name", "").lower()
    url = project.get("url", "")
    score = project.get("score", 0)
    stars = project.get("stars", 0)
    
    reasons = []
    
    # 1. 分数检查
    if score >= MY_MIN_SCORE:
        reasons.append(f"高分 ({score:.1f})")
    elif score >= 4.0:
        reasons.append(f"分数可接受 ({score:.1f})")
    else:
        return False, "分数太低"
    
    # 2. Stars 检查
    if stars >= 5000:
        reasons.append(f"高Stars ({stars})")
    elif stars >= MY_MIN_STARS:
        reasons.append(f"Stars OK ({stars})")
    else:
        return False, "Stars 太低"
    
    # 3. 排除 example/demo/test
    if "example" in name or "demo" in name or "test" in name or "sample" in name:
        return False, "示例项目"
    
    # 4. 检查是否已存在
    if skill_exists(name):
        return False, "已存在"
    
    # 5. 价值判断
    valuable_keywords = [
        "cli", "tool", "automation", "workflow", "generator",
        "parser", "converter", "validator", "builder", "framework",
        "client", "sdk", "wrapper", "integration", "api",
        "scraper", "crawler", "extractor", "processor"
    ]
    
    is_valuable = any(kw in name for kw in valuable_keywords)
    if not is_valuable:
        return False, "看起来没什么用"
    
    return True, "; ".join(reasons)


def main():
    """主流程"""
    print("=" * 60)
    print("🤖 AQA 自动决策器 - 我来决定")
    print("=" * 60)
    
    # 1. 加载建议
    suggestions = load_suggestions()
    log(f"📋 发现 {len(suggestions)} 个待评估项目")
    
    if not suggestions:
        log("无待处理项目")
        return
    
    log(f"\n🎯 我的评估标准:")
    log(f"   - 分数 >= {MY_MIN_SCORE}")
    log(f"   - Stars >= {MY_MIN_STARS}")
    log(f"   - 排除 example/demo/test")
    log(f"   - 有实际使用价值")
    log(f"   - Skill 不存在")
    
    # 2. 评估每个项目
    decisions = []
    skipped = []
    
    for project in suggestions:
        name = project.get("name", "unknown")
        url = project.get("url", "")
        
        should_create, reason = evaluate_project(project)
        
        if should_create:
            # 获取详细信息
            info = get_github_info(url)
            info["score"] = project.get("score", 0)
            decisions.append((name, info, reason))
        else:
            skipped.append((name, reason))
    
    # 3. 创建 Skills
    log(f"\n✅ 决定创建 {len(decisions)} 个 Skills:")
    
    created = []
    for name, info, reason in decisions:
        log(f"\n📦 {name}")
        log(f"   原因: {reason}")
        
        if create_skill(name, info):
            created.append(name)
            log(f"   ✅ 创建成功")
        else:
            log(f"   ❌ 创建失败")
    
    # 4. 清理已创建的
    if created:
        remaining = [s for s in suggestions if s.get("name") not in created]
        with open(SUGGESTIONS_FILE, "w") as f:
            json.dump(remaining, f, indent=2)
        
        log(f"\n✅ 完成! 创建 {len(created)} 个 Skills")
        for name in created:
            log(f"   - {name}")
        
        # 如果有跳过的
        if skipped:
            log(f"\n⏭️  跳过 {len(skipped)} 个:")
            for name, reason in skipped[:5]:  # 只显示前5个
                log(f"   - {name}: {reason}")
            if len(skipped) > 5:
                log(f"   ... 还有 {len(skipped) - 5} 个")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
