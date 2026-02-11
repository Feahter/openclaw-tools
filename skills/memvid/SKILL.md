---
name: memvid
description: "Memory layer for AI Agents. Replace complex RAG pipelines with a serverless, single-file memory layer. Give your agents instant retrieval and long-term memory."
triggers:
  - "memvid"
  - "memvid"
  - "memvid" if '/' in full else "memvid"
source:
  project: memvid/memvid
  url: https://github.com/memvid/memvid
  license: Apache-2.0
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:09:59
---

# Memvid

Memory layer for AI Agents. Replace complex RAG pipelines with a serverless, single-file memory layer. Give your agents instant retrieval and long-term memory.

## 项目信息

- **Stars**: 13,077
- **License**: Apache-2.0
- **语言**: Rust
- **GitHub**: [memvid/memvid](https://github.com/memvid/memvid)

## 核心功能

- based vector databases, Memvid enables fast retrieval directly from the file.
- agnostic, infrastructure-free memory layer that gives AI agents persistent, long-term memory they can carry anywhere.
- *organize AI memory as an append-only, ultra-efficient sequence of Smart Frames.**
- based design enables:
- Append-only writes without modifying or corrupting existing data
- Queries over past memory states

## 安装

```bash
mkdir -p ~/.cache/memvid/text-models

# Download ONNX model
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5.onnx

# Download tokenizer
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5_tokenizer.json
```

## 使用示例

```
cargo run --example basic_usage
```

## 适用场景

- 视频内容理解时
- 视频搜索时
- 视频分析
## 注意事项

*基于 memvid/memvid 官方文档生成*
*更新时间: 2026-02-11*
