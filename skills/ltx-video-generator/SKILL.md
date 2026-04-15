---
name: ltx-video-generator
description: |
  LTX 视频生成工具。根据文本描述生成视频，支持 fal.ai 和 Replicate 两个云端 API。
  触发场景：
  - "帮我生成一个视频"、"生成视频"、"文生视频"
  - "用 LTX 生成"、"生成一段..."
  - "把这段描述变成视频"
  需要配置 FAL_KEY 或 REPLICATE_API_TOKEN 环境变量。
---

# ltx-video-generator

基于 LTX-Video 模型，通过云端 API 实现文本直出视频。

## API 选择

| 平台 | 费用 | 速度 | 推荐场景 |
|------|------|------|---------|
| **fal.ai** | ~$0.02/次 | ~30s | 首选，便宜快 |
| **Replicate** | ~$0.024/次 | ~25s | 备选 |

## 环境变量配置

```bash
# fal.ai（推荐）
export FAL_KEY="your_fal_api_key"

# 或 Replicate
export REPLICATE_API_TOKEN="your_replicate_token"
```

获取 API Key：
- fal.ai：https://fal.ai/dashboard/keys
- Replicate：https://replicate.com/account/api-tokens

## 使用流程

### Step 1: 检查 API Key

```bash
# 检查哪个 key 可用
if [ -n "$FAL_KEY" ]; then
  echo "使用 fal.ai"
elif [ -n "$REPLICATE_API_TOKEN" ]; then
  echo "使用 Replicate"
else
  echo "❌ 未配置 API Key，请先设置 FAL_KEY 或 REPLICATE_API_TOKEN"
  exit 1
fi
```

### Step 2: 优化 Prompt

LTX 对 prompt 质量敏感，生成前先优化用户输入：

**好的 prompt 结构：**
```
[主体动作] + [具体动作细节] + [外观描述] + [环境背景] + [镜头角度] + [光线色彩]
```

**示例转换：**
- 用户输入：`一只猫在草地上玩耍`
- 优化后：`A fluffy orange tabby cat playfully chases a butterfly across a sunlit meadow. The cat leaps and swipes at the butterfly with its paws, its tail swishing with excitement. The meadow is filled with tall green grass and wildflowers in yellow and purple. The camera follows the cat at ground level, capturing its agile movements. Warm afternoon sunlight filters through the scene, casting long shadows across the grass.`

**优化规则：**
1. 必须用英文
2. 描述要具体，不超过 200 词
3. 包含：动作 + 外观 + 环境 + 镜头 + 光线
4. 从动作开始，不要用"A video of..."开头

### Step 3: 调用 API

#### 方案 A：fal.ai（推荐）

```python
#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
import time

FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    print("❌ 未设置 FAL_KEY")
    sys.exit(1)

def generate_video_fal(prompt, output_path=None, **kwargs):
    """
    调用 fal.ai LTX-Video API 生成视频
    
    参数：
    - prompt: 视频描述（英文）
    - output_path: 保存路径，默认 ~/Downloads/ltx_output.mp4
    - num_inference_steps: 推理步数，默认 30（质量/速度平衡）
    - guidance_scale: 引导强度，默认 3（3-5 创意，5-7 精确）
    - negative_prompt: 负面提示词
    - seed: 随机种子（可复现）
    """
    
    if output_path is None:
        output_path = os.path.expanduser(f"~/Downloads/ltx_{int(time.time())}.mp4")
    
    # 构建请求
    payload = {
        "prompt": prompt,
        "negative_prompt": kwargs.get("negative_prompt", 
            "low quality, worst quality, deformed, distorted, disfigured, "
            "motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly"),
        "num_inference_steps": kwargs.get("num_inference_steps", 30),
        "guidance_scale": kwargs.get("guidance_scale", 3),
    }
    if "seed" in kwargs:
        payload["seed"] = kwargs["seed"]
    
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"🎬 提交生成请求...")
    print(f"   Prompt: {prompt[:80]}...")
    
    # 提交请求
    req = urllib.request.Request(
        "https://queue.fal.run/fal-ai/ltx-video",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            request_id = result["request_id"]
            print(f"✅ 请求已提交，ID: {request_id}")
    except urllib.error.HTTPError as e:
        print(f"❌ 提交失败: {e.code} {e.read().decode()}")
        sys.exit(1)
    
    # 轮询状态
    print("⏳ 等待生成中...")
    status_url = f"https://queue.fal.run/fal-ai/ltx-video/requests/{request_id}/status"
    
    for i in range(60):  # 最多等 5 分钟
        time.sleep(5)
        req = urllib.request.Request(status_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            status = json.loads(resp.read())
        
        state = status.get("status")
        if state == "COMPLETED":
            print("✅ 生成完成！")
            break
        elif state == "FAILED":
            print(f"❌ 生成失败: {status}")
            sys.exit(1)
        else:
            print(f"   状态: {state} ({i*5}s)")
    
    # 获取结果
    result_url = f"https://queue.fal.run/fal-ai/ltx-video/requests/{request_id}"
    req = urllib.request.Request(result_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    
    video_url = result["video"]["url"]
    print(f"🎥 视频 URL: {video_url}")
    
    # 下载视频
    print(f"⬇️  下载到: {output_path}")
    urllib.request.urlretrieve(video_url, output_path)
    print(f"✅ 保存成功: {output_path}")
    
    return output_path, video_url

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate.py '视频描述'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    path, url = generate_video_fal(prompt, output)
    print(f"\n🎬 完成！")
    print(f"   本地路径: {path}")
    print(f"   在线 URL: {url}")
```

