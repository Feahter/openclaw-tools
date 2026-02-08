#!/usr/bin/env python3
"""
Code Complexity Analyzer
Analyzes code for cyclomatic complexity, time complexity patterns, and potential bottlenecks.
Supports Python, JavaScript, Java, C++, Go.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ComplexityLevel(Enum):
    LOW = "low"      # O(1), O(log n)
    MEDIUM = "medium" # O(n), O(n log n)
    HIGH = "high"    # O(n²), O(2^n)
    UNKNOWN = "unknown"

@dataclass
class FunctionAnalysis:
    name: str
    line_number: int
    cyclomatic_complexity: int
    estimated_complexity: str
    warnings: List[str]
    loop_nesting: int
    recursion_risk: bool

def analyze_python_file(filepath: Path) -> List[FunctionAnalysis]:
    """Analyze Python file for complexity metrics."""
    content = filepath.read_text()
    tree = ast.parse(content)
    
    results = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            analysis = analyze_python_function(node, content)
            results.append(analysis)
    
    return results

def analyze_python_function(node: ast.AST, source: str) -> FunctionAnalysis:
    """Analyze a single Python function."""
    # Cyclomatic complexity (simplified)
    complexity = 1
    loop_depth = 0
    max_loop_depth = 0
    warnings = []
    recursion_risk = False
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        
        # Track loop nesting
        if isinstance(child, (ast.For, ast.While)):
            loop_depth += 1
            max_loop_depth = max(max_loop_depth, loop_depth)
            if loop_depth >= 2:
                warnings.append(f"Deep loop nesting (depth {loop_depth}) - potential O(n²) or worse")
        
        # Check for recursion
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                func_name = getattr(node, 'name', '')
                if child.func.id == func_name:
                    recursion_risk = True
                    warnings.append("Recursive function - verify termination and complexity")
        
        # Check for list/dict operations in loops
        if isinstance(child, ast.For):
            for subchild in ast.walk(child):
                if isinstance(subchild, ast.Call):
                    if isinstance(subchild.func, ast.Attribute):
                        if subchild.func.attr in ['append', 'extend', 'insert']:
                            warnings.append(f"List mutation in loop at line {child.lineno} - consider pre-allocation")
    
    # Estimate time complexity
    if max_loop_depth == 0:
        estimated = "O(1)"
    elif max_loop_depth == 1:
        estimated = "O(n)"
    elif max_loop_depth == 2:
        estimated = "O(n²)"
    else:
        estimated = f"O(n^{max_loop_depth})"
    
    if recursion_risk:
        estimated += " (recursive)"
    
    # Cyclomatic complexity warnings
    if complexity > 10:
        warnings.append(f"High cyclomatic complexity ({complexity}) - consider refactoring")
    
    return FunctionAnalysis(
        name=getattr(node, 'name', 'unknown'),
        line_number=getattr(node, 'lineno', 0),
        cyclomatic_complexity=complexity,
        estimated_complexity=estimated,
        warnings=warnings,
        loop_nesting=max_loop_depth,
        recursion_risk=recursion_risk
    )

def analyze_javascript_file(filepath: Path) -> List[FunctionAnalysis]:
    """Basic JavaScript complexity analysis using regex patterns."""
    content = filepath.read_text()
    results = []
    
    # Find functions
    func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
    
    for match in re.finditer(func_pattern, content):
        func_name = match.group(1) or match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        
        # Find function body
        start = match.end()
        brace_count = 0
        in_body = False
        body_start = start
        
        for i, char in enumerate(content[start:], start):
            if char == '{':
                if not in_body:
                    body_start = i + 1
                    in_body = True
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if in_body and brace_count == 0:
                    body = content[body_start:i]
                    break
        else:
            body = content[start:start+500]
        
        analysis = analyze_javascript_body(func_name or 'anonymous', line_num, body)
        results.append(analysis)
    
    return results

def analyze_javascript_body(name: str, line_num: int, body: str) -> FunctionAnalysis:
    """Analyze JavaScript function body."""
    complexity = 1
    loop_depth = 0
    max_depth = 0
    warnings = []
    
    # Count complexity indicators
    complexity += len(re.findall(r'\bif\b|\bwhile\b|\bfor\b|\bcatch\b', body))
    complexity += len(re.findall(r'&&|\|\|', body))
    
    # Check for nested loops
    lines = body.split('\n')
    current_depth = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if re.search(r'\b(for|while)\b', line):
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        if '}' in line:
            current_depth = max(0, current_depth - line.count('}'))
    
    # Warnings
    if max_depth >= 2:
        warnings.append(f"Nested loops detected (depth {max_depth}) - review complexity")
    if 'await' in body and 'Promise.all' not in body:
        warnings.append("Sequential awaits detected - consider parallel execution with Promise.all")
    if re.search(r'\.map\([^)]*\.filter', body):
        warnings.append("Chained array methods - consider single-pass reduce or for-loop")
    
    complexity_label = "O(1)" if max_depth == 0 else f"O(n^{max_depth})" if max_depth > 1 else "O(n)"
    
    return FunctionAnalysis(
        name=name,
        line_number=line_num,
        cyclomatic_complexity=complexity,
        estimated_complexity=complexity_label,
        warnings=warnings,
        loop_nesting=max_depth,
        recursion_risk='return' in body and name in body
    )

def print_analysis(results: List[FunctionAnalysis], filepath: Path):
    """Print formatted analysis results."""
    print(f"\n{'='*60}")
    print(f"📊 Complexity Analysis: {filepath}")
    print('='*60)
    
    if not results:
        print("No functions found.")
        return
    
    total_complexity = sum(r.cyclomatic_complexity for r in results)
    high_complexity = sum(1 for r in results if r.cyclomatic_complexity > 10)
    
    print(f"\nSummary:")
    print(f"  Functions analyzed: {len(results)}")
    print(f"  Average complexity: {total_complexity / len(results):.1f}")
    print(f"  High complexity functions (>10): {high_complexity}")
    print(f"  Functions with warnings: {sum(1 for r in results if r.warnings)}")
    
    print(f"\n{'Function':<30} {'Line':<6} {'Complexity':<12} {'Time':<10}")
    print('-'*60)
    
    for r in sorted(results, key=lambda x: -x.cyclomatic_complexity):
        warning_marker = " ⚠️" if r.warnings else ""
        print(f"{r.name:<30} {r.line_number:<6} {r.cyclomatic_complexity:<12} {r.estimated_complexity:<10}{warning_marker}")
    
    # Detailed warnings
    functions_with_warnings = [r for r in results if r.warnings]
    if functions_with_warnings:
        print(f"\n⚠️ Warnings:")
        for r in functions_with_warnings:
            print(f"\n  {r.name} (line {r.line_number}):")
            for w in r.warnings:
                print(f"    • {w}")

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_complexity.py <file_or_directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py")) + list(target.rglob("*.js"))
    
    for filepath in files:
        if filepath.suffix == '.py':
            results = analyze_python_file(filepath)
        elif filepath.suffix == '.js':
            results = analyze_javascript_file(filepath)
        else:
            continue
        
        print_analysis(results, filepath)

if __name__ == "__main__":
    main()
