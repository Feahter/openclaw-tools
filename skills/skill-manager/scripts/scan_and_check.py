#!/usr/bin/env python3
"""
Scan skills directory and check for updates.
Usage: python scan_and_check.py [skills_dir]
"""

import os
import sys
import json
import subprocess
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

def get_remote_hash(github_url):
    """Get latest commit hash from GitHub"""
    try:
        result = subprocess.run(
            ['git', 'ls-remote', github_url, 'HEAD'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception:
        pass
    return None

def scan_skills(dir_path):
    """Scan directory for skills with GitHub metadata"""
    skills = []
    
    for item in dir_path.iterdir():
        if item.is_dir():
            skill_file = item / 'SKILL.md'
            if skill_file.exists():
                try:
                    content = skill_file.read_text()
                    frontmatter = parse_frontmatter(content)
                    
                    if frontmatter.get('github_url'):
                        local_hash = frontmatter.get('github_hash', 'unknown')
                        remote_hash = get_remote_hash(frontmatter['github_url'])
                        
                        is_stale = remote_hash and local_hash != remote_hash
                        
                        skills.append({
                            "name": frontmatter.get('name', item.name),
                            "github_url": frontmatter['github_url'],
                            "local_hash": local_hash,
                            "remote_hash": remote_hash,
                            "version": frontmatter.get('version', 'unknown'),
                            "is_stale": is_stale,
                            "path": str(item)
                        })
                except Exception as e:
                    print(f"Error scanning {item}: {e}")
    
    return skills

def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILLS_DIR
    
    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    print(f"Scanning {skills_dir}...")
    skills = scan_skills(skills_dir)
    
    # Generate report
    stale = [s for s in skills if s['is_stale']]
    current = [s for s in skills if not s['is_stale']]
    
    report = {
        "total": len(skills),
        "stale_count": len(stale),
        "current_count": len(current),
        "stale_skills": stale,
        "current_skills": current
    }
    
    print(json.dumps(report, indent=2))
    
    if stale:
        print(f"\n⚠️  {len(stale)} skills have updates available:")
        for s in stale:
            print(f"  - {s['name']}: {s['local_hash'][:7]} → {s['remote_hash'][:7] if s['remote_hash'] else '?'}")
    else:
        print("\n✅ All skills are current")

if __name__ == "__main__":
    main()
