# Language-Specific Optimization Guide

## Python Optimizations

### High-Impact Techniques

**1. Vectorization with NumPy/Pandas:**
```python
# Slow: Python loops
result = [x * 2 for x in data]

# Fast: NumPy vectorization
import numpy as np
result = np.array(data) * 2  # 10-100x faster
```

**2. Built-in Functions:**
```python
# Slow: manual loop
total = 0
for x in data:
    total += x

# Fast: built-in
sum(data)  # C-implemented

# Map/filter vs list comprehensions
[x for x in data if x > 0]  # Faster than filter()
```

**3. String Concatenation:**
```python
# Slow: O(n²) string copying
result = ""
for s in strings:
    result += s

# Fast: O(n) single allocation
result = "".join(strings)
```

**4. Dictionary/Set for Lookup:**
```python
# O(n) lookup
if item in list_data:
    pass

# O(1) lookup
set_data = set(list_data)
if item in set_data:
    pass
```

### Cython for Hot Paths

```cython
# example.pyx
def fast_sum(double[:] arr):
    cdef:
        double total = 0
        Py_ssize_t i
        Py_ssize_t n = arr.shape[0]
    
    for i in range(n):
        total += arr[i]
    
    return total
```

### Profiling Python

```python
# line_profiler
from line_profiler import LineProfiler

profiler = LineProfiler()
profiler.add_function(my_function)
profiler.run('my_function()')
profiler.print_stats()

# memory_profiler
from memory_profiler import profile

@profile
def my_function():
    pass
```

## JavaScript/TypeScript Optimizations

### V8 Optimization

**1. Hidden Classes & Shape Stability:**
```javascript
// Fast: consistent object shape
class Point {
    constructor(x, y) {
        this.x = x;  // Initialize in order
        this.y = y;
    }
}

// Slow: changing shape after creation
const p = {};
p.x = 1;  // Creates hidden class
p.y = 2;  // Transitions to new hidden class
p.z = 3;  // Another transition
```

**2. Avoid Deoptimizations:**
```javascript
// Bad: mixing types
function sum(a, b) {
    return a + b;  // Handles numbers AND strings
}

// Better: type-specialized
function sumNumbers(a, b) {
    return a + b;  // Monomorphic - always numbers
}
```

**3. Async Patterns:**
```javascript
// Sequential - slow
for (const url of urls) {
    await fetch(url);
}

// Parallel - fast
await Promise.all(urls.map(url => fetch(url)));

// Controlled concurrency
async function* batchProcess(items, batchSize) {
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        yield await Promise.all(batch.map(process));
    }
}
```

**4. Array Methods vs Loops:**
```javascript
// For small arrays - readable
const doubled = items.map(x => x * 2);

// For large arrays - faster
const doubled = [];
for (let i = 0; i < items.length; i++) {
    doubled[i] = items[i] * 2;
}
```

## Java Optimizations

### JVM Tuning

**1. Garbage Collection:**
```bash
# G1GC for balanced workloads
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200

# ZGC for low-latency (Java 11+)
-XX:+UseZGC
-XX:ZCollectionInterval=5

# Shenandoah for consistent latency
-XX:+UseShenandoahGC
```

**2. Collection Choices:**
```java
// ArrayList vs LinkedList
List<Integer> list = new ArrayList<>();  // Better cache locality

// HashMap initial capacity
Map<String, Data> map = new HashMap<>(expectedSize * 2);

// Primitive collections (Trove, Eclipse Collections)
TIntIntMap primitiveMap = new TIntIntHashMap();  // No boxing
```

**3. StringBuilder:**
```java
// String concatenation in loops
StringBuilder sb = new StringBuilder();
for (String s : strings) {
    sb.append(s);
}
String result = sb.toString();
```

### JIT Optimizations

```java
// Methods that benefit from JIT:
// - Called frequently (>10,000 times)
// - Small, hot loops
// - Consistent types (no megamorphic call sites)

// Force JIT compilation (testing)
-XX:CompileThreshold=1000
```

## C++ Optimizations

### Move Semantics

```cpp
// Copy (expensive)
std::vector<Data> create() {
    std::vector<Data> v(1000000);
    return v;  // Copy constructor
}

// Move (cheap)
std::vector<Data> create() {
    std::vector<Data> v(1000000);
    return v;  // Move constructor (C++11+)
}

// Explicit move
std::vector<Data> v1 = create();
std::vector<Data> v2 = std::move(v1);  // Transfer ownership
```

