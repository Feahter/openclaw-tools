---
name: novel-quality-guardian
description: 小说质量守护者 - 强制锚定 + 质量门 + 迭代机制。解决长篇小说创作中的人物走样、情节重复、前后矛盾等问题。核心原理：不是AI能力不行，而是锚定信息不够。触发场景：写新章节、质检、创作质量崩塌诊断。
triggers:
  - "小说质量"
  - "写作质量"
  - "章节检查"
  - "创作质量"
  - "OOC"
  - "伏笔追踪"
source:
  project: novel-quality-guardian
  url: ""
  license: ""
  auto_generated: true
  enhanced_via: talent-mind
  updated_at: "2026-02-23"
---

# 🎯 小说质量守护者

*基于三层递归分析的问题解决技能*

---

## 核心理念

**问题诊断**：长篇小说创作质量崩塌，不是 AI 能力不行，而是**锚定信息不够**。

**解决方案**：强制锚定 + 质量门 + 迭代机制

---

## 第一层：问题表征（天才思维）

| 表层问题 | 深层根因 | 解决方案 |
|---------|---------|---------|
| 人物走样 | 写作时没有锚定人物档案 | 强制读取人物档案 |
| 内容套娃 | 没有检查"这情节写过没有" | 情节重复检测 |
| 胡编乱造 | 分镜太简略，AI自由发挥 | 扩展规范约束 |
| 前后矛盾 | 没有追踪伏笔和细节 | 伏笔池追踪 |

---

## 第二层：强制锚定注入器

### 📋 写前必读清单

每次写新章节前，**强制读取**以下信息（不是建议，是必须）：

```
┌─────────────────────────────────────────────────────┐
│  【锚定注入】写前必须读取                          │
├─────────────────────────────────────────────────────┤
│  1. 人物档案                                        │
│     - 主角性格（3个核心特质）                        │
│     - 说话方式（口头禅、语气）                       │
│     - 当前状态（正在进行的事）                       │
│                                                     │
│  2. 前3章摘要                                      │
│     - 最新情节进展                                  │
│     - 关键决定                                      │
│     - 人物关系变化                                  │
│                                                     │
│  3. 伏笔池                                         │
│     - 待回收的坑                                    │
│     - 已埋设的新伏笔                                │
│     - 本章需要回收的伏笔                            │
│                                                     │
│  4. 本章分镜脚本                                   │
│     - 场景设定                                      │
│     - 核心事件                                      │
│     - 预期爽点                                      │
└─────────────────────────────────────────────────────┘
```

### 🎯 锚定信息提取脚本

```python
# anchor_injector.py - 自动提取锚定信息

import json
import os
from pathlib import Path

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels")

def get_chapter_anchor(novel_name: str, chapter_num: int) -> dict:
    """提取指定章节的锚定信息"""
    
    novel_path = NOVEL_DIR / novel_name
    
    # 1. 读取人物档案
    char_file = novel_path / "人物档案.md"
    char_info = read_file(char_file) if char_file.exists() else ""
    
    # 2. 读取前3章摘要
    summary_file = novel_path / "auxiliary" / "summaries"
    prev_chapters = []
    for i in range(max(1, chapter_num - 3), chapter_num):
        ch_file = summary_file / f"ch{i:03d}-summary.md"
        if ch_file.exists():
            prev_chapters.append(read_file(ch_file))
    
    # 3. 读取伏笔池
    vpool_file = novel_path / "伏笔池.md"
    vpool = read_file(vpool_file) if vpool_file.exists() else ""
    
    # 4. 本章分镜
    storyboard = novel_path / "分镜" / f"ch{chapter_num:03d}.md"
    storyboard_content = read_file(storyboard) if storyboard.exists() else ""
    
    return {
        "novel": novel_name,
        "chapter": chapter_num,
        "character_profile": char_info,
        "prev_summaries": prev_chapters,
        "vpool": vpool,
        "storyboard": storyboard_content
    }

def format_anchor_prompt(anchor: dict) -> str:
    """格式化锚定提示"""
    
    prompt = f"""
╔════════════════════════════════════════════════════════════╗
║  【锚定信息】{anchor['novel']} 第{anchor['chapter']}章              ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  【人物档案】                                              ║
║  {anchor['character_profile'][:500]}...                     ║
║                                                            ║
║  【前3章摘要】                                            ║
║  {''.join(anchor['prev_summaries'][:3])}                     ║
║                                                            ║
║  【伏笔池】                                               ║
║  {anchor['vpool'][:300]}...                                 ║
║                                                            ║
║  【本章分镜】                                             ║
║  {anchor['storyboard']}                                     ║
║                                                            ║
║  ⚠️ 写作时必须遵守以上锚定，人物不得OOC！              ║
╚════════════════════════════════════════════════════════════╝
"""
    return prompt
```

