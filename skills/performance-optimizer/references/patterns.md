# Optimization Patterns Catalog

## Creational Patterns

### Object Pool
**When to use:** High-frequency object creation/destruction

```python
class ConnectionPool:
    def __init__(self, factory, max_size=100):
        self.factory = factory
        self.max_size = max_size
        self.available = []
        self.in_use = set()
    
    def acquire(self):
        if self.available:
            conn = self.available.pop()
        else:
            conn = self.factory()
        self.in_use.add(id(conn))
        return conn
    
    def release(self, conn):
        if id(conn) in self.in_use:
            self.in_use.remove(id(conn))
            if len(self.available) < self.max_size:
                self.available.append(conn)
```

**Benefits:**
- Reduces allocation overhead
- Reduces GC pressure
- Predictable memory usage

### Lazy Initialization

```python
class ExpensiveResource:
    def __init__(self):
        self._resource = None
    
    @property
    def resource(self):
        if self._resource is None:
            self._resource = self._create_resource()
        return self._resource
```

## Structural Patterns

### Flyweight
**When to use:** Many similar objects, share immutable state

```python
class FontFlyweight:
    _cache = {}
    
    @classmethod
    def get(cls, name, size, style):
        key = (name, size, style)
        if key not in cls._cache:
            cls._cache[key] = Font(name, size, style)
        return cls._cache[key]

# Usage: thousands of characters share few font objects
```

### Copy-on-Write

```python
class CopyOnWriteList:
    def __init__(self, items=None):
        self._items = items or []
        self._copied = False
    
    def _ensure_writable(self):
        if not self._copied:
            self._items = self._items.copy()
            self._copied = True
    
    def append(self, item):
        self._ensure_writable()
        self._items.append(item)
```

## Behavioral Patterns

### Memoization

```python
from functools import lru_cache

# Automatic
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Manual with TTL
import time

def memoize_with_ttl(ttl_seconds):
    def decorator(func):
        cache = {}
        def wrapper(*args):
            now = time.time()
            if args in cache:
                result, expiry = cache[args]
                if now < expiry:
                    return result
            result = func(*args)
            cache[args] = (result, now + ttl_seconds)
            return result
        return wrapper
    return decorator
```

### Batch Processing

```python
class Batcher:
    def __init__(self, processor, batch_size=100, timeout_ms=10):
        self.processor = processor
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms
        self.batch = []
        self.last_flush = time.time()
    
    def add(self, item):
        self.batch.append(item)
        if len(self.batch) >= self.batch_size:
            self.flush()
        elif time.time() - self.last_flush > self.timeout_ms / 1000:
            self.flush()
    
    def flush(self):
        if self.batch:
            self.processor(self.batch)
            self.batch = []
            self.last_flush = time.time()
```

## Concurrency Patterns

### Producer-Consumer

```python
import queue
from threading import Thread

class Pipeline:
    def __init__(self, workers=4):
        self.work_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue()
        self.workers = workers
    
    def start(self, processor):
        for _ in range(self.workers):
            Thread(target=self._worker, args=(processor,), daemon=True).start()
    
    def _worker(self, processor):
        while True:
            item = self.work_queue.get()
            result = processor(item)
            self.result_queue.put(result)
            self.work_queue.task_done()
```

### Work Stealing

```rust
// Conceptual Rust implementation
use crossbeam::deque::{Worker, Stealer};

struct WorkStealingPool {
    workers: Vec<Worker<Task>>,
    stealers: Vec<Stealer<Task>>,
}

impl WorkStealingPool {
    fn execute(&self, worker_id: usize, task: Task) {
        self.workers[worker_id].push(task);
    }
    
    fn steal(&self, thief_id: usize) -> Option<Task> {
        // Try local queue first, then steal from others
        for (i, stealer) in self.stealers.iter().enumerate() {
            if i != thief_id {
                if let Some(task) = stealer.steal() {
                    return Some(task);
                }
            }
        }
        None
    }
}
```

### Circuit Breaker

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = State.CLOSED
        self.failures = 0
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = State.CLOSED
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = State.OPEN
```

## Data Access Patterns

### Cache-Aside (Lazy Loading)

```python
class CacheAside:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database
    
    def get(self, key):
        # Try cache first
        value = self.cache.get(key)
        if value is not None:
            return value
        
        # Cache miss - load from DB
        value = self.db.query(key)
        self.cache.set(key, value)
        return value
```

### Write-Through

```python
class WriteThroughCache:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database
    
    def set(self, key, value):
        # Write to both cache and DB
        self.db.update(key, value)
        self.cache.set(key, value)
```

### Read-Through with Bloom Filter

```python
import pybloom_live

class ReadThroughWithBloomFilter:
    def __init__(self, cache, database, expected_items=1000000, fp_rate=0.01):
        self.cache = cache
        self.db = database
        self.bloom = pybloom_live.BloomFilter(
            capacity=expected_items, 
            error_rate=fp_rate
        )
    
    def get(self, key):
        # Quick negative check
        if key not in self.bloom:
            return None
        
        # Try cache
        value = self.cache.get(key)
        if value is not None:
            return value
        
        # Load from DB
        value = self.db.query(key)
        if value:
            self.cache.set(key, value)
        return value
    
    def set(self, key, value):
        self.bloom.add(key)
        self.db.update(key, value)
        self.cache.set(key, value)
```

## Algorithmic Patterns

### Divide and Conquer

```python
def parallel_merge_sort(arr, threshold=10000):
    if len(arr) <= threshold:
        return sorted(arr)
    
    mid = len(arr) // 2
    
    # Parallel recursive calls
    with ThreadPoolExecutor() as executor:
        left_future = executor.submit(parallel_merge_sort, arr[:mid])
        right = parallel_merge_sort(arr[mid:])
        left = left_future.result()
    
    return merge(left, right)
```

### Sliding Window

```python
def sliding_window_optimized(arr, window_size):
    """O(n) instead of O(n*k)"""
    if len(arr) < window_size:
        return []
    
    # Compute first window
    window_sum = sum(arr[:window_size])
    results = [window_sum]
    
    # Slide the window
    for i in range(window_size, len(arr)):
        window_sum += arr[i] - arr[i - window_size]
        results.append(window_sum)
    
    return results
```

### Two Pointers

```python
def two_sum_sorted(arr, target):
    """O(n) instead of O(n²)"""
    left, right = 0, len(arr) - 1
    
    while left < right:
        current = arr[left] + arr[right]
        if current == target:
            return [left, right]
        elif current < target:
            left += 1
        else:
            right -= 1
    
    return None
```

## Performance Anti-Patterns

### String Concatenation in Loops

```python
# BAD: O(n²)
result = ""
for s in strings:
    result += s

# GOOD: O(n)
result = "".join(strings)
```

### Repeated Lookups

```python
# BAD: O(n) per iteration
for item in items:
    if item in large_list:  # Linear search
        process(item)

# GOOD: O(1) per iteration
large_set = set(large_list)  # O(n) once
for item in items:
    if item in large_set:
        process(item)
```

### Excessive Logging

```python
# BAD: String formatting even when log level filters it
logger.debug(f"Processing {expensive_computation()}")

# GOOD: Lazy evaluation
logger.debug("Processing %s", expensive_computation)  # Only if debug enabled
```
