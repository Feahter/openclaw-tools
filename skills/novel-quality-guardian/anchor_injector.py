#!/usr/bin/env python3
"""
锚定信息注入器 - 提取小说写作所需的锚定信息
用法:
    python anchor_injector.py <小说名> <章节号>
    python anchor_injector.py "重生之我是神豪" 101
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels")


@dataclass
class AnchorInfo:
    novel: str
    chapter: int
    main_char_name: str = ""
    char_profile: str = ""
    char_content: str = ""  # 完整人物档案内容
    catchphrases: List[str] = None
    prev_summaries: List[str] = None
    vpool: str = ""
    storyboard: str = ""
    prev_keywords: List[str] = None
    prev_scenes: List[str] = None
    relations: dict = None
    prev_time_markers: List[str] = None
    
    def __post_init__(self):
        if self.catchphrases is None:
            self.catchphrases = []
        if self.prev_summaries is None:
            self.prev_summaries = []
        if self.prev_keywords is None:
            self.prev_keywords = []
        if self.prev_scenes is None:
            self.prev_scenes = []
        if self.relations is None:
            self.relations = {}
        if self.prev_time_markers is None:
            self.prev_time_markers = []


def read_file(path: Path) -> str:
    """读取文件内容"""
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding='utf-8')
    except:
        return ""


def extract_char_profile(novel_path: Path) -> tuple:
    """提取人物档案"""
    # 尝试多种可能的文件名
    possible_names = ["人物档案.md", "人物档案v4.md", "人物库.md", "characters.md"]
    
    for name in possible_names:
        char_file = novel_path / name
        if char_file.exists():
            content = read_file(char_file)
            # 提取主角名
            main_char = ""
            for line in content.split('\n')[:20]:
                if '主角' in line or '男主的' in line or '姓名' in line:
                    main_char = line.split(':')[-1].strip()
                    break
            
            # 提取口头禅
            catchphrases = []
            for line in content.split('\n'):
                if '口头禅' in line or '惯用语' in line:
                    # 尝试提取后面的内容
                    parts = line.split(':')
                    if len(parts) > 1:
                        catchphrases = [p.strip() for p in parts[1].split(',')]
            
            return main_char, content, catchphrases
    
    return "", "", []


def extract_prev_summaries(novel_path: Path, chapter: int) -> tuple:
    """提取前3章摘要"""
    summaries = []
    keywords = []
    scenes = []
    
    # 尝试多种目录结构
    summary_dirs = [
        novel_path / "auxiliary" / "summaries",
        novel_path / "chapters" / "summaries",
        novel_path / "summaries",
    ]
    
    summary_dir = None
    for d in summary_dirs:
        if d.exists():
            summary_dir = d
            break
    
    if not summary_dir:
        return [], [], []
    
    # 读取前3章
    for i in range(max(1, chapter - 3), chapter):
        # 尝试多种文件名模式
        for pattern in [f"ch{i:03d}", f"ch{i}", f"第{i}章"]:
            for ext in ["-summary.md", "_summary.md", ".md"]:
                files = list(summary_dir.glob(f"{pattern}{ext}"))
                if files:
                    content = read_file(files[0])
                    summaries.append(content)
                    
                    # 提取关键词
                    for line in content.split('\n'):
                        if '关键词' in line or '核心' in line:
                            keywords.extend(line.split(':')[-1].strip().split(','))
                        if '场景' in line:
                            scenes.append(line.split(':')[-1].strip())
                    break
    
    return summaries, list(set(keywords)), list(set(scenes))


def extract_vpool(novel_path: Path) -> str:
    """提取伏笔池"""
    vpool_files = ["伏笔池.md", "vpool.md", "plot-hooks.md", "foreshadowing.md"]
    
    for name in vpool_files:
        vpool_file = novel_path / name
        if vpool_file.exists():
            return read_file(vpool_file)
    
    return ""


def extract_storyboard(novel_path: Path, chapter: int) -> str:
    """提取本章分镜"""
    # 尝试多种目录结构
    storyboard_dirs = [
        novel_path / "分镜",
        novel_path / "storyboards",
        novel_path / "chapters",
    ]
    
    storyboard_dir = None
    for d in storyboard_dirs:
        if d.exists():
            storyboard_dir = d
            break
    
    if not storyboard_dir:
        return ""
    
    # 读取本章分镜
    for pattern in [f"ch{chapter:03d}", f"ch{chapter}", f"第{chapter}章"]:
        for ext in [".md", "-storyboard.md", "_script.md"]:
            files = list(storyboard_dir.glob(f"{pattern}{ext}"))
            if files:
                return read_file(files[0])
    
    return ""


def extract_relations(novel_path: Path) -> dict:
    """提取人物关系"""
    # 从人物档案中提取关系
    main_char, char_content, _ = extract_char_profile(novel_path)
    
    relations = {}
    
    # 简单提取 - 找"与XXX的关系"这样的描述
    for line in char_content.split('\n'):
        if '关系' in line or '喜欢' in line or '仇' in line:
            parts = line.split(':')
            if len(parts) > 1:
                relations[parts[0].strip()] = parts[1].strip()
    
    return relations


def get_chapter_anchor(novel: str, chapter: int) -> AnchorInfo:
    """获取章节锚定信息"""
    
    novel_path = NOVEL_DIR / novel
    
    if not novel_path.exists():
        raise ValueError(f"小说目录不存在: {novel_path}")
    
    # 提取各项信息
    main_char, char_profile, catchphrases = extract_char_profile(novel_path)
    prev_summaries, prev_keywords, prev_scenes = extract_prev_summaries(novel_path, chapter)
    vpool = extract_vpool(novel_path)
    storyboard = extract_storyboard(novel_path, chapter)
    relations = extract_relations(novel_path)
    
    return AnchorInfo(
        novel=novel,
        chapter=chapter,
        main_char_name=main_char,
        char_profile=char_profile[:500],  # 只取前500字作为概要
        char_content=char_profile,  # 完整内容
        catchphrases=catchphrases,
        prev_summaries=prev_summaries,
        vpool=vpool,
        storyboard=storyboard,
        prev_keywords=prev_keywords,
        prev_scenes=prev_scenes,
        relations=relations
    )


def format_anchor_prompt(anchor: AnchorInfo) -> str:
    """格式化锚定提示"""
    
    prompt = f"""