---

## 第三层：质量门检测

### 🔍 写后必检清单

每章写完后，必须进行以下检测：

```
┌─────────────────────────────────────────────────────┐
│  【质量门】写后必须检测                               │
├─────────────────────────────────────────────────────┤
│  检测1: 人物OOC检测                                  │
│  □ 主角行为是否符合人物性格？                         │
│  □ 说话方式是否一致？                                │
│  □ 关键决定是否有合理动机？                          │
│                                                     │
│  检测2: 情节重复检测                                  │
│  □ 与前3章是否有类似情节？                           │
│  □ 是否在重复同一个爽点模式？                         │
│  □ 场景是否与前文重复？                              │
│                                                     │
│  检测3: 矛盾检测                                      │
│  □ 时间线是否合理？                                   │
│  □ 人物关系是否与前文一致？                          │
│  □ 已回收的伏笔是否不再出现？                         │
│                                                     │
│  检测4: 完整性检测                                   │
│  □ 本章埋设的伏笔是否记录？                          │
│  □ 是否需要回收旧伏笔？                              │
│  □ 章节结尾是否有钩子？                              │
│                                                     │
│  评分: _____ / 100                                   │
│  通过: ≥80分 / 不通过: <80分                         │
└─────────────────────────────────────────────────────┘
```

### 📊 评分算法

```python
# quality_gate.py - 质量门检测

class QualityGate:
    def __init__(self, chapter_content: str, anchor: dict):
        self.content = chapter_content
        self.anchor = anchor
        self.issues = []
        self.score = 100
    
    def check_ooc(self) -> int:
        """人物OOC检测 -30分"""
        issues = []
        
        # 检查主角名是否一致
        if self.anchor.get('main_char_name'):
            name = self.anchor['main_char_name']
            if name not in self.content:
                issues.append(f"⚠️ 主角{name}本章未出现")
        
        # 检查口头禅
        catchphrases = self.anchor.get('catchphrases', [])
        for cp in catchphrases:
            if cp not in self.content:
                issues.append(f"⚠️ 口头禅'{cp}'未出现")
        
        if issues:
            self.issues.extend(issues)
            return -30
        return 0
    
    def check_repetition(self) -> int:
        """情节重复检测 -25分"""
        issues = []
        
        # 与前章对比关键词
        prev_keywords = self.anchor.get('prev_keywords', [])
        content_keywords = set(self.content.split())
        
        overlap = prev_keywords & content_keywords
        if len(overlap) > 5:
            issues.append(f"⚠️ 与前文关键词重复: {overlap}")
        
        # 检查场景重复
        prev_scenes = self.anchor.get('prev_scenes', [])
        for scene in prev_scenes:
            if scene in self.content:
                issues.append(f"⚠️ 场景'{scene}'与前文重复")
        
        if issues:
            self.issues.extend(issues)
            return -25
        return 0
    
    def check_consistency(self) -> int:
        """矛盾检测 -25分"""
        issues = []
        
        # 检查时间线
        timeline = self.anchor.get('timeline', [])
        # ... 时间线逻辑
        
        # 检查人物关系
        relations = self.anchor.get('relations', {})
        for char, relation in relations.items():
            if f"{char}" in self.content and relation not in self.content:
                issues.append(f"⚠️ 人物{char}关系'{relation}'未体现")
        
        if issues:
            self.issues.extend(issues)
            return -25
        return 0
    
    def check_completeness(self) -> int:
        """完整性检测 -20分"""
        issues = []
        
        # 检查伏笔记录
        if not self.anchor.get('vpool_updated'):
            issues.append("⚠️ 伏笔池未更新")
        
        # 检查钩子
        if '下章' not in self.content and '下一章' not in self.content:
            issues.append("⚠️ 章节结尾无钩子")
        
        if issues:
            self.issues.extend(issues)
            return -20
        return 0
    
    def run_all_checks(self) -> dict:
        """运行所有检测"""
        
        self.score += self.check_ooc()
        self.score += self.check_repetition()
        self.score += self.check_consistency()
        self.score += self.check_completeness()
        
        self.score = max(0, self.score)  # 最低0分
        
        return {
            "score": self.score,
            "pass": self.score >= 80,
            "issues": self.issues,
            "recommendation": "通过" if self.score >= 80 else "需要重写"
        }
```

