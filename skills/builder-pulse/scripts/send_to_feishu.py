#!/usr/bin/env python3
"""
send_to_feishu.py — 发送 BuilderPulse 日报到飞书
"""

import urllib.request
import json
import sys
import os

def read_report(date):
    """读取日报"""
    path = f"/tmp/builder-pulse-{date}.md"
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def send_to_feishu(content, feishu_token):
    """发送消息到飞书"""
    url = "https://open.feishu.cn/open-apis/bot/v2/hook/" + feishu_token
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": "🤖 BuilderPulse 日报已生成，点击查看：\n" + content[:100] + "..."
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def main():
    date = sys.argv[1] if len(sys.argv) > 1 else "2026-04-16"
    token_file = os.path.expanduser("~/.openclaw/credentials/feishu-webhook.json")
    
    if not os.path.exists(token_file):
        print("❌ 未找到飞书 webhook 配置")
        sys.exit(1)
    
    with open(token_file, 'r') as f:
        token = json.load(f).get('webhook_token', '')
    
    content = read_report(date)
    if not content:
        print(f"❌ 未找到 {date} 的日报")
        sys.exit(1)
    
    result = send_to_feishu(content, token)
    print("✅ 发送成功" if result.get('code') == 0 else f"❌ 发送失败: {result}")

if __name__ == '__main__':
    main()
