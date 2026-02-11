---
name: mage-ai
description: "Modern ETL, Data Orchestration, and Pipeline Platform for Python and R"
triggers:
  - "mage-ai"
  - "mage"
  - "mage ai"
  - "data pipeline"
  - "etl pipeline"
source:
  project: mage-ai/mageai
  url: https://github.com/mage-ai/mageai
  license: Apache-2.0
  auto_generated: false
  enhanced_via: skill-creator
---

# Mage.ai

Modern ETL, Data Orchestration, and Pipeline Platform for Python and R.

## 项目信息

- **Stars**: 8,645
- **License**: Apache-2.0
- **语言**: Python
- **GitHub**: [mage-ai/mageai](https://github.com/mage-ai/mageai)

## 核心功能

- 低代码/无代码数据管道设计器
- 支持 Python 和 R 编程
- 实时和批处理数据处理
- 内置调度和监控
- 现代化 Web UI 界面
- 数据质量检查
- 多数据源支持

## 安装

```bash
# 使用 pip
pip install mage-ai

# 或使用 Docker
docker pull mageai/mage
```

## 快速开始

```python
# 1. 创建新项目
mage start my_project

# 2. 在浏览器中打开
# http://localhost:6789

# 3. 创建数据管道
# 使用拖拽式界面或 Python 代码
from mage import Mage

pipeline = Mage()
pipeline.run()
```

## 适用场景

- 构建 ETL 管道时
- 需要数据编排和调度时
- Python/R 数据处理
- 实时数据流水线
- 数据质量监控

## 常用命令

```bash
# 启动 Mage
mage start my_pipeline

# 运行管道
mage run my_pipeline

# 使用 Docker 运行
docker run -p 6789:6789 -v $(pwd):/home/src mageai/mage
```

## 注意事项

*基于 mage-ai/mageai 官方文档生成*
*更新时间: 2025-02-11*
