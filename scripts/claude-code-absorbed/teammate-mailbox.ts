/**
 * @license Absorbed from Claude Code (instructkr/claude-code, 2026-03-31 leak)
 * Original: src/utils/teammateMailbox.ts (simplified)
 * 
 * File-based messaging for agent swarms.
 * Each teammate has an inbox at .claude/teams/{team}/inboxes/{agent}.json
 * 
 * Usage:
 *   const mailbox = new TeammateMailbox('/data/.claude/teams')
 *   await mailbox.write('teammate-B', { from: 'teammate-A', text: 'hello' })
 *   const messages = await mailbox.read('teammate-B')
 */

import { mkdir, readFile, writeFile } from 'fs/promises'
import { join } from 'path'
import * as lockfile from './lazy-lockfile.js'

const LOCK_OPTIONS = {
  retries: { retries: 10, minTimeout: 5, maxTimeout: 100 },
}

export type TeammateMessage = {
  from: string
  text: string
  timestamp: string
  read: boolean
  summary?: string
}

export class TeammateMailbox {
  constructor(private teamsDir: string) {}

  private inboxPath(agentName: string, teamName = 'default'): string {
    const safe = (s: string) => s.replace(/[^a-zA-Z0-9_-]/g, '_')
    return join(this.teamsDir, safe(teamName), 'inboxes', `${safe(agentName)}.json`)
  }

  private async ensureInboxDir(teamName: string): Promise<void> {
    const safe = (s: string) => s.replace(/[^a-zA-Z0-9_-]/g, '_')
    await mkdir(join(this.teamsDir, safe(teamName), 'inboxes'), { recursive: true })
  }

  async write(
    toAgent: string,
    message: Omit<TeammateMessage, 'read'>,
    teamName = 'default',
  ): Promise<void> {
    const path = this.inboxPath(toAgent, teamName)
    await this.ensureInboxDir(teamName)

    const release = await lockfile.lock(path, LOCK_OPTIONS)
    try {
      let messages: TeammateMessage[] = []
      try {
        const raw = await readFile(path, 'utf-8')
        messages = JSON.parse(raw)
      } catch {
        // New inbox
      }
      messages.push({ ...message, read: false })
      await writeFile(path, JSON.stringify(messages, null, 2))
    } finally {
      await release()
    }
  }

  async read(agentName: string, teamName = 'default'): Promise<TeammateMessage[]> {
    const path = this.inboxPath(agentName, teamName)
    try {
      const raw = await readFile(path, 'utf-8')
      return JSON.parse(raw) as TeammateMessage[]
    } catch {
      return []
    }
  }

  async markRead(agentName: string, teamName = 'default'): Promise<void> {
    const path = this.inboxPath(agentName, teamName)
    const release = await lockfile.lock(path, LOCK_OPTIONS)
    try {
      const raw = await readFile(path, 'utf-8')
      const messages: TeammateMessage[] = JSON.parse(raw)
      messages.forEach(m => { m.read = true })
      await writeFile(path, JSON.stringify(messages, null, 2))
    } finally {
      await release()
    }
  }

  async unreadCount(agentName: string, teamName = 'default'): Promise<number> {
    const messages = await this.read(agentName, teamName)
    return messages.filter(m => !m.read).length
  }
}
