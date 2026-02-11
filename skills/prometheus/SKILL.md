---
name: prometheus
description: "The Prometheus monitoring system and time series database."
triggers:
  - "prometheus"
  - "prometheus"
  - "prometheus" if '/' in full else "prometheus"
source:
  project: prometheus/prometheus
  url: https://github.com/prometheus/prometheus
  license: Apache-2.0
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:09:59
---

# Prometheus

The Prometheus monitoring system and time series database.

## 项目信息

- **Stars**: 62,652
- **License**: Apache-2.0
- **语言**: Go
- **GitHub**: [prometheus/prometheus](https://github.com/prometheus/prometheus)

## 核心功能

- <h1 align="center" style="border-bottom: none">     <a href="https://prometheus.io" target="_blank"><img alt="Prometheus" src="/documentation/images/prometheus-logo.svg"></a><br>Prometheus </h1>

## 安装

```bash
docker run --name prometheus -d -p 127.0.0.1:9090:9090 prom/prometheus
```

## 使用示例

```
build:
    tags:
        all:
            - netgo
            - builtinassets
            - remove_all_sd           # Exclude all optional SDs
            - enable_kubernetes_sd    # Re-enable only kubernetes
```

## 适用场景

- 系统监控时
- 指标收集时
- 告警设置
## 注意事项

*基于 prometheus/prometheus 官方文档生成*
*更新时间: 2026-02-11*
