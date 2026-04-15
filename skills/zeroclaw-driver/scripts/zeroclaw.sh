#!/bin/bash
# ZeroClaw Driver Helper Script

ZEROCLAW="${ZEROCLAW:-/Users/fuzhuo/.openclaw/workspace/zeroclaw/target/debug/zeroclaw}"
CONFIG_DIR="${HOME}/.zeroclaw"

# Ensure config exists
mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
    cat > "$CONFIG_DIR/config.toml" << 'EOF'
default_provider = "openrouter"
default_model = "anthropic/claude-sonnet-4-6"
default_temperature = 0.7

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"

[autonomy]
level = "supervised"
workspace_only = true
allowed_commands = ["git", "npm", "cargo", "ls", "cat", "grep", "find", "echo", "pwd", "wc", "head", "tail", "date", "curl"]
forbidden_paths = ["/etc", "/root", "/usr", "/bin", "/sbin", "/lib", "/opt", "/boot", "/dev", "/proc", "/sys", "/var", "/tmp"]
max_actions_per_hour = 100
max_cost_per_day_cents = 1000
require_approval_for_medium_risk = false
block_high_risk_commands = true

[runtime]
kind = "native"

[heartbeat]
enabled = true
interval_minutes = 30

[cron]
enabled = true
max_run_history = 50

[channels_config]
cli = true

[memory]
backend = "sqlite"
auto_save = true
hygiene_enabled = true
EOF
fi

CMD="${1:-status}"
shift 2>/dev/null || true

case "$CMD" in
    status)
        $ZEROCLAW status
        ;;
    start)
        $ZEROCLAW daemon &
        echo "ZeroClaw daemon started (PID: $!)"
        ;;
    stop)
        pkill -f "zeroclaw" 2>/dev/null || echo "No ZeroClaw process found"
        ;;
    agent)
        $ZEROCLAW agent
        ;;
    daemon)
        $ZEROCLAW daemon
        ;;
    providers)
        $ZEROCLAW providers
        ;;
    cron)
        $ZEROCLAW cron "${@}"
        ;;
    skills)
        $ZEROCLAW skills "${@}"
        ;;
    help|--help|-h)
        echo "Usage: zeroclaw-driver <command>"
        echo ""
        echo "Commands:"
        echo "  status     - Show ZeroClaw status"
        echo "  start      - Start daemon in background"
        echo "  stop       - Stop running ZeroClaw"
        echo "  agent      - Start interactive agent"
        echo "  daemon     - Start daemon (foreground)"
        echo "  providers  - List available providers"
        echo "  cron       - Manage cron tasks"
        echo "  skills     - Manage skills"
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Run 'zeroclaw-driver help' for usage"
        exit 1
        ;;
esac
