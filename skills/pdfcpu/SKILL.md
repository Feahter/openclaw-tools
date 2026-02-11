---
name: pdfcpu
description: "A PDF processor written in Go."
triggers:
  - "pdfcpu"
  - "pdfcpu"
  - "pdfcpu" if '/' in full else "pdfcpu"
source:
  project: pdfcpu/pdfcpu
  url: https://github.com/pdfcpu/pdfcpu
  license: Apache-2.0
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:09:59
---

# Pdfcpu

A PDF processor written in Go.

## 项目信息

- **Stars**: 8,456
- **License**: Apache-2.0
- **语言**: Go
- **GitHub**: [pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu)

## 核心功能

- Please [create](https://github.com/pdfcpu/pdfcpu/issues/new/choose) an issue if you find a bug or want to propose a change.
- Feature requests - always welcome!
- Bug fixes - always welcome!
- PRs - let's [discuss](https://github.com/pdfcpu/pdfcpu/discussions) first or [create](https://github.com/pdfcpu/pdfcpu/issues/new/choose) an issue.
- pdfcpu is stable but still *Alpha* and occasionally undergoing heavy changes.
- The pdfcpu [discussion board](https://github.com/pdfcpu/pdfcpu/discussions) is open! Please engage in any form helpful for the community.

## 安装

```bash
$ git clone https://github.com/pdfcpu/pdfcpu
$ cd pdfcpu/cmd/pdfcpu
$ go install
$ pdfcpu version
```

## 使用示例

```
$ docker build -t pdfcpu .
# mount current host folder into container as /app to process files in the local host folder
$ docker run -it -v "$(pwd)":/app pdfcpu validate a.pdf
```

## 适用场景

- PDF 验证时
- PDF 加密时
- PDF 操作
## 注意事项

*基于 pdfcpu/pdfcpu 官方文档生成*
*更新时间: 2026-02-11*
