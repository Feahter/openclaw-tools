/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/utils/hooks/hookHelpers.ts (simplified)
 * 
 * Agent hook utilities: structured output enforcement + argument substitution.
 * For building LLM-based verification/callback hooks.
 * 
 * Usage:
 *   const outputTool = createStructuredOutputTool()
 *   registerStructuredOutputEnforcement(setAppState, sessionId)
 */

import { z } from 'zod'

// Schema for hook responses
export const hookResponseSchema = z.object({
  ok: z.boolean().describe('Whether the condition was met'),
  reason: z.string().describe('Reason, if condition was not met').optional(),
})

export type HookResponse = z.infer<typeof hookResponseSchema>

/**
 * Replace $ARGUMENTS, $0, $1, etc. in prompt with JSON input fields.
 */
export function addArgumentsToPrompt(prompt: string, jsonInput: string): string {
  let result = prompt.replace('$ARGUMENTS', jsonInput)
  try {
    const args = JSON.parse(jsonInput)
    if (Array.isArray(args)) {
      args.forEach((val, i) => {
        result = result.replace(`$${i}`, String(val))
      })
    } else if (typeof args === 'object' && args !== null) {
      Object.entries(args).forEach(([key, val]) => {
        result = result.replace(`$${key}`, String(val))
      })
    }
  } catch {
    // Not JSON, skip argument substitution
  }
  return result
}

/**
 * Create a StructuredOutput tool for hook responses.
 * Forces LLM to call this tool to complete verification.
 */
export function createStructuredOutputTool(): {
  inputSchema: z.ZodType
  prompt: () => string
} {
  return {
    inputSchema: hookResponseSchema,
    prompt: () =>
      `Use this tool to return your verification result. ` +
      `You MUST call this tool exactly once at the end of your response.`,
  }
}
