#!/usr/bin/env python3
"""
小说审稿脚本 - 重生带AI夯爆了
检测：衔接问题、前后矛盾、事实错误
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels/重生带AI夯爆了")
PROGRESS_FILE = NOVEL_DIR / "progress.json"
REPORT_FILE = NOVEL_DIR / "审稿报告.md"
LOCK_FILE = NOVEL_DIR / ".qa_lock"

# 已检查的章节记录
CHECKED_FILE = NOVEL_DIR / ".qa_checked.json"


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def load_progress():
    """加载进度"""
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_checked():
    """加载已检查章节"""
    if CHECKED_FILE.exists():
        with open(CHECKED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"chapters": [], "last_check": None}


def save_checked(checked):
    """保存检查记录"""
    with open(CHECKED_FILE, 'w', encoding='utf-8') as f:
        json.dump(checked, f, ensure_ascii=False, indent=2)


def extract_chapter_files():
    """提取所有章节文件"""
    files = list(NOVEL_DIR.glob("ch[0-9]*.md"))
    # 过滤掉 summary 和 storyboard
    files = [f for f in files if "summary" not in f.name and "storyboard" not in f.name]
    # 按章节号排序
    files.sort(key=lambda x: int(re.search(r'ch(\d+)', x.name).group(1)))
    return files


def load_chapter_content(file_path):
    """加载章节内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_key_info(content):
    """提取关键信息"""
    info = {
        "characters": set(),
        "locations": set(),
        "times": set(),
        "events": set(),
        "systems": set(),  # AI系统相关
    }
    
    # 提取人物
    character_patterns = [
        r'陈默|林清雅|苏晚晴|周伟|纳德拉|"上帝"|Lucifer|李明辉|陈曦'
    ]
    for pattern in character_patterns:
        matches = re.findall(pattern, content)
        info["characters"].update(matches)
    
    # 提取地点
    location_patterns = [
        r'旧金山|北京|上海|纽约|东京|马里亚纳海沟|太平洋|硅谷'
    ]
    for pattern in location_patterns:
        matches = re.findall(pattern, content)
        info["locations"].update(matches)
    
    # 提取AI系统
    system_patterns = [
        r'Aether|创世纪|量子火种|时间暂停|时间洞察|数据之眼|普罗米修斯'
    ]
    for pattern in system_patterns:
        matches = re.findall(pattern, content)
        info["systems"].update(matches)
    
    # 提取时间信息
    time_patterns = [
        r'\d+小时|\d+天|\d+月|\d+年',
        r'三天后|一周后|一个月后|第二天|傍晚|深夜|凌晨'
    ]
    for pattern in time_patterns:
        matches = re.findall(pattern, content)
        info["times"].update(matches)
    
    return info


def check_continuity(prev_info, curr_info, prev_num, curr_num):
    """检查衔接问题"""
    issues = []
    
    # 检查人物一致性
    prev_chars = prev_info["characters"]
    curr_chars = curr_info["characters"]
    
    # 检查是否有突兀消失的人物（在前面出现但本章没出现的重要人物）
    important_chars = {"陈默", "林清雅", "苏晚晴", "周伟"}
    disappeared = (prev_chars & important_chars) - curr_chars
    if disappeared and curr_num > prev_num + 3:
        issues.append({
            "type": "人物消失",
            "severity": "warning",
            "chapter": curr_num,
            "desc": f"重要人物{dappeared}在之前出现后，本章未出现"
        })
    
    return issues


def check_consistency(files, start_idx, count=5):
    """检查一致性（多章节）"""
    all_issues = []
    
    # 提取所有章节的关键信息
    chapter_infos = {}
    for i in range(start_idx, min(start_idx + count, len(files))):
        file = files[i]
        match = re.search(r'ch(\d+)', file.name)
        if not match:
            continue
        ch_num = int(match.group(1))
        content = load_chapter_content(file)
        chapter_infos[ch_num] = extract_key_info(content)
    
    # 按顺序检查
    ch_nums = sorted(chapter_infos.keys())
    for i in range(len(ch_nums) - 1):
        curr_ch = ch_nums[i]
        next_ch = ch_nums[i + 1]
        
        # 检查时间逻辑
        curr_time = chapter_infos[curr_ch]["times"]
        next_time = chapter_infos[next_ch]["times"]
        
        # 检查是否是时间倒流（简化检查）
        if curr_time and next_time:
            # 这里可以添加更复杂的时间逻辑检查
            pass
        
        # 检查人物状态矛盾（简化版）
        curr_chars = chapter_infos[curr_ch]["characters"]
        next_chars = chapter_infos[next_ch]["characters"]
        
        # 检查地点是否一致（如果是连续章节）
        if next_ch == curr_ch + 1:
            issues = check_continuity(
                chapter_infos[curr_ch],
                chapter_infos[next_ch],
                curr_ch,
                next_ch
            )
            all_issues.extend(issues)
    
    return all_issues


