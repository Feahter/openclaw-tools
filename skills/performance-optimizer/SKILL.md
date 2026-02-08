---
name: performance-optimizer
description: Comprehensive performance bottleneck detection and optimization algorithms with cross-language generalization capabilities. Use when analyzing code performance, identifying bottlenecks, optimizing algorithms, profiling applications, or designing high-performance systems. Covers systematic profiling methods, complexity analysis, caching strategies, memory optimization, concurrency patterns, and language-specific optimization techniques.
license: Complete terms in LICENSE.txt
---

# Performance Optimizer

A systematic approach to identifying and eliminating performance bottlenecks across programming languages and paradigms.

## Quick Start

**When performance issues arise:**
1. Measure first — establish baseline metrics
2. Profile to locate hotspots
3. Analyze root causes (algorithmic vs implementation)
4. Apply targeted optimizations
5. Verify improvements with benchmarks

## Core Methodology

### The OPTIMIZE Framework

```
O - Observe: Measure current performance
P - Profile: Identify hotspots and bottlenecks
T - Theorize: Hypothesize root causes
I - Implement: Apply targeted optimizations
M - Measure: Validate improvements
I - Iterate: Refine and repeat
Z - Zero-in: Focus on highest-impact changes
E - Evaluate: Ensure maintainability
```

### Performance Analysis Pyramid

```
    ┌─────────────────┐
    │   Algorithmic   │ ← O(n²) → O(n log n)
    │   Complexity    │   Biggest gains
    ├─────────────────┤
    │   Data Locality │ ← Cache efficiency
    │   & Memory      │   Memory layouts
    ├─────────────────┤
    │   System Calls  │ ← I/O batching
    │   & I/O         │   Async operations
    ├─────────────────┤
    │   Micro-        │ ← Loop unrolling
    │   optimizations │   SIMD, inlining
    └─────────────────┘
```

**Rule**: Optimize top-down. Algorithmic improvements beat micro-optimizations by orders of magnitude.

### USE Method (System Resource Analysis)

From Brendan Gregg's systems performance methodology. For every resource, check:

| Resource | Utilization | Saturation | Errors |
|----------|-------------|------------|--------|
| **CPU** | % busy time | run queue length | hw errors |
| **Memory** | % used | swap/page ops | OOM events |
| **Disk** | % busy time | I/O wait queue | disk errors |
| **Network** | % bandwidth | packet drops | conn errors |

**Saturation** = Work queued because resource is busy (latency-sensitive)

**Quick Check:**
```bash
# Linux - Check all resources
vmstat 1 5      # CPU, memory, swap
iostat -x 1 5   # Disk utilization
ss -tan | wc -l # Connection saturation
```

### Latency Distribution Analysis

Don't just measure average — understand the full distribution:

| Metric | What it tells you | When to worry |
|--------|-------------------|---------------|
| **p50** | Typical user experience | Baseline |
| **p95** | Worst-case for 95% users | > 2x p50 |
| **p99** | Tail latency, outliers | > 5x p50 |
| **Max** | Worst case ever | Spikes indicate issues |

