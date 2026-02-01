#!/usr/bin/env python3
"""
Skill Evolution Manager - 对话经验自动沉淀
"""
import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

SKILLS_DIRS = [
    "/Users/fuzhuo/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills",
    "/Users/fuzhuo/.openclaw/workspace/skills"
]

class SkillEvolutionManager:
    def __init__(self):
        self.evolution_log = Path(__file__).parent / ".skill-evolution-log.md"

    def analyze_conversation(self, conversation_text: str) -> List[Dict]:
        """分析对话，提取可沉淀的经验"""
        experiences = []

        # 识别修正模式
        patterns = [
            (r"应该[是|用|先|再]([^。]+)", "修正"),
            (r"[不|没]对|错了|不正确|应该是([^，]+)", "错误修正"),
            (r"更好的方式[是|应该]([^。]+)", "优化"),
            (r"其实应该([^。]+)", "优化"),
            (r"[记住|注意|切记|important][：:]([^。]+)", "重要提醒"),
        ]

        for pattern, exp_type in patterns:
            for match in re.finditer(pattern, conversation_text, re.IGNORECASE):
                experiences.append({
                    "type": exp_type,
                    "content": match.group(1).strip(),
                    "context": self._extract_context(conversation_text, match.start()),
                    "timestamp": datetime.now().isoformat()
                })

        return experiences

    def _extract_context(self, text: str, position: int, window: int = 200) -> str:
        """提取上下文"""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end].strip()

    def extract_skill_name(self, text: str) -> Optional[str]:
        """从文本中提取 Skill 名称"""
        patterns = [
            r"沉淀到[（\(]?([^）\)]+)[）\)]?",
            r"更新[（\(]?([^）\)]+)[）\)]?",
            r"添加到[（\(]?([^）\)]+)[）\)]?",
            r"(skill-[^\s]+)",
            r"([a-z0-9-]+)-skill",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().lower()
                return name.replace(" ", "-").replace("_", "-")

        return None

    def format_experience(self, experience: Dict) -> str:
        """格式化经验"""
        type_labels = {
            "修正": "🔧 修正",
            "错误修正": "⚠️ 错误修正",
            "优化": "✨ 优化",
            "重要提醒": "💡 重要提醒"
        }

        label = type_labels.get(experience["type"], "📝 经验")
        ts = experience["timestamp"][:10]

        return f'''

### {label} - {ts}

**场景**: {experience['context'][:100]}...

**问题-解决方案**: {experience['content']}
'''

    def find_skill_path(self, skill_name: str) -> Optional[Path]:
        """查找 Skill 文件路径"""
        for skills_dir in SKILLS_DIRS:
            if not os.path.exists(skills_dir):
                continue
            for item in os.listdir(skills_dir):
                # 精确匹配
                if item == skill_name or item == f"{skill_name}-skill":
                    p = Path(skills_dir) / item / "SKILL.md"
                    if p.exists():
                        return p
                # 模糊匹配
                if skill_name.replace("-", "") in item.replace("-", "").replace("_", ""):
                    p = Path(skills_dir) / item / "SKILL.md"
                    if p.exists():
                        return p
        return None

    def add_evolution_patch(self, skill_name: str, experience: Dict):
        """添加经验补丁到 Skill"""
        skill_path = self.find_skill_path(skill_name)
        if not skill_path:
            return False, f"Skill 不存在: {skill_name}"

        content = skill_path.read_text()
        patch = self.format_experience(experience)

        if "## 经验沉淀" in content:
            parts = content.split("## 经验沉淀")
            content = parts[0] + "## 经验沉淀" + patch + "\n" + (parts[1] if len(parts) > 1 else "")
        else:
            content += "\n\n## 经验沉淀\n"
            content += "以下经验来自实际使用中的修正和优化："
            content += patch

        skill_path.write_text(content)
        return True, str(skill_path)

    def evolve_from_conversation(self, conversation_text: str, target_skill: str = None):
        """从对话中沉淀经验"""
        skill_name = target_skill or self.extract_skill_name(conversation_text)
        if not skill_name:
            return {"error": "无法识别目标 Skill"}

        experiences = self.analyze_conversation(conversation_text)
        if not experiences:
            return {"error": "对话中未发现可沉淀的经验"}

        results = []
        for exp in experiences:
            success, msg = self.add_evolution_patch(skill_name, exp)
            results.append({"success": success, "message": msg})

        self._log_evolution(skill_name, results)

        return {
            "skill": skill_name,
            "experiences_found": len(experiences),
            "applied": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]])
        }

    def _log_evolution(self, skill_name: str, results: List[Dict]):
        """记录进化日志"""
        lines = [f"\n--- {datetime.now().isoformat()} ---"]
        for r in results:
            status = "✓" if r["success"] else "✗"
            lines.append(f"{status} {skill_name}: {r['message']}")
        
        with open(self.evolution_log, "a") as f:
            f.write("\n".join(lines))

    def list_history(self, skill_name: str = None):
        """列出进化历史"""
        if not self.evolution_log.exists():
            return []
        
        with open(self.evolution_log, "r") as f:
            content = f.read()
        
        entries = content.split("---")
        if skill_name:
            return [e.strip() for e in entries if e.strip() and skill_name in e]
        return [e.strip() for e in entries if e.strip()][-20:]

    def check_needs_evolution(self) -> List[Dict]:
        """检查需要进化的 Skills"""
        needs_work = []
        
        for skills_dir in SKILLS_DIRS:
            if not os.path.exists(skills_dir):
                continue
            for item in os.listdir(skills_dir):
                skill_path = Path(skills_dir) / item / "SKILL.md"
                if not skill_path.exists():
                    continue
                
                content = skill_path.read_text()
                for section, name in [("## 使用场景", "使用场景"), 
                                      ("## 注意事项", "注意事项"), 
                                      ("## 经验沉淀", "经验沉淀")]:
                    if section not in content:
                        needs_work.append({"skill": item, "missing": name})
                        break
        return needs_work

    def auto_evolve(self, skill_name: str):
        """自动优化 Skill"""
        for skills_dir in SKILLS_DIRS:
            skill_path = Path(skills_dir) / skill_name / "SKILL.md"
            if not skill_path.exists():
                continue
            
            content = skill_path.read_text()
            updates = []
            
            if "## 使用场景" not in content:
                updates.append("\n## 使用场景\n\n请根据实际使用情况补充。")
            if "## 注意事项" not in content:
                updates.append("\n## 注意事项\n\n- 此 Skill 仅供参考，请根据实际情况调整")
            
            if updates:
                content += "\n".join(updates)
                skill_path.write_text(content)
                return True
        return False

