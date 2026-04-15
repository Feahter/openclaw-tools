/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/utils/signal.ts
 * 
 * Tiny listener-set primitive for pure event signals (no stored state).
 * Collapses the ~8-line boilerplate into a one-liner.
 * 
 * Usage:
 *   const changed = createSignal<[string]>()
 *   export const subscribe = changed.subscribe
 *   // later: changed.emit('userSettings')
 */

export type Signal<Args extends unknown[] = []> = {
  subscribe: (listener: (...args: Args) => void) => () => void
  emit: (...args: Args) => void
  clear: () => void
}

export function createSignal<Args extends unknown[] = []>(): Signal<Args> {
  const listeners = new Set<(...args: Args) => void>()
  return {
    subscribe(listener) {
      listeners.add(listener)
      return () => { listeners.delete(listener) }
    },
    emit(...args) {
      for (const listener of listeners) listener(...args)
    },
    clear() {
      listeners.clear()
    },
  }
}
