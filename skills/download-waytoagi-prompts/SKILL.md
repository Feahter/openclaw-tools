---
name: download-waytoagi-prompts
description: Download AI prompts from waytoagi.com to local directory. Supports parallel downloads, retry failed downloads, and quick test mode. Multi-author support.
---

# Download WayToAGI Prompts (Optimized)

Download high-quality AI prompts from [waytoagi.com](https://www.waytoagi.com/zh/prompts) with parallel downloads and progress tracking.

## Usage

### Quick Test (Recommended First)
```
Use the download-waytoagi-prompts skill to test download 3 prompts
```
Download a few prompts to verify it works before downloading all.

### Download by Author
```
Use the download-waytoagi-prompts skill to download all prompts by 李继刚
Use the download-waytoagi-prompts skill to download 卡兹克's prompts
Use the download-waytoagi-prompts skill to download prompts by 云舒
```
Downloads with progress bar and parallel processing (5 workers).

### Discover Authors
```
Use the download-waytoagi-prompts skill to list all available authors
```
Fast scan - only checks first 5 prompts per page.

### Custom Options
```bash
# Download to custom directory
python skills/download-waytoagi-prompts/download-waytoagi-prompts.py --author "李继刚" --output /path/to/prompts

# Adjust parallel workers
python skills/download-waytoagi-prompts/download-waytoagi-prompts.py --author "李继刚" --workers 10
```

## Features (Optimizations)

| Feature | Description |
|---------|-------------|
| **Parallel Download** | 5 concurrent downloads (configurable) |
| **Progress Bar** | Real-time progress with tqdm |
| **Error Recovery** | Reports failed downloads with reasons |
| **Fast Discovery** | Only checks 5 prompts per page |
| **HTML Flexibility** | Multiple content extraction patterns |
| **Timeout Protection** | 15s timeout per request |
| **Test Mode** | Quick verification before bulk download |

## Directory Structure

```
assets/prompts/
├── 李继刚/
│   ├── README.md
│   ├── 质疑之锥.md
│   ├── 逻辑之刃.md
│   └── ...
└── 卡兹克/
    ├── README.md
    └── Deep Research: 写小说.md
```

## Examples

### Quick Test
```
Use the download-waytoagi-prompts skill to test
```
Downloads 3 prompts to /tmp/ for verification.

### Full Download
```
Use the download-waytoagi-prompts skill to download 李继刚's prompts
Output: assets/prompts/李继刚/

### All Authors
```
# Download multiple authors
Use the download-waytoagi-prompts skill to download 卡兹克's prompts
```

## Output Format

Each prompt saved as `{name}.md`:
```markdown
;; 作者: 李继刚
;; 版本: 0.1
;; 模型: Claude Sonnet
;; 用途: 七把武器之 质疑之锥
;; ━━━━━━━━━━━━━━
;; 设定如下内容为 your *System Prompt*
...
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Download timeout | Reduce `--workers` or check network |
| Wrong author | Verify author name spelling |
| Empty content | Try `--test` first |
| Rate limiting | Use `--workers 2` for slower downloads |

### Retry Failed Downloads
```bash
# Manual retry
python skills/download-waytoagi-prompts/download-waytoagi-prompts.py --author "李继刚"
```

## Supported Authors

- **李继刚**: 思维工具、语言学习 (41+ prompts)
- **卡兹克**: Deep Research 系列
- **云舒**: 内容创作、可视化工具

## Performance

| Mode | Speed | Use Case |
|------|-------|----------|
| Test (--test) | ~5s | Verification |
| Normal (--author) | ~30s | Daily use |
| High concurrency (--workers 10) | ~15s | Bulk download |
