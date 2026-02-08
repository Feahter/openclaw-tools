---
name: algorithm-toolkit
description: |
  算法优化工具箱 - 即拿即用的多语言算法代码库。
  
  **触发场景：**
  1. **性能优化** - "优化这段代码"、"太慢了"、"时间复杂度太高"
  2. **功能实现** - "实现 LRU 缓存"、"求第 K 大元素"、"字符串匹配"
  3. **内存优化** - "内存占用太高"、"处理海量数据"
  4. **并发优化** - "并发性能问题"、"线程安全"
  
  **提供两种风格：**
  - **竞赛版** - 最短代码、最快实现
  - **工程版** - 健壮、类型注解、异常处理
  
  **支持语言：** Python、JavaScript/TypeScript、Rust、Go、C++
  
  **使用方式：** 直接描述问题，自动匹配算法并提供可直接 copy-paste 的代码。
---

# 算法优化工具箱

## 快速决策

| 问题关键词 | 推荐算法 | 复杂度 |
|-----------|---------|--------|
| 查找第 K 大/小 | 快速选择 | O(n) |
| 频繁查找 | 哈希表 | O(1) |
| 范围查询 | 线段树/树状数组 | O(log n) |
| 去重/存在性判断 | 布隆过滤器 | O(k) |
| 字符串匹配 | KMP/AC 自动机 | O(n+m) |
| 最短路 | Dijkstra | O(E log V) |
| 最小生成树 | Kruskal | O(E log E) |
| 动态第 K 大 | 权值线段树 | O(log n) |

## 数据结构

### 并查集 (Union-Find)

**竞赛版 (Python)**
```python
class UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
    def find(self, x):
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])
        return self.p[x]
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.r[px] < self.r[py]:
            px, py = py, px
        self.p[py] = px
        if self.r[px] == self.r[py]:
            self.r[px] += 1
        return True
```

**工程版 (Python)**
```python
from typing import List

class UnionFind:
    """并查集 - 路径压缩 + 按秩合并"""
    
    def __init__(self, n: int):
        self._parent: List[int] = list(range(n))
        self._rank: List[int] = [0] * n
        self._count: int = n
    
    def find(self, x: int) -> int:
        """查找根节点，带路径压缩"""
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """合并两个集合，返回是否成功合并"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self._rank[px] < self._rank[py]:
            px, py = py, px
        self._parent[py] = px
        if self._rank[px] == self._rank[py]:
            self._rank[px] += 1
        self._count -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
    
    @property
    def count(self) -> int:
        return self._count
```

**Rust 版**
```rust
pub struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<u8>,
}

impl UnionFind {
    pub fn new(n: usize) -> Self {
        Self {
            parent: (0..n).collect(),
            rank: vec![0; n],
        }
    }
    
    pub fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            self.parent[x] = self.find(self.parent[x]);
        }
        self.parent[x]
    }
    
    pub fn union(&mut self, x: usize, y: usize) -> bool {
        let (px, py) = (self.find(x), self.find(y));
        if px == py {
            return false;
        }
        match self.rank[px].cmp(&self.rank[py]) {
            std::cmp::Ordering::Less => self.parent[px] = py,
            std::cmp::Ordering::Greater => self.parent[py] = px,
            _ => {
                self.parent[py] = px;
                self.rank[px] += 1;
            }
        }
        true
    }
}
```

### 线段树 (Segment Tree)

**竞赛版 (Python)**
```python
class SegTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.t = [0] * (4 * self.n)
        self._build(arr, 0, 0, self.n - 1)
    
    def _build(self, a, v, l, r):
        if l == r:
            self.t[v] = a[l]
        else:
            m = (l + r) // 2
            self._build(a, v*2+1, l, m)
            self._build(a, v*2+2, m+1, r)
            self.t[v] = self.t[v*2+1] + self.t[v*2+2]
    
    def update(self, idx, val):
        self._update(idx, val, 0, 0, self.n - 1)
    
    def _update(self, i, val, v, l, r):
        if l == r:
            self.t[v] = val
        else:
            m = (l + r) // 2
            if i <= m:
                self._update(i, val, v*2+1, l, m)
            else:
                self._update(i, val, v*2+2, m+1, r)
            self.t[v] = self.t[v*2+1] + self.t[v*2+2]
    
    def query(self, L, R):
        return self._query(L, R, 0, 0, self.n - 1)
    
    def _query(self, L, R, v, l, r):
        if L <= l and r <= R:
            return self.t[v]
        if r < L or R < l:
            return 0
        m = (l + r) // 2
        return self._query(L, R, v*2+1, l, m) + self._query(L, R, v*2+2, m+1, r)
```

### 树状数组 (Fenwick Tree)

