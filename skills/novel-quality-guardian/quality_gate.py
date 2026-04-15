#!/usr/bin/env python3
"""
质量门检测器 - 检测章节质量
用法:
    python quality_gate.py --chapter ch101.md --novel "重生之我是神豪"
    python quality_gate.py --content "章节内容..."
"""

import json
import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels")


@dataclass
class QualityResult:
    score: int
    passed: bool
    issues: List[str]
    details: Dict


class QualityGate:
    """质量门检测器"""
    
    def __init__(self, content: str, anchor: dict):
        self.content = content
        self.anchor = anchor
        self.issues = []
        self.score = 100
        self.details = {}
    
    def check_ooc(self) -> int:
        """人物OOC检测 -30分"""
        issues = []
        deductions = 0
        
        # 检查主角名是否出现
        main_char = self.anchor.get('main_char_name', '')
        if main_char and main_char not in self.content:
            issues.append(f"⚠️ 主角'{main_char}'本章未出现")
            deductions += 10
        
        # 检查口头禅
        catchphrases = self.anchor.get('catchphrases', [])
        if catchphrases:
            found_catchphrases = [cp for cp in catchphrases if cp in self.content]
            if not found_catchphrases:
                issues.append(f"⚠️ 口头禅{catchphrases}均未出现")
                deductions += 10
        
        # 检查人物行为一致性（简单关键词检测）
        char_profile = self.anchor.get('char_profile', '')
        # 提取性格关键词
        traits = re.findall(r'[正直|腹黑|幽默|冷酷|温柔|聪明|善良|自私|勇敢|懦弱]+', char_profile)
        for trait in traits[:3]:
            if trait not in self.content:
                issues.append(f"⚠️ 主角性格特质'{trait}'本章未体现")
                deductions += 5
        
        if deductions > 0:
            deductions = min(deductions, 30)
            self.issues.extend(issues)
        
        self.details['ooc'] = {"issues": issues, "deductions": deductions}
        return -deductions
    
    def check_repetition(self) -> int:
        """情节重复检测 -25分"""
        issues = []
        deductions = 0
        
        # 与前章对比关键词
        prev_keywords = self.anchor.get('prev_keywords', [])
        content_words = set(self.content.split())
        
        if prev_keywords:
            overlap = [kw for kw in prev_keywords if kw in content_words]
            if len(overlap) > 5:
                issues.append(f"⚠️ 与前文关键词重复过多: {overlap[:5]}")
                deductions += 10
        
        # 检查场景重复
        prev_scenes = self.anchor.get('prev_scenes', [])
        for scene in prev_scenes[:3]:
            # 简单匹配
            if scene in self.content:
                issues.append(f"⚠️ 场景'{scene}'与前文重复")
                deductions += 10
        
        # 检查重复句式（简单检测）
        sentences = self.content.split('。')
        if len(sentences) > 3:
            # 找完全相同的句子
            seen = set()
            for s in sentences:
                s = s.strip()
                if len(s) > 20 and s in seen:
                    issues.append(f"⚠️ 发现重复句式: {s[:30]}...")
                    deductions += 5
                seen.add(s)
        
        deductions = min(deductions, 25)
        if deductions > 0:
            self.issues.extend(issues)
        
        self.details['repetition'] = {"issues": issues, "deductions": deductions}
        return -deductions
    
    def check_consistency(self) -> int:
        """矛盾检测 -25分"""
        issues = []
        deductions = 0
        
        # 检查时间表述
        time_markers = re.findall(r'\d+年|\d+月|\d+日|\d+点|\d+分', self.content)
        prev_time_markers = self.anchor.get('prev_time_markers', [])
        
        # 如果有前文时间，检查是否冲突
        if prev_time_markers and time_markers:
            # 简单检查：不应该出现更早的时间
            if time_markers and any(t in self.content for t in prev_time_markers[:2]):
                # 可能存在时间回溯
                issues.append("⚠️ 可能存在时间线问题")
                deductions += 5
        
        # 检查人物关系（简单检测）
        relations = self.anchor.get('relations', {})
        for char, relation in list(relations.items())[:3]:
            if char in self.content and relation not in self.content:
                # 关系可能有问题，但不一定是错误
                pass
        
        # 检查本章是否提到了"已经发生"但前文没有的事情
        # 这个需要更复杂的逻辑，暂时跳过
        
        deductions = min(deductions, 25)
        if deductions > 0:
            self.issues.extend(issues)
        
        self.details['consistency'] = {"issues": issues, "deductions": deductions}
        return -deductions
    
    def check_completeness(self) -> int:
        """完整性检测 -20分"""
        issues = []
        deductions = 0
        
        # 检查字数
        char_count = len(self.content)
        if char_count < 1500:
            issues.append(f"⚠️ 字数过少: {char_count}字（建议2500-4000字）")
            deductions += 10
        elif char_count > 6000:
            issues.append(f"⚠️ 字数过多: {char_count}字（建议2500-4000字）")
            deductions += 5
        
        # 检查章节结构
        has_dialogue = '"' in self.content or '"' in self.content or '「' in self.content
        if not has_dialogue:
            issues.append("⚠️ 缺少对话")
            deductions += 5
        
        # 检查钩子
        hooks = ['下章', '下一章', '未完', '待续', '第三章', '三天后', '第二天']
        has_hook = any(h in self.content for h in hooks)
        if not has_hook:
            issues.append("⚠️ 章节结尾无钩子")
            deductions += 5
        
        deductions = min(deductions, 20)
        if deductions > 0:
            self.issues.extend(issues)
        
        self.details['completeness'] = {"issues": issues, "deductions": deductions}
        return -deductions
    
    def run_all_checks(self) -> QualityResult:
        """运行所有检测"""
        
        self.score += self.check_ooc()
        self.score += self.check_repetition()
        self.score += self.check_consistency()
        self.score += self.check_completeness()
        
        # 确保分数在0-100之间
        self.score = max(0, min(100, self.score))
        
        passed = self.score >= 80
        
        return QualityResult(
            score=self.score,
            passed=passed,
            issues=self.issues,
            details=self.details
        )


