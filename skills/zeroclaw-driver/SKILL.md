---
name: zeroclaw-driver
description: "Driver for ZeroClaw - a lightweight Rust-based AI agent runtime. Use this skill whenever: (1) User wants to run a lightweight AI assistant that uses minimal memory (under 5MB), (2) Need fast cold-start agent (under 10ms) for quick queries, (3) Running simple automated tasks in background with cron/heartbeat, (4) Using local AI models (Ollama, LM Studio, llama.cpp) for offline or cost-effective inference, (5) User mentions lightweight alternative to OpenClaw or wants to save resources, (6) Low-memory environment deployment like Raspberry Pi or edge devices, (7) User wants to test AI tasks without full OpenClaw overhead."
---

# ZeroClaw Driver

## Overview

ZeroClaw is a lightweight Rust-based AI agent runtime (~8MB binary, <5MB RAM). This skill provides commands to control ZeroClaw for lightweight AI tasks that don't need the full power of OpenClaw.

## Compatibility

- **Binary location**: `/Users/fuzhuo/.openclaw/workspace/zeroclaw/target/debug/zeroclaw`
- **Config path**: `~/.zeroclaw/config.toml`
- **Required**: Rust binary, ZeroClaw installed at above path
- **Optional**: Ollama/LM Studio for local models

## Quick Commands

```bash
ZEROCLAW="/Users/fuzhuo/.openclaw/workspace/zeroclaw/target/debug/zeroclaw"

# Status & Info
$ZEROCLAW status          # Check running status and config
$ZEROCLAW providers       # List available model providers

# Run modes
$ZEROCLAW agent           # Interactive chat session
$ZEROCLAW daemon         # Start background daemon (gateway + heartbeat + cron)

# Management
$ZEROCLAW cron list      # View scheduled tasks
$ZEROCLAW skills list    # List installed skills
$ZEROCLAW config         # Manage configuration
```

## Available Actions

| Action | Command | Use Case |
|--------|---------|----------|
| Status | `zeroclaw status` | Check if running, view config, providers, channels |
| Agent | `zeroclaw agent` | Interactive chat session |
| Daemon | `zeroclaw daemon` | Start background service with heartbeat |
| Stop | Ctrl+C | Stop daemon/agent |
| Cron | `zeroclaw cron list` | View scheduled tasks |
| Cron add | `zeroclaw cron add "task" "schedule"` | Add cron task |
| Skills | `zeroclaw skills list` | List installed skills |
| Config | `zeroclaw config get/set` | View/modify config |

## Configuration

Key settings in `~/.zeroclaw/config.toml`:

```toml
# Model provider
default_provider = "openrouter"  # or: anthropic, ollama, lmstudio, etc.
default_model = "anthropic/claude-sonnet-4-6"

# Autonomy
[autonomy]
level = "supervised"  # or: autonomous
workspace_only = true
allowed_commands = ["git", "npm", "cargo", "ls", "cat", "grep"]
max_actions_per_hour = 100
max_cost_per_day_cents = 1000

# Heartbeat (for autonomous mode)
[heartbeat]
enabled = true
interval_minutes = 30

# Memory
[memory]
backend = "sqlite"
auto_save = true
```

## Usage Examples

### Example 1: Quick status check
```
User: "check if zeroclaw is running"
Action: Run `zeroclaw status`
```

### Example 2: Start background daemon
```
User: "start zeroclaw as a background service"
Action: Run `zeroclaw daemon &` or `zeroclaw start` (via helper script)
```

### Example 3: Switch to local model
```
User: "use local llama model"
Action: Update config to use ollama provider, run `zeroclaw agent`
```

### Example 4: View providers
```
User: "what AI models can zeroclaw use?"
Action: Run `zeroclaw providers`
```

## Scripts

The skill includes a helper script at `scripts/zeroclaw.sh`:

```bash
# Usage
scripts/zeroclaw.sh status     # Check status
scripts/zeroclaw.sh start      # Start daemon in background
scripts/zeroclaw.sh stop       # Stop running instance
scripts/zeroclaw.sh agent      # Interactive mode
scripts/zeroclaw.sh providers  # List providers
```

## Important Notes

1. **Independent from OpenClaw**: ZeroClaw runs as a separate process with no shared context
2. **Best for**: Simple tasks, local models, background jobs, resource-constrained environments
3. **Not a replacement**: Complex multi-step tasks still benefit from full OpenClaw capabilities
4. **Supported providers**: 38+ providers including OpenAI, Anthropic, Ollama, LM Studio, vLLM, etc.

## When to Use This Skill

Use ZeroClaw when:
- User wants minimal resource usage
- Task is simple (single query, basic automation)
- Local/offline inference is preferred
- Background daemon with heartbeat is needed
- Running on limited hardware (Pi, edge devices)

Stick with OpenClaw when:
- Complex multi-step reasoning required
- Need full skill system integration
- Advanced memory/context management needed
- Complex tool orchestration