╔════════════════════════════════════════════════════════════╗
║  【锚定信息】{anchor.novel} 第{anchor.chapter}章                    ║
╠════════════════════════════════════════════════════════════╣

【人物档案】
主角名: {anchor.main_char_name}
口头禅: {', '.join(anchor.catchphrases) if anchor.catchphrases else '无'}
{anchor.char_profile[:800] if anchor.char_content else '（无档案）'}

【前{len(anchor.prev_summaries)}章摘要】
"""
    
    for i, summary in enumerate(anchor.prev_summaries):
        prompt += f"\n--- 前{len(anchor.prev_summaries)-i}章 ---\n{summary[:500]}"
    
    prompt += f"""

【伏笔池】
{anchor.vpool[:500] if anchor.vpool else '（无伏笔）'}

【本章分镜】
{anchor.storyboard[:1000] if anchor.storyboard else '（无分镜）'}

╠════════════════════════════════════════════════════════════╣
║  ⚠️ 写作规则                                            ║
║  1. 主角行为必须符合人物档案中的性格设定                 ║
║  2. 必须出现主角口头禅（{', '.join(anchor.catchphrases) if anchor.catchphrases else '无'}）                  ║
║  3. 不能与前3章情节重复                                  ║
║  4. 不能出现与前文矛盾的设定                            ║
║  5. 如有伏笔回收，必须更新伏笔池                        ║
╚════════════════════════════════════════════════════════════╝
"""
    
    return prompt


def main():
    if len(sys.argv) < 3:
        print("用法: python anchor_injector.py <小说名> <章节号>")
        print("示例: python anchor_injector.py 重生之我是神豪 101")
        sys.exit(1)
    
    novel = sys.argv[1]
    chapter = int(sys.argv[2])
    
    try:
        anchor = get_chapter_anchor(novel, chapter)
        print(format_anchor_prompt(anchor))
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
