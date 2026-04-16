#!/usr/bin/env python3
"""
gateway_health_checker.py — 飞书 Gateway 健康检查
检查 gateway-feishu.log 中最近消息的 reply 率
连续 2 次无 reply → 触发告警
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = Path.home() / ".openclaw/logs/gateway-feishu.log"
STATE_FILE = Path.home() / ".openclaw/workspace/.state/gateway-health-state.json"
ALERT_THRESHOLD_REPLY_RATE = 0.5  # reply rate below 50% = alert
ALERT_THRESHOLD_CONSECUTIVE = 2   # consecutive failures needed
LOOKBACK_MINUTES = 15              # check last 15 minutes
CHECK_INTERVAL_MINUTES = 5         # check every 5 minutes


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"consecutive_failures": 0, "last_check": None, "last_alert": None, "reply_rates": []}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_recent_log_lines():
    """读取最近 LOOKBACK_MINUTES 的日志行"""
    if not LOG_FILE.exists():
        return []

    cutoff = datetime.now() - timedelta(minutes=LOOKBACK_MINUTES)
    recent_lines = []
    cutoff_ts = cutoff.strftime("%Y-%m-%dT%H:%M")

    with open(LOG_FILE, errors="replace") as f:
        for line in f:
            # 提取时间戳
            m = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})", line)
            if m and m.group(1) >= cutoff_ts.replace("T", "T"):
                recent_lines.append(line.strip())
            elif m:
                log_time = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M")
                if log_time >= cutoff:
                    recent_lines.append(line.strip())
    return recent_lines


def parse_messages_and_replies(lines):
    """
    从日志解析：收到了多少消息，有多少收到了 reaction（reply）
    模式：
      - received message from ... → 收到消息
      - reaction event on message ... → 回复了消息
    返回：(total_received, total_replied, details)
    """
    received_ids = set()
    replied_ids = set()

    for line in lines:
        # 收到消息
        m = re.search(r"received message from [^ ]+ in .+ \((\w+)\)", line)
        if m:
            msg_id_m = re.search(r"message (om_\w+)", line)
            if msg_id_m:
                received_ids.add(msg_id_m.group(1))

        # reaction = reply
        if "reaction event on message" in line:
            msg_id_m = re.search(r"message (om_\w+)", line)
            if msg_id_m:
                replied_ids.add(msg_id_m.group(1))

    return len(received_ids), len(replied_ids & received_ids)


def check_health():
    state = load_state()
    lines = get_recent_log_lines()
    total, replied = parse_messages_and_replies(lines)

    if total == 0:
        # 没有消息，检查是否 gateway 还在运行
        # 检查是否有 channel status polling
        polling = any("channels.status" in l for l in lines)
        if not polling and len(lines) > 0:
            # 有日志但没有 polling，可能是 gateway 死了
            reply_rate = 0.0
        elif not polling:
            reply_rate = None  # 无法判断
        else:
            reply_rate = 1.0  # 有 polling，gateway 活着
    else:
        reply_rate = replied / total

    state["reply_rates"].append(reply_rate)
    state["reply_rates"] = state["reply_rates"][-10:]  # keep last 10
    state["last_check"] = datetime.now().isoformat()
    state["last_total"] = total
    state["last_replied"] = replied
    state["last_reply_rate"] = reply_rate

    # 判断是否需要告警
    should_alert = False
    if reply_rate is not None and reply_rate < ALERT_THRESHOLD_REPLY_RATE and total >= 2:
        state["consecutive_failures"] += 1
    else:
        state["consecutive_failures"] = 0

    if state["consecutive_failures"] >= ALERT_THRESHOLD_CONSECUTIVE:
        should_alert = True
        state["last_alert"] = datetime.now().isoformat()

    save_state(state)
    return {
        "ok": not should_alert,
        "reply_rate": reply_rate,
        "total": total,
        "replied": replied,
        "consecutive_failures": state["consecutive_failures"],
        "should_alert": should_alert,
        "last_check": state["last_check"],
        "last_alert": state.get("last_alert"),
    }


def send_alert(health):
    """通过飞书发送告警"""
    msg = (
        f"⚠️ **飞书 Gateway 告警**\n"
        f"时间：{health['last_check']}\n"
        f"最近15分钟：收到 {health['total']} 条消息\n"
        f"回复率：{health['reply_rate']:.0%}（阈值50%）\n"
        f"连续失败次数：{health['consecutive_failures']} / {ALERT_THRESHOLD_CONSECUTIVE}\n"
        f"最后告警：{health['last_alert'] or '首次'}\n\n"
        f"建议：检查 Gateway 进程 `openclaw gateway status`"
    )
    print(msg)
    return msg


if __name__ == "__main__":
    result = check_health()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["should_alert"]:
        alert_msg = send_alert(result)
        sys.exit(2)  # exit code 2 = alert triggered
    elif result["reply_rate"] is None:
        sys.exit(3)  # exit code 3 = unknown status
    else:
        sys.exit(0)  # exit code 0 = healthy
