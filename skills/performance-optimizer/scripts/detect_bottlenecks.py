#!/usr/bin/env python3
"""
Bottleneck Detector
Scans codebases for common performance anti-patterns and bottlenecks.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Bottleneck:
    pattern: str
    severity: str  # critical, high, medium, low
    line_number: int
    suggestion: str
    category: str

# Pattern definitions by language
PATTERNS = {
    'python': [
        {
            'name': 'N+1 Query',
            'pattern': r'for\s+\w+\s+in\s+\w+.*:\s*\n\s+\w+\.(filter|get|objects\.get)',
            'severity': 'critical',
            'suggestion': 'Use select_related() or prefetch_related() to batch queries',
            'category': 'database'
        },
        {
            'name': 'String Concatenation in Loop',
            'pattern': r'for\s+.*:\s*\n(?:.*\n)*?\s*\w+\s*\+?=\s*["\']',
            'severity': 'medium',
            'suggestion': 'Use list.append() and str.join() instead of += in loops',
            'category': 'memory'
        },
        {
            'name': 'Inefficient List Search',
            'pattern': r'if\s+\w+\s+in\s+\w+:\s*\n(?:.*\n)*?\s+(?:for|while|if)',
            'severity': 'high',
            'suggestion': 'Convert list to set for O(1) lookup: if item in set(items)',
            'category': 'algorithm'
        },
        {
            'name': 'Repeated Attribute Access',
            'pattern': r'for\s+\w+\s+in\s+range\(.*len\((\w+)\)',
            'severity': 'low',
            'suggestion': 'Cache len() result: n = len(items); for i in range(n)',
            'category': 'micro'
        },
        {
            'name': 'List/Dict Creation in Loop',
            'pattern': r'for\s+.*:\s*\n\s+\w+\s*=\s*(\[\]|\{\}|dict\(\)|list\(\))',
            'severity': 'medium',
            'suggestion': 'Move list/dict creation outside loop if possible',
            'category': 'memory'
        },
        {
            'name': 'Deep Recursion',
            'pattern': r'def\s+(\w+).*\n(?:.*\n)*?\s+\1\(',
            'severity': 'high',
            'suggestion': 'Consider iterative approach or memoization for deep recursion',
            'category': 'algorithm'
        },
    ],
    'javascript': [
        {
            'name': 'Await in Loop',
            'pattern': r'for\s*\([^)]*\)\s*\{[^}]*await[^}]*\}',
            'severity': 'critical',
            'suggestion': 'Use Promise.all() to run async operations in parallel',
            'category': 'concurrency'
        },
        {
            'name': 'Nested Array Methods',
            'pattern': r'\.(map|filter|reduce)\([^)]*\.(map|filter|reduce)',
            'severity': 'high',
            'suggestion': 'Combine into single pass or use for-loop for better performance',
            'category': 'algorithm'
        },
        {
            'name': 'JSON.parse in Loop',
            'pattern': r'for\s*\([^)]*\)\s*\{[^}]*JSON\.parse',
            'severity': 'medium',
            'suggestion': 'Parse JSON once outside loop or cache results',
            'category': 'cpu'
        },
        {
            'name': 'Unnecessary DOM Queries',
            'pattern': r'(for|while)\s*\([^)]*\)[^{]*\{[^}]*document\.(getElementById|querySelector)',
            'severity': 'high',
            'suggestion': 'Cache DOM references outside loop',
            'category': 'dom'
        },
    ],
    'java': [
        {
            'name': 'String Concatenation in Loop',
            'pattern': r'for\s*\([^)]*\)\s*\{[^}]*String\s+\w+\s*\+=',
            'severity': 'high',
            'suggestion': 'Use StringBuilder instead of String += in loops',
            'category': 'memory'
        },
        {
            'name': 'Unclosed Resources',
            'pattern': r'new\s+(FileInputStream|FileOutputStream|Connection|Statement)(?!.*close)',
            'severity': 'critical',
            'suggestion': 'Use try-with-resources or ensure close() is called',
            'category': 'resource'
        },
    ],
    'cpp': [
        {
            'name': 'Vector Push in Loop',
            'pattern': r'for\s*\([^)]*\)\s*[^}]*\.push_back',
            'severity': 'medium',
            'suggestion': 'Call reserve() before loop to prevent reallocations',
            'category': 'memory'
        },
    ],
    'go': [
        {
            'name': 'String Concatenation',
            'pattern': r'for\s+.*\{[^}]*\+\s*string',
            'severity': 'medium',
            'suggestion': 'Use strings.Builder for efficient string concatenation',
            'category': 'memory'
        },
    ]
}

def detect_bottlenecks(filepath: Path, lang: str) -> List[Bottleneck]:
    """Detect bottlenecks in a file."""
    content = filepath.read_text()
    lines = content.split('\n')
    results = []
    
    patterns = PATTERNS.get(lang, [])
    
    for pattern_def in patterns:
        regex = pattern_def['pattern']
        for match in re.finditer(regex, content, re.MULTILINE | re.DOTALL):
            line_num = content[:match.start()].count('\n') + 1
            results.append(Bottleneck(
                pattern=pattern_def['name'],
                severity=pattern_def['severity'],
                line_number=line_num,
                suggestion=pattern_def['suggestion'],
                category=pattern_def['category']
            ))
    
    return results

def print_report(results: Dict[Path, List[Bottleneck]], total_files: int):
    """Print formatted report."""
    print(f"\n{'='*70}")
    print("🔍 Bottleneck Detection Report")
    print('='*70)
    
    total_issues = sum(len(b) for b in results.values())
    critical = sum(1 for bs in results.values() for b in bs if b.severity == 'critical')
    high = sum(1 for bs in results.values() for b in bs if b.severity == 'high')
    medium = sum(1 for bs in results.values() for b in bs if b.severity == 'medium')
    low = sum(1 for bs in results.values() for b in bs if b.severity == 'low')
    
    print(f"\n📈 Summary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Files with issues: {len(results)}")
    print(f"  Total issues: {total_issues}")
    print(f"  🔴 Critical: {critical}")
    print(f"  🟠 High: {high}")
    print(f"  🟡 Medium: {medium}")
    print(f"  🟢 Low: {low}")
    
    if not results:
        print("\n✅ No bottlenecks detected!")
        return
    
    # Group by category
    by_category: Dict[str, List[tuple]] = {}
    for filepath, bottlenecks in results.items():
        for b in bottlenecks:
            if b.category not in by_category:
                by_category[b.category] = []
            by_category[b.category].append((filepath, b))
    
    print(f"\n📋 Detailed Findings:")
    print('-'*70)
    
    for category in sorted(by_category.keys()):
        items = by_category[category]
        print(f"\n{category.upper()} ({len(items)} issues):")
        
        for filepath, b in sorted(items, key=lambda x: (x[1].severity != 'critical', x[1].severity != 'high')):
            severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(b.severity, '⚪')
            print(f"  {severity_icon} {b.pattern}")
            print(f"     File: {filepath}:{b.line_number}")
            print(f"     Suggestion: {b.suggestion}")

def get_language(filepath: Path) -> str:
    """Determine language from file extension."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.go': 'go'
    }
    return ext_map.get(filepath.suffix, '')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Detect performance bottlenecks in code')
    parser.add_argument('target', help='File or directory to analyze')
    parser.add_argument('--lang', help='Language override (python, javascript, java, cpp, go)')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], 
                       default='low', help='Minimum severity to report')
    args = parser.parse_args()
    
    target = Path(args.target)
    
    if target.is_file():
        files = [target]
    else:
        files = [f for f in target.rglob('*') if f.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.cc', '.go']]
    
    results = {}
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    min_severity = severity_order[args.severity]
    
    for filepath in files:
        lang = args.lang or get_language(filepath)
        if not lang:
            continue
        
        bottlenecks = detect_bottlenecks(filepath, lang)
        # Filter by severity
        bottlenecks = [b for b in bottlenecks if severity_order[b.severity] >= min_severity]
        
        if bottlenecks:
            results[filepath] = bottlenecks
    
    print_report(results, len(files))

if __name__ == "__main__":
    main()