---

## 第四层：迭代机制

### 🔄 不达标 → 重写循环

```
质量门检测
    ↓
[评分 ≥ 80?] ──是──→ ✅ 通过 → 更新锚定 → 结束
    ↓ 否
┌───────────────────────┐
│  问题列表              │
│  1. xxx              │
│  2. xxx              │
│  3. xxx              │
└───────────────────────┘
    ↓
根据问题重写
    ↓
再次通过质量门
    ↓
[评分 ≥ 80?] ──是──→ ✅ 通过
    ↓ 否
[迭代次数 < 3?] ──是──→ 继续重写
    ↓ 否
⚠️ 标记需要人工介入
```

### 📈 迭代记录

```python
# iteration_tracker.py - 迭代追踪

class IterationTracker:
    def __init__(self, novel: str, chapter: int):
        self.novel = novel
        self.chapter = chapter
        self.iterations = []
    
    def add_attempt(self, score: int, issues: list):
        self.iterations.append({
            "attempt": len(self.iterations) + 1,
            "score": score,
            "issues": issues
        })
    
    def should_stop(self) -> bool:
        """是否停止迭代"""
        if len(self.iterations) >= 3:
            return True
        if self.iterations and self.iterations[-1]['score'] >= 80:
            return True
        return False
    
    def get_report(self) -> str:
        """生成迭代报告"""
        report = f"""
=== {self.novel} 第{self.chapter}章 迭代报告 ===

迭代次数: {len(self.iterations)}
最终得分: {self.iterations[-1]['score'] if self.iterations else 'N/A'}
状态: {'✅ 通过' if self.iterations and self.iterations[-1]['score'] >= 80 else '⚠️ 需人工介入'}

迭代详情:
"""
        for i, it in enumerate(self.iterations):
            report += f"  第{i+1}次: {it['score']}分 - {it['issues']}\n"
        
        return report
```

---

## 使用流程

### 1. 触发技能

当用户要求写新章节时：
```
用户: "帮我写重生之我是神豪 第101章"
```

### 2. 提取锚定信息

```bash
python anchor_injector.py "重生之我是神豪" 101
```

### 3. 生成带锚定的写作提示

将锚定信息注入 prompt，生成初稿。

### 4. 质量门检测

```bash
python quality_gate.py --chapter ch101.md --novel "重生之我是神豪"
```

### 5. 迭代或通过

- 评分 ≥80 → 更新伏笔池 → 结束
- 评分 <80 → 标记问题 → 重写 → 回到步骤4

---

## 配套文件

| 文件 | 功能 |
|------|------|
| `anchor_injector.py` | 提取锚定信息 |
| `quality_gate.py` | 质量门检测 |
| `iteration_tracker.py` | 迭代追踪 |
| `vpool_manager.py` | 伏笔池管理 |

---

## 核心原则

1. **强制锚定** - 写前必须读取，不是建议
2. **质量门** - 写后必须检测，不是敷衍
3. **迭代** - 不达标就重写，不是凑合
4. **记录** - 每次迭代都记录，便于复盘

---

*这个技能解决的不是"AI能力"问题，而是"锚定信息不够"的执行机制问题。*
