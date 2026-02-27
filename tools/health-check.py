#!/usr/bin/env python3
"""
健康检查脚本 - Health Check
检查系统关键组件状态，输出健康报告
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"


class HealthChecker:
    def __init__(self):
        self.checks = []
        self.timestamp = datetime.now()
    
    def check(self, name: str, func) -> Dict:
        """执行单个检查"""
        try:
            result = func()
            status = "ok" if result.get("status") == "ok" else "warning"
            return {"name": name, "status": status, **result}
        except Exception as e:
            return {"name": name, "status": "error", "message": str(e)}
    
    def check_gateway(self) -> Dict:
        """检查 Gateway 状态"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"status": "ok", "message": "Gateway 运行中"}
            return {"status": "error", "message": result.stderr[:100]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        try:
            result = subprocess.run(
                ["df", "-h", str(WORKSPACE)],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                usage = parts[4].replace('%', '')
                if int(usage) > 90:
                    return {"status": "error", "usage": f"{usage}%", "message": "磁盘空间不足"}
                return {"status": "ok", "usage": f"{usage}%"}
            return {"status": "warning", "message": "无法获取磁盘信息"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_recent_heartbeat(self) -> Dict:
        """检查最近心跳"""
        try:
            reports = sorted(DATA_DIR.glob("heartbeat-report-*.json"))
            if not reports:
                return {"status": "error", "message": "无心跳报告"}
            
            latest = reports[-1]
            mtime = datetime.fromtimestamp(latest.stat().st_mtime)
            age_minutes = (self.timestamp - mtime).total_seconds() / 60
            
            if age_minutes > 120:  # 超过2小时
                return {"status": "error", "age": f"{age_minutes:.0f}分钟", "message": "心跳过旧"}
            return {"status": "ok", "age": f"{age_minutes:.0f}分钟"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_skills(self) -> Dict:
        """检查 Skills 数量"""
        try:
            skills_dir = WORKSPACE / "skills"
            skills = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            if len(skills) < 10:
                return {"status": "warning", "count": len(skills), "message": "Skills 数量偏少"}
            return {"status": "ok", "count": len(skills)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_task_board(self) -> Dict:
        """检查任务看板"""
        try:
            task_file = WORKSPACE / "task-board.json"
            if not task_file.exists():
                return {"status": "warning", "message": "无任务看板"}
            
            with open(task_file) as f:
                tasks = json.load(f)
            
            done = sum(1 for t in tasks if t.get("status") == "done")
            total = len(tasks)
            
            return {"status": "ok", "total": total, "done": done, "pending": total - done}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_logs(self) -> Dict:
        """检查错误日志"""
        try:
            log_file = WORKSPACE / "data" / "logs" / "error.log"
            if not log_file.exists():
                return {"status": "ok", "errors": 0}
            
            with open(log_file) as f:
                lines = f.readlines()
            
            # 检查最近1小时的错误
            recent_errors = []
            cutoff = self.timestamp.timestamp() - 3600
            
            for line in lines[-100:]:
                try:
                    # 简单解析时间戳
                    if 'ERROR' in line or 'CRITICAL' in line:
                        recent_errors.append(line.strip())
                except:
                    pass
            
            if len(recent_errors) > 10:
                return {"status": "warning", "errors": len(recent_errors), "message": "错误偏多"}
            return {"status": "ok", "errors": len(recent_errors)}
        except Exception as e:
            return {"status": "ok", "errors": 0}
    
    def run_all(self) -> List[Dict]:
        """运行所有检查"""
        checks = [
            ("Gateway", self.check_gateway),
            ("磁盘空间", self.check_disk_space),
            ("心跳", self.check_recent_heartbeat),
            ("Skills", self.check_skills),
            ("任务看板", self.check_task_board),
            ("错误日志", self.check_logs),
        ]
        
        results = []
        for name, func in checks:
            result = self.check(name, func)
            results.append(result)
            self.checks.append(result)
        
        return results


def main():
    checker = HealthChecker()
    
    print("=" * 50)
    print(f"🔍 健康检查 - {checker.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = checker.run_all()
    
    # 统计
    ok = sum(1 for r in results if r["status"] == "ok")
    warning = sum(1 for r in results if r["status"] == "warning")
    error = sum(1 for r in results if r["status"] == "error")
    
    print(f"\n📊 总体状态: {ok} ✅ / {warning} ⚠️ / {error} ❌")
    print("-" * 50)
    
    for r in results:
        icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}[r["status"]]
        msg = r.get("message", r.get("usage", r.get("age", "")))
        print(f"  {icon} {r['name']}: {msg}")
    
    print("-" * 50)
    
    if error > 0:
        print(f"\n⚠️  发现 {error} 个问题，请检查！")
        sys.exit(1)
    elif warning > 0:
        print(f"\n💡 发现 {warning} 个警告项")
        sys.exit(0)
    else:
        print("\n✅ 系统健康")
        sys.exit(0)


if __name__ == "__main__":
    main()