### Cache-Friendly Code

```cpp
// Bad: jumping through memory
for (int j = 0; j < cols; j++)
    for (int i = 0; i < rows; i++)
        sum += matrix[i][j];

// Good: sequential access
for (int i = 0; i < rows; i++)
    for (int j = 0; j < cols; j++)
        sum += matrix[i][j];

// Structure of Arrays vs Array of Structures
// AoS (bad for SIMD/cache)
struct Particle { float x, y, z; };
std::vector<Particle> particles;

// SoA (good for SIMD/cache)
struct Particles {
    std::vector<float> x, y, z;
};
```

### Compiler Optimizations

```bash
# Optimization levels
-O0  # Debug, no optimization
-O2  # Standard optimizations
-O3  # Aggressive optimizations
-Ofast  # O3 + disregard standards compliance

# Profile-guided optimization
-fprofile-generate  # Run with training data
-fprofile-use        # Compile with profile data

# Link-time optimization
-flto
```

## Go Optimizations

### Goroutines & Channels

```go
// Worker pool pattern
func workerPool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}
```

### Memory Optimization

```go
// Pre-allocate slices
// Bad: multiple allocations
var result []int
for i := 0; i < n; i++ {
    result = append(result, i)
}

// Good: single allocation
result := make([]int, 0, n)
for i := 0; i < n; i++ {
    result = append(result, i)
}

// String building
// Bad: string concatenation
var s string
for _, part := range parts {
    s += part
}

// Good: strings.Builder
var b strings.Builder
b.Grow(estimatedSize)
for _, part := range parts {
    b.WriteString(part)
}
s := b.String()
```

### Escape Analysis

```go
// Stack allocation (fast)
func stackAlloc() int {
    x := 1
    return x
}

// Heap allocation (slower)
func heapAlloc() *int {
    x := 1
    return &x  // Escapes to heap
}

// Check with: go build -gcflags="-m"
```

## Rust Optimizations

### Zero-Cost Abstractions

```rust
// Iterator chains compile to efficient loops
let sum: i32 = (0..1000)
    .map(|x| x * 2)
    .filter(|x| x % 3 == 0)
    .sum();

// Same performance as:
let mut sum = 0;
for x in 0..1000 {
    let doubled = x * 2;
    if doubled % 3 == 0 {
        sum += doubled;
    }
}
```

### SIMD

```rust
use std::arch::x86_64::*;

#[target_feature(enable = "avx2")]
unsafe fn sum_avx2(arr: &[f32]) -> f32 {
    let mut sum = _mm256_setzero_ps();
    
    for chunk in arr.chunks_exact(8) {
        let vec = _mm256_loadu_ps(chunk.as_ptr());
        sum = _mm256_add_ps(sum, vec);
    }
    
    // Horizontal sum
    let hsum = _mm256_hadd_ps(sum, sum);
    let hsum = _mm256_hadd_ps(hsum, hsum);
    _mm_cvtss_f32(_mm256_castps256_ps128(hsum))
}
```

### Unsafe for Performance

```rust
// Bounds check elimination
pub fn get_unchecked(arr: &[i32], idx: usize) -> i32 {
    unsafe { *arr.get_unchecked(idx) }
}

// Raw pointers for low-level control
pub fn fast_copy(src: &[u8], dst: &mut [u8]) {
    unsafe {
        std::ptr::copy_nonoverlapping(
            src.as_ptr(),
            dst.as_mut_ptr(),
            src.len()
        );
    }
}
```

## General Cross-Language Tips

### Algorithm Selection

| Problem | Avoid | Prefer |
|---------|-------|--------|
| Frequent lookups | Linear search | Hash map |
| Ordered data | Unsorted array | B-tree, sorted vec |
| Min/max tracking | Linear scan | Heap |
| Range queries | Scan | Segment tree, Fenwick |

### Memory Patterns

1. **Access sequentially** - improves cache prefetching
2. **Keep hot data small** - fits in cache lines
3. **Avoid pointer chasing** - linked lists, deep objects
4. **Pool allocations** - reuse objects in hot paths
5. **Consider arena allocators** - bulk free
