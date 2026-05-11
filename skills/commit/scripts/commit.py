#!/usr/bin/env python3
"""commit.py — 智能 git commit 工具"""

import subprocess
import sys
import re
from pathlib import Path

TYPE_MAP = {
    'feat': '新功能',
    'fix': '修复 bug',
    'docs': '文档更新',
    'style': '代码格式（不影响功能）',
    'refactor': '重构',
    'perf': '性能优化',
    'test': '测试相关',
    'chore': '构建/工具变动',
}

TYPE_PATTERNS = {
    'feat': [r'new', r'add', r'feature', r'init'],
    'fix': [r'fix', r'bug', r'hotfix', r'patch'],
    'docs': [r'readme', r'docs?/', r'\.md$', r'doc'],
    'test': [r'test', r'spec', r'__tests?__'],
    'refactor': [r'refactor', r'rename', r'rewrite'],
    'perf': [r'perf', r'speed', r'optim'],
    'chore': [r'chore', r'tool', r'script'],
}

def run(cmd, capture=True):
    """执行 shell 命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture,
            text=True, timeout=30, cwd=Path.cwd()
        )
        return result.stdout.strip() if capture else ''
    except Exception as e:
        return f'Error: {e}'

def get_status():
    """获取 git 状态"""
    return run('git status --porcelain')

def get_diff_stat():
    """获取 diff 统计"""
    return run('git diff --stat')

def get_changed_files():
    """获取变更文件列表"""
    output = run('git diff --name-only')
    if not output:
        output = run('git diff --cached --name-only')
    return [f for f in output.split('\n') if f]

def detect_type(files):
    """根据变更文件推断类型"""
    patterns = {
        'docs': [r'readme', r'docs?/', r'\.md$'],
        'test': [r'test', r'spec', r'__tests?__'],
        'fix': [r'fix', r'bug', r'hotfix'],
        'feat': [r'new', r'add', r'feature'],
        'refactor': [r'refactor', r'rename', r'rewrite'],
    }

    for f in files:
        for t, pats in TYPE_PATTERNS.items():
            if any(re.search(p, f.lower()) for p in pats):
                return t
    return 'feat'

def generate_message(files, dry_run=False):
    """生成 commit message"""
    status = get_status()
    if not status:
        return None, 'Nothing to commit (working tree clean)'

    diff_stat = get_diff_stat()
    changed_files = get_changed_files()

    # 简单推断
    commit_type = detect_type(changed_files)
    type_desc = TYPE_MAP.get(commit_type, commit_type)

    # 生成 subject
    if len(changed_files) == 1:
        subject = changed_files[0].split('/')[-1].replace('_', ' ').replace('-', ' ')
    else:
        subject = f'Update {len(changed_files)} files'

    message = f'{commit_type}: {subject}'

    if dry_run:
        return message, diff_stat

    return message, diff_stat

def do_commit(message):
    """执行 commit"""
    # Stage all changes
    run('git add -A', capture=False)

    # Commit
    result = run(f'git commit -m "{message}"')
    if 'nothing to commit' in result.lower():
        return result
    return result or 'Committed successfully'

def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args or '-n' in args
    commit_type = None

    # 解析 type
    if '--type' in args:
        idx = args.index('--type')
        if idx + 1 < len(args):
            commit_type = args[idx + 1]

    message, details = generate_message(None, dry_run=dry_run)

    if message is None:
        print(details)
        sys.exit(0)

    print('=== Commit Message ===')
    print(message)
    print()
    print('=== Changes ===')
    print(details)
    print()

    if dry_run:
        print('(dry-run mode, no commit created)')
    else:
        result = do_commit(message)
        print(result)

if __name__ == '__main__':
    main()
