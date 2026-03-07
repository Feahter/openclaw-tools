---
name: auto-content-creator
title: Auto Content Creator - AI-Powered Content Generation
version: 1.0.0
description: 基于素材自动生成内容，支持多种创作类型、模板风格管理、一键发布到多平台
tags: ["自动化创作", "content-generation", "ai-writing", "content-automation", "template-management", "multi-platform-publishing", "文案生成", "内容创作"]
metadata:
  author_name: "OpenClaw System"
  author_role: "Content Workflow Automation"
  supported_platforms:
    - "Twitter/X"
    - "WeChat/微信公众号"
    - "Weibo/微博"
    - "Feishu/Lark"
    - "Telegram"
    - "Medium"
    - "WordPress"
    - "Bilibili"
  supported_content_types:
    - "社交媒体帖子"
    - "博客文章"
    - "视频脚本"
    - "图文排版"
    - "营销文案"
    - "产品描述"
  features:
    - "智能内容生成"
    - "多模板支持"
    - "风格自定义"
    - "批量创作"
    - "一键发布"
---

# 自动化创作系统 (Auto Content Creator)

基于素材库智能生成多样化内容，支持模板管理、风格定制和多平台一键发布。

## 适用场景

- **社交媒体运营**：自动生成 Twitter/X、微博、微信推文
- **内容营销**：批量生成营销文案、产品描述、广告语
- **视频创作**：自动生成 BiliBili、YouTube 视频脚本
- **博客写作**：基于素材自动撰写博客文章
- **图文排版**：生成配图文案和排版建议
- **跨平台适配**：一键生成适配多平台的内容版本

## 核心功能

### 1. 智能内容生成

| 生成类型 | 输入要求 | 输出格式 |
|---------|---------|---------|
| **社交帖子** | 素材+主题 | 推文/短文（带标签） |
| **博客文章** | 素材+大纲 | 完整文章（Markdown） |
| **视频脚本** | 素材+风格 | 分镜脚本+旁白 |
| **营销文案** | 产品信息+卖点 | 多版本文案 |
| **图文配文** | 图片+主题 | 配文+话题标签 |
| **产品描述** | 产品信息 | SEO优化描述 |

### 2. 模板管理系统

```
模板库结构：
├── templates/
│   ├── social/
│   │   ├── twitter-casual.yaml
│   │   ├── twitter-professional.yaml
│   │   ├── wechat-article.yaml
│   │   └── weibo-trending.yaml
│   ├── blog/
│   │   ├── tutorial.yaml
│   │   ├── review.yaml
│   │   ├── listicle.yaml
│   │   └── case-study.yaml
│   ├── video/
│   │   ├── tutorial-script.yaml
│   │   ├── vlog.yaml
│   │   └── product-demo.yaml
│   └── marketing/
│       ├── ad-copy.yaml
│       ├── product-desc.yaml
│       └── email-marketing.yaml
├── styles/
│   ├── professional.yaml
│   ├── casual.yaml
│   ├── humorous.yaml
│   └── inspirational.yaml
└── custom/
    └── (用户自定义模板)
```

### 3. 风格定制引擎

支持自定义内容风格，与模板配合使用：

| 风格类型 | 特点 | 适用场景 |
|---------|------|---------|
| **专业正式** | 严谨用词、逻辑清晰 | 技术博客、行业分析 |
| **轻松随和** | 口语化、幽默 | 社交媒体、日常分享 |
| **激励鼓舞** | 正能量、情感化 | 品牌宣传、励志内容 |
| **简洁高效** | 短句、重点突出 | 新闻简报、产品更新 |
| **故事叙事** | 叙事结构、情节 | 品牌故事、案例分享 |

### 4. 一键发布系统

```
发布流程：
素材输入 → 内容生成 → 预览确认 → 格式适配 → 一键发布 → 结果反馈
```

支持平台：
- **Twitter/X**：自动配图、话题标签、字符限制
- **微信公众号**：Markdown 转换、封面图、摘要
- **微博**：长文/短文、话题、热搜词
- **Feishu**：文档发布、飞书文章
- **Telegram**：频道发布、格式化
- **Medium**：专业排版、标签系统
- **WordPress**：草稿/发布、分类、标签
- **Bilibili**：稿件投稿、专栏文章

