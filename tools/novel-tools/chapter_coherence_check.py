#!/usr/bin/env python3
"""
小说章节衔接自动检查工具
检查5项衔接问题：场景/时间/情绪/因果/信息连续性

用法:
    python chapter_coherence_check.py <章节文件路径>
    python chapter_coherence_check.py <上一章文件路径> <本章文件路径>
"""

import re
import sys
from pathlib import Path

# 常见场景跳跃模式
SCENE_JUMP_PATTERNS = [
    r"^(于是|然后|接着|之后|突然)$",
    r"^(与此同时|就在这时候|就在此时)$",
]

# 时间跳跃模式（无过渡）
TIME_JUMP_NO_TRANSITION = [
    r"^第二天$",
    r"^第三天$",
    r"^几天后$",
    r"^几个小时后$",
    r"^半小时后$",
]

# 情绪断崖模式
EMOTION_WHIPLASH = [
    (r"(开心|高兴|兴奋|激动)", r"(难过|悲伤|沮丧|愤怒)", 0.3),
    (r"(害怕|恐惧|担心)", r"(开心|高兴|大笑)", 0.3),
]

# 章节类型关键词
CHAPTER_TYPE_KEYWORDS = {
    "关键章": ["死亡", "牺牲", "决战", "高潮", "表白", "决裂", "反转", "揭露", "突破", "升级"],
    "日常章": ["早上", "下午", "晚上", "吃饭", "睡觉", "聊天", "学习", "修炼"],
}


