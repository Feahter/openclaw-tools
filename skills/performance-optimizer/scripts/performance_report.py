#!/usr/bin/env python3
"""
Performance Report Generator
Compares baseline and optimized performance metrics.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
import statistics

@dataclass
class Metric:
    name: str
    baseline: float
    optimized: float
    unit: str = "ms"
    
    @property
    def improvement(self) -> float:
        if self.baseline == 0:
            return 0
        return ((self.baseline - self.optimized) / self.baseline) * 100
    
    @property
    def speedup(self) -> float:
        if self.optimized == 0:
            return 0
        return self.baseline / self.optimized

def load_metrics(filepath: Path) -> Dict[str, float]:
    """Load metrics from JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return data.get('metrics', data)

def generate_report(baseline_file: Path, optimized_file: Path) -> List[Metric]:
    """Generate comparison report."""
    baseline = load_metrics(baseline_file)
    optimized = load_metrics(optimized_file)
    
    metrics = []
    all_keys = set(baseline.keys()) | set(optimized.keys())
    
    for key in sorted(all_keys):
        metrics.append(Metric(
            name=key,
            baseline=baseline.get(key, 0),
            optimized=optimized.get(key, 0),
            unit=infer_unit(key)
        ))
    
    return metrics

def infer_unit(metric_name: str) -> str:
    """Infer unit from metric name."""
    name_lower = metric_name.lower()
    if 'time' in name_lower or 'latency' in name_lower or 'duration' in name_lower:
        return 'ms'
    elif 'memory' in name_lower or 'size' in name_lower:
        return 'MB'
    elif 'throughput' in name_lower or 'rate' in name_lower:
        return 'ops/sec'
    elif 'cpu' in name_lower:
        return '%'
    return 'units'

def print_report(metrics: List[Metric]):
    """Print formatted report."""
    print(f"\n{'='*70}")
    print("📊 Performance Comparison Report")
    print('='*70)
    
    if not metrics:
        print("No metrics to compare.")
        return
    
    # Summary statistics
    improvements = [m.improvement for m in metrics if m.baseline > 0]
    if improvements:
        avg_improvement = statistics.mean(improvements)
        max_improvement = max(improvements)
        print(f"\n📈 Overall Improvements:")
        print(f"  Average: {avg_improvement:+.1f}%")
        print(f"  Best: {max_improvement:+.1f}%")
    
    print(f"\n{'Metric':<30} {'Baseline':<12} {'Optimized':<12} {'Change':<12} {'Speedup':<10}")
    print('-'*70)
    
    total_baseline = 0
    total_optimized = 0
    
    for m in metrics:
        change = f"{m.improvement:+.1f}%"
        speedup = f"{m.speedup:.2f}x"
        
        # Color coding for significant changes
        icon = "🚀" if m.improvement > 50 else "✅" if m.improvement > 0 else "⚠️" if m.improvement < 0 else "➖"
        
        print(f"{m.name:<30} {m.baseline:,.2f} {m.unit:<6} {m.optimized:,.2f} {m.unit:<6} {change:<12} {speedup:<10} {icon}")
        
        total_baseline += m.baseline
        total_optimized += m.optimized
    
    print('-'*70)
    
    # Totals
    if total_baseline > 0:
        total_change = ((total_baseline - total_optimized) / total_baseline) * 100
        total_speedup = total_baseline / total_optimized if total_optimized > 0 else 0
        print(f"{'TOTAL':<30} {total_baseline:,.2f} {'':<6} {total_optimized:,.2f} {'':<6} {total_change:+.1f}%{'':<6} {total_speedup:.2f}x")
    
    # Highlight significant findings
    regressions = [m for m in metrics if m.improvement < -5]
    major_wins = [m for m in metrics if m.improvement > 50]
    
    if major_wins:
        print(f"\n🎯 Major Improvements (>50%):")
        for m in major_wins:
            print(f"  • {m.name}: {m.improvement:+.1f}% faster ({m.speedup:.2f}x)")
    
    if regressions:
        print(f"\n⚠️ Regressions Detected:")
        for m in regressions:
            print(f"  • {m.name}: {m.improvement:+.1f}% slower")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate performance comparison report')
    parser.add_argument('--baseline', required=True, help='Baseline metrics JSON file')
    parser.add_argument('--after', required=True, help='Optimized metrics JSON file')
    parser.add_argument('--output', help='Output report to JSON file')
    args = parser.parse_args()
    
    baseline_path = Path(args.baseline)
    after_path = Path(args.after)
    
    if not baseline_path.exists():
        print(f"Error: Baseline file not found: {baseline_path}")
        sys.exit(1)
    
    if not after_path.exists():
        print(f"Error: After file not found: {after_path}")
        sys.exit(1)
    
    metrics = generate_report(baseline_path, after_path)
    print_report(metrics)
    
    if args.output:
        output_path = Path(args.output)
        report_data = {
            'metrics': [asdict(m) for m in metrics],
            'summary': {
                'improvements': [m.name for m in metrics if m.improvement > 0],
                'regressions': [m.name for m in metrics if m.improvement < 0]
            }
        }
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n💾 Report saved to: {output_path}")

if __name__ == "__main__":
    main()
