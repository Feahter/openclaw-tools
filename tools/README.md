# OpenClaw Tools - AI Agent Utilities

Tools for managing multiple LLM APIs and local models.

## ⚠️ Security Notice

**Never commit real API keys to this repo!**
- Keys are stored in `~/.api-keys/` (not tracked by git)
- See [SECURITY.md](./SECURITY.md) for best practices

## Features

- **API Key Manager** - Manage multiple LLM providers with one CLI
- **Auto-Switcher** - Automatically switches to backup APIs when primary runs out
- **Local Model Dashboard** - Web UI for Ollama models + API keys (增强版)
- **API Reserve Scanner** - Scan and collect available APIs

## Quick Start

```bash
# Clone or download
cd tools/

# Make executables
chmod +x *.py

# List all APIs
python3 api-key-manager.py list

# Add a new API
python3 api-key-manager.py add <provider> <key> [name]

# Start auto-switcher (background)
python3 api-auto-switch.py monitor &

# Start local dashboard (web UI) - NEW UI!
python3 local-model-manager.py
# Open http://localhost:8766
```

## Supported Providers (15+)

| Provider | Status | Provider | Status |
|----------|--------|----------|--------|
| OpenAI | ✓ | Perplexity | ✓ |
| Anthropic | ✓ | Mistral | ✓ |
| Google | ✓ | Zhipu (智谱) | ✓ |
| DeepSeek | ✓ | Dashscope (阿里) | ✓ |
| Groq | ✓ | SiliconFlow | ✓ |
| TogetherAI | ✓ | HuggingFace | ✓ |
| Cerebras | ✓ | OpenCode | ✓ |
| Ollama | ✓ | | |

## Local Model Manager - Web UI Features

```
http://localhost:8766
```

**UI 优化:**
- ✅ 现代化深色主题，渐变效果
- ✅ 响应式布局，适配移动端
- ✅ 流畅动画和悬停效果
- ✅ 搜索/过滤模型

**交互增强:**
- ✅ 实时刷新 (5秒自动)
- ✅ 一键启动/删除模型
- ✅ API Key 测试功能
- ✅ 复制 Key 到剪贴板
- ✅ Toast 通知反馈

**功能扩展:**
- ✅ 用量统计 (请求数/Tokens/费用)
- ✅ 14+ Provider 支持
- ✅ 快捷建议提示
- ✅ 加载状态指示

## Task Board - 任务看板

```
http://localhost:8767
```

**功能特性:**
- 📋 四列看板: 待办 / 进行中 / 已完成 / 暂停
- 🎯 优先级标签: 高/中/低
- 🏷️ 自定义标签分类
- 📊 进度追踪
- 🔍 搜索/过滤
- 📤 导出 JSON
- 📥 导入示例任务
- 🔄 自动同步 (5秒刷新)

**使用场景:**
- 追踪我正在主动处理的任务
- 规划下一步工作
- 记录项目进度

## File Structure

```
tools/
├── api-key-manager.py      # Main CLI for key management
├── api-auto-switch.py      # Auto-switch when balance low
├── local-model-manager.py  # Web dashboard (增强版)
├── task-board.py           # 任务看板 - 主动任务追踪 ⭐新增
├── api-reserve-scanner.py  # Scan for free APIs
└── API_REGISTRATION_LINKS.md  # API signup links
```

## Requirements

- Python 3.10+
- No external dependencies (uses only stdlib)
- Ollama (optional, for local models)

## License

MIT

---

Built by OpenClawBuilder & @FeahterZ
