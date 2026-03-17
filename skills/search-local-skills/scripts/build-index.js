#!/usr/bin/env node
/**
 * build-index.js
 * Scans all installed skill directories and builds a lightweight JSON index.
 * Output: skills-index.json in the same directory as this script.
 *
 * Usage:
 *   node build-index.js [--output <path>]
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

// ── Config ────────────────────────────────────────────────────────────────────

const SKILL_ROOTS = [
  path.join(os.homedir(), '.openclaw/workspace/skills'),
  path.join(os.homedir(), '.openclaw/skills'),
  '/Applications/QClaw.app/Contents/Resources/openclaw/config/skills',
];

const args = process.argv.slice(2);
const outputIdx = args.indexOf('--output');
const OUTPUT_PATH = outputIdx !== -1
  ? args[outputIdx + 1]
  : path.join(path.dirname(new URL(import.meta.url).pathname), 'skills-index.json');

// ── YAML frontmatter parser (no deps) ────────────────────────────────────────

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const yaml = match[1];
  const result = {};

  // name
  const nameMatch = yaml.match(/^name:\s*(.+)$/m);
  if (nameMatch) result.name = nameMatch[1].trim().replace(/^['"]|['"]$/g, '');

  // description — handles inline, quoted, and block scalar (|)
  const descMatch = yaml.match(/^description:\s*([\s\S]*?)(?=\n\S|\n---|\n$|$)/m);
  if (descMatch) {
    let raw = descMatch[1].trim();
    if (raw.startsWith('|')) {
      // block scalar: collect indented lines
      const blockMatch = yaml.match(/^description:\s*\|\r?\n((?:[ \t]+.+\r?\n?)*)/m);
      if (blockMatch) {
        raw = blockMatch[1]
          .split('\n')
          .map(l => l.replace(/^[ \t]{2}/, ''))
          .join('\n')
          .trim();
      }
    } else {
      raw = raw.replace(/^['"]|['"]$/g, '');
    }
    result.description = raw;
  }

  // triggers (array)
  const triggersMatch = yaml.match(/^triggers:\r?\n((?:[ \t]+-[ \t]+.+\r?\n?)*)/m);
  if (triggersMatch) {
    result.triggers = triggersMatch[1]
      .split('\n')
      .map(l => l.replace(/^[ \t]+-[ \t]+/, '').replace(/^['"]|['"]$/g, '').trim())
      .filter(Boolean);
  }

  return result;
}

// ── Scanner ───────────────────────────────────────────────────────────────────

function scanRoot(rootDir) {
  const entries = [];
  if (!fs.existsSync(rootDir)) return entries;

  for (const name of fs.readdirSync(rootDir)) {
    const skillDir = path.join(rootDir, name);
    const skillMd = path.join(skillDir, 'SKILL.md');
    if (!fs.existsSync(skillMd)) continue;

    try {
      const content = fs.readFileSync(skillMd, 'utf8');
      const meta = parseFrontmatter(content);
      if (!meta.name && !meta.description) continue;

      entries.push({
        name: meta.name || name,
        dir: skillDir,
        skillMd,
        description: meta.description || '',
        triggers: meta.triggers || [],
      });
    } catch {
      // skip unreadable files
    }
  }
  return entries;
}

// ── Main ──────────────────────────────────────────────────────────────────────

const seen = new Set();
const index = [];

for (const root of SKILL_ROOTS) {
  for (const entry of scanRoot(root)) {
    if (seen.has(entry.name)) continue; // first occurrence wins (workspace > system)
    seen.add(entry.name);
    index.push(entry);
  }
}

const output = {
  builtAt: new Date().toISOString(),
  count: index.length,
  skills: index,
};

fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2), 'utf8');
console.log(`✓ Built index: ${index.length} skills → ${OUTPUT_PATH}`);