**竞赛版 (Python)**
```python
class BIT:
    def __init__(self, n):
        self.n = n
n        self.t = [0] * (n + 1)
    
    def add(self, i, delta):
        while i <= self.n:
            self.t[i] += delta
            i += i & -i
    
    def sum(self, i):
        res = 0
        while i > 0:
            res += self.t[i]
            i -= i & -i
        return res
    
    def range_sum(self, l, r):
        return self.sum(r) - self.sum(l - 1)
```

**Go 版**
```go
type BIT struct {
    n int
    tree []int
}

func NewBIT(n int) *BIT {
    return &BIT{n: n, tree: make([]int, n+1)}
}

func (b *BIT) Add(i, delta int) {
    for i <= b.n {
        b.tree[i] += delta
        i += i & -i
    }
}

func (b *BIT) Sum(i int) int {
    res := 0
    for i > 0 {
        res += b.tree[i]
        i -= i & -i
    }
    return res
}
```

### LRU 缓存

**竞赛版 (Python)**
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)
```

**Rust 版**
```rust
use std::collections::HashMap;

pub struct LRUCache<K, V> {
    capacity: usize,
    cache: HashMap<K, V>,
    order: Vec<K>,
}

impl<K: Clone + Eq + std::hash::Hash, V> LRUCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            cache: HashMap::with_capacity(capacity),
            order: Vec::with_capacity(capacity),
        }
    }
    
    pub fn get(&mut self, key: &K) -> Option<&V> {
        if self.cache.contains_key(key) {
            let idx = self.order.iter().position(|k| k == key).unwrap();
            let k = self.order.remove(idx);
            self.order.push(k);
            self.cache.get(key)
        } else {
            None
        }
    }
    
    pub fn put(&mut self, key: K, value: V) {
        if self.cache.contains_key(&key) {
            let idx = self.order.iter().position(|k| k == &key).unwrap();
            self.order.remove(idx);
        } else if self.order.len() >= self.capacity {
            let k = self.order.remove(0);
            self.cache.remove(&k);
        }
        self.order.push(key.clone());
        self.cache.insert(key, value);
    }
}
```

## 查找算法

### 快速选择 (第 K 大/小)

**竞赛版 (Python)**
```python
import random

def quickselect(arr, k):
    """找第 k 小元素 (0-indexed)"""
    if len(arr) == 1:
        return arr[0]
    
    pivot = random.choice(arr)
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]
    
    if k < len(lows):
        return quickselect(lows, k)
    elif k < len(lows) + len(pivots):
        return pivots[0]
    else:
        return quickselect(highs, k - len(lows) - len(pivots))

# 找第 K 大
def find_kth_largest(arr, k):
    return quickselect(arr, len(arr) - k)
```

**工程版 (Python)**
```python
import random
from typing import List, TypeVar

T = TypeVar('T')

