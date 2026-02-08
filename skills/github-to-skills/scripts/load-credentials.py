#!/usr/bin/env python3
"""
凭证加载器 - 为所有 GitHub 相关脚本提供统一的凭证访问
"""
import os
import json
from pathlib import Path

def get_github_token():
    """从凭证文件获取 GitHub Token"""
    credentials_file = Path.home() / ".openclaw" / "credentials" / "github.json"
    
    if credentials_file.exists():
        try:
            with open(credentials_file) as f:
                data = json.load(f)
                return data.get('GITHUB_TOKEN', '')
        except Exception:
            pass
    return os.environ.get('GITHUB_TOKEN', '')

def configure_git_credential():
    """配置 git 使用凭证"""
    token = get_github_token()
    if token:
        # 设置 git credential helper
        os.system('git config --global credential.helper store')
        # 添加 remote URL with token (临时方案)
        return token
    return None

if __name__ == "__main__":
    token = get_github_token()
    if token:
        print(f"✅ GitHub Token loaded: {token[:4]}...{token[-4:]}")
    else:
        print("❌ No GitHub Token found")
