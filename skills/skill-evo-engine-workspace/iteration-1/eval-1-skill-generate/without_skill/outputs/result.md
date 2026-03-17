# Skill Creation Result — GitHub Stars Extractor

## Summary

Successfully created a skill for extracting GitHub repository star counts (and related metadata) using the GitHub REST API.

---

## Skill Details

| Field | Value |
|---|---|
| **Skill Name** | `github-stars` |
| **Skill Directory** | `/Users/fuzhuo/.openclaw/workspace/skills/github-stars/` |
| **SKILL.md Path** | `/Users/fuzhuo/.openclaw/workspace/skills/github-stars/SKILL.md` |
| **File Size** | 5,781 bytes |

---

## What Was Created

### `/Users/fuzhuo/.openclaw/workspace/skills/github-stars/SKILL.md`

A complete skill file covering:

1. **Trigger phrases** — Chinese and English phrases that should activate this skill (e.g. "查一下 xxx/yyy 有多少 stars", "how many stars does ... have", "star 数对比")

2. **Step-by-step instructions** for the agent:
   - **Step 1**: Parse repo identifiers from user input (supports `owner/repo`, full GitHub URLs, `github.com/...` format)
   - **Step 2**: Fetch data via `GET https://api.github.com/repos/{owner}/{repo}` using the `web_fetch` tool
   - **Step 3**: Optionally use `GITHUB_TOKEN` env var for higher rate limits (60 → 5000 req/hr)
   - **Step 4**: Format results — single repo card or multi-repo comparison table sorted by stars
   - **Step 5**: Handle batch requests sequentially to avoid rate limits

3. **Output formats**:
   - Single repo: emoji-decorated card with stars, forks, watchers, issues, language, last push, description
   - Multiple repos: markdown comparison table + "🏆 Stars 最多的是..." summary

4. **Error handling** for 404 (not found), 403/429 (rate limited), network errors, invalid formats

5. **Example interactions** (4 examples covering single repo, batch comparison, full URL, ambiguous input)

6. **Optional enhancements**: trending repos, star history, star growth rate, batch from file

---

## API Validation

Tested the GitHub API during skill creation:

```
GET https://api.github.com/repos/facebook/react
→ Stars: 244,009 | Forks: 50,810 | Language: JavaScript ✅
```

The API works without authentication for public repos. The skill is ready to use immediately.

---

## Approach Used

- **No external dependencies** — uses only the built-in `web_fetch` tool and optionally `exec` for token detection
- **No authentication required** for public repos (though token support is documented)
- **Pure REST API** — no scraping, no third-party services
- Designed to be **self-contained**: the SKILL.md alone is sufficient for an agent to execute the full workflow

---

## Notes

- The skill was created **without reading any existing skill file** — built entirely from general knowledge of the GitHub API and OpenClaw skill conventions
- Rate limit: 60 unauthenticated requests/hour is sufficient for typical use; the skill documents how to configure a token for heavier use
- The skill handles both Chinese and English user inputs naturally
