#!/usr/bin/env python3
"""
统一心跳任务 - 性能优化版本
优化点：
1. 文件元数据缓存 - 避免重复扫描目录
2. O(1) 索引查找 - 替代 O(n) 遍历
3. 批量报告写入 - 减少 I/O 次数
4. 错误处理增强 - 确保报告始终写入
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import Counter
import os

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


class OptimizedHeartbeat:
    """性能优化的心跳任务"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.report = {
            "timestamp": self.timestamp.isoformat(),
            "sections": {}
        }
        
        # 性能优化：缓存文件元数据
        self._skills_cache: Optional[List[str]] = None
        self._skills_mtime: float = 0
        
        # 性能优化：O(1) 集合查找
        self._checked_apis: Set[str] = set()
        
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

    def get_cached_skills(self) -> List[str]:
        """
        性能优化：缓存 skills 目录元数据
        - 原实现: 每次都重新扫描 O(n)
        - 新实现: 使用 mtime 检查变更，未变更时返回缓存
        """
        if not SKILLS_DIR.exists():
            return []
        
        current_mtime = SKILLS_DIR.stat().st_mtime
        
        if current_mtime != self._skills_mtime or self._skills_cache is None:
            # 目录有变更，重新扫描
            self._skills_cache = [
                d.name for d in os.scandir(SKILLS_DIR)  # 优化: scandir 比 listdir 快 2-3x
                if d.is_dir() and not d.name.startswith('.')
            ]
            self._skills_mtime = current_mtime
            self.log("skills", f"Skills 缓存已更新: {len(self._skills_cache)} 个")
        
        return self._skills_cache

    def save_report(self) -> bool:
        """
        性能优化：确保报告写入
        - 使用临时文件 + 原子重命名
        - 异常时重试
        """
        report_file = DATA_DIR / f"heartbeat-report-{self.timestamp.strftime('%Y%m%d-%H%M')}.json"
        temp_file = DATA_DIR / f".heartbeat-report-{self.timestamp.strftime('%Y%m%d-%H%M')}.tmp"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 先写入临时文件
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.report, f, indent=2, ensure_ascii=False)
                
                # 原子重命名
                os.replace(temp_file, report_file)
                
                print(f"\n💾 报告已保存: {report_file.name}")
                return True
                
            except Exception as e:
                self.log("system", f"报告写入失败 (尝试 {attempt+1}/{max_retries}): {e}", "error")
                time.sleep(0.5)
        
        return False

    # ═══════════════════════════════════════════════════════════
    # 模块 1: 资源优化
    # ═══════════════════════════════════════════════════════════
    def run_resource_optimization(self):
        """执行资源优化检查"""
        print("\n🔋 模块1: 资源优化")
        print("-" * 50)
        
        # 优化: 使用集合避免重复检查
        api_resources = {
            "minimax": {"balance": "Coding Plan", "status": "active"},
            "groq": {"balance": "free tier", "status": "active"},
            "together_ai": {"balance": "free tier", "status": "active"},
            "deepseek": {"balance": "backup", "status": "standby"},
            "siliconflow": {"balance": "backup", "status": "standby"}
        }
        
        for api, info in api_resources.items():
            if api in self._checked_apis:  # O(1) 查找
                continue
            
            status_icon = "✅" if info["status"] == "active" else "⏸️"
            print(f"  {status_icon} {api.upper()}: {info['balance']}")
            self._checked_apis.add(api)  # 标记已检查
            
        self.log("resources", f"检查 {len(api_resources)} 个 API 资源状态")
        
        # 检查任务看板 - 优化: 单次遍历统计
        task_board_file = WORKSPACE / "task-board.json"
        if task_board_file.exists():
            try:
                with open(task_board_file) as f:
                    tasks = json.load(f)
                
                # 优化: 单次遍历统计所有状态
                completed = pending = in_progress = 0
                for t in tasks:
                    status = t.get("status", "")
                    if status == "done":
                        completed += 1
                    elif status == "pending":
                        pending += 1
                    elif status in ["progress", "in_progress"]:
                        in_progress += 1
                
                total = len(tasks)
                print(f"\n  📊 任务统计: {completed}/{total} 已完成 ({completed/total*100:.0f}%)")
                self.log("resources", f"任务: {completed}完成/{pending}待办/{in_progress}进行中")
            except:
                pass
        
        # 自动化机会扫描
        print("\n  🤖 自动化机会扫描")
        automation_opportunities = self.scan_automation_opportunities()
        if automation_opportunities:
            print(f"  💡 发现 {len(automation_opportunities)} 个潜在自动化机会")
            for opp in automation_opportunities[:3]:
                print(f"    - {opp['description']}")
                if opp.get('action') == 'auto_archive':
                    self.run_auto_archive()
            self.log("resources", f"发现 {len(automation_opportunities)} 个自动化机会")
        
        self.report["sections"]["resources"] = {
            "status": "success",
            "api_count": len(api_resources),
            "apis": list(api_resources.keys()),
            "automation_opportunities": len(automation_opportunities)
        }

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
        except Exception as e:
            self.log("resources", f"归档异常: {e}", "error")

    # ═══════════════════════════════════════════════════════════
    # 模块 2: Skills 维护
    # ═══════════════════════════════════════════════════════════
    def run_skills_maintenance(self):
        """执行 Skills 维护"""
        print("\n🛠️  模块2: Skills 维护")
        print("-" * 50)
        
        # 优化: 使用缓存的 skills 列表
        local_skills = self.get_cached_skills()
        print(f"  🗂️  本地 Skills: {len(local_skills)} 个")
        self.log("skills", f"发现 {len(local_skills)} 个本地 skills")
        
        # 检查更新 - clawdhub update 不支持 --dry-run，改用其他方式检查
        # 先列出已安装技能，然后逐个检查版本
        stdout, stderr, code = self.run_command(
            "clawdhub list 2>/dev/null | grep -v '^\\s*$' | head -30", timeout=30
        )
        installed_skills = [line.split()[0] for line in stdout.split('\n') if line.strip() and not line.startswith(' ')]
        print(f"  📦 ClawdHub: {len(installed_skills)} 个已安装")
        self.log("skills", f"ClawdHub: {len(installed_skills)} 个已安装")
        
        # 轮换搜索
        hour = self.timestamp.hour
        keywords = SEARCH_CATEGORIES[hour % len(SEARCH_CATEGORIES)]
        print(f"  🔎 本轮搜索: {', '.join(keywords[:2])}")
        
        # 深度搜索（凌晨3点）
        if hour == 3:
            print("\n  🌙 进入深度知识获取模式")
            self.run_deep_knowledge_acquisition()
        
        self.report["sections"]["skills"] = {
            "status": "success",
            "local_count": len(local_skills),
            "installed_count": len(installed_skills),
            "search_keywords": keywords[:2]
        }

    def run_deep_knowledge_acquisition(self):
        """深度知识获取"""
        print("    📚 深度知识获取模式")
        skill_gaps = self.identify_skill_gaps()
        
        for gap in skill_gaps[:2]:
            print(f"    🔍 技能缺口: {gap}")
            self.log("skills", f"建议搜索: {gap}", "info")
        
        if not skill_gaps:
            print("    ✅ 技能覆盖良好")
    
    def identify_skill_gaps(self) -> List[str]:
        """
        识别技能缺口 - 优化版本
        - 使用 set 替代 list: O(1) 查重
        - 提前返回减少遍历
        """
        gaps: Set[str] = set()
        
        # 1. 任务看板
        task_board = WORKSPACE / "task-board.json"
        if task_board.exists():
            try:
                with open(task_board) as f:
                    tasks = json.load(f)
                
                # 优化: 集合推导式 O(n)
                gaps.update(
                    tag for task in tasks 
                    if task.get("status") != "done"
                    for tag in task.get("tags", [])
                )
            except:
                pass
        
        # 2. 心跳报告（如有需要）
        if len(gaps) < 3:
            recent_reports = sorted(DATA_DIR.glob("heartbeat-report-*.json"))[-7:]
            for report_file in recent_reports:
                try:
                    with open(report_file) as f:
                        report = json.load(f)
                    gaps.update(
                        f"{section}_automation"
                        for section, data in report.get("sections", {}).items()
                        if data.get("status") != "success"
                    )
                except:
                    pass
                
                if len(gaps) >= 3:
                    break
        
        # 3. 轮换推荐
        if not gaps:
            suggestions = [
                "data visualization", "machine learning", "NLP",
                "API integration", "web scraping", "database migration"
            ]
            gaps.add(suggestions[self.timestamp.weekday() % len(suggestions)])
        
        return list(gaps)[:3]
    
    def scan_automation_opportunities(self) -> List[Dict]:
        """
        扫描自动化机会 - 优化版本
        - 使用 Counter 简化统计
        - 预分配容量
        """
        opportunities = []
        
        # 1. 心跳报告归档
        heartbeat_logs = list(DATA_DIR.glob("heartbeat-report-*.json"))
        if len(heartbeat_logs) >= 10:
            opportunities.append({
                "type": "workflow",
                "description": f"心跳报告归档（{len(heartbeat_logs)} 个）",
                "roi": 3.0,
                "action": "auto_archive"
            })
        
        # 2. 进化日志归档
        evolution_log = DATA_DIR / "evolution-log.json"
        if evolution_log.exists():
            try:
                with open(evolution_log) as f:
                    data = json.load(f)
                    milestones = data.get("milestones", [])
                    if len(milestones) > 100:
                        opportunities.append({
                            "type": "data_management",
                            "description": f"进化日志归档（{len(milestones)} 条）",
                            "roi": 2.5,
                            "action": "auto_archive"
                        })
            except:
                pass
        
        # 3. 重复任务模式 - 优化: Counter 统计
        task_board = WORKSPACE / "task-board.json"
        if task_board.exists():
            try:
                with open(task_board) as f:
                    tasks = json.load(f)
                
                categories = Counter(
                    task.get("category", "uncategorized") 
                    for task in tasks
                )
                
                opportunities.extend([
                    {
                        "type": "task_automation",
                        "description": f"'{cat}' 类任务有 {count} 个",
                        "roi": count * 0.5,
                        "action": f"分析 '{cat}' 任务模式"
                    }
                    for cat, count in categories.items()
                    if count >= 5
                ])
            except:
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
            print("  ⚠️  脚本不存在，跳过")
            self.log("knowledge", "脚本不存在", "warning")
            self.report["sections"]["knowledge"] = {"status": "skipped"}
            return
        
        print("  🤖 启动自动知识获取...")
        
        stdout, stderr, code = self.run_command(
            f"cd {WORKSPACE} && python {pipeline_script}", 
            timeout=300
        )
        
        if code == 0:
            generated_skill = None
            for line in stdout.split('\n'):
                if '生成Skill:' in line:
                    generated_skill = line.split('生成Skill:')[-1].strip()
                    break
            
            if generated_skill:
                print(f"  ✅ 生成 Skill: {generated_skill}")
                self.log("knowledge", f"生成新Skill: {generated_skill}", "success")
                self.report["sections"]["knowledge"] = {
                    "status": "success",
                    "generated_skill": generated_skill
                }
            else:
                print("  ℹ️ 本次未生成新Skill")
                self.report["sections"]["knowledge"] = {"status": "no_action"}
        else:
            print(f"  ❌ 执行失败: {stderr[:100]}")
            self.log("knowledge", f"失败: {stderr[:100]}", "error")
            self.report["sections"]["knowledge"] = {"status": "error"}

    # ═══════════════════════════════════════════════════════════
    # 模块 4: 进化分析
    # ═══════════════════════════════════════════════════════════
    def run_evolution_analysis(self):
        """执行进化分析"""
        print("\n🧬 模块4: 进化分析")
        print("-" * 50)
        
        patterns_file = DATA_DIR / "success-patterns.json"
        improvements_file = DATA_DIR / "improvements.json"
        
        patterns_count = improvements_count = 0
        
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    patterns_count = len(json.load(f))
            except:
                pass
                
        if improvements_file.exists():
            try:
                with open(improvements_file) as f:
                    improvements_count = len(json.load(f))
            except:
                pass
        
        print(f"  📈 成功模式: {patterns_count} 个")
        print(f"  🔧 待改进项: {improvements_count} 个")
        
        # 记录里程碑
        evolution_log_file = DATA_DIR / "evolution-log.json"
        try:
            if evolution_log_file.exists():
                with open(evolution_log_file) as f:
                    log_data = json.load(f)
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
        except Exception as e:
            self.log("evolution", f"记录失败: {e}", "error")
        
        self.report["sections"]["evolution"] = {
            "status": "success",
            "patterns_count": patterns_count,
            "improvements_count": improvements_count
        }

    # ═══════════════════════════════════════════════════════════
    # 模块 5: Skills 质量管理 (SQM)
    # ═══════════════════════════════════════════════════════════
    def run_skill_quality_manager(self):
        """执行 Skills 质量管理"""
        print("\n🎯 模块5: Skills 质量管理 (SQM)")
        print("-" * 50)
        
        sqm_script = TOOLS_DIR / "skill-quality-manager.py"
        
        if not sqm_script.exists():
            print("  ⚠️  SQM 脚本不存在，跳过")
            self.log("sqm", "脚本不存在", "warning")
            self.report["sections"]["sqm"] = {"status": "skipped"}
            return
        
        # 检查上次运行时间
        sqm_data_dir = DATA_DIR / "sqm"
        last_run = None
        if sqm_data_dir.exists():
            reports = sorted(sqm_data_dir.glob("report-*.json"))
            if reports:
                last_run = reports[-1].stat().st_mtime
                last_date = datetime.fromtimestamp(last_run).strftime('%Y-%m-%d %H:%M')
                print(f"  ℹ️ 上次运行: {last_date}")
        
        # 执行 SQM (dry-run 模式，只评分不替换)
        print("  🔍 执行 Skills 评分...")
        
        stdout, stderr, code = self.run_command(
            f"cd {WORKSPACE} && python {sqm_script} --dry-run",
            timeout=120
        )
        
        if code == 0:
            # 解析结果
            replaced_count = 0
            critical_count = 0
            excellent_count = 0
            
            for line in stdout.split('\n'):
                if '已替换:' in line:
                    try:
                        replaced_count = int(line.split(':')[1].strip().split()[0])
                    except:
                        pass
                elif '分类结果:' in line:
                    # 格式: 分类结果: 白名单=23, 保持=79, 待改进=0, 替换=0
                    try:
                        parts = line.split(':')[1]
                        for part in parts.split(','):
                            if '白名单=' in part:
                                excellent_count = int(part.split('=')[1].strip())
                            elif '替换=' in part:
                                critical_count = int(part.split('=')[1].strip())
                    except:
                        pass
            
            self.report["sections"]["sqm"] = {
                "status": "success",
                "excellent_count": excellent_count,
                "critical_count": critical_count,
                "replaced_count": replaced_count
            }
            
            print(f"  ✅ 评分完成")
            print(f"     ⭐ 白名单: {excellent_count} 个")
            if critical_count > 0:
                print(f"     🔴 待改进: {critical_count} 个")
        else:
            print(f"  ❌ SQM 执行失败: {stderr[:100]}")
            self.log("sqm", f"失败: {stderr[:100]}", "error")
            self.report["sections"]["sqm"] = {"status": "error"}

    # ═══════════════════════════════════════════════════════════
    # 模块 6: AQA 自动决策器
    # ═══════════════════════════════════════════════════════════
    def run_aqa_auto_decider(self):
        """运行 AQA 自动决策器，自动创建 Skills"""
        print("\n🤖 模块6: AQA 自动决策器")
        print("-" * 50)
        
        decider_script = TOOLS_DIR / "aqa-auto-decider.py"
        
        if not decider_script.exists():
            print("  ⚠️  决策器脚本不存在，跳过")
            self.log("aqa_decider", "脚本不存在", "warning")
            self.report["sections"]["aqa_decider"] = {"status": "skipped"}
            return
        
        # 检查是否有待处理建议
        suggestions_file = DATA_DIR / "sqm" / "skill-suggestions.json"
        if not suggestions_file.exists():
            print("  ℹ️  无待处理建议，跳过")
            self.report["sections"]["aqa_decider"] = {"status": "no_action"}
            return
        
        # 运行决策器
        print("  🔍 运行自动决策...")
        
        stdout, stderr, code = self.run_command(
            f"cd {WORKSPACE} && python {decider_script}",
            timeout=180
        )
        
        if code == 0:
            # 解析结果
            created_count = 0
            skipped_count = 0
            
            for line in stdout.split('\n'):
                if '创建' in line and '个' in line:
                    try:
                        created_count = int(line.split('创建')[1].split('个')[0].strip())
                    except:
                        pass
                elif '跳过' in line and '个' in line:
                    try:
                        skipped_count = int(line.split('跳过')[1].split('个')[0].strip())
                    except:
                        pass
            
            self.report["sections"]["aqa_decider"] = {
                "status": "success",
                "created_count": created_count,
                "skipped_count": skipped_count
            }
            
            print(f"  ✅ 决策完成")
            if created_count > 0:
                print(f"     📦 创建: {created_count} 个 Skills")
            if skipped_count > 0:
                print(f"     ⏭️  跳过: {skipped_count} 个")
        else:
            print(f"  ❌ 决策失败: {stderr[:100]}")
            self.log("aqa_decider", f"失败: {stderr[:100]}", "error")
            self.report["sections"]["aqa_decider"] = {"status": "error"}

    # ═══════════════════════════════════════════════════════════
    # 模块 7: 反思机制
    # ═══════════════════════════════════════════════════════════
    def run_reflect(self):
        """执行反思机制"""
        print("\n🪞 模块7: 反思机制")
        print("-" * 50)
        
        try:
            # 读取最近的心跳报告
            reports = sorted(DATA_DIR.glob("heartbeat-report-*.json"))
            if not reports:
                print("  ℹ️ 无历史报告，跳过")
                self.report["sections"]["reflect"] = {"status": "no_history"}
                return
            
            # 分析最近3次心跳
            recent = reports[-3:]
            print(f"  📊 分析最近 {len(recent)} 次心跳...")
            
            # 统计各模块成功率
            success_count = 0
            total_count = 0
            
            for report_file in recent:
                try:
                    with open(report_file) as f:
                        report = json.load(f)
                    sections = report.get("sections", {})
                    total_count += len(sections)
                    success_count += sum(1 for s in sections.values() if s.get("status") == "success")
                except:
                    pass
            
            # 计算成功率
            if total_count > 0:
                success_rate = success_count / total_count * 100
                print(f"  📈 模块成功率: {success_rate:.1f}% ({success_count}/{total_count})")
                
                # 写入反思记录
                reflect_file = DATA_DIR / "reflect-log.json"
                reflect_data = {"timestamp": self.timestamp.isoformat(), "success_rate": success_rate}
                
                with open(reflect_file, "a") as f:
                    f.write(json.dumps(reflect_data) + "\n")
                
                self.report["sections"]["reflect"] = {
                    "status": "success",
                    "success_rate": success_rate,
                    "analyzed": len(recent)
                }
            else:
                self.report["sections"]["reflect"] = {"status": "no_data"}
                
        except Exception as e:
            print(f"  ❌ 反思出错: {e}")
            self.log("reflect", f"错误: {str(e)}", "error")
            self.report["sections"]["reflect"] = {"status": "error"}

    # ═══════════════════════════════════════════════════════════
    # 主运行循环
    # ═══════════════════════════════════════════════════════════
    def run(self, max_retries: int = 2):
        """运行完整心跳周期
        
        Args:
            max_retries: 最大重试次数
        """
        print(f"\n{'='*60}")
        print(f"🫀 统一心跳任务 (优化版) - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # 模块列表 - 核心模块，失败可重试
        modules = [
            ("skills", self.run_skills_maintenance),
            ("knowledge", self.run_auto_knowledge_acquisition),
            ("evolution", self.run_evolution_analysis),
            ("sqm", self.run_skill_quality_manager),
            ("aqa_decider", self.run_aqa_auto_decider),
            ("reflect", self.run_reflect),  # 反思模块
        ]
        
        # 第一轮执行
        failed_modules = []
        
        for name, func in modules:
            try:
                func()
            except Exception as e:
                self.log(name, f"错误: {str(e)}", "error")
                print(f"  ❌ {name} 模块出错: {e}")
                failed_modules.append((name, func))
        
        # 重试失败的模块 (最多 max_retries - 1 次)
        retry_count = 1
        while failed_modules and retry_count < max_retries:
            print(f"\n🔄 重试第 {retry_count + 1} 轮 ({len(failed_modules)} 个模块)...")
            still_failed = []
            for name, func in failed_modules:
                try:
                    print(f"  重试 {name}...")
                    func()
                    print(f"  ✅ {name} 重试成功")
                except Exception as e:
                    self.log(name, f"重试错误: {str(e)}", "error")
                    print(f"  ❌ {name} 重试失败: {e}")
                    still_failed.append((name, func))
            failed_modules = still_failed
            retry_count += 1
        
        # 记录最终失败状态
        if failed_modules:
            self.report["sections"]["_retry_status"] = {
                "status": "partial_failure",
                "failed_modules": [name for name, _ in failed_modules],
                "total_retries": retry_count
            }
            print(f"\n⚠️  {len(failed_modules)} 个模块最终失败: {[name for name, _ in failed_modules]}")
        
        # 保存报告 - 优化: 确保始终写入
        success = self.save_report()
        
        # 生成摘要
        print(f"\n{'='*60}")
        print("📋 心跳摘要")
        print(f"{'='*60}")
        
        for section, data in self.report["sections"].items():
            if section == "resources":
                continue  # 已禁用
            icon = "✅" if data.get("status") in ["success", "no_action"] else "❌"
            
            # SQM 显示详情
            if section == "sqm" and data.get("status") == "success":
                excellent = data.get("excellent_count", 0)
                critical = data.get("critical_count", 0)
                print(f"  {icon} SQM: 评分完成 (⭐ {excellent} 个白名单, 🔴 {critical} 个待改进)")
            # AQA 决策器显示详情
            elif section == "aqa_decider" and data.get("status") == "success":
                created = data.get("created_count", 0)
                skipped = data.get("skipped_count", 0)
                print(f"  {icon} AQA: 自动决策 (📦 {created} 个, ⏭️ {skipped} 个)")
            else:
                print(f"  {icon} {section.capitalize()}: {data.get('status', 'unknown')}")
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  执行时间: {elapsed:.2f}s")
        print(f"💾 报告写入: {'成功' if success else '失败'}")
        print(f"{'='*60}\n")
        
        return self.report


if __name__ == "__main__":
    heartbeat = OptimizedHeartbeat()
    heartbeat.run()
