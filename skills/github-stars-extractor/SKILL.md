---
name: github-stars-extractor
description: Extract GitHub repository star counts and statistics. Use when the user asks about GitHub stars, repository popularity, or wants to compare star counts across repos. Triggered by queries like "how many stars does X have", "compare repo stars", "GitHub trending", or any mention of GitHub star counts.
---

# GitHub Stars Extractor

Extract GitHub repository star counts and related statistics.

## When to Use

- User asks "how many stars does [repo] have"
- User wants to compare stars across multiple repositories
- User mentions GitHub trending or popular repos
- User wants to know repository popularity/statistics

## How It Works

1. Use GitHub API or web scraping to fetch repository data
2. Extract star count, forks, watchers, and other metrics
3. Present in a clean, readable format

## Tools Needed

- `gh` CLI (GitHub CLI) - `gh repo view <owner/repo>`
- Or use GitHub API via curl/requests
- Or use web search to find star counts

## Output Format

```
Repository: owner/repo
Stars: ⭐ X,XXX
Forks: XX
Watchers: XX
Last updated: YYYY-MM-DD
```

## Examples

**Input:** "How many stars does openclaw/openclaw have?"
**Output:** "openclaw/openclaw has 2,347 stars"

**Input:** "Compare these repos: vercel/next.js and nuxt/nuxt"
**Output:** 
- vercel/next.js: ⭐ 115k stars
- nuxt/nuxt: ⭐ 65k stars

## Notes

- Always verify the exact owner/repo format
- Handle private repos gracefully (may not be accessible)
- Provide source links when possible
