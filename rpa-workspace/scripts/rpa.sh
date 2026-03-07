#!/bin/bash
# OpenClaw RPA CLI - 基于 browser-use CLI 的浏览器自动化
# 用法: ./rpa.sh [command] [args...]

RPA_DIR="$HOME/rpa-workspace"
SCREENSHOTS="$RPA_DIR/screenshots"
LOGS="$RPA_DIR/logs"

# 确保目录存在
mkdir -p "$SCREENSHOTS" "$LOGS"

# 设置 PATH
export PATH="$HOME/Library/Python/3.13/bin:$PATH"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[RPA]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGS/rpa_$(date +%Y%m%d).log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOGS/rpa_$(date +%Y%m%d).log"
}

# 打开网页
open_url() {
    local url=$1
    log "打开网页: $url"
    browser-use --browser real --profile Default open "$url"
}

# 点击元素
click_element() {
    local index=$1
    log "点击元素: $index"
    browser-use --session default click "$index"
}

# 输入文字
type_text() {
    local index=$1
    local text=$2
    log "输入文字到 $index: $text"
    browser-use --session default input "$index" "$text"
}

# 截图
take_screenshot() {
    local name=${1:-"screenshot_$(date +%Y%m%d_%H%M%S)"}
    local path="$SCREENSHOTS/${name}.png"
    log "截图: $path"
    browser-use --session default screenshot "$path"
    echo "$path"
}

# 获取页面状态
get_state() {
    browser-use --session default state
}

# 发送键盘按键
send_keys() {
    local keys=$1
    log "发送按键: $keys"
    browser-use --session default keys "$keys"
}

# 滚动页面
scroll_page() {
    local direction=$1
    local amount=${2:-500}
    log "滚动 $direction: $amount"
    browser-use --session default scroll "$direction" --amount "$amount"
}

# 等待并截图
wait_and_screenshot() {
    local seconds=$1
    local name=${2:-"wait_$(date +%Y%m%d_%H%M%S)"}
    log "等待 ${seconds}秒..."
    sleep "$seconds"
    take_screenshot "$name"
}

# 运行自定义任务
run_task() {
    local task_name=$1
    local script_file="$RPA_DIR/scripts/${task_name}.sh"
    
    if [ -f "$script_file" ]; then
        log "执行任务脚本: $task_name"
        bash "$script_file"
    else
        error "任务脚本不存在: $script_file"
        return 1
    fi
}

# 列出可用任务
list_tasks() {
    log "可用任务:"
    ls -1 "$RPA_DIR/scripts/" 2>/dev/null | grep -v "^_" | head -20
}

# 帮助
show_help() {
    echo "OpenClaw RPA CLI"
    echo ""
    echo "用法: rpa.sh [command] [args...]"
    echo ""
    echo "命令:"
    echo "  open <url>              打开网页"
    echo "  click <index>           点击元素"
    echo "  type <index> <text>     输入文字"
    echo "  screenshot [name]      截图"
    echo "  state                   获取页面状态"
    echo "  keys <keys>             发送按键"
    echo "  scroll <up|down> [px]  滚动"
    echo "  wait <seconds> [name]  等待并截图"
    echo "  run <task>             运行任务脚本"
    echo "  list                   列出可用任务"
    echo "  help                   显示帮助"
    echo ""
    echo "示例:"
    echo "  rpa.sh open https://baidu.com"
    echo "  rpa.sh screenshot baidu_home"
    echo "  rpa.sh run my_task"
}

# 主命令处理
case "$1" in
    open)
        open_url "$2"
        ;;
    click)
        click_element "$2"
        ;;
    type)
        type_text "$2" "$3"
        ;;
    screenshot)
        take_screenshot "$2"
        ;;
    state)
        get_state
        ;;
    keys)
        send_keys "$2"
        ;;
    scroll)
        scroll_page "$2" "$3"
        ;;
    wait)
        wait_and_screenshot "$2" "$3"
        ;;
    run)
        run_task "$2"
        ;;
    list)
        list_tasks
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
