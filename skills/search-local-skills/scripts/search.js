#!/usr/bin/env node
/**
 * search.js
 * Searches the local skills index by keyword/phrase.
 * Auto-rebuilds the index when skills directories have changed since last build.
 *
 * Usage:
 *   node search.js <query> [--top <n>] [--index <path>] [--force-rebuild]
 *
 * Output: JSON to stdout.
 */

import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import os from 'os';

// ── Skill roots (must match build-index.js) ───────────────────────────────────

const SKILL_ROOTS = [
  path.join(os.homedir(), '.openclaw/workspace/skills'),
  path.join(os.homedir(), '.openclaw/skills'),
  '/Applications/QClaw.app/Contents/Resources/openclaw/config/skills',
];

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);

// ── Args ──────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

const topIdx = args.indexOf('--top');
const TOP_N = topIdx !== -1 ? parseInt(args[topIdx + 1], 10) : 8;

const indexIdx = args.indexOf('--index');
const INDEX_PATH = indexIdx !== -1
  ? args[indexIdx + 1]
  : path.join(SCRIPT_DIR, 'skills-index.json');

const FORCE_REBUILD = args.includes('--force-rebuild');

const queryParts = args.filter((a, i) => {
  if (a.startsWith('--')) return false;
  if (i > 0 && args[i - 1].startsWith('--')) return false;
  return true;
});
const QUERY = queryParts.join(' ').trim().toLowerCase();

if (!QUERY) {
  console.error('Usage: node search.js <query> [--top <n>] [--index <path>] [--force-rebuild]');
  process.exit(1);
}

// ── Staleness check ───────────────────────────────────────────────────────────

/**
 * Returns the latest mtime (ms) across all SKILL.md files in the given roots.
 * Also counts total skill dirs so we can detect additions/deletions.
 */
function scanRootsMeta() {
  let latestMtime = 0;
  let skillCount = 0;

  for (const root of SKILL_ROOTS) {
    if (!fs.existsSync(root)) continue;
    let entries;
    try { entries = fs.readdirSync(root); } catch { continue; }

    for (const name of entries) {
      const skillMd = path.join(root, name, 'SKILL.md');
      try {
        const stat = fs.statSync(skillMd);
        skillCount++;
        if (stat.mtimeMs > latestMtime) latestMtime = stat.mtimeMs;
      } catch {
        // not a skill dir
      }
    }
  }
  return { latestMtime, skillCount };
}

function needsRebuild() {
  if (FORCE_REBUILD) return { rebuild: true, reason: 'forced' };
  if (!fs.existsSync(INDEX_PATH)) return { rebuild: true, reason: 'index missing' };

  let index;
  try {
    index = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  } catch {
    return { rebuild: true, reason: 'index unreadable' };
  }

  const indexTime = new Date(index.builtAt).getTime();
  const { latestMtime, skillCount } = scanRootsMeta();

  // Any SKILL.md modified after the index was built?
  if (latestMtime > indexTime) {
    return { rebuild: true, reason: `skill file changed after index (${new Date(latestMtime).toISOString()})` };
  }

  // Skill count changed (install/uninstall)?
  if (skillCount !== index.count) {
    return { rebuild: true, reason: `skill count changed (index: ${index.count}, current: ${skillCount})` };
  }

  return { rebuild: false };
}

// ── Auto-rebuild ──────────────────────────────────────────────────────────────

const { rebuild, reason } = needsRebuild();

if (rebuild) {
  process.stderr.write(`[search-local-skills] Rebuilding index (${reason})...\n`);
  try {
    execFileSync(process.execPath, [path.join(SCRIPT_DIR, 'build-index.js'), '--output', INDEX_PATH], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    process.stderr.write('[search-local-skills] Index rebuilt ✓\n');
  } catch (e) {
    process.stderr.write(`[search-local-skills] Rebuild failed: ${e.message}\n`);
    if (!fs.existsSync(INDEX_PATH)) process.exit(2);
    process.stderr.write('[search-local-skills] Using stale index as fallback.\n');
  }
}

// ── Load index ────────────────────────────────────────────────────────────────

const { skills, builtAt } = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));

// ── Scoring ───────────────────────────────────────────────────────────────────

const queryTokens = QUERY.split(/\s+/).filter(Boolean);

function score(skill) {
  const nameL = skill.name.toLowerCase();
  const descL = skill.description.toLowerCase();
  const triggersL = (skill.triggers || []).map(t => t.toLowerCase());

  let s = 0;

  // Exact full-query match
  if (nameL.includes(QUERY)) s += 40;
  if (triggersL.some(t => t.includes(QUERY))) s += 30;
  if (descL.includes(QUERY)) s += 20;

  // Per-token matches
  for (const tok of queryTokens) {
    if (nameL.includes(tok)) s += 10;
    if (triggersL.some(t => t.includes(tok))) s += 8;
    if (descL.includes(tok)) s += 4;
  }

  // Boost: name starts with query token
  if (queryTokens.some(tok => nameL.startsWith(tok))) s += 5;

  return s;
}

// ── Search ────────────────────────────────────────────────────────────────────

const results = skills
  .map(skill => ({ ...skill, _score: score(skill) }))
  .filter(s => s._score > 0)
  .sort((a, b) => b._score - a._score)
  .slice(0, TOP_N)
  .map(({ _score, ...skill }) => ({
    name: skill.name,
    skillMd: skill.skillMd,
    dir: skill.dir,
    score: _score,
    description: skill.description.length > 200
      ? skill.description.slice(0, 200).trimEnd() + '…'
      : skill.description,
    triggers: skill.triggers?.slice(0, 5) || [],
  }));

// ── Output ────────────────────────────────────────────────────────────────────

console.log(JSON.stringify({
  query: QUERY,
  indexAge: builtAt,
  indexRebuilt: rebuild,
  totalSkills: skills.length,
  matches: results,
}, null, 2));
