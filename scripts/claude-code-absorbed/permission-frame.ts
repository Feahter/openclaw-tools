/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/hooks/toolPermission/useToolPermission.ts (inferred pattern)
 * 
 * Tool permission system for Agent CLI tools.
 * Handles ask/deny/auto-approve per tool invocation.
 * 
 * Usage:
 *   const perm = createPermissionSystem({ mode: 'default' })
 *   const result = await perm.check('BashTool', { command: 'ls' })
 *   if (result.requiresApproval) {
 *     const decision = await perm.promptUser('BashTool', { command: 'ls' })
 *   }
 */

export type PermissionMode = 'default' | 'plan' | 'auto' | 'bypass'

export type PermissionResult =
  | { allowed: true }
  | { allowed: false; reason: string }
  | { requiresApproval: true; tool: string; input: unknown }

export type ToolPermissionChecker = {
  check: (toolName: string, input: unknown) => PermissionResult
  setMode: (mode: PermissionMode) => void
  getMode: () => PermissionMode
  approve: (toolName: string, input: unknown) => void
  deny: (toolName: string, input: unknown) => void
}

const ALWAYS_DENY = new Set([
  'Shell',
  'Eval',
  'Exec',
  '__import__',
])

export function createPermissionSystem(opts: {
  mode: PermissionMode
  onPrompt?: (tool: string, input: unknown) => Promise<'approve' | 'deny'>
  onAutoApprove?: (tool: string, input: unknown) => boolean
}): ToolPermissionChecker {
  let mode = opts.mode
  const approvedCache = new Map<string, boolean>()

  function cacheKey(tool: string, input: unknown): string {
    return `${tool}:${JSON.stringify(input)}`
  }

  function checkDangerous(input: unknown): boolean {
    if (typeof input !== 'object' || input === null) return false
    const obj = input as Record<string, unknown>
    for (const key of Object.keys(obj)) {
      if (ALWAYS_DENY.has(key)) return true
      if (typeof obj[key] === 'string' && /__import__|eval|exec\s*\(/.test(obj[key] as string)) return true
    }
    return false
  }

  return {
    setMode(newMode: PermissionMode) {
      mode = newMode
      if (newMode !== 'default') approvedCache.clear()
    },

    getMode() {
      return mode
    },

    check(toolName: string, input: unknown): PermissionResult {
      if (mode === 'bypass') return { allowed: true }
      if (mode === 'auto') {
        const autoApproved = opts.onAutoApprove?.(toolName, input)
        if (autoApproved) return { allowed: true }
      }
      if (checkDangerous(input)) {
        return { allowed: false, reason: 'Dangerous operation blocked' }
      }
      const cached = approvedCache.get(cacheKey(toolName, input))
      if (cached === true) return { allowed: true }
      if (mode === 'plan') return { allowed: true }
      if (mode === 'default') {
        return { requiresApproval: true, tool: toolName, input }
      }
      return { requiresApproval: true, tool: toolName, input }
    },

    approve(toolName: string, input: unknown) {
      approvedCache.set(cacheKey(toolName, input), true)
    },

    deny(_toolName: string, _input: unknown) {
      // Could throw or log; for now just don't cache approval
    },
  }
}