def load_chapter(path: str) -> str:
    """加载章节内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_first_para(text: str) -> str:
    """提取第一段"""
    paras = text.split('\n\n')
    for p in paras:
        if p.strip():
            return p.strip()[:200]
    return ""


def extract_last_para(text: str) -> str:
    """提取最后一段"""
    paras = text.split('\n\n')
    for p in reversed(paras):
        if p.strip():
            return p.strip()[:200]
    return ""


def check_scene_transition(text: str) -> list:
    """检查场景连续性"""
    issues = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 检测无过渡的场景跳跃
        for pattern in SCENE_JUMP_PATTERNS:
            if re.match(pattern, line):
                # 检查前一句是否有关联
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if not any(kw in prev_line for kw in ["因为", "所以", "于是", "但是", "然而"]):
                        issues.append({
                            "type": "场景跳跃",
                            "severity": "🔴 严重",
                            "line": i + 1,
                            "content": line[:50],
                            "suggestion": "添加场景转移句，说明如何从上一场景到达此处"
                        })
    
    return issues


def check_time_transition(text: str) -> list:
    """检查时间连续性"""
    issues = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 检测时间跳跃
        for pattern in TIME_JUMP_NO_TRANSITION:
            if re.match(pattern, line):
                # 检查上下文是否有时间过渡
                has_transition = False
                for j in range(max(0, i-2), i):
                    prev = lines[j].strip()
                    if any(kw in prev for kw in ["经过", "等待", "终于", "直到", "天色", "夜色"]):
                        has_transition = True
                        break
                
                if not has_transition:
                    issues.append({
                        "type": "时间断裂",
                        "severity": "🔴 严重",
                        "line": i + 1,
                        "content": line[:50],
                        "suggestion": "加入时间过渡句，如'战斗结束后的第三天'"
                    })
    
    return issues


def check_emotion_continuity(text: str) -> list:
    """检查情绪连续性"""
    issues = []
    
    # 简化版：检测段落首句情绪词变化
    emotion_words_positive = ["开心", "高兴", "兴奋", "激动", "喜悦", "快乐", "满足", "欣慰"]
    emotion_words_negative = ["难过", "悲伤", "沮丧", "愤怒", "恐惧", "害怕", "担心", "绝望"]
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    for i in range(1, len(paragraphs)):
        prev = paragraphs[i-1]
        curr = paragraphs[i]
        
        has_pos_prev = any(w in prev for w in emotion_words_positive)
        has_neg_prev = any(w in prev for w in emotion_words_negative)
        has_pos_curr = any(w in curr for w in emotion_words_positive)
        has_neg_curr = any(w in curr for w in emotion_words_negative)
        
        # 情绪180度转弯
        if (has_pos_prev and has_neg_curr) or (has_neg_prev and has_pos_curr):
            # 检查是否有过渡
            if not any(w in curr[:50] for w in ["但是", "然而", "突然", "只是", "直到"]):
                issues.append({
                    "type": "情绪断崖",
                    "severity": "🟠 中等",
                    "line": i + 1,
                    "content": curr[:50],
                    "suggestion": "加入情绪缓冲句，如'笑了三秒后，他深吸一口气'"
                })
    
    return issues


def check_causality(text: str) -> list:
    """检查因果连续性"""
    issues = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # 检测突然出现的事件（无因有果）
        if line.startswith(("突然", "就在这时", "没想到", "谁知")):
            if i > 0:
                prev = lines[i-1].strip()
                # 检查是否有因果关联词
                if not any(kw in prev for kw in ["因为", "所以", "于是", "导致", "造成", "因此"]):
                    # 检查是否有前一事件作为铺垫
                    if i > 2:
                        prev2 = lines[i-2].strip()
                        if not any(kw in prev2 for kw in ["看到", "听到", "发现", "感觉"]):
                            issues.append({
                                "type": "因果断裂",
                                "severity": "🟠 中等",
                                "line": i + 1,
                                "content": line[:50],
                                "suggestion": "加入因果过渡，说明为何发生此事"
                            })
    
    return issues


def check_info_continuity(text: str) -> list:
    """检查信息连续性"""
    issues = []
    
    # 检测首次出现的人物/物品（需要简单介绍）
    new_entity_patterns = [
        (r"^[A-Z][a-z]+", "英文名"),
        (r"^[【\[].*?[】\]]", "系统提示"),
    ]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern, name in new_entity_patterns:
            matches = re.findall(pattern, line)
            if matches:
                # 检查是否在前面介绍过（简化检查）
                prev_text = '\n'.join(lines[:i])
                if not any(m in prev_text for m in matches):
                    # 只在关键位置提示
                    if i < 5:  # 前5行
                        issues.append({
                            "type": "信息突兀",
                            "severity": "🟡 轻微",
                            "line": i + 1,
                            "content": matches[0][:30],
                            "suggestion": f"首次出现{matches[0]}，建议简短介绍"
                        })
    
    return issues


def determine_chapter_type(text: str) -> str:
    """判断章节类型"""
    for ctype, keywords in CHAPTER_TYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return ctype
    return "普通章"


def check_chapter(prev_path: str, curr_path: str = None) -> dict:
    """检查章节衔接"""
    result = {
        "prev_chapter": prev_path,
        "curr_chapter": curr_path or prev_path,
        "chapter_type": "普通章",
        "issues": [],
        "passed": True
    }
    
    if curr_path:
        curr_text = load_chapter(curr_path)
        result["chapter_type"] = determine_chapter_type(curr_text)
        
        # 执行5项检查
        result["issues"].extend(check_scene_transition(curr_text))
        result["issues"].extend(check_time_transition(curr_text))
        result["issues"].extend(check_emotion_continuity(curr_text))
        result["issues"].extend(check_causality(curr_text))
        result["issues"].extend(check_info_continuity(curr_text))
    
    # 判断是否通过
    critical = [i for i in result["issues"] if "严重" in i.get("severity", "")]
    result["passed"] = len(critical) == 0
    
    return result


def print_report(result: dict):
    """打印报告"""
    print(f"\n{'='*60}")
    print(f"📖 章节衔接检查报告")
    print(f"{'='*60}")
    print(f"章节类型: {result['chapter_type']}")
    print(f"检查文件: {result['curr_chapter']}")
    print()
    
    if not result["issues"]:
        print("✅ 通过！未发现衔接问题")
        return
    
    # 按严重程度分组
    critical = [i for i in result["issues"] if "严重" in i.get("severity", "")]
    medium = [i for i in result["issues"] if "中等" in i.get("severity", "")]
    minor = [i for i in result["issues"] if "轻微" in i.get("severity", "")]
    
    print(f"❌ 发现 {len(result['issues'])} 个问题:")
    print(f"   🔴 严重: {len(critical)}")
    print(f"   🟠 中等: {len(medium)}")
    print(f"   🟡 轻微: {len(minor)}")
    print()
    
    for issue in result["issues"]:
        print(f"{issue['severity']} [{issue['type']}] 第{issue['line']}行")
        print(f"   内容: {issue['content']}...")
        print(f"   建议: {issue['suggestion']}")
        print()
    
    if not result["passed"]:
        print("⚠️ 建议修改后再进行下一章创作")
    else:
        print("✅ 整体通过，可继续创作")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if len(sys.argv) == 2:
        result = check_chapter(sys.argv[1])
    else:
        result = check_chapter(sys.argv[1], sys.argv[2])
    
    print_report(result)
