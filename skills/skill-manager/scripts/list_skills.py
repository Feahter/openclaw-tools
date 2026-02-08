#!/usr/bin/env python3
"""
List all installed skills.
Usage: python list_skills.py [skills_dir]
"""

import os
import sys
import yaml
from pathlib import Path

SKILLS_DIR = Path(os.environ.get('SKILLS_DIR', '~/.claude/skills')).expanduser()

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown"""
    if content.startswith('---'):
        end = content[4:].find('\n---')
        if end != -1:
            try:
                return yaml.safe_load(content[4:4+end])
            except:
                pass
    return {}

def list_skills(dir_path):
    """List all skills with metadata"""
    skills = []
    
    for item in dir_path.iterdir():
        if item.is_dir():
            skill_file = item / 'SKILL.md'
            if skill_file.exists():
                try:
                    content = skill_file.read_text()
                    frontmatter = parse_frontmatter(content)
                    
                    skills.append({
                        "name": frontmatter.get('name', item.name),
                        "description": frontmatter.get('description', 'No description'),
                        "github_url": frontmatter.get('github_url', 'Local'),
                        "version": frontmatter.get('version', 'unknown'),
                        "is_github_based": bool(frontmatter.get('github_url'))
                    })
                except Exception as e:
                    skills.append({
                        "name": item.name,
                        "error": str(e)
                    })
    
    return skills

def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILLS_DIR
    
    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    skills = list_skills(skills_dir)
    
    print(f"Found {len(skills)} skills:\n")
    
    for s in skills:
        if 'error' in s:
            print(f"❌ {s['name']}: {s['error']}")
        else:
            github_mark = "🌐" if s['is_github_based'] else "📦"
            print(f"{github_mark} {s['name']} v{s['version']}")
            print(f"   {s['description'][:60]}...")
            if s['github_url'] != 'Local':
                print(f"   Source: {s['github_url']}")
            print()

if __name__ == "__main__":
    main()
