# 完整算法代码库

## 数据结构实现

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
        self.t = [0] * (n + 1)
    
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

**工程版 (Python)**
```python
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class Node:
    key: int
    val: int
    prev: Optional['Node'] = None
    next: Optional['Node'] = None

class LRUCache:
    """LRU 缓存 - 哈希 + 双向链表"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[int, Node] = {}
        self.head = Node(0, 0)  # 哑节点
        self.tail = Node(0, 0)  # 哑节点
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add(node)
        return node.val
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._add(node)
        if len(self.cache) > self.capacity:
            lru = self.head.next
            self._remove(lru)
            del self.cache[lru.key]
    
    def _remove(self, node: Node) -> None:
        prev, nxt = node.prev, node.next
        prev.next = nxt
        nxt.prev = prev
    
    def _add(self, node: Node) -> None:
        prev = self.tail.prev
        prev.next = node
        node.prev = prev
        node.next = self.tail
        self.tail.prev = node
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

---

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

