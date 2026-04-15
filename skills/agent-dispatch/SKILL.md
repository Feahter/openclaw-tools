---
name: agent-dispatch
description: Lightweight agent registry and router. Consult BEFORE performing specialized work such as code review, security audit, debugging, refactoring, performance optimization, infrastructure, data analysis, API design, testing, documentation, or any domain-specific engineering task. Maps tasks to installed subagents so work is delegated instead of done inline.
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    homepage: https://github.com/userFRM/agent-dispatch
    always: false
    skillKey: agent-dispatch
---

# Agent dispatch

You have specialized subagents installed. **Before doing specialized work yourself, check this index and dispatch to the appropriate agent.**

## How to use

1. You encounter a task that matches a domain below
2. Look up the agent name in the index
3. Verify the agent is installed (check your agents directory)
4. Dispatch to it using your platform's subagent/session mechanism
5. Only do the work yourself if no matching agent is installed

### Platform-specific dispatch

| Platform | Agent location | Dispatch mechanism |
|----------|---------------|-------------------|
| Claude Code | `~/.claude/agents/` | `Task` tool with agent name |
| OpenClaw | `~/.openclaw/workspace/` or skill-managed | `sessions_spawn` tool |
| Cursor | `.cursor/agents/` | Agent invocation |
| Codex | `.codex/agents/` | Agent invocation |

Use whichever mechanism your platform provides for spawning a subagent or isolated session. If your platform does not have a programmatic dispatch tool, instruct the user to invoke the agent manually (e.g., `/agent-name` or by name) and pause until it completes.

## Known limitations

- Each keyword maps to exactly one agent (TOML requires unique keys). If you need one keyword to fan out to multiple agents, use a composite agent name or pick the most relevant one.

## Agent index

Scan this index by **keyword**. The format is `keyword = "agent-name"`.

```toml
# ── Code quality ──────────────────────────────────
review          = "code-reviewer"
refactor        = "refactoring-specialist"
lint            = "code-reviewer"
code-quality    = "code-reviewer"
simplify        = "refactoring-specialist"
dead-code       = "refactoring-specialist"

# ── Security ─────────────────────────────────────
security        = "security-auditor"
vulnerability   = "security-auditor"
owasp           = "security-auditor"
secrets         = "security-auditor"
penetration     = "penetration-tester"
audit           = "security-auditor"
compliance      = "compliance-auditor"
ad-security     = "ad-security-reviewer"

# ── Debugging and errors ─────────────────────────
debug           = "debugger"
error           = "error-detective"
stacktrace      = "debugger"
crash           = "debugger"
troubleshoot    = "debugger"

# ── Testing ──────────────────────────────────────
test            = "qa-expert"
e2e             = "test-automator"
unit-test       = "test-automator"
integration     = "test-automator"
accessibility   = "accessibility-tester"

# ── Performance ──────────────────────────────────
performance     = "performance-engineer"
optimize        = "performance-engineer"
profiling       = "performance-engineer"
bottleneck      = "performance-engineer"
chaos           = "chaos-engineer"

# ── Architecture and design ──────────────────────
api-design      = "api-designer"
architecture    = "architect-reviewer"
microservices   = "microservices-architect"
graphql         = "graphql-architect"
websocket       = "websocket-engineer"

# ── Frontend ─────────────────────────────────────
react           = "react-specialist"
nextjs          = "nextjs-developer"
vue             = "vue-expert"
angular         = "angular-architect"
ui              = "ui-designer"
frontend        = "frontend-developer"
electron        = "electron-pro"

# ── Backend ──────────────────────────────────────
backend         = "backend-developer"
django          = "django-developer"
rails           = "rails-expert"
spring          = "spring-boot-engineer"
laravel         = "laravel-specialist"
dotnet          = "dotnet-core-expert"

# ── Languages ────────────────────────────────────
typescript      = "typescript-pro"
javascript      = "javascript-pro"
python          = "python-pro"
rust            = "rust-engineer"
golang          = "golang-pro"
java            = "java-architect"
kotlin          = "kotlin-specialist"
swift           = "swift-expert"
cpp             = "cpp-pro"
csharp          = "csharp-developer"
elixir          = "elixir-expert"
php             = "php-pro"
sql             = "sql-pro"
flutter         = "flutter-expert"
powershell      = "powershell-7-expert"

# ── Infrastructure ───────────────────────────────
docker          = "docker-expert"
kubernetes      = "kubernetes-specialist"
terraform       = "terraform-engineer"
terragrunt      = "terragrunt-expert"
cloud           = "cloud-architect"
aws             = "cloud-architect"
azure           = "azure-infra-engineer"
cicd            = "deployment-engineer"
devops          = "devops-engineer"
sre             = "sre-engineer"
platform        = "platform-engineer"
network         = "network-engineer"
incident        = "devops-incident-responder"
database        = "database-administrator"

# ── Data and AI ──────────────────────────────────
data-analysis   = "data-analyst"
data-eng        = "data-engineer"
data-science    = "data-scientist"
machine-learning = "machine-learning-engineer"
ml-ops          = "mlops-engineer"
llm             = "llm-architect"
nlp             = "nlp-engineer"
prompt-eng      = "prompt-engineer"
postgres        = "postgres-pro"
db-optimize     = "database-optimizer"

# ── Developer experience ─────────────────────────
documentation   = "documentation-engineer"
cli             = "cli-developer"
build           = "build-engineer"
dependencies    = "dependency-manager"
git-workflow    = "git-workflow-manager"
dx              = "dx-optimizer"
legacy          = "legacy-modernizer"
mcp             = "mcp-developer"
tooling         = "tooling-engineer"

# ── Specialized domains ─────────────────────────
blockchain      = "blockchain-developer"
fintech         = "fintech-engineer"
gamedev         = "game-developer"
iot             = "iot-engineer"
embedded        = "embedded-systems"
payments        = "payment-integration"
seo             = "seo-specialist"
mobile          = "mobile-app-developer"

# ── Business and product ────────────────────────
product         = "product-manager"
project         = "project-manager"
technical-write = "technical-writer"
ux-research     = "ux-researcher"
scrum           = "scrum-master"
business        = "business-analyst"

# ── Orchestration ────────────────────────────────
coordinate      = "multi-agent-coordinator"
organize        = "agent-organizer"
workflow        = "workflow-orchestrator"
distribute      = "task-distributor"
```

## Dispatch decision

**Dispatch** when:
- The task is clearly specialized (security review, performance profiling, etc.)
- The agent can work independently with clear inputs/outputs
- The work would consume significant main context

**Do it yourself** when:
- The task is a quick one-liner (not worth spawning an agent)
- You need tight back-and-forth with the user
- The task spans multiple domains simultaneously
- No matching agent is installed

## Verifying agent availability

Before dispatching, confirm the agent exists in your platform's agent directory. If not found, do the work yourself. Do not fail silently.
