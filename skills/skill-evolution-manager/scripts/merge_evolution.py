#!/usr/bin/env python3
"""
Merge evolution data into skill's evolution.json.
Usage: python merge_evolution.py <skill_path> <json_string>
"""

import os
import sys
import json
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_evolution.py <skill_path> <json_string>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    new_data = json.loads(sys.argv[2])
    
    evolution_file = skill_path / 'evolution.json'
    
    # Load existing or create new
    if evolution_file.exists():
        existing = json.loads(evolution_file.read_text())
    else:
        existing = {
            "preferences": [],
            "fixes": [],
            "custom_prompts": "",
            "updated_at": None
        }
    
    # Merge preferences (avoid duplicates)
    if 'preferences' in new_data:
        for pref in new_data['preferences']:
            if pref not in existing['preferences']:
                existing['preferences'].append(pref)
    
    # Merge fixes (avoid duplicates)
    if 'fixes' in new_data:
        for fix in new_data['fixes']:
            if fix not in existing['fixes']:
                existing['fixes'].append(fix)
    
    # Merge custom prompts
    if 'custom_prompts' in new_data:
        if existing['custom_prompts']:
            existing['custom_prompts'] = f"{existing['custom_prompts']}\n{new_data['custom_prompts']}"
        else:
            existing['custom_prompts'] = new_data['custom_prompts']
    
    existing['updated_at'] = str(Path(__file__).stat().st_mtime)
    
    evolution_file.write_text(json.dumps(existing, indent=2))
    print(f"✅ Merged evolution into {evolution_file}")
    print(json.dumps(existing, indent=2))

if __name__ == "__main__":
    main()