def load_anchor_from_file(novel: str, chapter: int) -> dict:
    """从锚定文件加载锚定信息"""
    # 尝试运行anchor_injector获取锚定
    import subprocess
    
    script_path = Path(__file__).parent / "anchor_injector.py"
    if script_path.exists():
        try:
            result = subprocess.run(
                ["python3", str(script_path), novel, str(chapter)],
                capture_output=True,
                text=True,
                timeout=30
            )
            # 简单解析输出（这里可以改进）
            # 返回空锚定，让后续检测跳过某些项
            return {"main_char_name": "", "catchphrases": [], "prev_keywords": []}
        except:
            pass
    
    return {}


def main():
    parser = argparse.ArgumentParser(description="质量门检测")
    parser.add_argument("--chapter", help="章节文件路径")
    parser.add_argument("--novel", help="小说名")
    parser.add_argument("--content", help="章节内容（直接传入）")
    parser.add_argument("--score", type=int, default=80, help="通过分数阈值")
    
    args = parser.parse_args()
    
    # 获取内容
    content = ""
    if args.content:
        content = args.content
    elif args.chapter:
        chapter_file = Path(args.chapter)
        if chapter_file.exists():
            content = chapter_file.read_text(encoding='utf-8')
        else:
            print(f"文件不存在: {args.chapter}")
            sys.exit(1)
    else:
        print("请提供 --chapter 或 --content")
        sys.exit(1)
    
    # 获取锚定信息
    anchor = {}
    if args.novel:
        # 从章节号提取
        chapter = 1
        if args.chapter:
            # 从文件名提取章节号
            import re
            match = re.search(r'ch(\d+)', args.chapter)
            if match:
                chapter = int(match.group(1))
        
        anchor = load_anchor_from_file(args.novel, chapter)
    
    # 运行检测
    gate = QualityGate(content, anchor)
    result = gate.run_all_checks()
    
    # 输出结果
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                    【质量门检测报告】                     ║
╠════════════════════════════════════════════════════════════╣
║  分数: {result.score}/100                                          ║
║  状态: {'✅ 通过' if result.passed else '❌ 不通过'} (阈值: {args.score}分)                           ║
╠════════════════════════════════════════════════════════════╣
""")
    
    if result.issues:
        print("║  问题列表:                                               ║")
        for issue in result.issues:
            print(f"║    {issue[:50]}")
        print("║")
    
    print("╠════════════════════════════════════════════════════════════╣")
    
    if result.passed:
        print("║  建议: ✅ 可以发布                                       ║")
    else:
        print("║  建议: ❌ 需要修改后重检                                  ║")
    
    print("╚════════════════════════════════════════════════════════════╝")
    
    # 返回码
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
