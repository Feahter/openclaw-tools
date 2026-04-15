#!/usr/bin/env python3
"""
Generate best practices section from evolution.json and append to SKILL.md.
Usage: python smart_stitch.py <skill_path>
"""

import os
import sys
import json
from pathlib import Path

def generate_section(evolution):
    """Generate markdown section from evolution data"""
    lines = ["\n## User-Learned Best Practices & Constraints\n"]
    lines.append("_This section is auto-generated from user feedback._\n")
    
    if evolution.get('preferences'):
        lines.append("### User Preferences")
        lines.append("- " + "\n- ".join(evolution['preferences']))
        lines.append("")
    
    if evolution.get('fixes'):
        lines.append("### Applied Fixes")
        lines.append("- " + "\n- ".join(evolution['fixes']))
        lines.append("")
    
    if evolution.get('custom_prompts'):
        lines.append("### Custom Prompts")
        lines.append(f"```\n{evolution['custom_prompts']}\n```")
        lines.append("")
    
    if evolution.get('updated_at'):
        lines.append(f"_Last updated: {evolution['updated_at']}_")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python smart_stitch.py <skill_path>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    evolution_file = skill_path / 'evolution.json'
    skill_file = skill_path / 'SKILL.md'
    
    if not evolution_file.exists():
        print("No evolution.json found")
        sys.exit(0)
    
    if not skill_file.exists():
        print("No SKILL.md found")
        sys.exit(1)
    
    evolution = json.loads(evolution_file.read_text())
    section = generate_section(evolution)
    
    # Remove existing best practices section
    skill_content = skill_file.read_text()
    import re
    skill_content = re.sub(r'\n## User-Learned Best Practices.*?(?=\n## |\Z)', '', skill_content, flags=re.DOTALL)
    
    # Append new section
    skill_content += section
    skill_file.write_text(skill_content)
    
    print(f"✅ Stitched evolution into {skill_file}")

if __name__ == "__main__":
    main()
