#!/usr/bin/env python3
"""
AQA 自动决策器 - 我来决定是否创建 Skills

工作流程：
1. 加载 AQA 发现的高分项目
2. 我评估并决定是否创建
3. 直接创建 Skills（不调用 GitHub API，使用建议池已有信息）
"""

import json
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


def skill_exists(name: str) -> bool:
    """检查 Skill 是否已存在"""
    return (SKILLS_DIR / name).exists()


def create_skill(project: dict) -> bool:
    """创建 Skill（使用建议池已有信息）"""
    name = project.get("name", "")
    url = project.get("url", "")
    score = project.get("score", 0)
    stars = project.get("stars", 0)
    
    skill_dir = SKILLS_DIR / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # 描述（截取）
    description = project.get("reason", "").replace('"', "'")[:200]
    if not description:
        description = f"Auto-generated skill for {name}"
    
    skill_md = f"""---
name: {name}
description: "{description}"
triggers:
  - "{name}"
  - "{name.replace('-', ' ').replace('_', ' ')}"
source:
  project: {name}
  url: {url}
  auto_generated: true
  generated_at: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
  score: {score}
---

# {name.replace('-', ' ').replace('_', ' ').title()}

Auto-generated skill from GitHub project.

## 项目信息

- **Stars**: {stars}
- **Score**: {score}
- **URL**: {url}

## 使用方式

（请根据项目 README 补充使用方式）

## 注意事项

*本 Skill 由 AQA 自动创建*
*创建时间: {datetime.now().strftime('%Y-%m-%d')}*
"""

    (skill_dir / "SKILL.md").write_text(skill_md)

    # 生成 _meta.json
    meta = {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": "AQA-Auto",
        "category": "auto-generated",
        "tags": ["auto-generated"],
        "capabilities": ["待补充"],
        "scripts": [],
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "source_url": url,
        "stars": stars,
        "score": score,
    }

    (skill_dir / "_meta.json").write_text(json.dumps(meta, indent=2))

    return True


def evaluate_project(project: dict) -> tuple:
    """
    我来评估项目是否值得创建 Skill

    返回: (是否创建, 原因)
    """
    name = project.get("name", "").lower()
    score = project.get("score", 0)
    stars = project.get("stars", 0)

    reasons = []

    # 1. 分数检查
    if score >= MY_MIN_SCORE:
        reasons.append(f"高分 ({score:.1f})")
    else:
        return False, f"分数太低 ({score:.1f})"

    # 2. Stars 检查
    if stars >= 5000:
        reasons.append(f"高Stars ({stars})")
    elif stars >= MY_MIN_STARS:
        reasons.append(f"Stars OK ({stars})")
    else:
        return False, "Stars 太低"

    # 3. 排除 example/demo/test
    excluded = ["example", "demo", "test", "sample"]
    if any(e in name for e in excluded):
        return False, "示例项目"

    # 4. 检查是否已存在
    if skill_exists(name):
        return False, "已存在"

    # 5. 排除模板/启动项目
    useless_patterns = ["-starter", "-boilerplate", "-template", "awesome-"]
    if any(pattern in name for pattern in useless_patterns):
        return False, "模板/启动项目"

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
    log(f"   - 排除 example/demo/test/模板")
    log(f"   - Skill 不存在")

    # 2. 评估每个项目
    decisions = []
    skipped = []

    for project in suggestions:
        name = project.get("name", "unknown")

        should_create, reason = evaluate_project(project)

        if should_create:
            decisions.append((name, project, reason))
        else:
            skipped.append((name, reason))

    # 3. 创建 Skills
    log(f"\n✅ 决定创建 {len(decisions)} 个 Skills:")

    created = []
    for name, project, reason in decisions:
        log(f"\n📦 {name}")
        log(f"   原因: {reason}")

        if create_skill(project):
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

        # 显示跳过的
        if skipped:
            log(f"\n⏭️  跳过 {len(skipped)} 个:")
            for name, reason in skipped[:10]:
                log(f"   - {name}: {reason}")
            if len(skipped) > 10:
                log(f"   ... 还有 {len(skipped) - 10} 个")
    else:
        log("\n⚠️  没有创建任何 Skills")

        if skipped:
            log(f"\n⏭️  跳过 {len(skipped)} 个:")
            for name, reason in skipped[:10]:
                log(f"   - {name}: {reason}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
