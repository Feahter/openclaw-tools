# 完整算法代码库

## 目录

- [并查集 (Union-Find)](#并查集-union-find)
- [线段树 (Segment Tree)](#线段树-segment-tree)
- [树状数组 (Fenwick Tree)](#树状数组-fenwick-tree)
- [堆 (Heap)](#堆-heap)
- [LRU 缓存](#lru-缓存)
- [快速选择 (QuickSelect)](#快速选择-quickselect)
- [字符串匹配 KMP](#字符串匹配-kmp)
- [Dijkstra 最短路](#dijkstra-最短路)
- [Kruskal 最小生成树](#kruskal-最小生成树)
- [Leiden 社区检测](#leiden-社区检测)

---

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


---

## 社区检测算法

### Leiden 算法

**用途**：在大规模图上高效检测连通社区，比 Louvain 更优（无孤立节点）。

**核心思想**：三阶段迭代（移动→精细化→缩放），保证每个社区内部连通。

**算法定性**
```
| 维度 | 分析 |
|------|------|
| 本质 | Louvain + 精细化 + 超图缩放 |
| 核心思想 | Phase1 粗分 → Phase2 细化社区内部 → Phase3 压缩图继续迭代 |
| 时间复杂度 | O(n log n) |
| 空间复杂度 | O(n + m) |
| 解决什么问题 | Louvain 产生的孤立节点和悬挂社区 |
```

**与 Louvain 对比**
```
┌─────────────────┬────────────────────┬─────────────────┐
│ 经典算法        │ 相似点             │ 改进点          │
├─────────────────┼────────────────────┼─────────────────┤
│ Louvain         │ 模块度优化         │ 孤立节点问题    │
│ Leiden          │ 局部移动 + 聚合    │ +精细化 + 超图  │
└─────────────────┴────────────────────┴─────────────────┘
```

**Leiden 三阶段伪代码**
```python
def leiden(graph):
    # Phase 1: Locally move nodes (standard Louvain)
    partition = louvain_phase1(graph)

    while True:
        # Phase 2: Refinement — only move within communities
        refined = refine_within_communities(partition)

        # Phase 3: Zoom-out — compress refined into supernodes
        supergraph = compress_to_supernodes(refined)

        if supergraph.has_improved():
            graph = supergraph
        else:
            return refined

def refine_within_communities(partition):
    # 1. Sort nodes by community (range grouping)
    sorted_nodes = group_by_community(partition)
    # 2. For each community subrange, run local move
    for community_range in get_ranges(sorted_nodes):
        merge_nodes_subset(community_range)
    return refined_partition

def merge_nodes_subset(start, stop):
    # Only consider moves within [start, stop)
    # Guarantees nodes never leave their community
    current = identify_micro_communities(start, stop)
    for node in range(start, stop):
        best = find_best_community(node, current)
        move(node, best)
```

**核心公式 — 模块度增益**
```
ΔQ = (k_i_in / 2m) - (Σ_tot / (2m)²) × k_i

其中:
- k_i_in：节点 i 到目标社区的边权重和
- m：图中所有边权重和
- Σ_tot：目标社区所有边的权重和
- k_i：节点 i 的度（包含自环）
```

**关键数据结构**
```python
# 稀疏映射 — 只存储非零权重，避免 O(n) 稀疏数组
SparseMap<community_id, weight>  # 社区权重表

# 稀疏队列 — O(1) 入队出队 + 随机遍历
SparseQueueSet  # 随机游走遍历节点

# 节点排序数组 — 按社区 ID 连续存储
nodes_sorted_by_community  # 用于区间操作 merge_nodes_subset
communities_bounds         # 每个社区的起止索引
```

**使用 graphology（推荐）**
```javascript
import Graph from 'graphology';
import leiden from 'graphology-communities-leiden'; // 或 vendored 版本

const graph = new Graph();
graph.addEdge('A', 'B');
graph.addEdge('B', 'C');
graph.addEdge('D', 'E');

const communities = leiden(graph, {
  resolution: 0.1,    // <1 更多小区，>1 更少大区
  randomness: 0.01,   // 精细化随机性
  randomWalk: true,   // 随机顺序遍历
});

// communities: Map<nodeId, communityId>
```

**Python 最小实现（原理版）**
```python
# Leiden 本质 = Louvain + refine + zoom-out
# 核心在 refine：节点只在社区内部移动，保证连通性

def leiden_simple(adj_list, resolution=1.0):
    # Phase 1: Louvain 粗分
    communities = louvain(adj_list, resolution)

    # Phase 2: 精细化（只在社区内）
    refined = {}
    for node, comm in communities.items():
        # 构建子图，只在社区内部找更好的位置
        local_neighbors = {n: adj_list[n] for n in nodes_in(comm)}
        best = find_local_optimum(node, local_neighbors, resolution)
        refined[node] = best

    # Phase 3: 压缩超图继续迭代
    supergraph = build_supernode_graph(refined, adj_list)
    if improved(refined, supergraph):
        return leiden_simple(supergraph, resolution)
    return refined
```

**Leiden 评价**
```
| 指标         │ 评分    │ 说明                          |
|--------------|---------|-------------------------------|
| 连通性保证   │ ⭐⭐⭐⭐⭐ | 三阶段设计保证无孤立节点      |
| 时间复杂度   │ ⭐⭐⭐⭐  | O(n log n)，比 Louvain 略快    |
| 简洁性       │ ⭐⭐⭐    | 比 Louvain 复杂（3阶段）       |
| 调参难度     │ ⭐⭐⭐    | resolution 和 randomness 敏感  |
| 工程成熟度   │ ⭐⭐⭐⭐  | graphology 有完整实现          |
```

**Leiden 适用场景**
| 场景 | 边权重设计 |
|------|-----------|
| 代码依赖社区 | CALLS 边权重 = 1 |
| 社交网络好友分组 | 互动频率 |
| 推荐系统协同过滤 | 用户-物品评分 |
| 知识图谱概念归类 | 实体关系类型权重 |
```


---

## 竞赛算法口诀（Kimi OI/ACM 速查）

*来源：Kimi 算法概念速览 | 2026-04-08*

### 口诀原文
```
区间更新线段树  连通分量并查集  缩点重建强连通
有向无环拓扑排  大数越界高精度  递归爆栈改迭代
最长回文马拉车  无序查找哈希表  有序查找平衡树
区间求和削缀和  有序问题上二分  最值问题搞个堆
```

### 1. 线段树 + 懒标记 (Segment Tree + Lazy Propagation)
| 维度 | 内容 |
|------|------|
| **用途** | 区间修改（加/乘/覆盖）+ 区间查询（和/最值） |
| **复杂度** | O(log n) 单次操作 |
| **核心** | 懒标记延迟下传，避免更新到叶子节点 |
| **模板题** | 区间加+区间求和，动态 RMQ |

### 2. 并查集 (Union-Find) — 已有，详见上方

### 3. 强连通分量缩点 (SCC / Tarjan)
| 维度 | 内容 |
|------|------|
| **算法** | Tarjan（一次 DFS）或 Kosaraju（两次 DFS） |
| **核心** | low-link 值判断割点，同一 SCC 内节点可互达 |
| **缩点** | 每个 SCC 压缩为 DAG 上的单个节点 |
| **应用** | 2-SAT，必经点查询，图中环检测 |

```python
# Tarjan SCC（竞赛版）
def tarjan(u):
    dfn[u] = low[u] = ++timer
    stack.append(u)
    for v in g[u]:
        if not dfn[v]:
            tarjan(v)
            low[u] = min(low[u], low[v])
        elif v in stack:
            low[u] = min(low[u], dfn[v])
    if low[u] == dfn[u]:
        # 弹出栈形成SCC
        while True:
            w = stack.pop()
            scc.append(w)
            if w == u: break
```

### 4. 拓扑排序 (Topological Sort)
| 维度 | 内容 |
|------|------|
| **前提** | 仅 DAG（有向无环图） |
| **Kahn** | BFS，入度为 0 入队 |
| **DFS 版** | 后序遍历逆序输出 |
| **应用** | 任务调度、环检测、DAG 上 DP |

### 5. 高精度计算 (Big Integer)
| 维度 | 内容 |
|------|------|
| **场景** | 数值超 long long 范围（>10^18） |
| **实现** | 数组/字符串模拟竖式运算 |
| **优化** | FFT/NTT 加速乘法 O(n log n)，压位（4位/9位一存） |

### 6. 递归改迭代 (Stack Overflow)
| 维度 | 内容 |
|------|------|
| **问题** | 递归深度 > 10^5 导致栈溢出 |
| **方案** | 显式栈模拟递归，或改 BFS |
| **Morris** | 遍历二叉树不使用栈和递归 |

### 7. Manacher 算法 (最长回文)
| 维度 | 内容 |
|------|------|
| **功能** | O(n) 求最长回文子串长度+位置 |
| **核心** | 维护最右回文边界 R， 利用对称性 |
| **预处理** | 插入分隔符（#）统一奇偶长度 |

```python
# Manacher 竞赛版
s = '#' + '#'.join(t) + '#'
p = [0] * len(s)
c = r = 0
for i in range(len(s)):
    p[i] = min(p[2*c-i], r-i) if i < r else 1
    while i-p[i] >= 0 and i+p[i] < len(s) and s[i-p[i]] == s[i+p[i]]:
        p[i] += 1
    if i + p[i] > r:
        c, r = i, i + p[i]
return max(p) - 1  # 最长回文长度
```

### 8. 哈希表 — 已有，详见上方

### 9. 平衡二叉搜索树 (Balanced BST)
| 类型 | 特点 |
|------|------|
| **AVL** | 严格平衡，高度差≤1 |
| **Treap** | 期望平衡，代码简单，支持分裂合并 |
| **Splay** | 访问即旋转到根 |
| **红黑树** | C++ std::map/set |
| **FHQ-Treap** | 无旋Treap，支持区间操作+持久化 |

### 10. 前缀和 + 差分 — 已有，详见上方

### 11. 二分查找 — 已有，详见上方

### 12. 堆 (Heap) — 已有，详见上方

### 口诀规律总结
| 句式 | 含义 |
|------|------|
| "搞个/削/改" | 优化手段（堆优化、前缀和、递归改迭代） |
| "上/搞" | 适用场景（有序上二分、最值搞堆） |
| "重建/缩点" | 图论建模（SCC缩点、DAG重建） |

### 竞赛思维
遇到区间操作 → 线段树/前缀和
遇到连通性 → 并查集
遇到回文 → Manacher
遇到最值 → 堆/单调栈
遇到有序 → 二分
