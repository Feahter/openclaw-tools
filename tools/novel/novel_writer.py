#!/usr/bin/env python3
"""
神豪小说创作任务生成器
每次只生成一个明确的创作任务，确保按顺序、按要求创作
"""
import json
import os
from pathlib import Path

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels/重生之我是神豪")
STATE_FILE = NOVEL_DIR / "创作进度.json"

# 分镜脚本顺序（章节范围）
STORYBOARDS = [
    # 前卷
    ("前卷", "storyboards/storyboard_01_系统激活.md", 1, 10),
    ("前卷", "storyboards/storyboard_02_资本萌芽.md", 11, 20),
    # 中卷
    ("中卷", "storyboards/storyboard_09_帝国雏形.md", 21, 30),
    ("中卷", "storyboards/storyboard_10_明星光环.md", 31, 40),
    ("中卷", "storyboards/storyboard_11_上流宴会.md", 41, 50),
    ("中卷", "storyboards/storyboard_12_媒体焦点.md", 51, 60),
    ("中卷", "storyboards/storyboard_13_全球布局.md", 61, 70),
    ("中卷", "storyboards/storyboard_14_行业巨头.md", 71, 80),
    # 后卷
    ("后卷", "storyboards/storyboard_25_反思.md", 81, 100),
]

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"current_chapter": 1, "completed": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_current_task():
    """获取当前应该创作的任务"""
    state = load_state()
    current = state.get("current_chapter", 1)
    
    # 找到当前章节属于哪个分镜
    for volume, sb_file, start_ch, end_ch in STORYBOARDS:
        if start_ch <= current <= end_ch:
            sb_path = NOVEL_DIR / volume / sb_file
            if sb_path.exists():
                # 读取分镜脚本
                with open(sb_path) as f:
                    sb_content = f.read()
                return {
                    "chapter": current,
                    "volume": volume,
                    "sb_file": sb_file,
                    "sb_path": str(sb_path),
                    "sb_content": sb_content[:2000],  # 只返回前2000字
                }
    
    return None

def get_next_task_prompt():
    """生成下一个创作任务的 prompt"""
    task = get_current_task()
    if not task:
        return "所有章节已创作完成！"
    
    prompt = f"""
## 创作任务

**章节**: 第{task['chapter']}章
**卷**: {task['volume']}

**分镜脚本摘要**:
{task['sb_content']}

## 创作要求

1. **严格按分镜脚本创作**，不要自由发挥后续内容
2. **主角**: 周明轩（不是叶辰！）
3. **女主**: 苏雨晴
4. **系统**: 至尊神豪系统
5. **字数**: 约3000字
6. **保存位置**: `/Users/fuzhuo/.openclaw/workspace/novels/重生之我是神豪/{task['volume']}/chapters/ch{task['chapter']:03d}_xxx.md`

## 五项自检（必须满足）
- [ ] 场景具体：说"在哪"不说"什么圈子"
- [ ] 画面感：闭眼能想象画面
- [ ] 数字感知：大数字换算成可感描述
- [ ] 反派存在：有明确对手
- [ ] 情感共鸣：普通人能代入

## 禁止事项（违反直接失败）
- ❌ 不要写超过当前章节编号的内容
- ❌ 不要写"表白成功后"、"确立关系后"等后续情节
- ❌ 主角名字必须是周明轩，不能是叶辰或其他

创作完成后，运行以下命令标记完成：
```
python /Users/fuzhuo/.openclaw/workspace/tools/novel_writer.py --complete
```
"""
    return prompt

def find_current_by_files():
    """通过检查已存在的文件来确定当前章节"""
    import re
    
    # 检查所有卷的目录
    volumes = ["前卷", "中卷", "后卷"]
    max_ch = 0
    max_ch_volume = "前卷"
    
    for volume in volumes:
        chapters_dir = NOVEL_DIR / volume / "chapters"
        if not chapters_dir.exists():
            continue
        
        for f in chapters_dir.glob("ch*.md"):
            name = f.stem
            match = re.search(r'ch(\d+)', name)
            if match:
                ch = int(match.group(1))
                if ch > max_ch:
                    max_ch = ch
                    max_ch_volume = volume
    
    # 返回下一个章节
    return max_ch + 1 if max_ch > 0 else 1, max_ch_volume

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--complete":
        # 通过文件确定当前章节
        current, _ = find_current_by_files()
        state = load_state()
        state["current_chapter"] = current + 1
        if "completed" not in state:
            state["completed"] = []
        if current not in state["completed"]:
            state["completed"].append(current)
        save_state(state)
        print(f"✅ 第{current}章已完成！下一章: 第{state['current_chapter']}章")
    else:
        # 确保 current_chapter 与文件同步（只增不减）
        state = load_state()
        file_based, volume = find_current_by_files()
        if file_based > state.get("current_chapter", 1):
            state["current_chapter"] = file_based
            save_state(state)
        print(get_next_task_prompt())
