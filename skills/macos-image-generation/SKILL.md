---
name: macos-image-generation
description: 在 macOS 上本地部署 AI 文生图工具（Stable Diffusion）。支持 InvokeAI 和 Diffusers，提供安装、模型管理、生成工作流的完整指南。
triggers:
  - "macos 文生图"
  - "本地部署 stable diffusion"
  - "苹果电脑 图像生成"
  - "mac ai绘画"
  - "invokeai 安装"
  - "mps 图像生成"
---

# macOS 文生图本地部署

在 macOS 上搭建本地 AI 图像生成环境，支持 Apple Silicon (M1/M2/M3/M4) 和 Intel Mac。

## 适用场景

- 隐私优先：图片完全本地生成，不上传云端
- 无需订阅：一次性配置，无限使用
- 离线可用：不依赖网络连接
- 自定义控制：完全控制模型、参数、工作流

## 系统要求诊断

运行前，先确认系统环境：

```bash
# 检查 macOS 版本
sw_vers

# 检查 Python 版本
python3 --version

# 检查芯片架构
uname -m  # arm64=Apple Silicon, x86_64=Intel

# 检查内存
sysctl hw.memsize | awk '{print $2/1024/1024/1024 " GB"}'
```

### 最低配置

| 配置 | SD 1.5 (512x512) | SDXL (1024x1024) | FLUX (1024x1024) |
|------|------------------|------------------|------------------|
| **Apple Silicon** | M1 + 8GB 内存 | M1 Pro + 16GB 内存 | M2 Pro + 24GB 内存 |
| **Intel** | 不支持 GPU 加速 | 不推荐 | 不推荐 |
| **磁盘空间** | 10GB + 20GB 模型 | 10GB + 50GB 模型 | 10GB + 100GB 模型 |

### ⚠️ 兼容性警告

| macOS 版本 | InvokeAI 4.x | 解决方案 |
|-----------|--------------|----------|
| **14+ (Sonoma+)** | ✅ 完全支持 | 使用官方 Launcher |
| **12-13** | ❌ 不支持 | 使用手动安装方案 |

## 方案选择

根据你的需求选择：

| 方案 | 难度 | 功能 | 推荐场景 |
|------|------|------|---------|
| **A: InvokeAI (推荐)** | ⭐⭐ 中等 | 完整 WebUI、画布、工作流 | 日常使用、专业创作 |
| **B: Diffusers 脚本** | ⭐ 简单 | 基础文生图 | 快速体验、开发集成 |

---

## 方案 A: InvokeAI 完整安装

### 路径 1: 官方 Launcher (macOS 14+)

最简单的安装方式，自动处理依赖：

```bash
# 1. 下载 Launcher
# 访问: https://github.com/invoke-ai/launcher/releases
# 下载: Invoke.Community.Edition-latest-arm64.dmg

# 2. 安装
dmg 拖入 Applications，双击运行

# 3. 首次启动
- 点击 "Install" 选择安装路径
- 等待自动下载依赖（10-30分钟）
- 完成后点击 "Launch"

# 4. 安装模型
- 打开 WebUI 后进入 Models 标签
- 点击 "Starter Models" 安装基础模型
- 推荐先安装 SD 1.5 或 SDXL 基础模型
```

### 路径 2: 手动安装 (macOS 12/13)

适用于旧系统或需要更多控制：

```bash
# 1. 创建虚拟环境
python3 -m venv ~/invokeai-env
source ~/invokeai-env/bin/activate

# 2. 安装 InvokeAI
pip install invokeai --use-pep517 --extra-index-url https://download.pytorch.org/whl/cpu

# 3. 初始化配置
invokeai-configure

# 4. 启动
invokeai-web
```

### InvokeAI 核心工作流

#### 1. 基础文生图

```
Text to Image 节点 → 输入提示词 → 选择模型 → 生成
```

**关键参数：**
| 参数 | 说明 | 推荐值 |
|------|------|--------|
| **Steps** | 去噪步数 | 20-30 (SD1.5), 30-50 (SDXL) |
| **CFG Scale** | 提示词遵循度 | 7-9 (平衡), 12+ (严格) |
| **Sampler** | 采样算法 | Euler a (快速), DPM++ 2M Karras (质量) |
| **Seed** | 随机种子 | -1 (随机), 固定值 (复现) |

#### 2. 使用 Canvas 编辑

```
生成图片 → 进入 Canvas → Inpaint/Outpaint → 重绘
```

**画布功能：**
- **Inpaint**: 局部重绘（修改特定区域）
- **Outpaint**: 向外扩展画面
- **Control Layers**: 基于参考图生成

#### 3. 工作流复用

保存工作流为 `.json`，以后直接加载：
```
Workflows → Save → 命名 → 下次 Load
```

---

## 方案 B: Diffusers 快速脚本

适合开发者或只需要基础功能：

### 安装

```bash
# 创建环境
python3 -m venv ~/diffusers-env
source ~/diffusers-env/bin/activate

# 安装依赖
pip install torch torchvision diffusers transformers accelerate

# Apple Silicon 额外安装
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
```

### 基础生成脚本

创建 `generate.py`：

