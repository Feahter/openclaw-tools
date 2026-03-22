#!/usr/bin/env python3
"""
LTX Video Generator - fal.ai 版本
用法: python3 generate.py "视频描述（英文）" [输出路径]
"""
import os, sys, json, urllib.request, urllib.error, time

FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    print("❌ 未设置 FAL_KEY\n请运行: export FAL_KEY=your_key")
    sys.exit(1)

def generate(prompt, output_path=None, steps=30, guidance=3, negative=None, seed=None):
    if output_path is None:
        output_path = os.path.expanduser(f"~/Downloads/ltx_{int(time.time())}.mp4")
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative or "low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly",
        "num_inference_steps": steps,
        "guidance_scale": guidance,
    }
    if seed: payload["seed"] = seed
    
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    
    print(f"🎬 提交请求...")
    req = urllib.request.Request(
        "https://queue.fal.run/fal-ai/ltx-video",
        data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            request_id = json.loads(r.read())["request_id"]
        print(f"✅ ID: {request_id}")
    except urllib.error.HTTPError as e:
        print(f"❌ 失败: {e.code} {e.read().decode()}"); sys.exit(1)
    
    status_url = f"https://queue.fal.run/fal-ai/ltx-video/requests/{request_id}/status"
    print("⏳ 生成中...", end="", flush=True)
    for i in range(72):
        time.sleep(5)
        with urllib.request.urlopen(urllib.request.Request(status_url, headers=headers)) as r:
            s = json.loads(r.read())["status"]
        if s == "COMPLETED": print(" ✅"); break
        elif s == "FAILED": print(f"\n❌ 失败"); sys.exit(1)
        else: print(".", end="", flush=True)
    
    with urllib.request.urlopen(urllib.request.Request(
        f"https://queue.fal.run/fal-ai/ltx-video/requests/{request_id}", headers=headers)) as r:
        video_url = json.loads(r.read())["video"]["url"]
    
    print(f"⬇️  下载中...")
    urllib.request.urlretrieve(video_url, output_path)
    print(f"✅ 保存: {output_path}")
    print(f"🔗 URL: {video_url}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 generate.py '英文描述' [输出路径.mp4]")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
