---
name: tools-ui
description: "---"
triggers:
  - "tools-ui"
  - "tools ui"
source:
  project: tools-ui
  url: ""
  license: ""
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:32:49
---

# Tools Ui

---
# Tool UI Components

Tool lifecycle components from [ui.inference.sh](https://ui.inference.sh).

## Quick Start

```bash
npx shadcn@latest add https://ui.inference.sh/r/tools.json
```

## Tool States

| State | Description |
|-------|-------------|
| `pending` | Tool call requested, waiting to execute |
| `running` | Tool is currently executing |
| `approval` | Requires human approval before execution |
| `success` | Tool completed successfully |
| `error` | Tool execution failed |

## Components

### Tool Call Display

```tsx
import { ToolCall } from "@/registry/blocks/tools/tool-call"

<ToolCall
  name="search_web"
  args={{ query: "latest AI news" }}
  status="running"
/>
```

### Tool Result

```tsx
import { ToolResult } from "@/registry/blocks/tools/tool-result"

<ToolResult
  name="search_web"
  result={{ results: [...] }}
  status="success"
/>
```

### Tool Approval

```tsx
import { ToolApproval } from "@/registry/blocks/tools/tool-approval"

<ToolApproval
  name="send_email"
  args={{ to: "user@example.com", subject: "Hello" }}
  onApprove={() => executeTool()}
  onDeny={() => cancelTool()}
/>
```

## Full Example

```tsx
import { ToolCall, ToolResult, ToolApproval } from "@/registry/blocks/tools"

function ToolDisplay({ tool }) {
  if (tool.status === 'approval') {
    return (
      <ToolApproval
        name={tool.name}
        args={tool.args}
        onApprove={tool.approve}
        onDeny={tool.deny}
      />
    )
  }

  if (tool.result) {
    return (
      <ToolResult
        name={tool.name}
        result={tool.result}
        status={tool.status}
      />
    )
  }

  return (
    <ToolCall
      name={tool.name}
      args={tool.args}
      status={tool.status}
    />
  )
}
```

## Styling Tool Cards

```tsx
<ToolCall
  name="read_file"
  args={{ path: "/src/index.ts" }}
  status="running"
  className="border-blue-500"
/>
```

## Tool Icons

Tools automatically get icons based on their name:

| Pattern | Icon |
|---------|------|
| `search*`, `find*` | Search |
| `read*`, `get*` | File |
| `write*`, `create*` | Pencil |
| `delete*`, `remove*` | Trash |
| `send*`, `email*` | Mail |
| Default | Wrench |

## With Agent Component

The Agent component handles tool lifecycle automatically:

```tsx
import { Agent } from "@/registry/blocks/agent/agent"

<Agent
  proxyUrl="/api/inference/proxy"
  config={{
    core_app: { ref: 'openrouter/claude-sonnet-45@0fkg6xwb' },
    tools: [
      {
        name: 'search_web',
        description: 'Search the web',
        parameters: { query: { type: 'string' } },
        requiresApproval: true, // Enable approval flow
      },
    ],
  }}
/>
```

## Related Skills

```bash
# Full agent component (recommended)
npx skills add inference-sh/agent-skills@agent-ui

# Chat UI blocks
npx skills add inference-sh/agent-skills@chat-ui

# Widgets for tool results
npx skills add inference-sh/agent-skills@widgets-ui
```

## Documentation

- [Adding Tools to Agents](https://inference.sh/docs/agents/adding-tools) - Equip agents with tools
- [Human-in-the-Loop](https://inference.sh/docs/runtime/human-in-the-loop) - Approval flows
- [Tool Approval Gates](https://inference.sh/blog/tools/approval-gates) - Implementing approvals

Component docs: [ui.inference.sh/blocks/tools](https://ui.inference.sh/blocks/tools)


## 适用场景

- 当用户需要 --- 时

## 注意事项

*基于 skill-creator SOP 强化*
*更新时间: 2026-02-11*