```python
import torch
from diffusers import StableDiffusionPipeline

# 加载模型（首次会自动下载）
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32
)

# Apple Silicon 使用 MPS
if torch.backends.mps.is_available():
    pipe = pipe.to("mps")
    # MPS 需要预热
    _ = pipe("warmup", num_inference_steps=1)
else:
    pipe = pipe.to("cpu")

# 生成图片
prompt = "a beautiful sunset over mountains, digital art"
image = pipe(
    prompt,
    num_inference_steps=25,
    guidance_scale=7.5,
    height=512,
    width=512
).images[0]

# 保存
image.save("output.png")
print("Saved: output.png")
```

### 运行

```bash
python generate.py
```

---

## 模型管理

### 推荐模型（适合入门）

| 模型 | 类型 | 大小 | 特点 |
|------|------|------|------|
| **SD 1.5** | 基础 | 4GB | 快速、低显存、生态丰富 |
| **SDXL Base** | 基础 | 7GB | 高质量、1024x1024 原生 |
| **RealVisXL** | 写实 | 7GB | 照片级人像 |
| **Animagine XL** | 动漫 | 7GB | 二次元风格 |
| **FLUX.1-schnell** | 高质量 | 24GB | 顶级质量，需大内存 |

### 模型下载渠道

1. **Hugging Face** (官方推荐)
   ```bash
   # 使用 huggingface-cli
   pip install huggingface-hub
   huggingface-cli download runwayml/stable-diffusion-v1-5
   ```

2. **Civitai** (社区模型)
   - 网站: https://civitai.com
   - 下载 `.safetensors` 模型文件
   - 放入 InvokeAI 的 models 目录

3. **InvokeAI 内置**
   - WebUI → Models → Starter Models
   - 一键安装官方推荐模型

---

## 提示词工程基础

### 基础结构

```
[主体], [细节描述], [风格], [质量词]
```

**示例：**
```
a red fox sitting in a snowy forest, detailed fur, golden hour lighting, 
digital painting, highly detailed, 8k, masterpiece
```

### 常用质量词

| 类别 | 词汇 |
|------|------|
| **质量** | masterpiece, best quality, highly detailed, 8k, sharp focus |
| **风格** | digital art, oil painting, anime style, photorealistic |
| **负面** | blurry, low quality, deformed, bad anatomy, watermark |

### InvokeAI 提示词技巧

- 支持权重语法: `(word:1.2)` 增强, `(word:0.8)` 减弱
- 支持 Attention: `[word]` 减弱, `(word)` 增强
- 使用 Dynamic Prompts 随机组合

---

## 性能优化

### Apple Silicon 优化

```yaml
# invokeai.yaml 配置
use_cpu: false
precision: float16      # MPS 推荐
max_cache_size: 6       # 根据内存调整 (GB)
```

### 低内存模式

```yaml
# invokeai.yaml
low_vram: true          # 显存不足时启用
sequential_guidance: true  # 降低内存占用
```

### 生成速度对比

| 配置 | SD 1.5 512x512 | SDXL 1024x1024 |
|------|---------------|----------------|
| M1 8GB | 2-3 min | 5-8 min |
| M1 Pro 16GB | 30-60 sec | 2-3 min |
| M2 Pro 24GB | 15-30 sec | 1-2 min |

---

## 常见问题解决

### 1. MPS 后端报错

**现象**: `MPS backend out of memory`

**解决**:
```bash
# 重启 Python 进程释放内存
# 降低分辨率或 batch size
# 启用低内存模式
```

### 2. 模型加载失败

**现象**: `safetensors` 相关错误

**解决**:
```bash
# 更新 safetensors
pip install -U safetensors

# 重新下载模型（可能文件损坏）
```

### 3. Python 版本冲突

**现象**: `InvokeAI 不支持 Python 3.13`

**解决**:
```bash
# 安装 Python 3.11
brew install python@3.11

# 使用 pyenv
pyenv install 3.11.9
pyenv local 3.11.9
```

### 4. 端口被占用

**现象**: `Address already in use`

**解决**:
```bash
# 更换端口
invokeai-web --port 9090
```

---

## 最佳实践

### 1. 首次使用建议

1. 先安装 SD 1.5 模型（最小、最快）
2. 生成几张测试图熟悉界面
3. 再尝试 SDXL 和复杂工作流
4. 保存成功的工作流模板

### 2. 项目管理

```
~/invokeai/
├── models/          # 模型文件
├── outputs/         # 生成的图片
├── workflows/       # 保存的工作流
└── databases/       # 数据库（定期备份）
```

### 3. 定期维护

```bash
# 更新 InvokeAI
invokeai-update

# 清理缓存
uv cache clean

# 备份数据库
cp ~/invokeai/databases/invokeai.db ~/backup/
```

---

## 学习资源

- **InvokeAI 文档**: https://invoke-ai.github.io/InvokeAI
- **官方 Discord**: https://discord.gg/ZmtBAhwWhy
- **入门视频**: YouTube 搜索 "InvokeAI Getting Started"
- **模型社区**: https://civitai.com

---

## 参考来源

基于 InvokeAI 官方文档和最佳实践整理：
- https://github.com/invoke-ai/InvokeAI
- https://invoke-ai.github.io/InvokeAI/installation/

License: Apache-2.0 (InvokeAI)
