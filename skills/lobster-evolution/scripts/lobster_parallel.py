#!/usr/bin/env python3
"""
lobster_parallel.py — lobster-evolution 并行执行引擎

【算法优化 v2】从顺序执行 → DAG并行：
- 旧：5个分析脚本顺序执行，总时间 = sum(各脚本)
- 新：DAG依赖分析 + 并行执行，总时间 = max(关键路径)

依赖关系：
  session-miner (独立) ──┐
                          ├──> skill-proposer ──> evolution-summary
  skill-health (独立) ──┤
  user-preference (独立) ──┘

依赖分析：
  Phase 1（并行）：session-miner + skill-health + user-preference
  Phase 2（顺序）：skill-proposer（依赖 Phase 1 结果）
  Phase 3（并行）：evolution-summary（依赖 Phase 2 结果）
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SKILLS_DIR = Path.home() / ".openclaw/workspace/skills/lobster-evolution/scripts"
STATE_DIR = Path.home() / ".openclaw/workspace/.state/evolution"
STATE_DIR.mkdir(parents=True, exist_ok=True)


async def run_script(name: str, script: str, timeout: int = 300) -> dict[str, Any]:
    """异步运行单个脚本，带超时保护"""
    t0 = time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            "python3", str(script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        elapsed = time.time() - t0
        return {
            "name": name,
            "script": str(script),
            "ok": proc.returncode == 0,
            "elapsed": elapsed,
            "stdout": stdout.decode("utf-8", errors="ignore")[:500],
            "stderr": stderr.decode("utf-8", errors="ignore")[:500],
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"name": name, "ok": False, "elapsed": time.time() - t0, "error": "timeout"}
    except Exception as e:
        return {"name": name, "ok": False, "elapsed": time.time() - t0, "error": str(e)}


async def run_phase1_parallel():
    """Phase 1：三个独立脚本并行执行"""
    scripts = [
        ("session-miner", SKILLS_DIR / "session-miner.py"),
        ("skill-health", SKILLS_DIR / "skill-health-monitor.py"),
        ("user-preference", SKILLS_DIR / "user-preference-profile.py"),
    ]
    tasks = [run_script(name, script) for name, script in scripts if script.exists()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {r["name"]: r for r in results if isinstance(r, dict)}


async def run_phase2_sequential():
    """Phase 2：按顺序执行（依赖 Phase 1 结果）"""
    proposer = SKILLS_DIR / "skill-proposer.py"
    if not proposer.exists():
        return {}
    result = await run_script("skill-proposer", proposer)
    return {"skill-proposer": result}


async def run_phase3_parallel():
    """Phase 3：汇总脚本并行（依赖 Phase 2）"""
    scripts = [
        ("self-healer", SKILLS_DIR / "self-healer.py"),
        ("evolution-summary", SKILLS_DIR / "evolution-summary.py"),
    ]
    tasks = [run_script(name, script) for name, script in scripts if script.exists()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {r["name"]: r for r in results if isinstance(r, dict)}


def report_summary(results: dict, total_time: float):
    """生成并行执行报告"""
    lines = ["## lobster-evolution 并行执行报告", ""]
    for name, r in results.items():
        icon = "✅" if r.get("ok") else "❌"
        elapsed = r.get("elapsed", 0)
        err = r.get("error", "")
        lines.append(f"{icon} **{name}** — {elapsed:.1f}s" + (f" | {err}" if err else ""))
    lines.append(f"**总耗时**：{total_time:.1f}s（并行优化 vs {sum(r.get('elapsed',0) for r in results.values()):.1f}s顺序）")
    return "\n".join(lines)


async def main():
    print("🕸️ lobster-evolution 并行执行引擎 v2")
    print(f"Phase 1: 3个脚本并行...")
    t0 = time.time()

    # Phase 1: 并行
    phase1 = await run_phase1_parallel()
    phase1_time = time.time() - t0
    print(f"Phase 1 完成 ({phase1_time:.1f}s)")

    # Phase 2: 顺序
    t2 = time.time()
    phase2 = await run_phase2_sequential()
    phase2_time = time.time() - t2
    print(f"Phase 2 完成 ({phase2_time:.1f}s)")

    # Phase 3: 并行
    t3 = time.time()
    phase3 = await run_phase3_parallel()
    phase3_time = time.time() - t3
    print(f"Phase 3 完成 ({phase3_time:.1f}s)")

    all_results = {**phase1, **phase2, **phase3}
    total = time.time() - t0
    summary = report_summary(all_results, total)
    print(f"\n{summary}")

    # 写入状态文件
    (STATE_DIR / "parallel-report.md").write_text(summary)
    return all_results


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if all(r.get("ok") for r in result.values()) else 1)
