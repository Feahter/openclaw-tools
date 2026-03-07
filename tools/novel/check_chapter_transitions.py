#!/usr/bin/env python3
"""
章节衔接检测工具 v2.0
基于QA衔接检查清单（5项必检）

改进：
- 更准确的正文提取
- 卷末/全书完检测
- 更多场景跳跃模式

使用方法：
    python3 check_transitions.py <小说目录>
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 时间词库（需要过渡的）
TIME_JUMP_WORDS = [
    '第二天', '三天后', '一周后', '一个月后', '几小时后', '几分钟后',
    '半小时后', '一天后', '两天后', '五天后', '十天后', '一年后',
    '倒计时', '时间流逝', '转眼间', '片刻后', '须臾间'
]

# 场景词库（可能跳跃的）
SCENE_WORDS = [
    '东京', '纽约', '北京', '上海', '伦敦', '巴黎', '硅谷', '深圳',
    '马尔代夫', '酒店', '机场', '医院', '学校', '公司', '家里'
]

# 好的过渡词
GOOD_TRANSITIONS = [
    '于是', '然后', '接着', '随后', '之后', '离开', '回到', '赶往',
    '走向', '乘坐', '登上了', '走进了', '回到了', '三小时后',
    '半小时后', '二十分钟后', '挂了电话', '放下手机', '站起身',
    '会议结束后', '战斗结束后', '收购战结束后', '几天后', '那之后',
    '这之后', '这天', '那天', '几天后'
]

# 卷末标记
VOLUME_END_MARKERS = [
    '本卷完', '本卷结束', '全书完', '第一卷', '第二卷', '第三卷', '第四卷',
    '第N卷', '卷终', '卷末', '最终章', '大结局'
]


def extract_real_ending(content: str) -> str:
    """提取真正的正文结尾（去除元数据）"""
    lines = content.split('\n')
    
    # 从后往前找，找到第一个非元数据的段落
    real_lines = []
    found_content = False
    
    for line in reversed(lines):
        line = line.strip()
        
        # 跳过明显的元数据行
        if line in ['---', '```', '***'] or line.startswith('字数') or line.startswith('创作时间'):
            if found_content:
                break
            continue
        
        # 跳过纯数字行
        if re.match(r'^[\d\s,，.]+$', line):
            continue
            
        if line:
            found_content = True
            real_lines.insert(0, line)
    
    return '\n'.join(real_lines[-10:]) if real_lines else ''


def extract_real_beginning(content: str) -> str:
    """提取真正的正文开头"""
    lines = content.split('\n')
    
    # 跳过标题，从正文开始
    real_lines = []
    found_title = False
    
    for line in lines:
        line = line.strip()
        
        # 跳过标题
        if line.startswith('# ') or line.startswith('## '):
            found_title = True
            continue
        
        if found_title and line:
            real_lines.append(line)
            if len(real_lines) >= 5:
                break
    
    return '\n'.join(real_lines)


def has_volume_end_marker(text: str) -> bool:
    """检测是否有卷末标记"""
    text_lower = text.lower()
    for marker in VOLUME_END_MARKERS:
        if marker in text:
            return True
    return False


def check_transition(chapter_file: str, next_file: str) -> Dict:
    """检查两个章节之间的衔接"""
    result = {
        'chapter': os.path.basename(chapter_file),
        'next': os.path.basename(next_file),
        'issues': [],
        'score': 10,
        'pass': True
    }
    
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(next_file, 'r', encoding='utf-8') as f:
            content2 = f.read()
    except Exception as e:
        result['issues'].append({'type': 'error', 'msg': str(e)})
        return result
    
    # 提取真实开头和结尾
    ending = extract_real_ending(content1)
    beginning = extract_real_beginning(content2)
    
    if not ending or not beginning:
        result['issues'].append({'type': 'error', 'msg': '无法提取内容'})
        return result
    
    ending = ending.strip()
    beginning = beginning.strip()
    
    # 检查1: 卷末标记问题
    if has_volume_end_marker(ending) and not has_volume_end_marker(beginning):
        # 检查是否有过渡
        has_transition = any(word in ending or word in beginning for word in GOOD_TRANSITIONS)
        if not has_transition:
            result['issues'].append({
                'type': 'volume_end',
                'severity': 'medium',
                'msg': '卷末/全书完标记后无过渡直接跳转',
                'fix': '加入时间/场景过渡说明'
            })
            result['score'] -= 3
    
    # 检查2: 时间跳跃
    has_time_jump = any(word in beginning for word in TIME_JUMP_WORDS)
    has_transition = any(word in ending or word in beginning for word in GOOD_TRANSITIONS)
    
    if has_time_jump and not has_transition:
        result['issues'].append({
            'type': 'time_jump',
            'severity': 'low',
            'msg': '时间跳跃但无过渡词',
            'fix': '加入时间过渡句'
        })
        result['score'] -= 1
    
    # 检查3: 场景跳跃（更严格的检测）
    # 如果开头直接是地名+描述，且结尾没有转移词，可能是场景跳跃
    scene_pattern = r'^([^\n]{2,8})(的|里|中|上|下)([^\n]{0,15})'
    if re.match(scene_pattern, beginning[:100]):
        # 检查是否有场景转移
        has_scene_change = any(word in beginning[:150] for word in SCENE_WORDS)
        has_movement = any(word in ending[-200:] + beginning[:200] for word in 
                         ['走到', '来到', '回到', '离开', '前往', '登上', '下了', '乘车', '驾驶'])
        
        if has_scene_change and not has_movement and not has_transition:
            result['issues'].append({
                'type': 'scene_jump',
                'severity': 'medium',
                'msg': '可能存在场景跳跃（无转移过程）',
                'fix': '加入场景转移句'
            })
            result['score'] -= 2
    
    # 检查4: 情绪突变
    emotion_end = re.findall(r'(高兴|开心|兴奋|悲伤|愤怒|恐惧|担心|紧张)', ending[-200:])
    emotion_begin = re.findall(r'(高兴|开心|兴奋|悲伤|愤怒|恐惧|担心|紧张)', beginning[:200])
    
    if emotion_end and emotion_begin:
        # 如果情绪完全不同，可能有问题
        if set(emotion_end) != set(emotion_begin):
            result['issues'].append({
                'type': 'emotion_jump',
                'severity': 'low',
                'msg': f'情绪变化: {emotion_end} → {emotion_begin}',
                'fix': '可能需要情绪缓冲'
            })
            result['score'] -= 0.5
    
    result['issues'] = result['issues']
    result['pass'] = result['score'] >= 7
    
    return result


def analyze_novel(novel_dir: str) -> Dict:
    """分析整本小说的章节衔接"""
    novel_path = Path(novel_dir)
    
    # 收集所有章节文件（递归）
    chapters = []
    for pattern in ['**/ch*.md', '*.md']:
        chapters.extend(novel_path.glob(pattern))
    
    # 过滤和排序
    chapters = [c for c in chapters if '_summary' not in c.name 
                and '_planning' not in c.name 
                and '_qa_' not in c.name
                and 'ch' in c.name]
    chapters = sorted(chapters, key=lambda x: x.name)
    
    # 如果有ch001-ch030在子目录，需要正确排序
    # 提取数字进行排序
    def sort_key(x):
        match = re.search(r'ch(\d+)', x.name.lower())
        return int(match.group(1)) if match else 0
    
    chapters.sort(key=sort_key)
    
    results = {
        'novel': novel_path.name,
        'total_chapters': len(chapters),
        'transitions': [],
        'summary': {
            'total': len(chapters) - 1 if len(chapters) > 1 else 0,
            'passed': 0,
            'failed': 0,
            'issues': {
                'volume_end': 0,
                'time_jump': 0,
                'scene_jump': 0,
                'emotion_jump': 0
            }
        }
    }
    
    # 检查每对相邻章节
    for i in range(len(chapters) - 1):
        result = check_transition(str(chapters[i]), str(chapters[i + 1]))
        results['transitions'].append(result)
        
        if result['pass']:
            results['summary']['passed'] += 1
        else:
            results['summary']['failed'] += 1
        
        for issue in result['issues']:
            issue_type = issue['type']
            if issue_type in results['summary']['issues']:
                results['summary']['issues'][issue_type] += 1
    
    return results


def print_report(results: Dict):
    """打印分析报告"""
    print("\n" + "="*60)
    print(f"📚 {results['novel']} - 章节衔接分析报告")
    print("="*60)
    
    summary = results['summary']
    
    if summary['total'] == 0:
        print("\n⚠️ 未找到章节文件")
        return
    
    print(f"\n📊 统计:")
    print(f"   总章节数: {results['total_chapters']}")
    print(f"   衔接检查数: {summary['total']}")
    print(f"   ✅ 通过: {summary['passed']}")
    print(f"   ❌ 未通过: {summary['failed']}")
    
    pass_rate = summary['passed']/summary['total']*100 if summary['total'] > 0 else 0
    print(f"   通过率: {pass_rate:.1f}%")
    
    # 问题分布
    issue_total = sum(summary['issues'].values())
    if issue_total > 0:
        print(f"\n📋 问题分布:")
        for issue_type, count in summary['issues'].items():
            if count > 0:
                print(f"   - {issue_type}: {count}处")
    
    # 打印问题章节
    failed_transitions = [t for t in results['transitions'] if not t['pass']]
    if failed_transitions:
        print(f"\n⚠️ 需要修复的章节衔接 ({len(failed_transitions)}处):")
        for t in failed_transitions:
            print(f"\n   {t['chapter']} → {t['next']}")
            print(f"   得分: {t['score']}/10")
            for issue in t['issues']:
                severity_emoji = {'low': '🟡', 'medium': '🟠', 'high': '🔴'}.get(issue.get('severity', 'low'), '⚪')
                print(f"   {severity_emoji} {issue['msg']}")
                if 'fix' in issue:
                    print(f"      💡 修复建议: {issue['fix']}")
    
    if not failed_transitions and issue_total == 0:
        print(f"\n✅ 所有章节衔接良好!")
    
    print("\n" + "="*60)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 check_transitions.py <小说目录>")
        print("示例: python3 check_transitions.py novels/重生带AI夯爆了")
        sys.exit(1)
    
    novel_dir = sys.argv[1]
    
    if not os.path.isdir(novel_dir):
        print(f"错误: 目录不存在: {novel_dir}")
        sys.exit(1)
    
    print(f"🔍 分析中: {novel_dir}")
    results = analyze_novel(novel_dir)
    print_report(results)


if __name__ == '__main__':
    main()