## 核心工具/命令

### 内容生成命令

```bash
# 社交媒体帖子
generate post --type=twitter --素材=design-materials --style=casual --length=short
generate post --type=wechat --素材=product-info --style=professional --length=long

# 博客文章
generate blog --topic="AI发展趋势" --素材=ai-news --template=tutorial --words=2000
generate blog --outline="要点" --素材=reference --template=case-study --structure=markdown

# 视频脚本
generate script --topic="产品评测" --素材=product-demo --style=engaging --duration=10min
generate script --theme="科技趋势" --素材=tech-news --template=vlog --sections=5

# 营销文案
generate marketing --type=ad-copy --product="新产品" --卖点=3 --cta=true
generate marketing --type=product-desc --product="产品A" --features --seo_optimized

# 图文配文
generate social-image --images=./photos/ --theme=旅行 --platform=instagram --with_hashtags

# 批量生成
batch generate --type=posts --素材=week-materials --count=7 --schedule=daily
```

### 模板管理命令

```bash
# 列出模板
template list --category=blog --detailed=true
template list --style=professional --platform=twitter

# 使用模板
template use twitter-casual --素材=inspiration --output=tweet.md

# 创建模板
template create --name=my-template --category=social --base=twitter-casual.yaml
template create --interactive=true --引导创建

# 编辑模板
template edit my-template --修改配置
template test my-template --test_input=sample.md

# 导入/导出模板
template export my-template --dest=./backups/
template import ./template.yaml --category=custom
```

### 风格管理命令

```bash
# 风格设置
style set --name=professional --config=./styles/pro.yaml
style set --name=casual --preset=friendly

# 风格预览
style preview professional --sample_topic=AI
style compare --style1=professional --style2=casual --topic=产品发布

# 自定义风格
style create --name=brand-voice --tone=创新 --vocabulary=tech-terms --examples=./brand-posts.txt
```

### 发布命令

```bash
# 单平台发布
publish twitter --file=tweet.md --schedule=now --images=./cover.png
publish wechat --file=article.md --title="标题" --cover=./cover.jpg --draft=false
publish medium --file=post.md --tags=AI,Tech --status=draft

# 多平台同步发布
publish multi --file=content.md --platforms=twitter,weibo,medium --auto_format=true

# 定时发布
schedule publish --file=post.md --platforms=wechat --time="2026-02-14 09:00:00"

# 发布预览
preview publish --platform=twitter --file=tweet.md --check_length=true
preview publish --platform=wechat --file=article.md --check_images=true

# 发布历史
publish history --platform=twitter --days=7
publish status --platform=wechat --article_id=xxx
```

### 素材整合命令

```bash
# 从素材库选择
素材 select --source=material-collector --tags=设计,灵感 --type=images --limit=10

# 素材预处理
素材 process --from=raw/ --resize_images=true --extract_text=true

# 素材与内容关联
素材 link --content=post.md --materials=images/ --layout=horizontal
```

## 配置说明

### 配置文件位置

```
~/.openclaw/config/auto-content-creator.yaml
```

### 基础配置

```yaml
# 基础设置
output:
  base_path: ~/content-output
  drafts_folder: drafts
  published_folder: published
  templates_folder: templates
  styles_folder: styles

# 默认设置
defaults:
  language: zh
  style: professional
  platform: twitter
  length: medium
```

### 模板配置

```yaml
templates:
  default_folder: ~/content-output/templates
  custom_folder: ~/content-output/templates/custom
  auto_save: true
  version_control: true

  # 模板变量
  variables:
    - name: title
      required: true
    - name: author
      default: "作者"
    - name: date
      auto: today
```

### 发布配置

```yaml
publishing:
  # 平台认证
  platforms:
    twitter:
      api_key: ${TWITTER_API_KEY}
      api_secret: ${TWITTER_API_SECRET}
      access_token: ${TWITTER_ACCESS_TOKEN}
      access_secret: ${TWITTER_ACCESS_SECRET}
    
    wechat:
      app_id: ${WECHAT_APP_ID}
      app_secret: ${WECHAT_APP_SECRET}
    
    medium:
      integration_token: ${MEDIUM_TOKEN}
    
    feishu:
      app_id: ${FEISHU_APP_ID}
      app_secret: ${FEISHU_APP_SECRET}
  
  # 发布设置
  auto_format: true
  max_retries: 3
  retry_delay: 5
```

