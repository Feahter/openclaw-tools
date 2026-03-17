# eval-3-recursive-runner — Without Skill: Result

## Task
用 recursive-runner 执行一个会先失败再成功的任务，展示自动重试机制。

---

## Approach
Wrote a Python retry mechanism **from scratch** (no skill files used).

- `flaky_task()` — a function that raises `RuntimeError` on the first call and returns success on the second.
- `recursive_runner()` — a recursive function that retries the task up to `max_retries` times, waiting `delay` seconds between attempts.

---

## Source Code

```python
"""
Retry Mechanism Demo — fails on first call, succeeds on second.
Simulates the "recursive-runner" auto-retry pattern from scratch.
"""

import time

# --- State tracker (simulates a flaky external service) ---
call_count = 0


def flaky_task():
    """A task that fails on the first attempt and succeeds on the second."""
    global call_count
    call_count += 1
    print(f"  [Attempt {call_count}] Running task...")

    if call_count == 1:
        raise RuntimeError("Transient error: service temporarily unavailable")

    # Second call succeeds
    return "✅ Task completed successfully!"


# --- Recursive runner with auto-retry ---
def recursive_runner(task_fn, max_retries=3, delay=0.5, attempt=1):
    """
    Recursively retries task_fn up to max_retries times.
    Each retry waits `delay` seconds before trying again.
    """
    print(f"\n[recursive_runner] Attempt {attempt}/{max_retries}")
    try:
        result = task_fn()
        print(f"[recursive_runner] ✅ Success on attempt {attempt}: {result}")
        return result
    except Exception as e:
        print(f"[recursive_runner] ❌ Attempt {attempt} failed: {e}")
        if attempt >= max_retries:
            print(f"[recursive_runner] 🚫 Max retries ({max_retries}) reached. Giving up.")
            raise
        print(f"[recursive_runner] ⏳ Waiting {delay}s before retry...")
        time.sleep(delay)
        return recursive_runner(task_fn, max_retries=max_retries, delay=delay, attempt=attempt + 1)


# --- Run the demo ---
if __name__ == "__main__":
    print("=" * 55)
    print("  recursive-runner: Auto-Retry Mechanism Demo")
    print("=" * 55)
    print("\nTask: flaky_task() — fails on attempt 1, succeeds on attempt 2")

    try:
        final_result = recursive_runner(flaky_task, max_retries=3, delay=0.3)
        print(f"\n[FINAL RESULT] {final_result}")
    except Exception as e:
        print(f"\n[FINAL RESULT] Task ultimately failed: {e}")

    print("\n" + "=" * 55)
    print(f"  Total calls made: {call_count}")
    print("=" * 55)
```

---

## Execution Output

```
=======================================================
  recursive-runner: Auto-Retry Mechanism Demo
=======================================================

Task: flaky_task() — fails on attempt 1, succeeds on attempt 2

[recursive_runner] Attempt 1/3
  [Attempt 1] Running task...
[recursive_runner] ❌ Attempt 1 failed: Transient error: service temporarily unavailable
[recursive_runner] ⏳ Waiting 0.3s before retry...

[recursive_runner] Attempt 2/3
  [Attempt 2] Running task...
[recursive_runner] ✅ Success on attempt 2: ✅ Task completed successfully!

[FINAL RESULT] ✅ Task completed successfully!

=======================================================
  Total calls made: 2
=======================================================
```

---

## Summary

| Metric | Value |
|---|---|
| Approach | Hand-written recursive retry (no skill) |
| Total attempts | 2 |
| Failure on attempt | 1 (RuntimeError) |
| Success on attempt | 2 |
| Max retries configured | 3 |
| Retry delay | 0.3s |
| Final result | ✅ Task completed successfully! |

**Verdict:** The retry mechanism works correctly. The task failed on attempt 1 with a transient error, and the recursive runner automatically retried, succeeding on attempt 2 — demonstrating the auto-retry pattern without any skill dependency.
