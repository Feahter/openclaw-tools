# Complexity Analysis Guide

## Time Complexity Reference

### Fundamental Classes

| Complexity | Name | Example |
|------------|------|---------|
| O(1) | Constant | Array access, hash lookup |
| O(log n) | Logarithmic | Binary search, tree operations |
| O(n) | Linear | Single loop, linear search |
| O(n log n) | Linearithmic | Merge sort, heap sort |
| O(n²) | Quadratic | Nested loops, bubble sort |
| O(n³) | Cubic | Triple nested loops |
| O(2^n) | Exponential | Subset generation, brute force |
| O(n!) | Factorial | Permutations, traveling salesman |

### Common Algorithm Complexities

**Sorting:**
- QuickSort: O(n log n) avg, O(n²) worst
- MergeSort: O(n log n) guaranteed
- HeapSort: O(n log n) guaranteed
- Counting Sort: O(n + k) for integers

**Search:**
- Binary Search: O(log n)
- Hash Table: O(1) avg, O(n) worst
- B-Tree: O(log n)

**Graph:**
- BFS/DFS: O(V + E)
- Dijkstra: O((V + E) log V)
- Floyd-Warshall: O(V³)

**Dynamic Programming:**
- Fibonacci: O(n) with memoization
- Knapsack: O(nW)
- LCS: O(mn)

## Space Complexity

### Memory Usage Patterns

| Pattern | Space | Notes |
|---------|-------|-------|
| Iterative | O(1) - O(n) | Depends on data structures |
| Recursive | O(depth) | Stack frames |
| Memoization | O(states) | Cache size |
| DP Table | O(n²) typical | 2D problems |

### Cache Complexity

**Cache-Oblivious Algorithms:**
- Work for any cache size without tuning
- Examples: Cache-oblivious B-trees, matrix multiplication

**Cache Efficiency Metrics:**
- Cache hit rate > 95% for hot paths
- Cache line utilization
- False sharing elimination

## Amortized Analysis

**When to Use:**
- Data structures with occasional expensive operations
- Dynamic arrays (vector)
- Union-Find
- Splay trees

**Example - Dynamic Array:**
```
Append operation:
- Most appends: O(1)
- Resize: O(n) but happens every n operations
- Amortized: O(1)
```

## Practical Complexity Guidelines

### What n means in practice

| n | Feasible Algorithms |
|---|---------------------|
| ≤ 10 | O(n!), O(2^n) |
| ≤ 20 | O(2^n) with pruning |
| ≤ 100 | O(n³) |
| ≤ 1,000 | O(n²) |
| ≤ 100,000 | O(n log n) |
| ≤ 10^6 | O(n) or O(n log n) |
| ≤ 10^9 | O(log n), O(1) |

### Complexity Reduction Strategies

**1. Use Better Data Structures:**
```
List lookup:    O(n)     → Hash map: O(1)
Array insert:   O(n)     → Linked list: O(1)
Linear search:  O(n)     → BST: O(log n)
```

**2. Preprocessing:**
```
Query array max: O(n) per query
Precompute: O(n) once, O(1) per query

Sort for binary search: O(n log n) once
```

**3. Pruning:**
```
Brute force: O(2^n)
Branch and bound: Much better in practice
```

**4. Approximation:**
```
TSP exact: O(n!)
TSP approximation: O(n²) with 1.5x bound
```

## Profiling Complexity

### Empirical Measurement

```python
def measure_complexity(func, input_sizes):
    """Measure empirical time complexity."""
    times = []
    for n in input_sizes:
        data = generate_data(n)
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        times.append((n, elapsed))
    return times

# Plot to identify complexity class
# Linear: constant slope on linear scale
# Quadratic: linear on log-log scale with slope ~2
# Exponential: linear on semi-log scale
```

### Complexity Inference

| Observation | Likely Complexity |
|-------------|-------------------|
| Time doubles when n doubles | O(n) |
| Time quadruples when n doubles | O(n²) |
| Time constant regardless of n | O(1) |
| Time increases by constant when n doubles | O(log n) |
| Time slightly more than doubles | O(n log n) |
