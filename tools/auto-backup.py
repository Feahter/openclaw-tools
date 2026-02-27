#!/usr/bin/env python3
"""
自动备份脚本 - Auto Backup
自动备份关键数据到本地归档目录
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
BACKUP_DIR = WORKSPACE / "data" / "backups"
ARCHIVE_DIR = WORKSPACE / "data" / "archived"

# 需要备份的关键文件/目录
BACKUP_TARGETS = [
    ("memory", "memory", "*.md"),
    ("task-board.json", "data", "task-board.json"),
    ("config", "config", "*.yaml"),
]

# 保留天数
RETENTION_DAYS = 30


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_backup_name(prefix: str) -> str:
    """生成备份文件名"""
    return f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def backup_file(src: Path, dest_dir: Path) -> bool:
    """备份单个文件"""
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        return True
    except Exception as e:
        log(f"备份失败 {src}: {e}")
        return False


def backup_dir(src: Path, dest_dir: Path, pattern: str = "*") -> bool:
    """备份目录"""
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules'))
        return True
    except Exception as e:
        log(f"备份失败 {src}: {e}")
        return False


def cleanup_old_backups():
    """清理旧备份"""
    if not BACKUP_DIR.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    
    for item in BACKUP_DIR.iterdir():
        if item.is_dir():
            # 检查目录修改时间
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                log(f"删除旧备份: {item.name}")
                shutil.rmtree(item)


def main():
    log("=" * 50)
    log("🚀 自动备份开始")
    log("=" * 50)
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 今天的备份目录
    today_dir = BACKUP_DIR / get_backup_name("daily")
    
    success_count = 0
    fail_count = 0
    
    for target, category, pattern in BACKUP_TARGETS:
        src = WORKSPACE / target
        dest = today_dir / category
        
        if not src.exists():
            log(f"跳过 (不存在): {target}")
            continue
        
        if src.is_dir():
            if backup_dir(src, dest):
                success_count += 1
                log(f"✅ 备份目录: {target}")
            else:
                fail_count += 1
        else:
            if backup_file(src, dest):
                success_count += 1
                log(f"✅ 备份文件: {target}")
            else:
                fail_count += 1
    
    # 清理旧备份
    log("\n🧹 清理旧备份...")
    cleanup_old_backups()
    
    # 写入备份记录
    record = {
        "timestamp": datetime.now().isoformat(),
        "backup_dir": str(today_dir),
        "success": success_count,
        "failed": fail_count,
        "targets": [t[0] for t in BACKUP_TARGETS]
    }
    
    record_file = BACKUP_DIR / "backup-records.json"
    records = []
    if record_file.exists():
        try:
            records = json.load(open(record_file))
        except:
            records = []
    
    records.append(record)
    records = records[-100:]  # 保留最近100条
    
    with open(record_file, 'w') as f:
        json.dump(records, f, indent=2)
    
    log("\n" + "=" * 50)
    log(f"✅ 备份完成: {success_count} 成功, {fail_count} 失败")
    log(f"📁 备份位置: {today_dir}")
    log("=" * 50)


if __name__ == "__main__":
    main()
