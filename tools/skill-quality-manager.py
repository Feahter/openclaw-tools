#!/usr/bin/env python3
"""
Skill Quality Manager (SQM)
自动评分、分类、替换低分 Skills

功能：
1. 评分引擎 - 使用频率 × 成功率 × 维护系数
2. 分类器 - 白名单/保持/改进/替换
3. 搜索器 - 找同类高分替代
4. 验证器 - 安装后跑 quick_validate
5. 执行引擎 - 安全替换
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import shutil
import re

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
SQM_DIR = DATA_DIR / "sqm"
BACKUP_DIR = SQM_DIR / "backup"

# 评分权重
WEIGHT_FREQUENCY = 0.25   # 使用频率权重
WEIGHT_SUCCESS = 0.20     # 成功率权重
WEIGHT_DOC = 0.25         # 文档质量权重
WEIGHT_CONFIG = 0.15       # 配置完整性权重
WEIGHT_SCRIPTS = 0.15     # 脚本可用性权重

# 阈值（基于实际数据分布调整）
SCORE_EXCELLENT = 0.40    # 白名单阈值
SCORE_GOOD = 0.30         # 保持阈值
SCORE_WARNING = 0.25      # 替换阈值（warning 也参与改进）

# 备份保留期
BACKUP_DAYS = 7


class SQM:
    """Skill Quality Manager"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.report = {
            "timestamp": self.timestamp.isoformat(),
            "version": "1.0.0",
            "scores": {},
            "actions": [],
            "whitelist": [],
            "summary": {}
        }
        SQM_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg: str, level: str = "info"):
        """日志记录"""
        icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "action": "🔄"}
        print(f"  {icon.get(level, 'ℹ️')} {msg}")
    
    def run_command(self, cmd: str, timeout: int = 60) -> Tuple[str, str, int]:
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
    
    # ═══════════════════════════════════════════════════════════
    # 模块 1: 收集使用数据
    # ═══════════════════════════════════════════════════════════
    def collect_usage_data(self) -> Dict[str, Dict]:
        """收集 Skills 使用数据"""
        self.log("收集使用数据...", "info")
        
        usage_data = {}
        skills_dir = WORKSPACE / "skills"
        
        if not skills_dir.exists():
            self.log("Skills 目录不存在", "error")
            return {}
        
        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir() or skill_path.name.startswith('.'):
                continue
            
            skill_name = skill_path.name
            usage_data[skill_name] = {
                "path": str(skill_path),
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "last_used": None,
                "update_time": self.get_update_time(skill_path),
                "files": self.count_files(skill_path),
                "has_readme": (skill_path / "SKILL.md").exists(),
            }
        
        # 从心跳报告补充调用数据
        heartbeat_reports = list((DATA_DIR).glob("heartbeat-report-*.json"))
        for report_file in heartbeat_reports[-7:]:  # 最近7天
            try:
                with open(report_file) as f:
                    report = json.load(f)
                
                skills_section = report.get("sections", {}).get("skills", {})
                if "local_count" in skills_section:
                    # 可能需要更细粒度的调用数据
                    pass
            except:
                pass
        
        self.log(f"发现 {len(usage_data)} 个 Skills", "success")
        return usage_data
    
    def get_update_time(self, path: Path) -> Optional[str]:
        """获取技能更新时间"""
        try:
            mtime = path.stat().st_mtime
            return datetime.fromtimestamp(mtime).isoformat()
        except:
            return None
    
    def count_files(self, path: Path) -> int:
        """统计文件数量"""
        count = 0
        try:
            for _ in path.rglob("*"):
                count += 1
        except:
            pass
        return count
    
    # ═══════════════════════════════════════════════════════════
    # 模块 2: 评分引擎
    # ═══════════════════════════════════════════════════════════
    def calculate_scores(self, usage_data: Dict) -> Dict[str, Dict]:
        """计算评分 - 多维度质量评估"""
        self.log("计算评分...", "info")

        scores = {}

        # 预计算全局基准（用于归一化）
        all_files = [d.get("files", 0) for d in usage_data.values()]
        max_files = max(all_files) if all_files else 1
        all_readme_size = []
        all_meta_fields = []

        # 第一遍：收集基准数据
        for skill_name, data in usage_data.items():
            skill_path = Path(data["path"])
            
            # README 大小
            readme_path = skill_path / "SKILL.md"
            if readme_path.exists():
                all_readme_size.append(readme_path.stat().st_size)
            
            # _meta.json 字段数
            meta_path = skill_path / "_meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                        all_meta_fields.append(len(meta))
                except:
                    pass

        # 基准值
        max_readme_size = max(all_readme_size) if all_readme_size else 1
        max_meta_fields = max(all_meta_fields) if all_meta_fields else 1

        for skill_name, data in usage_data.items():
            skill_path = Path(data["path"])
            
            # 1. 使用频率 (0-1) - 权重 40%
            calls = data.get("calls", 0)
            freq_score = 0.1  # 基础分
            if calls > 0:
                freq_score = min(1.0, 0.3 + 0.7 * (calls / max([d.get("calls", 0) for d in usage_data.values()] or [1])))

            # 2. 成功率 (0-1) - 权重 30%
            successes = data.get("successes", 0)
            failures = data.get("failures", 0)
            total = successes + failures
            if total > 0:
                success_score = successes / total
            else:
                # 无调用数据时，根据是否有 README 给分
                success_score = 0.5 if data.get("has_readme") else 0.3

            # 3. 文档质量 (0-1) - 权重 15%
            doc_score = 0.3  # 基础分
            readme_path = skill_path / "SKILL.md"
            if readme_path.exists():
                size = readme_path.stat().st_size
                doc_score = 0.3 + 0.7 * (size / max_readme_size)  # 0.3-1.0

            # 4. 配置完整性 (0-1) - 权重 10%
            config_score = 0.2  # 基础分
            meta_path = skill_path / "_meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                        field_count = len(meta)
                        config_score = 0.3 + 0.7 * (field_count / max_meta_fields)
                except:
                    pass

            # 5. 脚本可用性 (0-1) - 权重 5%
            scripts_dir = skill_path / "scripts"
            if scripts_dir.exists() and scripts_dir.is_dir():
                scripts = list(scripts_dir.glob("*.py"))
                if scripts:
                    # 检查有多少是可执行的
                    executable_count = 0
                    for script in scripts:
                        if script.stat().st_mode & 0o111:
                            executable_count += 1
                    script_score = executable_count / len(scripts)
                else:
                    script_score = 0.5
            else:
                script_score = 0.3

            # 综合评分
            final_score = (
                freq_score * WEIGHT_FREQUENCY +
                success_score * WEIGHT_SUCCESS +
                doc_score * WEIGHT_DOC +
                config_score * WEIGHT_CONFIG +
                script_score * WEIGHT_SCRIPTS
            )

            # 风险惩罚
            if calls == 0 and not data.get("has_readme"):
                final_score *= 0.5

            scores[skill_name] = {
                "score": round(final_score, 3),
                "frequency": round(freq_score, 3),
                "success": round(success_score, 3),
                "doc_quality": round(doc_score, 3),
                "config": round(config_score, 3),
                "scripts": round(script_score, 3),
                "calls": calls,
                "has_readme": data.get("has_readme", False),
                "files": data.get("files", 0),
                "status": self.get_status(final_score)
            }

        self.log(f"完成 {len(scores)} 个 Skills 评分", "success")
        return scores
    
    def get_status(self, score: float) -> str:
        """获取状态标签"""
        if score >= SCORE_EXCELLENT:
            return "excellent"  # 白名单
        elif score >= SCORE_GOOD:
            return "good"       # 保持
        elif score >= SCORE_WARNING:
            return "warning"    # 待改进
        else:
            return "critical"   # 替换
    
    # ═══════════════════════════════════════════════════════════
    # 模块 3: 分类处理
    # ═══════════════════════════════════════════════════════════
    def categorize_skills(self, scores: Dict) -> Dict[str, List[str]]:
        """分类 Skills"""
        categories = {
            "excellent": [],   # 白名单
            "good": [],        # 保持
            "warning": [],     # 待改进
            "critical": []     # 替换
        }

        for skill_name, data in scores.items():
            status = data["status"]
            if status not in categories:
                status = "good"  # 默认归入保持
            categories[status].append(skill_name)

        # 按分数排序
        for key in categories:
            categories[key].sort(
                key=lambda x: scores.get(x, {}).get("score", 0),
                reverse=True
            )

        self.log(f"分类结果: 白名单={len(categories['excellent'])}, "
                f"保持={len(categories['good'])}, "
                f"待改进={len(categories['warning'])}, "
                f"替换={len(categories['critical'])}", "success")

        return categories
    
    # ═══════════════════════════════════════════════════════════
    # 模块 4: 搜索替代
    # ═══════════════════════════════════════════════════════════
    def search_replacement(self, skill_name: str) -> List[Dict]:
        """搜索同类高分替代"""
        self.log(f"搜索替代: {skill_name}...", "info")
        
        candidates = []
        
        # 1. 先查 ClawdHub
        stdout, stderr, code = self.run_command(
            f"clawdhub search {skill_name} 2>/dev/null | head -20", timeout=30
        )
        
        if code == 0 and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        candidates.append({
                            "source": "clawdhub",
                            "name": parts[0],
                            "score": float(parts[1]) if parts[1].replace('.', '').isdigit() else 0,
                            "raw": line
                        })
        
        # 2. GitHub 搜索（如果 ClawdHub 没找到）
        if not candidates:
            self.log(f"ClawdHub 无结果，尝试 GitHub...", "info")
            
            # 解析 skill 名称获取关键词
            keywords = self.extract_keywords(skill_name)
            
            for keyword in keywords[:2]:
                stdout, stderr, code = self.run_command(
                    f'gh search repos "{keyword} skill" --sort=stars --limit=5 --json name,stargazerCount,updatedAt 2>/dev/null',
                    timeout=30
                )
                
                if code == 0 and stdout:
                    try:
                        repos = json.loads(stdout)
                        for repo in repos:
                            candidates.append({
                                "source": "github",
                                "name": repo["name"],
                                "stars": repo.get("stargazerCount", 0),
                                "updated": repo.get("updatedAt", ""),
                                "score": min(1.0, repo.get("stargazerCount", 0) / 1000)  # 归一化
                            })
                    except:
                        pass
        
        # 按分数排序
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        self.log(f"找到 {len(candidates)} 个候选", "success")
        return candidates[:5]  # 只返回前5个
    
    def extract_keywords(self, skill_name: str) -> List[str]:
        """从技能名提取关键词"""
        # 移除常见前缀
        name = re.sub(r'^(skill-|tools-|scripts-)', '', skill_name.lower())
        # 分割 camelCase / snake_case
        words = re.findall(r'[a-zA-Z]+', name)
        return words
    
    # ═══════════════════════════════════════════════════════════
    # 模块 5: 安装验证
    # ═══════════════════════════════════════════════════════════
    def install_and_validate(self, candidate: Dict) -> bool:
        """安装并验证候选技能"""
        self.log(f"安装验证: {candidate['name']}...", "info")
        
        # 安装
        install_cmd = f"clawdhub install {candidate['name']}"
        if candidate.get('source') == 'github':
            install_cmd = f"clawdhub install github.com/{candidate['name']}"
        
        stdout, stderr, code = self.run_command(install_cmd, timeout=120)
        
        if code != 0:
            self.log(f"安装失败: {stderr[:50]}", "error")
            return False
        
        # 验证 - 跑 quick_validate
        skill_path = WORKSPACE / "skills" / candidate['name']
        
        if skill_path.exists():
            validate_result = self.quick_validate(skill_path)
            if validate_result["valid"]:
                self.log(f"✅ 验证通过", "success")
                return True
            else:
                self.log(f"❌ 验证失败: {validate_result.get('errors', [])}", "error")
                # 清理安装失败的
                self.run_command(f"rm -rf {skill_path}", timeout=10)
                return False
        
        self.log("安装后未找到文件", "error")
        return False
    
    def quick_validate(self, skill_path: Path) -> Dict:
        """快速验证 Skill"""
        errors = []
        warnings = []
        
        # 检查必要文件
        if not (skill_path / "SKILL.md").exists():
            errors.append("缺少 SKILL.md")
        
        # 检查 _meta.json
        meta_path = skill_path / "_meta.json"
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                    if "name" not in meta:
                        warnings.append("缺少 name")
            except:
                errors.append("_meta.json 解析失败")
        
        # 检查脚本可执行
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                if not script.stat().st_mode & 0o111:
                    warnings.append(f"脚本不可执行: {script.name}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    # ═══════════════════════════════════════════════════════════
    # 模块 6: 安全替换
    # ═══════════════════════════════════════════════════════════
    def safe_replace(self, old_skill: str, new_skill: str) -> bool:
        """安全替换技能"""
        self.log(f"🔄 替换 {old_skill} → {new_skill}", "action")
        
        old_path = WORKSPACE / "skills" / old_skill
        backup_path = BACKUP_DIR / f"{old_skill}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # 1. 备份
        try:
            shutil.move(str(old_path), str(backup_path))
            self.log(f"已备份: {backup_path.name}", "success")
        except Exception as e:
            self.log(f"备份失败: {e}", "error")
            return False
        
        # 2. 记录操作
        self.report["actions"].append({
            "type": "replace",
            "old_skill": old_skill,
            "new_skill": new_skill,
            "timestamp": self.timestamp.isoformat(),
            "backup_path": str(backup_path)
        })
        
        # 3. 清理旧备份（超过7天）
        self.clean_old_backups()
        
        return True
    
    def clean_old_backups(self):
        """清理过期备份"""
        cutoff = self.timestamp - timedelta(days=BACKUP_DAYS)
        
        for backup_dir in BACKUP_DIR.iterdir():
            if backup_dir.is_dir():
                try:
                    # 从目录名提取日期
                    parts = backup_dir.name.split('_')
                    if len(parts) >= 2:
                        date_str = parts[1] + '_' + parts[2]
                        backup_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        if backup_date < cutoff:
                            shutil.rmtree(backup_dir)
                            self.log(f"清理过期备份: {backup_dir.name}", "info")
                except:
                    pass
    
    # ═══════════════════════════════════════════════════════════
    # 模块 7: 执行替换
    # ═══════════════════════════════════════════════════════════
    def execute_replacements(self, categories: Dict[str, List[str]], scores: Dict):
        """执行替换 - critical 和 warning 都参与"""
        self.log("\n🔍 开始低分技能替换...", "info")

        replaced = []
        skipped = []
        improved = []  # warning 改进列表

        # 处理 critical (必须替换)
        for skill_name in categories.get("critical", []):
            self.log(f"\n🔴 Critical: {skill_name}", "warning")
            result = self._try_replace_skill(skill_name, scores[skill_name]["score"])
            if result["replaced"]:
                replaced.append(result["data"])
            else:
                skipped.append(skill_name)

        # 处理 warning (尝试改进)
        for skill_name in categories.get("warning", []):
            self.log(f"\n⚠️ Warning: {skill_name}", "info")
            score = scores[skill_name]["score"]

            # 1. 先搜索替代
            candidates = self.search_replacement(skill_name)

            if candidates:
                # 2. 尝试安装验证（只尝试最好的候选）
                best_candidate = candidates[0]
                if self.install_and_validate(best_candidate):
                    # 3. 安全替换
                    if self.safe_replace(skill_name, best_candidate["name"]):
                        improved.append({
                            "old": skill_name,
                            "new": best_candidate["name"],
                            "score_before": score,
                            "score_after": scores.get(best_candidate["name"], {}).get("score", 0)
                        })
                        continue

            # 4. 无法替换时，生成具体改进建议
            improvement = self._generate_improvement_suggestion(skill_name, scores[skill_name])
            improved.append({
                "skill": skill_name,
                "suggestion": improvement["suggestion"],
                "score_before": score
            })

        return {"replaced": replaced, "skipped": skipped, "improved": improved}

    def _try_replace_skill(self, skill_name: str, old_score: float) -> Dict:
        """尝试替换单个技能"""
        candidates = self.search_replacement(skill_name)

        if not candidates:
            return {"replaced": False, "data": None}

        for candidate in candidates:
            if self.install_and_validate(candidate):
                if self.safe_replace(skill_name, candidate["name"]):
                    return {
                        "replaced": True,
                        "data": {
                            "old": skill_name,
                            "new": candidate["name"],
                            "score": old_score
                        }
                    }

        return {"replaced": False, "data": None}

    def _generate_improvement_suggestion(self, skill_name: str, data: Dict) -> Dict:
        """生成具体改进建议"""
        suggestions = []

        # 分析缺失项
        if data.get("scripts", 0) < 0.5:
            suggestions.append("添加/完善 scripts 目录")

        if data.get("doc_quality", 0) < 0.5:
            suggestions.append("扩展 SKILL.md 文档")

        if data.get("config", 0) < 0.5:
            suggestions.append("完善 _meta.json 配置")

        if data.get("frequency", 0) < 0.3:
            suggestions.append("增加使用频率")

        return {
            "skill": skill_name,
            "suggestion": "; ".join(suggestions) if suggestions else "整体质量一般",
            "details": data
        }
    
    # ═══════════════════════════════════════════════════════════
    # 模块 8: 报告生成
    # ═══════════════════════════════════════════════════════════
    def generate_report(self, categories: Dict, scores: Dict, exec_result: Dict):
        """生成报告"""
        # 更新白名单
        whitelist = categories.get("excellent", [])

        # 读取旧白名单合并
        old_whitelist = []
        whitelist_file = SQM_DIR / "whitelist.json"
        if whitelist_file.exists():
            try:
                with open(whitelist_file) as f:
                    old_whitelist = json.load(f)
            except:
                pass

        # 合并白名单（去重）
        combined_whitelist = list(dict.fromkeys(old_whitelist + whitelist))

        # 保存白名单
        with open(whitelist_file, 'w') as f:
            json.dump(combined_whitelist, f, indent=2)

        # 构建报告
        self.report["scores"] = scores
        self.report["categories"] = {
            k: len(v) for k, v in categories.items()
        }
        self.report["whitelist"] = combined_whitelist
        self.report["actions"].extend(exec_result.get("replaced", []))
        self.report["summary"] = {
            "total_skills": len(scores),
            "excellent": len(categories.get("excellent", [])),
            "good": len(categories.get("good", [])),
            "warning": len(categories.get("warning", [])),
            "critical": len(categories.get("critical", [])),
            "replaced": len(exec_result.get("replaced", [])),
            "skipped": len(exec_result.get("skipped", []))
        }
        
        # 保存报告
        report_file = SQM_DIR / f"report-{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        # 保存最新评分榜
        scoreboard_file = SQM_DIR / "scoreboard.json"
        with open(scoreboard_file, 'w', encoding='utf-8') as f:
            json.dump({
                "updated": self.timestamp.isoformat(),
                "scores": scores
            }, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def print_summary(self, categories: Dict, exec_result: Dict):
        """打印摘要"""
        print(f"\n{'='*60}")
        print("📊 Skill Quality Manager - 执行摘要")
        print(f"{'='*60}")

        print(f"\n🏷️  分类统计:")
        print(f"   ⭐ 白名单: {len(categories.get('excellent', []))} 个")
        print(f"   ✅ 保持:   {len(categories.get('good', []))} 个")
        print(f"   ⚠️  待改进: {len(categories.get('warning', []))} 个")
        print(f"   🔴 替换:   {len(categories.get('critical', []))} 个")

        print(f"\n🔄 执行操作:")
        replaced = exec_result.get("replaced", [])
        print(f"   已替换: {len(replaced)} 个")
        for item in replaced:
            print(f"      {item['old']} → {item['new']}")

        skipped = exec_result.get("skipped", [])
        print(f"   跳过:   {len(skipped)} 个")

        improved = exec_result.get("improved", [])
        if improved:
            print(f"\n💡 改进建议: {len(improved)} 个")
            for item in improved[:5]:  # 只显示前5个
                if "suggestion" in item:
                    print(f"      • {item['skill']}: {item['suggestion'][:50]}...")
                else:
                    print(f"      • {item['old']} → {item['new']}")

        # 白名单 Top 10
        print(f"\n⭐ 白名单 Top 10:")
        whitelist = categories.get("excellent", [])[:10]
        for i, skill in enumerate(whitelist, 1):
            score = self.report["scores"].get(skill, {}).get("score", 0)
            print(f"   {i:2d}. {skill} ({score})")

        print(f"\n{'='*60}\n")
    
    # ═══════════════════════════════════════════════════════════
    # 主运行
    # ═══════════════════════════════════════════════════════════
    def run(self, auto_replace: bool = True):
        """运行完整流程"""
        print(f"\n{'='*60}")
        print("🛠️  Skill Quality Manager v1.0.0")
        print(f"📅 {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # 1. 收集数据
        usage_data = self.collect_usage_data()
        
        # 2. 计算评分
        scores = self.calculate_scores(usage_data)
        
        # 3. 分类
        categories = self.categorize_skills(scores)
        
        # 4. 执行替换
        if auto_replace:
            exec_result = self.execute_replacements(categories, scores)
        else:
            exec_result = {"replaced": [], "skipped": [], "warnings": []}
        
        # 5. 生成报告
        report_file = self.generate_report(categories, scores, exec_result)
        
        # 6. 打印摘要
        self.print_summary(categories, exec_result)
        
        elapsed = time.time() - start_time
        print(f"⏱️  执行时间: {elapsed:.2f}s")
        print(f"💾 报告已保存: {report_file.name}\n")
        
        return self.report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Quality Manager")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描，不执行替换")
    parser.add_argument("--report", action="store_true", help="显示上次报告")
    args = parser.parse_args()
    
    sqm = SQM()
    
    if args.report:
        # 显示上次报告
        reports = sorted((SQM_DIR / "report-*.json").glob("*"))
        if reports:
            with open(reports[-1]) as f:
                print(f.read())
        else:
            print("暂无报告")
        return 0
    
    sqm.run(auto_replace=not args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
