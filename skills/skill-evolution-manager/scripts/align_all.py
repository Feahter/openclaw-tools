#!/usr/bin/env python3
"""
Align all skills: stitch evolution.json into SKILL.md for all skills.
Usage: python align_all.py [skills_dir]
"""

import os
import sys
import json
from pathlib import Path

SKILLS_DIR = Path(os.environ.get('SKILLS_DIR', '~/.claude/skills')).expanduser()

def align_skill(skill_path):
    """Align a single skill"""
    evolution_file = skill_path / 'evolution.json'
    skill_file = skill_path / 'SKILL.md'
    
    if not evolution_file.exists() or not skill_file.exists():
        return False
    
    # Run smart_stitch via import
    import scripts.smart_stitch as ss
    ss.main()
    return True

def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILLS_DIR
    
    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    aligned = 0
    skipped = 0
    
    for item in skills_dir.iterdir():
        if item.is_dir():
            evolution_file = item / 'evolution.json'
            if evolution_file.exists():
                print(f"Aligning {item.name}...")
                # Run the smart_stitch script directly
                import subprocess
                result = subprocess.run(
                    ['python', 'scripts/smart_stitch.py', str(item)],
                    cwd=str(item),
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    aligned += 1
                    print(f"  ✅ {item.name}")
                else:
                    print(f"  ❌ {item.name}: {result.stderr}")
            else:
                skipped += 1
    
    print(f"\n✅ Aligned {aligned} skills, skipped {skipped}")

if __name__ == "__main__":
    main()
