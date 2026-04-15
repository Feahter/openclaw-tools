/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/utils/QueryGuard.ts
 * 
 * Synchronous state machine for async query lifecycle.
 * Compatible with React's useSyncExternalStore.
 * 
 * Three states: idle | dispatching | running
 * Prevents re-entry during the async gap between queue dequeue and query start.
 */

import { createSignal } from './signal.js'

export class QueryGuard {
  private _status: 'idle' | 'dispatching' | 'running' = 'idle'
  private _generation = 0
  private _changed = createSignal()

  /** Reserve for queue processing. idle → dispatching. Returns false if busy. */
  reserve(): boolean {
    if (this._status !== 'idle') return false
    this._status = 'dispatching'
    this._changed.emit()
    return true
  }

  /** Cancel reservation when queue had nothing to process. dispatching → idle. */
  cancelReservation(): void {
    if (this._status !== 'dispatching') return
    this._status = 'idle'
    this._changed.emit()
  }

  /** Start a query. Returns generation on success, null if already running. */
  tryStart(): number | null {
    if (this._status === 'running') return null
    this._status = 'running'
    ++this._generation
    this._changed.emit()
    return this._generation
  }

  /** End a query. Returns true if this generation is still current. */
  end(generation: number): boolean {
    if (this._generation !== generation) return false
    if (this._status !== 'running') return false
    this._status = 'idle'
    this._changed.emit()
    return true
  }

  /** Force-end regardless of generation. For onCancel. */
  forceEnd(): void {
    if (this._status === 'idle') return
    this._status = 'idle'
    ++this._generation
    this._changed.emit()
  }

  get isActive(): boolean {
    return this._status !== 'idle'
  }

  get generation(): number {
    return this._generation
  }

  // useSyncExternalStore interface
  subscribe = this._changed.subscribe

  getSnapshot = (): boolean => {
    return this._status !== 'idle'
  }
}
