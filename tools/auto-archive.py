#!/usr/bin/env python3
"""
数据归档自动化脚本
- 归档心跳报告（保留最近30天）
- 归档进化里程碑（按月归档）
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def archive_heartbeat_reports():
    """归档心跳报告，保留最近30天"""
    data_dir = Path("/Users/fuzhuo/.openclaw/workspace/data")
    archive_dir = data_dir / "archived" / "heartbeat"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    cutoff_date = datetime.now() - timedelta(days=30)
    reports = list(data_dir.glob("heartbeat-report-*.json"))
    
    archived = 0
    for report in reports:
        # 从文件名提取日期
        try:
            date_str = report.stem.replace("heartbeat-report-", "")
            report_date = datetime.strptime(date_str, "%Y%m%d-%H%M")
            
            if report_date < cutoff_date:
                # 按年月创建子目录
                month_dir = archive_dir / report_date.strftime("%Y-%m")
                month_dir.mkdir(exist_ok=True)
                
                dest = month_dir / report.name
                shutil.move(str(report), str(dest))
                archived += 1
        except:
            continue
    
    return archived

def archive_evolution_milestones():
    """按月归档进化里程碑"""
    data_dir = Path("/Users/fuzhuo/.openclaw/workspace/data")
    log_file = data_dir / "evolution-log.json"
    archive_dir = data_dir / "archived" / "evolution"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    if not log_file.exists():
        return 0, 0
    
    with open(log_file) as f:
        data = json.load(f)
    
    milestones = data.get("milestones", [])
    
    # 按月份分组
    by_month = {}
    current_month = datetime.now().strftime("%Y-%m")
    
    for m in milestones:
        try:
            ts = m.get("timestamp", "")
            month = ts[:7]  # YYYY-MM
            
            if month != current_month:
                by_month.setdefault(month, []).append(m)
        except:
            continue
    
    # 归档历史月份
    archived_count = 0
    for month, month_milestones in by_month.items():
        archive_file = archive_dir / f"milestones-{month}.json"
        
        # 合并已有归档
        if archive_file.exists():
            with open(archive_file) as f:
                existing = json.load(f)
            month_milestones = existing.get("milestones", []) + month_milestones
        
        with open(archive_file, 'w') as f:
            json.dump({"milestones": month_milestones}, f, indent=2)
        
        archived_count += len(month_milestones)
    
    # 保留当前月份到主文件
    current_milestones = [m for m in milestones if m.get("timestamp", "").startswith(current_month)]
    data["milestones"] = current_milestones[-50:]  # 最多保留50条
    
    with open(log_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return archived_count, len(current_milestones)

def main():
    print("🗂️  执行数据归档...")
    print("-" * 50)
    
    # 1. 归档心跳报告
    hb_archived = archive_heartbeat_reports()
    print(f"  📁 心跳报告归档: {hb_archived} 个")
    
    # 2. 归档进化里程碑
    ev_archived, ev_kept = archive_evolution_milestones()
    print(f"  📁 进化里程碑归档: {ev_archived} 个")
    print(f"  📄 本月保留: {ev_kept} 个")
    
    print("-" * 50)
    print("✅ 归档完成")
    
    return {
        "heartbeat_archived": hb_archived,
        "evolution_archived": ev_archived,
        "evolution_kept": ev_kept
    }

if __name__ == "__main__":
    main()