**Tail latency root causes:**
- GC pauses
- Lock contention
- Queue buildup (Little's Law: L = λW)
- Cache eviction

```python
# Latency distribution measurement
import numpy as np
from typing import List

def analyze_latency(latencies_ms: List[float]):
    """Analyze latency distribution with percentile breakdown."""
    latencies = np.array(latencies_ms)
    
    print(f"Count: {len(latencies)}")
    print(f"Min:   {np.min(latencies):.2f}ms")
    print(f"p50:   {np.percentile(latencies, 50):.2f}ms")
    print(f"p95:   {np.percentile(latencies, 95):.2f}ms")
    print(f"p99:   {np.percentile(latencies, 99):.2f}ms")
    print(f"Max:   {np.max(latencies):.2f}ms")
    
    # Tail latency ratio (p99/p50)
    tail_ratio = np.percentile(latencies, 99) / np.percentile(latencies, 50)
    print(f"\nTail ratio (p99/p50): {tail_ratio:.2f}x")
    if tail_ratio > 10:
        print("⚠️  High tail latency — check for blocking operations")
```

## Bottleneck Identification

### 1. Measurement First

```python
# Universal timing decorator
import time
import functools
from typing import Callable, Any

def benchmark(iterations: int = 1):
    """Universal benchmarking decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            times = []
            result = None
            for _ in range(iterations):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            print(f"{func.__name__}: {avg_time:.4f}s (avg of {iterations})")
            return result
        return wrapper
    return decorator

# Usage
@benchmark(iterations=100)
def slow_function():
    pass
```

### 2. Profiling Patterns

**CPU Profiling:**
```python
# Python - cProfile integration
import cProfile
import pstats
import io

def profile_function(func, *args, **kwargs):
    """Profile any function and return sorted stats."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())
    return result
```

**Memory Profiling:**
```python
# Memory tracking pattern (language-agnostic concept)
import tracemalloc

def track_memory(func):
    """Track memory usage of function execution."""
    tracemalloc.start()
    result = func()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Current: {current / 1024 / 1024:.2f} MB")
    print(f"Peak: {peak / 1024 / 1024:.2f} MB")
    return result
```

### 3. Common Bottleneck Patterns

| Pattern | Symptom | Detection | Solution |
|---------|---------|-----------|----------|
| **N+1 Query** | DB calls in loops | Profile shows many similar queries | Batch queries, use JOINs |
| **Quadratic Loop** | Slow on large inputs | O(n²) complexity in profiling | Use hash maps, sorting |
| **Memory Churn** | GC pressure, high CPU | Frequent allocations | Object pooling, pre-allocation |
| **Cache Thrashing** | Inconsistent performance | Cache miss spikes | Improve locality, padding |
| **Lock Contention** | Thread blocking | High wait times | Fine-grained locks, lock-free |
| **I/O Blocking** | Low CPU, high latency | I/O wait in system calls | Async, batching, caching |

## Optimization Strategies

### Algorithmic Optimizations

**Complexity Reduction:**
```python
# Before: O(n²) - nested loops
for i in data:
    for j in data:
        if i.id == j.parent_id:  # Linear search
            process(i, j)

# After: O(n) - hash map lookup
id_map = {j.id: j for j in data}
for i in data:
    if i.parent_id in id_map:  # O(1) lookup
        process(i, id_map[i.parent_id])
```

**Space-Time Tradeoff:**
```python
# Memoization pattern (universal)
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Data Structure Selection

| Use Case | Avoid | Prefer | Complexity Gain |
|----------|-------|--------|-----------------|
| Frequent lookups | List | Hash Map/Set | O(n) → O(1) |
| Range queries | Unsorted array | BST/Segment Tree | O(n) → O(log n) |
| Min/Max tracking | Linear scan | Heap | O(n) → O(log n) |
| String matching | Naive search | KMP/Rabin-Karp | O(nm) → O(n+m) |
| Graph traversal | Recursive DFS | Iterative + Stack | Stack overflow safe |

### Memory Optimization

**Cache-Friendly Patterns:**
```cpp
// Column-major vs Row-major (C/C++/Rust example)
// BAD: Cache-unfriendly access
for (int j = 0; j < cols; j++)
    for (int i = 0; i < rows; i++)
        sum += matrix[i][j];  // Jumping through memory

// GOOD: Sequential access
for (int i = 0; i < rows; i++)
    for (int j = 0; j < cols; j++)
        sum += matrix[i][j];  // Sequential cache lines
```

**Object Pooling Pattern:**
```python
class ObjectPool:
    """Universal object pooling pattern."""
    def __init__(self, factory, max_size=100):
        self.factory = factory
        self.max_size = max_size
        self.available = []
        self.in_use = set()
    
    def acquire(self):
        obj = self.available.pop() if self.available else self.factory()
        self.in_use.add(id(obj))
        return obj
    
    def release(self, obj):
        if id(obj) in self.in_use:
            self.in_use.remove(id(obj))
            if len(self.available) < self.max_size:
                self.available.append(obj)
```

### Concurrency Optimization

**Parallel Processing Patterns:**
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

def parallel_map(func, data, max_workers=None, use_processes=False):
    """Universal parallel processing pattern."""
    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    with Executor(max_workers=max_workers) as executor:
        return list(executor.map(func, data))

# CPU-bound: Use processes
results = parallel_map(heavy_computation, data, use_processes=True)

# I/O-bound: Use threads
results = parallel_map(fetch_url, urls, use_processes=False)
```

**Lock-Free Patterns:**
```python
import queue
from threading import Lock

# Producer-Consumer with queue
work_queue = queue.Queue(maxsize=1000)
results_queue = queue.Queue()

# Thread-safe without explicit locks
work_queue.put(item)
result = results_queue.get()
```

## Language-Specific Optimizations

See `references/language-specific.md` for detailed optimizations per language:
- Python: Vectorization with NumPy, Cython extensions
- JavaScript: V8 optimization, async patterns
- Java: JVM tuning, garbage collection
- C++: Move semantics, template metaprogramming
- Go: Goroutines, channel patterns
- Rust: Zero-cost abstractions, SIMD

## The Performance Budget

**Define constraints upfront:**
```
Response Time Budgets:
├─ API Endpoint: < 200ms (p99)
├─ Database Query: < 50ms
├─ Cache Lookup: < 5ms
└─ Client Render: < 16ms (60fps)

Memory Budgets:
├─ Per Request: < 100MB
├─ Heap Growth: < 10%/hour
└─ GC Pause: < 50ms
```

**Optimization Priority Matrix:**
```
High Impact + Low Effort  → Do First
High Impact + High Effort  → Plan Carefully  
Low Impact + Low Effort   → Fill Time Gaps
Low Impact + High Effort  → Avoid
```

## Performance Testing Guide

### Types of Performance Tests

| Test Type | Purpose | When to Run |
|-----------|---------|-------------|
| **Load Test** | Behavior at expected load | Release validation |
| **Stress Test** | Breaking point, recovery | Capacity planning |
| **Spike Test** | Sudden load changes | Auto-scaling validation |
| **Soak Test** | Memory leaks, degradation | Long-running services |

### Load Model Design

**Representative load includes:**
1. **Throughput**: Requests per second
2. **Mix**: Read vs write ratio
3. **Pattern**: Steady, ramp-up, burst
4. **Data**: Realistic data distributions

```python
# Example: Gradual ramp-up test
import time

def ramp_up_test(func, start_rps=10, max_rps=1000, duration_per_step=60):
    """Gradually increase load to find saturation point."""
    current_rps = start_rps
    
    while current_rps <= max_rps:
        print(f"Testing at {current_rps} RPS for {duration_per_step}s...")
        
        # Run load at current RPS
        metrics = run_load(func, rps=current_rps, duration=duration_per_step)
        
        # Check for saturation (USE method)
        if metrics.error_rate > 0.01 or metrics.p99_latency > 500:
            print(f"⚠️  Saturation detected at {current_rps} RPS")
            print(f"   Error rate: {metrics.error_rate:.2%}")
            print(f"   P99 latency: {metrics.p99_latency:.2f}ms")
            break
        
        current_rps *= 2  # Double the load
    
    return current_rps  # Saturation point
```

### Queue Theory Primer

**Little's Law**: L = λW
- L = Average number of items in system
- λ = Arrival rate (items per second)
- W = Average time in system

**Key insight**: As utilization approaches 100%, queue length (and latency) grows exponentially.

```
Utilization vs Queue Length:
├─ 50%  → Low queueing
├─ 80%  → Moderate queueing  ← Target for headroom
├─ 90%  → Significant queueing
└─ 95%+ → Queue explodes, latency spikes
```

**Rule of thumb**: Keep resource utilization below 80% for latency-sensitive services.

## Automated Analysis Scripts

Use the bundled scripts for systematic analysis:

```bash
# Analyze Python code complexity
python scripts/analyze_complexity.py target_file.py

# Detect common anti-patterns
python scripts/detect_bottlenecks.py --lang python src/

# Generate performance report
python scripts/performance_report.py --baseline before.json --after after.json
```

## Anti-Patterns to Avoid

1. **Premature Optimization** — "We should forget about small efficiencies, say about 97% of the time"
2. **Optimization Without Measurement** — Guessing bottlenecks wastes time
3. **Micro-optimization Blindness** — Missing algorithmic improvements
4. **Complexity for Speed** — Unmaintainable code for marginal gains
5. **Ignoring Big-O** — Focusing on constants while ignoring growth rates

## References

- **Complexity Analysis**: See [references/complexity-guide.md](references/complexity-guide.md)
- **Language-Specific Tips**: See [references/language-specific.md](references/language-specific.md)
- **Optimization Patterns**: See [references/patterns.md](references/patterns.md)