#### 方案 B：Replicate

```python
#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import time

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
MODEL_VERSION = "lightricks/ltx-video"

def generate_video_replicate(prompt, output_path=None, **kwargs):
    headers = {
        "Authorization": f"Bearer {REPLICATE_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    
    payload = {
        "input": {
            "prompt": prompt,
            "num_inference_steps": kwargs.get("num_inference_steps", 30),
            "guidance_scale": kwargs.get("guidance_scale", 3),
        }
    }
    
    req = urllib.request.Request(
        f"https://api.replicate.com/v1/models/{MODEL_VERSION}/predictions",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    
    # 轮询
    prediction_url = result["urls"]["get"]
    for _ in range(60):
        time.sleep(5)
        req = urllib.request.Request(prediction_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            status = json.loads(resp.read())
        if status["status"] == "succeeded":
            video_url = status["output"]
            break
        elif status["status"] == "failed":
            raise Exception(f"生成失败: {status['error']}")
    
    if output_path is None:
        output_path = os.path.expanduser(f"~/Downloads/ltx_{int(time.time())}.mp4")
    
    urllib.request.urlretrieve(video_url, output_path)
    return output_path, video_url
```

### Step 4: 执行生成

```bash
# 保存脚本到临时目录
cat > /tmp/ltx_generate.py << 'EOF'
[上面的 generate_video_fal 代码]
EOF

# 执行
python3 /tmp/ltx_generate.py "你的视频描述"
```

### Step 5: 打开视频

```bash
# macOS
open ~/Downloads/ltx_*.mp4

# 或用 QuickTime
open -a "QuickTime Player" ~/Downloads/ltx_*.mp4
```

## Prompt 优化模板

用户输入中文时，先翻译并扩展：

```
用户说：[中文描述]

优化为英文 prompt，包含：
1. 主体 + 核心动作（1句）
2. 动作细节（1-2句）
3. 外观/环境描述（1-2句）
4. 镜头运动（1句）
5. 光线/色彩（1句）

总长度：100-200词
```

## 参数调优

| 场景 | guidance_scale | num_inference_steps |
|------|---------------|---------------------|
| 快速预览 | 3 | 20 |
| 平衡（默认） | 3-4 | 30 |
| 高质量 | 5-6 | 40-50 |
| 精确还原 prompt | 6-7 | 40 |

## 费用估算

| 次数 | fal.ai | Replicate |
|------|--------|-----------|
| 1次 | $0.02 | $0.024 |
| 10次 | $0.20 | $0.24 |
| 100次 | $2.00 | $2.40 |

## 常见问题

**Q: 视频质量差？**
A: 提高 `num_inference_steps` 到 40+，`guidance_scale` 到 5-6

**Q: 视频不符合描述？**
A: Prompt 要更具体，用英文，描述要精确

**Q: 生成超时？**
A: 正常，fal.ai 约 30s，Replicate 约 25s，等待即可

**Q: API Key 在哪里配置？**
A: 运行 `export FAL_KEY=xxx` 或加入 `~/.zshrc`

## 注意事项

1. **Prompt 必须英文** — 中文效果差
2. **描述要具体** — 越详细越好
3. **视频时长** — 默认约 5 秒，768x512 分辨率
4. **版权** — 生成内容遵循 LTX OpenRail-M 许可
