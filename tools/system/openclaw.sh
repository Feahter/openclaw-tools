#!/bin/bash
#
# OpenClaw 工具集一键启动
# 支持后台启动和前台查看
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查端口是否运行
check_port() {
    local port=$1
    if curl -s "http://localhost:$port/api/status" > /dev/null 2>&1 || \
       curl -s "http://localhost:$port" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 打印状态
print_status() {
    local port=$1
    local name=$2
    if check_port $port; then
        echo -e "  ${GREEN}✓${NC} $name : http://localhost:$port"
    else
        echo -e "  ${RED}✗${NC} $name : http://localhost:$port (未运行)"
    fi
}

start_all() {
    echo -e "${BLUE}🚀 启动 OpenClaw 工具集...${NC}\n"
    
    # 启动主服务
    cd "$TOOLS_DIR"
    python3 local-model-manager.py &
    
    # 等待启动
    sleep 3
    
    echo -e "${GREEN}✅ 启动完成！${NC}\n"
    echo -e "${YELLOW}📊 服务状态:${NC}"
    print_status 8765 "统一控制台"
    print_status 8799 "模型管理"
    print_status 8769 "任务看板"
    print_status 8770 "Token统计"
    print_status 8771 "自动化"
    
    echo ""
    echo -e "${BLUE}🌐 访问地址:${NC}"
    echo "  统一控制台: http://localhost:8765"
    echo "  模型管理:   http://localhost:8799"
    echo "  任务看板:   http://localhost:8769"
    echo ""
}

status() {
    echo -e "${BLUE}📊 OpenClaw 服务状态${NC}\n"
    print_status 8765 "统一控制台"
    print_status 8768 "模型管理"
    print_status 8769 "任务看板"
    print_status 8770 "Token统计"
    print_status 8771 "自动化"
}

stop_all() {
    echo -e "${YELLOW}🛑 停止所有服务...${NC}"
    pkill -f "local-model-manager.py\|task-board.py\|token-stats.py\|automation-workflow.py\|unified-console.py\|api-auto-switch.py" 2>/dev/null || true
    echo -e "${GREEN}✅ 已停止${NC}"
}

restart_all() {
    stop_all
    sleep 1
    start_all
}

# 主命令
case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status
        ;;
    *)
        echo -e "${BLUE}OpenClaw 工具集管理${NC}"
        echo ""
        echo "用法: $0 {start|stop|restart|status}"
        echo ""
        echo "命令:"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo ""
        ;;
esac
