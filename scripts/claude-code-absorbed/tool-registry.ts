/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/tools.ts tool registration + feature DCE pattern
 * 
 * Feature-gated tool registry with compile-time dead code elimination.
 * Bun bun:bundle pattern — adapted for Node.js / other runtimes.
 * 
 * Bun version (use bun:bundle):
 *   import { feature } from 'bun:bundle'
 *   const tools = feature('MY_FEATURE') ? [ExtraTool] : []
 * 
 * Portable Node.js version (this file):
 */

type Tool = {
  name: string
  description?: string
  execute: (input: unknown) => Promise<unknown>
}

type ToolRegistryOptions = {
  features?: Record<string, boolean>
}

export function createToolRegistry(
  baseTools: Tool[],
  opts: ToolRegistryOptions = {},
): {
  register: (tool: Tool) => void
  get: (name: string) => Tool | undefined
  list: () => Tool[]
  registerFeature: (name: string, tools: Tool[]) => void
} {
  const toolMap = new Map<string, Tool>(baseTools.map(t => [t.name, t]))

  return {
    register(tool: Tool) {
      toolMap.set(tool.name, tool)
    },

    get(name: string) {
      return toolMap.get(name)
    },

    list() {
      return Array.from(toolMap.values())
    },

    registerFeature(name: string, tools: Tool[]) {
      const enabled = opts.features?.[name] ?? false
      if (enabled) {
        tools.forEach(t => toolMap.set(t.name, t))
      }
    },
  }
}

// Example: How Claude Code uses feature flags with Bun
/*
import { feature } from 'bun:bundle'

// Inactive code completely stripped at build time
const cronTools = feature('AGENT_TRIGGERS')
  ? [CronCreateTool, CronDeleteTool, CronListTool]
  : []

const RemoteTriggerTool = feature('AGENT_TRIGGERS_REMOTE')
  ? require('./tools/RemoteTriggerTool/RemoteTriggerTool.js').RemoteTriggerTool
  : null

const SleepTool =
  feature('PROACTIVE') || feature('KAIROS')
    ? require('./tools/SleepTool/SleepTool.js').SleepTool
    : null
*/
