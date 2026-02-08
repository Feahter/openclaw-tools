#!/bin/bash
# agent-commander 辅助脚本

# 查看当前会话状态
status() {
    openclaw session_status 2>/dev/null || echo "无法获取会话状态"
}

# 列出所有会话
list() {
    echo "📋 会话列表:"
    openclaw sessions_list --kinds main,sub-agent --limit 20
}

# 创建子会话
spawn() {
    local task="$1"
    local label="${2:-task-$(date +%s)}"
    local model="${3:-}"
    
    if [ -z "$task" ]; then
        echo "用法: spawn <任务描述> [标签] [模型]"
        return 1
    fi
    
    echo "🚀 启动子会话: $label"
    echo "📝 任务: $task"
    [ -n "$model" ] && echo "🤖 模型: $model"
    
    # 返回创建命令（实际执行需要通过 OpenClaw CLI）
    echo ""
    echo "请在 OpenClaw 中执行:"
    echo "sessions_spawn --task \"$task\" --label \"$label\"${model:+ --model $model}"
}

# 发送消息到会话
send() {
    local session="$1"
    local msg="$2"
    
    if [ -z "$session" ] || [ -z "$msg" ]; then
        echo "用法: send <会话key> <消息>"
        return 1
    fi
    
    echo "📨 发送消息到 $session:"
    echo "$msg"
    echo ""
    echo "请在 OpenClaw 中执行:"
    echo "sessions_send \"$session\" \"$msg\""
}

# 监控会话
monitor() {
    local session="${1:-main}"
    echo "👁️ 监控会话: $session"
    openclaw sessions_history --sessionKey "$session" --limit 20 --includeTools
}

# 上下文检查
check_context() {
    echo "🔍 上下文检查:"
    status | grep -E "Tokens|Context" || echo "无法解析上下文信息"
}

# 主入口
case "$1" in
    status|list|spawn|send|monitor|check)
        "$1" "${@:2}"
        ;;
    *)
        echo "Agent Commander - 会话管理工具"
        echo ""
        echo "用法: $0 <命令> [参数]"
        echo ""
        echo "命令:"
        echo "  status       查看当前会话状态"
        echo "  list         列出所有会话"
        echo "  spawn <任务> [标签] [模型]  创建子会话"
        echo "  send <会话> <消息>         发送消息"
        echo "  monitor [会话]              监控会话历史"
        echo "  check                      检查上下文使用"
        ;;
esac