### 生成配置

```yaml
generation:
  # AI 模型
  model: gpt-4
  temperature: 0.7
  max_tokens: 2000
  
  # 内容设置
  auto_hashtags: true
  max_hashtags: 5
  auto_emoji: false
  
  # SEO 设置
  seo_optimization: true
  keyword_extraction: true
```

### 风格配置

```yaml
styles:
  professional:
    tone: formal
    vocabulary: technical
    sentence_length: medium
    emoji: false
    hashtags: false
  
  casual:
    tone: friendly
    vocabulary: casual
    sentence_length: short
    emoji: true
    hashtags: true
  
  custom_styles:
    brand_voice:
      tone: innovative
      keywords:
        - 创新
        - 突破
        - 引领
      banned_words:
        - 便宜
        - 打折
```

## 使用示例

### 示例 1：生成一周社交媒体内容

```bash
# 设置素材来源
素材 select --source=material-collector --tags=本周热点 --type=all

# 批量生成
batch generate --type=posts --素材=selected --count=7 \
  --template=twitter-casual --style=friendly --schedule=daily

# 预览和修改
for i in {1..7}; do
  preview publish --platform=twitter --file=drafts/day${i}.md
done

# 一周发布
publish multi --platforms=twitter,weibo --schedule=week
```

### 示例 2：创建产品发布博客

```bash
# 收集素材
素材 select --source=material-collector --tags=产品,发布 --type=images,text

# 生成文章
generate blog --topic="产品X发布" \
  --素材=product-materials \
  --template=tutorial \
  --style=professional \
  --words=3000

# 生成配套社交媒体
generate social-image --images=product-screenshots --platform=twitter
generate post --type=twitter --素材=product-news --length=short

# 发布到多平台
publish multi --files=article.md,tweet.md,cover.png \
  --platforms=medium,wordpress,twitter
```

### 示例 3：视频脚本创作

```bash
# 收集相关素材
素材 select --source=material-collector --tags=教程,软件 --type=videos,text

# 生成脚本
generate script --topic="新手入门指南" \
  --素材=tutorial-materials \
  --style=engaging \
  --duration=15min \
  --sections=5

# 生成配套图文
generate social-image --images=screenshots --theme=教程 --platform=bilibili

# 发布到 Bilibili 和 YouTube
publish bilibili --file=script.md --title="新手入门完整指南" --tags=教程,入门
publish youtube --file=script.md --title="Complete Beginner's Guide" --tags=tutorial
```

### 示例 4：营销活动文案

```bash
# 收集品牌素材
素材 select --source=material-collector --tags=品牌,活动 --type=all

# 生成多版本营销文案
generate marketing --type=ad-copy \
  --product="春季促销" \
  --素材=campaign-materials \
  --variations=5 \
  --cta=true

# 生成配套社交媒体
generate post --type=post \
  --素材=campaign \
  --template=weibo-trending \
  --hashtags=true

# 排期发布
schedule publish --platforms=twitter,weibo,wechat \
  --start_date="2026-03-01" \
  --frequency=daily \
  --posts_per_day=3
```

## 与其他 Skills 的配合

| 场景 | 使用 Skill |
|------|-----------|
| 收集素材 | `material-collector` |
| 素材创作 | `auto-content-creator` |
| 浏览器操作 | `browser-automation` |
| 定时发布 | `cron-scheduling` |
| X平台发布 | `x-post-automation` |
| 图片生成 | `macos-image-generation` |
| 设计资源 | `design-resources-for-developers` |

## 注意事项

1. **版权合规**：确保生成内容不侵犯版权
2. **平台规则**：遵守各平台的内容政策
3. **人工审核**：重要发布建议先预览确认
4. **数据统计**：发布后跟踪数据表现
5. **持续优化**：根据反馈调整风格和模板

## 输出位置

所有生成内容保存在 `~/content-output/` 目录：
- 草稿：`drafts/`
- 已发布：`published/`
- 模板：`templates/`
- 样式：`styles/`
- 日志：`logs/generation.log`
