---
name: gitnexus
description: "零服务器代码智能引擎 - 知识图谱 + MCP"
triggers:
  - "gitnexus"
  - "代码知识图谱"
  - "bug追踪"
  - "代码探索"
  - "影响分析"
  - "重构计划"
---

# GitNexus - 代码智能引擎

整合了5个子功能的完整代码智能工具箱。

## 子功能

### 1. gitnexus (核心)
- 代码知识图谱
- 零服务器架构
- MCP 支持

### 2. gitnexus-debugging
- Bug追踪和调用链分析
- 错误定位

### 3. gitnexus-exploring
- 探索不熟悉代码
- 理解架构

### 4. gitnexus-impact-analysis
- 修改前的 blast radius 分析
- 评估影响范围

### 5. gitnexus-refactoring
- 安全重构计划
- 依赖映射

## 使用方式

直接说需求，自动选择子功能：
- "这个bug在哪里" → debugging
- "这段代码做什么" → exploring  
- "改动这个会影响到什么" → impact-analysis
- "怎么重构这个模块" → refactoring
