# Eval-3: RecursiveRunner 自动重试机制演示

**执行时间:** 2026-03-17 22:53 (GMT+8)  
**技能路径:** `/Users/fuzhuo/.openclaw/workspace/skills/skill-evo-engine`  
**脚本:** `scripts/recursive_runner.py`

---

## 一、RecursiveRunner 工作原理

`RecursiveRunner` 是 skill-evo-engine 的核心模块，实现了带自我纠错的递归执行机制：

```
execute(input)
  → evaluator(result) → score (0.0–1.0)
      ≥ success_threshold (默认 0.8) → 返回成功
      < threshold → adjust_strategy(input, result, attempt) → 新 input → 重试
      达到 max_retries → 返回最佳结果
```

执行历史自动持久化到 `~/.openclaw/workspace/memory/skill-evo-logs.json`。

---

## 二、内置 Demo 运行结果（`recursive_runner.py` 直接执行）

```
==================================================
RecursiveRunner 测试
==================================================

  [执行] 第 1 次尝试...
  [调整] 尝试 #1: 第一次尝试失败
  [执行] 第 2 次尝试...

结果:
{
  "status": "success",
  "result": {
    "error": null,
    "data": "成功!",
    "items": [1, 2, 3]
  },
  "attempts": 2,
  "score": 1.0,
  "history": [
    {
      "attempt": 1,
      "timestamp": "2026-03-17T22:53:51.620562",
      "input": "{'test': 'data'}",
      "result": {"error": "第一次尝试失败", "data": null},
      "score": 0.0,
      "adjusted_input": "{'test': 'data', '_retry_count': 1, '_last_error': '第一次尝试失败'}"
    },
    {
      "attempt": 2,
      "timestamp": "2026-03-17T22:53:51.620896",
      "input": "{'test': 'data', '_retry_count': 1, '_last_error': '第一次尝试失败'}",
      "result": {"error": null, "data": "成功!", "items": [1, 2, 3]},
      "score": 1.0
    }
  ]
}
```

### 内置 Demo 关键指标

| 指标 | 值 |
|------|-----|
| 状态 | ✅ SUCCESS |
| 总尝试次数 | 2 |
| 第 1 次得分 | 0.0（失败） |
| 第 2 次得分 | 1.0（成功） |
| 最终得分 | 1.0 |

---

## 三、自定义演示：`flaky_skill`（先失败再成功）

### 演示代码

```python
from scripts.recursive_runner import RecursiveRunner

attempt_counter = {"n": 0}

def flaky_skill(input_data: dict) -> dict:
    """模拟不稳定技能：第1次超时失败，第2次成功"""
    attempt_counter["n"] += 1
    n = attempt_counter["n"]
    if n == 1:
        return {"error": "网络超时，请重试", "data": None}
    return {"error": None, "data": f"任务完成！共处理 {input_data.get('items', 0)} 条记录"}

def my_evaluator(result: dict) -> float:
    return 0.0 if result.get("error") else 1.0

def my_adjuster(input_data: dict, last_result: dict, attempt: int) -> dict:
    adjusted = dict(input_data)
    adjusted["_retry_attempt"] = attempt + 1
    adjusted["_last_error"] = last_result.get("error", "unknown")
    return adjusted

runner = RecursiveRunner(max_retries=3, success_threshold=0.8)
result = runner.run(
    skill_executor=flaky_skill,
    input_data={"task": "process_records", "items": 42},
    evaluator=my_evaluator,
    adjust_strategy=my_adjuster
)
```

### 运行输出

```
============================================================
RecursiveRunner 自定义演示：先失败再成功
============================================================

初始输入: {'task': 'process_records', 'items': 42}
最大重试次数: 3  |  成功阈值: 0.8

    → flaky_skill 内部执行第 1 次 | input keys: ['task', 'items']
    → 评估得分: 0.0  (error='网络超时，请重试')
    → 策略调整: 注入 _retry_attempt=1, _last_error='网络超时，请重试'
    → flaky_skill 内部执行第 2 次 | input keys: ['task', 'items', '_retry_attempt', '_last_error']
    → 评估得分: 1.0  (error=None)

============================================================
最终结果摘要
============================================================
  状态      : SUCCESS
  总尝试次数: 2
  最终得分  : 1.0
  返回数据  : 任务完成！共处理 42 条记录

执行历史:
  ❌ 第 1 次  得分=0.0  error='网络超时，请重试'
  ✅ 第 2 次  得分=1.0  error=None
```

### 自定义演示关键指标

| 指标 | 值 |
|------|-----|
| 状态 | ✅ SUCCESS |
| 总尝试次数 | **2**（最大允许 3） |
| 第 1 次得分 | **0.0**（网络超时，失败） |
| 第 2 次得分 | **1.0**（成功） |
| 最终得分 | **1.0** |
| 策略调整 | 将错误信息注入下次输入（`_retry_attempt`, `_last_error`） |

---

## 四、累计执行统计（来自持久化日志）

```json
{
  "total_runs": 8,
  "success": 5,
  "failed": 3,
  "success_rate": 0.625
}
```

---

## 五、结论

`RecursiveRunner` 的自动重试机制工作正常：

1. **第 1 次执行** → 技能返回错误 → 评估得分 `0.0` < 阈值 `0.8` → 触发策略调整
2. **策略调整** → 将错误信息（`_last_error`）和重试计数（`_retry_attempt`）注入新输入
3. **第 2 次执行** → 技能成功 → 评估得分 `1.0` ≥ 阈值 `0.8` → 立即返回，不再重试
4. **执行历史** 完整记录每次尝试的输入、输出、得分，并持久化到日志文件

整个流程无需人工干预，完全自动化。
