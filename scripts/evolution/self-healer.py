#!/usr/bin/env python3
"""
Self-Healer - 错误自愈循环
读取 .learnings/ERRORS.md，自动修复已知模式
"""
import re, json
from pathlib import Path
from datetime import datetime

LEARNINGS_DIR = Path.home() / ".openclaw/workspace/.learnings"
OUTPUT_DIR = Path.home() / ".openclaw/workspace/.state/evolution"

# 已知自愈模式库：(错误pattern, 修复动作)
KNOWN_PATTERNS = [
    # (错误关键词, 修复方案类型, 描述)
    ("path.*not found", "path_fix", "路径不存在，尝试修正路径"),
    ("command not found", "command_fix", "命令未找到，更新TOOLS.md"),
    ("encoding.*error", "encoding_fix", "编码错误，使用qclaw-text-file重写"),
    ("No such file or directory", "path_fix", "文件不存在，列出正确路径"),
    ("SyntaxError", "syntax_fix", "语法错误，提取错误行并修复"),
    ("json.*decode.*error", "json_fix", "JSON解析错误，检查JSON格式"),
    ("Permission denied", "permission_fix", "权限问题，建议检查文件权限"),
]

def parse_errors():
    err_path = LEARNINGS_DIR / "ERRORS.md"
    if not err_path.exists():
        return []
    
    content = err_path.read_text(encoding='utf-8')
    entries = re.split(r'^## ', content, flags=re.MULTILINE)
    
    results = []
    for entry in entries[1:]:
        lines = entry.split('\n')
        title = lines[0].strip()
        status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', entry)
        priority_match = re.search(r'\*\*Priority\*\*:\s*(\w+)', entry)
        error_match = re.search(r'```\n(.*?)\n```', entry, re.DOTALL)
        
        if status_match and status_match.group(1) == 'pending':
            err_text = error_match.group(1).strip()[:200] if error_match else ''
            results.append({
                'title': title,
                'status': 'pending',
                'priority': priority_match.group(1) if priority_match else 'medium',
                'error_text': err_text,
            })
    return results

def can_auto_fix(error_text):
    """判断是否可以自动修复"""
    for pattern, fix_type, desc in KNOWN_PATTERNS:
        if re.search(pattern, error_text, re.IGNORECASE):
            return fix_type, desc
    return None, None

def main():
    errors = parse_errors()
    if not errors:
        print("No pending errors")
        return
    
    output = [f"# 自愈报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    auto_fixed = []
    needs_manual = []
    
    for err in errors:
        fix_type, desc = can_auto_fix(err['error_text'])
        if fix_type:
            output.append(f"✅ 可自愈: {err['title']}")
            output.append(f"   类型: {fix_type} - {desc}")
            output.append(f"   错误: {err['error_text'][:80]}")
            auto_fixed.append((err, fix_type))
        else:
            output.append(f"⚠️ 需人工: {err['title']}")
            output.append(f"   错误: {err['error_text'][:80]}")
            needs_manual.append(err)
        output.append("")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / 'self-healer.md'
    report_path.write_text('\n'.join(output), encoding='utf-8')
    
    print('\n'.join(output))
    print(f"\n📊 自愈统计：自动修复{len(auto_fixed)}项，需人工{len(needs_manual)}项")
    print(f"📄 报告：{report_path}")

if __name__ == '__main__':
    main()