def check_facts(files, start_idx, count=5):
    """检查事实错误"""
    issues = []
    
    for i in range(start_idx, min(start_idx + count, len(files))):
        file = files[i]
        match = re.search(r'ch(\d+)', file.name)
        if not match:
            continue
        ch_num = int(match.group(1))
        content = load_chapter_content(file)
        
        # 检查明显的事实错误（简化版）
        
        # 1. 检查数字是否合理
        # 股价不可能为负数
        if re.search(r'股价.*-[0-9]+', content):
            issues.append({
                "type": "事实错误",
                "severity": "error",
                "chapter": ch_num,
                "desc": "股价出现负数"
            })
        
        # 2. 检查时间是否合理（如"1999年出生，2026年50岁"）
        year_matches = re.findall(r'(19\d{2})年出生', content)
        for year in year_matches:
            age = 2026 - int(year)
            if age > 60 or age < 0:
                issues.append({
                    "type": "事实错误",
                    "severity": "warning",
                    "chapter": ch_num,
                    "desc": f"出生年份{year}计算年龄不合理"
                })
        
        # 3. 检查AI系统名称一致性
        if "Aether" in content and "aether" in content:
            issues.append({
                "type": "大小写不一致",
                "severity": "info",
                "chapter": ch_num,
                "desc": "Aether大小写不统一"
            })
    
    return issues


def generate_report(all_issues):
    """生成审稿报告"""
    if not all_issues:
        return "# 审稿报告\n\n✅ 未发现明显问题\n"
    
    # 按严重程度分组
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]
    
    report = "# 审稿报告\n\n"
    report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"## 统计\n\n"
    report += f"- 严重错误: {len(errors)}\n"
    report += f"- 警告: {len(warnings)}\n"
    report += f"- 提示: {len(infos)}\n\n"
    
    if errors:
        report += "## 🚫 严重错误\n\n"
        for e in errors:
            report += f"- ch{e['chapter']}: {e['desc']}\n"
        report += "\n"
    
    if warnings:
        report += "## ⚠️ 警告\n\n"
        for w in warnings:
            report += f"- ch{w['chapter']}: {w['desc']}\n"
        report += "\n"
    
    if infos:
        report += "## ℹ️ 提示\n\n"
        for i in infos:
            report += f"- ch{i['chapter']}: {i['desc']}\n"
        report += "\n"
    
    # 按章节汇总
    by_chapter = defaultdict(list)
    for issue in all_issues:
        by_chapter[issue["chapter"]].append(issue)
    
    report += "## 📑 章节问题汇总\n\n"
    for ch in sorted(by_chapter.keys()):
        report += f"### ch{ch}\n\n"
        for issue in by_chapter[ch]:
            report += f"- [{issue['severity']}] {issue['type']}: {issue['desc']}\n"
        report += "\n"
    
    report += "---\n\n"
    report += "*本报告由自动审稿系统生成*\n"
    
    return report


def main():
    """主函数"""
    log("=" * 50)
    log("小说审稿任务启动")
    log("=" * 50)
    
    # 检查锁文件
    if LOCK_FILE.exists():
        log("审稿任务正在运行，跳过")
        return
    
    # 创建锁文件
    LOCK_FILE.write_text(str(os.getpid()))
    
    try:
        # 加载进度
        progress = load_progress()
        completed = progress.get('completed_chapters', 0)
        
        log(f"当前进度: {completed}/120")
        
        # 检查小说是否已完结
        if completed < 120:
            log(f"小说未完结 ({completed}/120)，跳过审稿")
            return
        
        log("小说已完结，开始审稿！")
        
        # 加载已检查记录
        checked = load_checked()
        
        # 获取所有章节文件
        files = extract_chapter_files()
        total = len(files)
        
        # 确定检查范围（每次5章）
        # 从上次检查的位置继续
        start_idx = checked.get("last_index", 0)
        
        # 如果还有未检查的章节
        if start_idx >= total:
            log("所有章节已检查完毕")
            # 可以在这里触发最终报告生成
            start_idx = 0  # 重新检查
        
        # 检查5章
        count = min(5, total - start_idx)
        if count <= 0:
            log("没有章节需要检查")
            return
        
        log(f"检查章节: {start_idx+1} - {start_idx+count}")
        
        # 执行检查
        continuity_issues = check_consistency(files, start_idx, count)
        fact_issues = check_facts(files, start_idx, count)
        all_issues = continuity_issues + fact_issues
        
        # 更新已检查记录
        checked["chapters"] = list(set(checked.get("chapters", []) + [f"ch{i}" for i in range(start_idx, start_idx+count)]))
        checked["last_index"] = start_idx + count
        checked["last_check"] = datetime.now().isoformat()
        save_checked(checked)
        
        # 生成报告
        report = generate_report(all_issues)
        REPORT_FILE.write_text(report, encoding='utf-8')
        
        log(f"发现问题: {len(all_issues)} 个")
        log(f"报告已保存: {REPORT_FILE.name}")
        
    except Exception as e:
        log(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理锁文件
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
        log("审稿任务完成")


if __name__ == "__main__":
    main()