def quickselect(arr: List[T], k: int) -> T:
    """
    快速选择算法 - 找第 k 小元素 (0-indexed)
    平均时间复杂度: O(n), 最坏 O(n²)
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} 超出范围 [0, {len(arr)})")
    
    arr = arr.copy()
    
    def partition(left: int, right: int, pivot_idx: int) -> int:
        pivot = arr[pivot_idx]
        arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
        store_idx = left
        for i in range(left, right):
            if arr[i] < pivot:
                arr[store_idx], arr[i] = arr[i], arr[store_idx]
                store_idx += 1
        arr[right], arr[store_idx] = arr[store_idx], arr[right]
        return store_idx
    
    def select(left: int, right: int, k: int) -> T:
        if left == right:
            return arr[left]
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        if k == pivot_idx:
            return arr[k]
        elif k < pivot_idx:
            return select(left, pivot_idx - 1, k)
        else:
            return select(pivot_idx + 1, right, k)
    
    return select(0, len(arr) - 1, k)
```

### 二分查找

**竞赛版 (Python)**
```python
def bisect_left(arr, x):
    """第一个 >= x 的位置"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def bisect_right(arr, x):
    """第一个 > x 的位置"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

## 图论算法

### Dijkstra 最短路

**竞赛版 (Python)**
```python
import heapq

def dijkstra(graph, start):
    """
    graph: {u: [(v, weight), ...]}
    返回距离数组
    """
    n = len(graph)
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist
```

**Rust 版**
```rust
use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn dijkstra(graph: &[Vec<(usize, i64)>], start: usize) -> Vec<i64> {
    let n = graph.len();
    let mut dist = vec![i64::MAX; n];
    dist[start] = 0;
    let mut pq = BinaryHeap::new();
    pq.push(Reverse((0, start)));
    
    while let Some(Reverse((d, u))) = pq.pop() {
        if d > dist[u] {
            continue;
        }
        for &(v, w) in &graph[u] {
            let new_dist = d + w;
            if new_dist < dist[v] {
                dist[v] = new_dist;
                pq.push(Reverse((new_dist, v)));
            }
        }
    }
    dist
}
```

### 最小生成树 (Kruskal)

**竞赛版 (Python)**
```python
def kruskal(n, edges):
    """
    edges: [(weight, u, v), ...]
    返回 (总权重, MST边集)
    """
    edges.sort()
    uf = UF(n)
    mst_weight = 0
    mst_edges = []
    
    for w, u, v in edges:
        if uf.union(u, v):
            mst_weight += w
            mst_edges.append((u, v, w))
    
    return mst_weight, mst_edges
```

## 字符串算法

### KMP 字符串匹配

**竞赛版 (Python)**
```python
def kmp_search(text, pattern):
    """返回所有匹配起始位置"""
    if not pattern:
        return []
    
    # 构建部分匹配表
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    # 匹配
    result = []
    i = j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == len(pattern):
            result.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return result
```

**Go 版**
```go
func KMPSearch(text, pattern string) []int {
    if len(pattern) == 0 {
        return []int{}
    }
    
    // 构建 LPS 数组
    lps := make([]int, len(pattern))
    for i, length := 1, 0; i < len(pattern); {
        if pattern[i] == pattern[length] {
            length++
            lps[i] = length
            i++
        } else if length != 0 {
            length = lps[length-1]
        } else {
            lps[i] = 0
            i++
        }
    }
    
    // 匹配
    var result []int
    for i, j := 0, 0; i < len(text); {
        if pattern[j] == text[i] {
            i++
            j++
        }
        if j == len(pattern) {
            result = append(result, i-j)
            j = lps[j-1]
        } else if i < len(text) && pattern[j] != text[i] {
            if j != 0 {
                j = lps[j-1]
            } else {
                i++
            }
        }
    }
    return result
}
```

## 概率数据结构

### 布隆过滤器

**Python**
```python
import mmh3
import math

class BloomFilter:
    def __init__(self, capacity, error_rate=0.001):
        """
        capacity: 预期元素数量
        error_rate: 可接受的误报率
        """
        self.size = self._optimal_size(capacity, error_rate)
        self.hash_count = self._optimal_hash_count(self.size, capacity)
        self.bit_array = [0] * self.size
    
    def _optimal_size(self, n, p):
        return int(-(n * math.log(p)) / (math.log(2) ** 2))
    
    def _optimal_hash_count(self, m, n):
        return max(1, int((m / n) * math.log(2)))
    
    def add(self, item):
        for i in range(self.hash_count):
            idx = mmh3.hash(item, i) % self.size
            self.bit_array[idx] = 1
    
    def __contains__(self, item):
        return all(
            self.bit_array[mmh3.hash(item, i) % self.size]
            for i in range(self.hash_count)
        )
```

## 位运算技巧

### 常用操作

**Python**
```python
# 判断奇偶
is_odd = x & 1

# 除以 2
half = x >> 1

# 乘以 2
double = x << 1

# 最低位 1
lowbit = x & -x

# 去掉最低位 1
x &= x - 1

# 判断 2 的幂
is_power_of_2 = (x & (x - 1)) == 0 and x != 0

# 统计 1 的个数
count = x.bit_count()  # Python 3.10+
```

**C++**
```cpp
// 最低位 1
int lowbit(int x) { return x & -x; }

// 统计 1 的个数
int popcount(int x) { return __builtin_popcount(x); }

// 前导零个数
int clz(int x) { return __builtin_clz(x); }
```

## 性能优化模式

### 空间换时间

```python
# 前缀和 - 区间查询 O(1)
prefix = [0] * (n + 1)
for i in range(n):
    prefix[i+1] = prefix[i] + arr[i]
# query(l, r) = prefix[r+1] - prefix[l]

# 哈希预处理 - 快速查找
index_map = {v: i for i, v in enumerate(arr)}

# 打表预处理
MAX = 10**6 + 5
fac = [1] * MAX
for i in range(1, MAX):
    fac[i] = fac[i-1] * i % MOD
```

### 滚动数组

```python
# 只依赖前一行的 DP
dp = [0] * m
for i in range(n):
    new_dp = [0] * m
    for j in range(m):
        new_dp[j] = max(dp[j], new_dp[j-1]) + grid[i][j]
    dp = new_dp
```

## 语言特定优化

### Python 加速

```python
# 使用内置函数
sum(arr)  # 快于手动循环

# 列表推导
[x*2 for x in arr]  # 快于 map

# join 代替 +=
''.join(strings)  # 快于 result += s

# 局部变量缓存
append = list.append
for x in data:
    append(x)

# __slots__ 省内存
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x, self.y = x, y
```

### Rust 零成本抽象

```rust
// 迭代器链 - 零成本
let sum: i32 = (0..100)
    .filter(|x| x % 2 == 0)
    .map(|x| x * x)
    .sum();

// 常量泛型
fn array_sum<T: Default + Add<Output=T> + Copy, const N: usize>(arr: [T; N]) -> T {
    arr.iter().fold(T::default(), |acc, &x| acc + x)
}
```
