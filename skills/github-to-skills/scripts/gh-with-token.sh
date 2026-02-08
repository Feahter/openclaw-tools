#!/bin/bash
# GitHub CLI Wrapper - 自动使用凭证文件中的 Token

CREDENTIALS_FILE="$HOME/.openclaw/credentials/github.json"

if [ -f "$CREDENTIALS_FILE" ]; then
    export GH_TOKEN=$(python3 -c "import json; print(json.load(open('$CREDENTIALS_FILE')).get('GITHUB_TOKEN', ''))" 2>/dev/null)
fi

exec /usr/local/bin/gh "$@"
