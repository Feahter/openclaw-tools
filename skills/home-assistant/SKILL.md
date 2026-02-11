---
name: home-assistant
description: "Open source home automation platform that puts local control and privacy first"
triggers:
  - "home-assistant"
  - "home assistant"
  - "hass"
  - "智能家居"
  - "home automation"
source:
  project: home-assistant/core
  url: https://github.com/home-assistant/core
  license: Apache-2.0
  auto_generated: false
  enhanced_via: skill-creator
---

# Home Assistant

Open source home automation platform that puts local control and privacy first.

## 项目信息

- **Stars**: 84,751
- **License**: Apache-2.0
- **语言**: Python
- **GitHub**: [home-assistant/core](https://github.com/home-assistant/core)

## 核心功能

- 本地控制优先（不依赖云端）
- 保护隐私，数据存储在本地
- 支持 2000+ 智能设备集成
- 自动化规则引擎
- 现代化 Web 和移动端 UI
- 强大的社区支持
- 语音助手集成

## 安装

```bash
# 使用 Docker（推荐）
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Asia/Shanghai \
  -v /PATH_TO_CONFIG:/config \
  --network=host \
  homeassistant/home-assistant:stable

# 或使用 Python 虚拟环境
pip3 install homeassistant
hass
```

## 快速开始

```yaml
# configuration.yaml 示例
homeassistant:
  name: Home
  unit_system: metric
  time_zone: Asia/Shanghai

# 添加自动化示例
automation:
  - alias: 开灯自动化
    trigger:
      platform: sun
      event: sunset
    action:
      service: light.turn_on
      entity_id: light.living_room
```

## 适用场景

- 构建智能家居系统时
- 需要本地隐私保护时
- 多品牌设备整合时
- 自定义自动化规则时
- 语音控制集成时

## 常用集成

- 灯光控制（Philips Hue, Yeelight, IKEA）
- 传感器（温度、湿度、人体感应）
- 安防摄像头
- 空调/电视控制
- 门锁和车库门

## 注意事项

*基于 home-assistant/core 官方文档生成*
*更新时间: 2025-02-11*
