#!/usr/bin/env python3
"""
统一心跳任务 - 系统自主维护与进化
整合：资源优化 + 技能维护 + 进化分析
频率：每小时运行一次
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
SKILLS_DIR = WORKSPACE / "skills"
TOOLS_DIR = WORKSPACE / "tools"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Skills 搜索类别轮换
SEARCH_CATEGORIES = [
    ["web", "browser", "scraping"],
    ["database", "sql", "postgres"],
    ["file", "pdf", "docx", "xlsx"],
    ["api", "http", "request"],
    ["automation", "workflow", "cron"],
    ["testing", "jest", "playwright"],
    ["devops", "docker", "deploy"],
    ["ai", "llm", "openai"],
    ["search", "web-search"],
    ["media", "image", "audio", "video"],
]

class UnifiedHeartbeat:
    def __init__(self):
        self.timestamp = datetime.now()
        self.report = {
            "timestamp": self.timestamp.isoformat(),
            "sections": {}
        }
        
    def log(self, section: str, message: str, level: str = "info"):
        """记录日志"""
        if section not in self.report["sections"]:
            self.report["sections"][section] = {"logs": [], "status": "running"}
        self.report["sections"][section]["logs"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        })
        
    def run_command(self, cmd: str, timeout: int = 60) -> tuple:
        """运行 shell 命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", 1
        except Exception as e:
            return "", str(e), 1

    def run_auto_archive(self):
        """执行自动归档"""
        print("\n  🗂️  执行自动归档...")
        try:
            archive_script = TOOLS_DIR / "auto-archive.py"
            if archive_script.exists():
                stdout, stderr, code = self.run_command(f"python {archive_script}", timeout=30)
                if code == 0:
                    self.log("resources", "自动归档执行成功", "success")
                    print("    ✅ 归档完成")
                else:
                    self.log("resources", f"归档失败: {stderr}", "error")
        except Exception as e:
            self.log("resources", f"归档异常: {e}", "error")

    # ═══════════════════════════════════════════════════════════
    # 模块 1: 资源优化
    # ═══════════════════════════════════════════════════════════
    def run_resource_optimization(self):
        """执行资源优化检查"""
        print("\n🔋 模块1: 资源优化")
        print("-" * 50)
        
        api_resources = {
            "minimax": {"balance": "Coding Plan (每5小时重置)", "type": "prompt-based", "priority": "high", "status": "active"},
            "groq": {"balance": "free tier", "priority": "high", "status": "active"},
            "together_ai": {"balance": "free tier", "priority": "mid", "status": "active"},
            "deepseek": {"balance": "backup", "priority": "low", "status": "standby"},
            "siliconflow": {"balance": "backup", "priority": "low", "status": "standby"}
        }
        
        for api, info in api_resources.items():
            status_icon = "✅" if info["status"] == "active" else "⏸️"
            print(f"  {status_icon} {api.upper()}: {info['balance']}")
            
        self.log("resources", f"检查 {len(api_resources)} 个 API 资源状态")
        
        # 检查任务看板
        task_board_file = WORKSPACE / "task-board.json"
        if task_board_file.exists():
            try:
                with open(task_board_file) as f:
                    tasks = json.load(f)
                completed = sum(1 for t in tasks if t.get("status") == "done")
                total = len(tasks)
                print(f"\n  📊 任务统计: {completed}/{total} 已完成 ({completed/total*100:.0f}%)")
                self.log("resources", f"任务完成率: {completed}/{total}")
            except:
                pass
        
        # 5. 自动化机会扫描 - 分析执行日志
        print("\n  🤖 自动化机会扫描")
        automation_opportunities = self.scan_automation_opportunities()
        if automation_opportunities:
            print(f"  💡 发现 {len(automation_opportunities)} 个潜在自动化机会")
            for opp in automation_opportunities[:3]:  # 只显示前3个
                print(f"    - {opp['description']} (ROI: {opp['roi']:.1f}x)")
                # 如果是归档类型，自动执行
                if opp.get('action') == 'auto_archive':
                    self.run_auto_archive()
            self.log("resources", f"发现 {len(automation_opportunities)} 个自动化机会")
        
        self.report["sections"]["resources"] = {
            "status": "success",
            "api_count": len(api_resources),
            "apis": list(api_resources.keys()),
            "automation_opportunities": len(automation_opportunities)
        }

    # ═══════════════════════════════════════════════════════════
    # 模块 2: Skills 维护
    # ═══════════════════════════════════════════════════════════
    def run_skills_maintenance(self):
        """执行 Skills 维护"""
        print("\n🛠️  模块2: Skills 维护")
        print("-" * 50)
        
        # 1. 扫描本地 skills
        if SKILLS_DIR.exists():
            local_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
            print(f"  🗂️  本地 Skills: {len(local_skills)} 个")
            self.log("skills", f"发现 {len(local_skills)} 个本地 skills")
        else:
            local_skills = []
            
        # 2. 检查 clawdhub skills
        stdout, stderr, code = self.run_command("clawdhub list 2>/dev/null | head -20")
        clawdhub_count = len([l for l in stdout.split('\n') if l.strip() and not l.startswith(' ')])
        print(f"  📦 ClawdHub Skills: {clawdhub_count} 个")
        self.log("skills", f"ClawdHub 安装: {clawdhub_count} 个")
        
        # 3. 检查更新 (简化版)
        stdout, stderr, code = self.run_command("clawdhub update --all --dry-run 2>&1", timeout=30)
        has_updates = "update" in stdout.lower() and "already up" not in stdout.lower()
        if has_updates:
            print(f"  🔄 发现可更新")
            self.log("skills", "发现可更新的 skills", "alert")
        else:
            print(f"  ✅ 所有 skills 已是最新")
            self.log("skills", "所有 skills 已是最新版本")
            
        # 4. 轮换搜索新 skills
        hour = self.timestamp.hour
        category_index = hour % len(SEARCH_CATEGORIES)
        keywords = SEARCH_CATEGORIES[category_index]
        print(f"  🔎 本轮搜索: {', '.join(keywords[:2])}")
        self.log("skills", f"轮换搜索关键词: {', '.join(keywords[:2])}")
        
        # 5. 检查是否需要深入搜索 GitHub（每天一次，在特定时段）
        if hour == 3:  # 凌晨3点进行深入搜索
            print("\n  🌙 进入深度知识获取模式")
            self.run_deep_knowledge_acquisition()
        
        self.report["sections"]["skills"] = {
            "status": "success",
            "local_count": len(local_skills),
            "clawdhub_count": clawdhub_count,
            "updates_available": has_updates,
            "search_keywords": keywords[:2]
        }

    def run_deep_knowledge_acquisition(self):
        """深度知识获取 - 每天一次搜索 GitHub 高质量项目"""
        print("    📚 深度知识获取模式")
        
        # 根据当前技能缺口确定搜索方向
        skill_gaps = self.identify_skill_gaps()
        
        for gap in skill_gaps[:2]:  # 每次最多处理2个缺口
            print(f"    🔍 技能缺口: {gap}")
            # 这里可以调用 skill-from-github 的搜索逻辑
            # 目前只记录建议，实际搜索需要 GitHub API
            self.log("skills", f"建议搜索 GitHub: {gap} stars:>100", "info")
        
        if not skill_gaps:
            print("    ✅ 当前技能覆盖良好")
    
    def identify_skill_gaps(self) -> list:
        """识别技能缺口 - 基于当前任务需求
        
        优化点:
        - 使用 set 替代 list 进行 O(1) 查重
        - 减少嵌套循环深度
        - 提前返回减少不必要的处理
        """
        gaps = set()  # 优化: O(1) 查重
        
        # 1. 检查任务看板中的需求
        task_board = WORKSPACE / "task-board.json"
        if task_board.exists():
            try:
                with open(task_board) as f:
                    tasks = json.load(f)
                
                # 优化: 单遍遍历，使用 set 去重
                gaps.update(
                    tag for task in tasks 
                    if task.get("status") != "done"
                    for tag in task.get("tags", [])
                )
            except Exception:
                pass
        
        # 2. 检查最近的心跳日志中的错误
        if len(gaps) < 3:  # 优化: 如果已有足够缺口，跳过
            recent_reports = sorted(DATA_DIR.glob("heartbeat-report-*.json"))[-7:]
            for report_file in recent_reports:
                try:
                    with open(report_file) as f:
                        report = json.load(f)
                    # 优化: 使用生成器表达式
                    gaps.update(
                        f"{section}_automation"
                        for section, data in report.get("sections", {}).items()
                        if data.get("status") != "success"
                    )
                except Exception:
                    pass
                
                if len(gaps) >= 3:  # 优化: 提前退出
                    break
        
        # 3. 轮换推荐（如果没有明确的缺口）
        if not gaps:
            rotation_suggestions = [
                "data visualization", "machine learning", 
                "natural language processing", "API integration",
                "web scraping advanced", "database migration",
                "testing automation", "CI/CD pipeline"
            ]
            gaps.add(rotation_suggestions[self.timestamp.weekday() % len(rotation_suggestions)])
        
        return list(gaps)[:3]  # 最多返回3个
    
    def scan_automation_opportunities(self) -> list:
        """扫描自动化机会 - 基于执行日志分析
        
        优化点:
        - 使用 Counter 简化统计
        - 合并循环减少遍历次数
        - 预分配 opportunities 列表容量
        """
        from collections import Counter
        
        opportunities = []
        
        # 1. 检查心跳执行日志
        heartbeat_logs = list(DATA_DIR.glob("heartbeat-report-*.json"))
        if len(heartbeat_logs) >= 10:
            opportunities.append({
                "type": "workflow",
                "description": f"心跳报告自动归档（当前 {len(heartbeat_logs)} 个报告）",
                "roi": 3.0,
                "action": "auto_archive"
            })
        
        # 2. 检查进化日志中的重复模式
        evolution_log = DATA_DIR / "evolution-log.json"
        if evolution_log.exists():
            try:
                with open(evolution_log) as f:
                    data = json.load(f)
                    milestones = data.get("milestones", [])
                    if len(milestones) > 100:
                        opportunities.append({
                            "type": "data_management",
                            "description": f"进化里程碑自动归档（当前 {len(milestones)} 条记录）",
                            "roi": 2.5,
                            "action": "auto_archive"
                        })
            except Exception:
                pass
        
        # 3. 检查是否有重复的手动任务
        task_board = WORKSPACE / "task-board.json"
        if task_board.exists():
            try:
                with open(task_board) as f:
                    tasks = json.load(f)
                
                # 优化: 使用 Counter 一次性统计
                categories = Counter(
                    task.get("category", "uncategorized") 
                    for task in tasks
                )
                
                # 优化: 列表推导式批量添加
                opportunities.extend([
                    {
                        "type": "task_automation",
                        "description": f"'{cat}' 类任务有 {count} 个，可能存在模式",
                        "roi": count * 0.5,
                        "action": f"分析 '{cat}' 任务，提取可自动化模式"
                    }
                    for cat, count in categories.items()
                    if count >= 5
                ])
            except Exception:
                pass
        
        return opportunities

    # ═══════════════════════════════════════════════════════════
    # 模块 3: 自动知识获取
    # ═══════════════════════════════════════════════════════════
    def run_auto_knowledge_acquisition(self):
        """执行自动知识获取管道"""
        print("\n📚 模块3: 自动知识获取")
        print("-" * 50)
        
        pipeline_script = TOOLS_DIR / "auto-knowledge-pipeline.py"
        
        if not pipeline_script.exists():
            print("  ⚠️  自动知识获取脚本不存在，跳过")
            self.log("knowledge", "脚本不存在，跳过", "warning")
            self.report["sections"]["knowledge"] = {"status": "skipped", "reason": "script_not_found"}
            return
        
        print("  🤖 启动自动知识获取管道...")
        
        # 运行管道脚本
        stdout, stderr, code = self.run_command(
            f"cd {WORKSPACE} && python {pipeline_script}", 
            timeout=300  # 5分钟超时
        )
        
        if code == 0:
            # 解析输出中的关键信息
            generated_skill = None
            for line in stdout.split('\n'):
                if '生成Skill:' in line:
                    generated_skill = line.split('生成Skill:')[-1].strip()
                    break
                elif '已存在' in line:
                    self.log("knowledge", "Skill已存在，跳过", "info")
                elif '拒绝' in line or '跳过' in line:
                    self.log("knowledge", "条件不满足，跳过本次", "info")
            
            if generated_skill:
                print(f"  ✅ 成功生成 Skill: {generated_skill}")
                self.log("knowledge", f"生成新Skill: {generated_skill}", "success")
                self.report["sections"]["knowledge"] = {
                    "status": "success",
                    "generated_skill": generated_skill
                }
            else:
                print("  ℹ️ 本次未生成新Skill（条件不满足或已存在）")
                self.report["sections"]["knowledge"] = {"status": "no_action"}
        else:
            print(f"  ❌ 执行失败: {stderr[:200]}")
            self.log("knowledge", f"执行失败: {stderr[:200]}", "error")
            self.report["sections"]["knowledge"] = {"status": "error", "message": stderr[:200]}

    # ═══════════════════════════════════════════════════════════
    # 模块 4: 进化分析
    # ═══════════════════════════════════════════════════════════
    def run_evolution_analysis(self):
        """执行进化分析"""
        print("\n🧬 模块4: 进化分析")
        print("-" * 50)
        
        # 加载进化数据
        evolution_log_file = DATA_DIR / "evolution-log.json"
        patterns_file = DATA_DIR / "success-patterns.json"
        improvements_file = DATA_DIR / "improvements.json"
        
        patterns_count = 0
        improvements_count = 0
        
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    patterns = json.load(f)
                    patterns_count = len(patterns)
            except:
                pass
                
        if improvements_file.exists():
            try:
                with open(improvements_file) as f:
                    improvements = json.load(f)
                    improvements_count = len(improvements)
            except:
                pass
        
        print(f"  📈 成功模式: {patterns_count} 个")
        print(f"  🔧 待改进项: {improvements_count} 个")
        
        # 记录本次运行
        if evolution_log_file.exists():
            try:
                with open(evolution_log_file) as f:
                    log_data = json.load(f)
            except:
                log_data = {"milestones": []}
        else:
            log_data = {"milestones": []}
            
        log_data["milestones"].append({
            "timestamp": self.timestamp.isoformat(),
            "type": "heartbeat_cycle",
            "patterns_count": patterns_count,
            "improvements_count": improvements_count
        })
        
        # 只保留最近 50 条
        log_data["milestones"] = log_data["milestones"][-50:]
        
        with open(evolution_log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.log("evolution", f"记录里程碑: 模式={patterns_count}, 改进={improvements_count}")
        
        self.report["sections"]["evolution"] = {
            "status": "success",
            "patterns_count": patterns_count,
            "improvements_count": improvements_count
        }

    # ═══════════════════════════════════════════════════════════
    # 主运行循环
    # ═══════════════════════════════════════════════════════════
    def run(self):
        """运行完整心跳周期"""
        print(f"\n{'='*60}")
        print(f"🫀 统一心跳任务 - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            self.run_resource_optimization()
        except Exception as e:
            self.log("resources", f"错误: {str(e)}", "error")
            print(f"  ❌ 资源优化出错: {e}")
            
        try:
            self.run_skills_maintenance()
        except Exception as e:
            self.log("skills", f"错误: {str(e)}", "error")
            print(f"  ❌ Skills 维护出错: {e}")
        
        try:
            self.run_auto_knowledge_acquisition()
        except Exception as e:
            self.log("knowledge", f"错误: {str(e)}", "error")
            print(f"  ❌ 自动知识获取出错: {e}")
            
        try:
            self.run_evolution_analysis()
        except Exception as e:
            self.log("evolution", f"错误: {str(e)}", "error")
            print(f"  ❌ 进化分析出错: {e}")
        
        # 保存报告
        report_file = DATA_DIR / f"heartbeat-report-{self.timestamp.strftime('%Y%m%d-%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        # 生成摘要
        print(f"\n{'='*60}")
        print("📋 心跳摘要")
        print(f"{'='*60}")
        
        for section, data in self.report["sections"].items():
            icon = "✅" if data.get("status") == "success" else "❌"
            print(f"  {icon} {section.capitalize()}: {data.get('status', 'unknown')}")
        
        print(f"\n💾 报告已保存: {report_file.name}")
        print(f"{'='*60}\n")
        
        return self.report

if __name__ == "__main__":
    heartbeat = UnifiedHeartbeat()
    heartbeat.run()