def main():
    parser = argparse.ArgumentParser(description="Skill Evolution Manager")
    parser.add_argument("action", choices=["evolve", "list", "check", "auto"])
    parser.add_argument("--conversation", "-c", help="对话内容")
    parser.add_argument("--skill", "-s", help="目标 Skill")
    parser.add_argument("--file", "-f", help="对话文件")
    args = parser.parse_args()

    manager = SkillEvolutionManager()

    if args.action == "evolve":
        conversation = ""
        if args.file:
            conversation = Path(args.file).read_text()
        elif args.conversation:
            conversation = args.conversation
        else:
            print("请提供对话内容")
            return
        
        result = manager.evolve_from_conversation(conversation, args.skill)
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"✓ 已沉淀到 {result['skill']}")
            print(f"  发现 {result['experiences_found']} 条，成功应用 {result['applied']} 条")

    elif args.action == "list":
        history = manager.list_history(args.skill)
        print("\n=== 进化历史 ===")
        for e in history:
            print(e)
            print()

    elif args.action == "check":
        needs = manager.check_needs_evolution()
        print(f"\n需要进化的 Skills ({len(needs)}):")
        for n in needs:
            print(f"  • {n['skill']} - 缺少 {n['missing']}")

    elif args.action == "auto":
        if not args.skill:
            print("请指定 Skill")
            return
        if manager.auto_evolve(args.skill):
            print(f"✓ 已优化 {args.skill}")
        else:
            print(f"无需优化")

if __name__ == "__main__":
    main()
