#!/usr/bin/env python3
"""
Delete a skill.
Usage: python delete_skill.py <skill_name> [skills_dir]
"""

import os
import sys
import shutil
from pathlib import Path

SKILLS_DIR = Path(os.environ.get('SKILLS_DIR', '~/.claude/skills')).expanduser()

def main():
    if len(sys.argv) < 2:
        print("Usage: python delete_skill.py <skill_name> [skills_dir]")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    skills_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else SKILLS_DIR
    
    skill_path = skills_dir / skill_name
    
    if not skill_path.exists():
        print(f"Skill not found: {skill_name}")
        sys.exit(1)
    
    # Confirm deletion
    response = input(f"Delete {skill_path}? [y/N]: ")
    if response.lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    try:
        shutil.rmtree(skill_path)
        print(f"✅ Deleted {skill_name}")
    except Exception as e:
        print(f"❌ Failed to delete: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
