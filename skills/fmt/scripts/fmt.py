#!/usr/bin/env python3
"""fmt.py — 代码格式化工具，调用 Prettier"""

import subprocess
import sys
from pathlib import Path

PRETTIER_EXTS = {
    '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
    '.css', '.scss', '.html', '.yaml', '.yml', '.vue', '.svelte'
}

def get_files(paths):
    """解析输入路径，返回文件列表"""
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(str(path))
        elif path.is_dir():
            # 递归查找所有支持的文件
            for ext in PRETTIER_EXTS:
                files.extend([str(f) for f in path.rglob(f'*{ext}')])
        else:
            # glob 模式
            files.extend([str(f) for f in Path('.').glob(p) if f.is_file()])
    return list(set(files))

def format_file(file_path):
    """格式化单个文件"""
    ext = Path(file_path).suffix.lower()
    if ext not in PRETTIER_EXTS:
        return f'— Skipped (not supported): {file_path}'

    try:
        result = subprocess.run(
            ['prettier', '--write', file_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return f'✓ Formatted: {file_path}'
        else:
            return f'✗ Error: {file_path} — {result.stderr}'
    except subprocess.TimeoutExpired:
        return f'✗ Timeout: {file_path}'
    except Exception as e:
        return f'✗ Exception: {file_path} — {e}'

def main():
    # 跳过脚本自身路径（sys.argv[0]）
    args = sys.argv[1:]

    if not args:
        print('Usage: fmt.py <file_or_dir_or_glob> [...]')
        sys.exit(1)

    files = get_files(args)

    if not files:
        print('No files found.')
        sys.exit(1)

    print(f'Formatting {len(files)} file(s)...\n')

    for f in files:
        print(format_file(f))

if __name__ == '__main__':
    main()
