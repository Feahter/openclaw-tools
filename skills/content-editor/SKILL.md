---
name: content-editor
title: Content Editor - Manuscript Polishing & Enhancement
version: 1.0.0
description: 审稿润色系统，支持语言润色、逻辑检查、结构优化、风格统一、错别字修正，可联动内容生成系统
tags: ["内容编辑", "proofreading", "editing", "polishing", "text-enhancement", "错别字检查", "润色", "审稿", "逻辑检查"]
metadata:
  author_name: "OpenClaw System"
  author_role: "Writing Quality Assurance"
  supported_platforms:
    - "通用文本"
    - "Markdown"
    - "Word/DOCX"
    - "协作平台"
  supported_content_types:
    - "小说章节"
    - "文章段落"
    - "营销文案"
    - "技术文档"
    - "学术稿件"
  features:
    - "语言润色优化"
    - "逻辑一致性检查"
    - "结构节奏把控"
    - "风格统一调整"
    - "错别字/语法检查"
    - "内容生成联动"
---

# 文稿润色师 (Content Editor)

专业审稿润色工具，从语言、逻辑、结构、风格四个维度全面提升文稿质量，支持自动化检查和人工审核结合。

## 适用场景

- **小说审稿**：章节润色、对话优化、描写增强
- **文章编辑**：博客/公众号文章的语言优化
- **营销文案**：标题优化、卖点提炼、转化率提升
- **技术文档**：表达清晰化、专业术语规范化
- **学术论文**：逻辑严谨性、格式规范性
- **翻译校对**：译文润色、本地化优化
- **内容改写**：风格转换、篇幅调整

## 核心功能

### 1. 语言润色

| 润色类型 | 功能说明 | 输出效果 |
|---------|---------|---------|
| **用词优化** | 同义词替换、词汇升级 | 更精准/更生动 |
| **句式调整** | 主动/被动、长短句变换 | 更流畅/节奏感 |
| **冗余删除** | 重复表达、废话去除 | 更精炼 |
| **表达升级** | 平淡→精彩、朴素→华丽 | 更吸引人 |
| **口语化** | 调整语气、更自然 | 更亲切 |
| **正式化** | 调整措辞、更专业 | 更严谨 |

### 2. 逻辑检查

- **前后一致**：人物设定、时间线、事件顺序
- **因果合理**：逻辑链条、推理连贯
- **因果谬误**：倒因为果、强加因果
- **自相矛盾**：观点冲突、设定打架
- **逻辑漏洞**：论据不足、以偏概全
- **节奏合理性**：情节发展是否过快/过慢

### 3. 结构优化

```
结构检查维度：
├── 段落层面
│   ├── 段落主题清晰度
│   ├── 段落衔接流畅度
│   ├── 段落长度合理性
├── 章节层面
│   ├── 章节划分合理性
│   ├── 章节过渡自然度
│   ├── 重点章节占比
└── 整体层面
    ├── 开头吸引力
    ├── 中段充实度
    └── 结尾完整性
```

### 4. 风格统一

- **全文风格一致**：确保无风格突变
- **人称视角统一**：避免视角跳变
- **时态一致**：避免时态混乱
- **用词统一**：同义词使用规范
- **语气统一**：全书/全文语气协调
- **格式规范**：标题、标点、段落格式统一

### 5. 错别字/语法检查

- **错别字检测**：同音字、形近字错误
- **语法错误**：主谓搭配、成分残缺
- **标点规范**：全半角、标点使用
- **格式规范**：空格、换行、缩进
- **专有名词**：人名/地名/术语一致性

## 核心工具/命令

### 基础润色命令

```bash
# 全文润色
polish full --file=manuscript.md --level=standard --output=polished.md

# 轻度润色
polish light --file=chapter.md --focus=grammar_style --preserve_voice=true

# 深度润色
polish deep --file=novel.md --level=comprehensive --enhancement=all

# 指定维度润色
polish --file=article.md --focus=vocabulary --tone=professional
polish --file=story.md --focus=dialogue --style=natural
polish --file=essay.md --focus=logic --check_consistency=true
```

### 分项检查命令

```bash
# 错别字检查
check typos --file=manuscript.md --output=typos_report.md --auto_fix=false
check typos --file=chapter.md --types=homophone,visual --auto_fix=true

# 语法检查
check grammar --file=text.md --categories=all --severity=high
check grammar --file=dialogue.md --focus=conversational --report=grammar.yaml

# 逻辑检查
check logic --file=plot.md --aspects=causality,consistency,coherence
check logic --file=character.md --consistency=character_traits

# 风格检查
check style --file=manuscript.md --style_guide=literary --deviations=true
check style --file=article.md --focus=voice,tense,perspective

# 结构检查
check structure --file=chapter.md --level=scene --balance=true
check structure --file=novel.md --aspects=pacing,transitions,proportion
```

### 优化增强命令

```bash
# 语言增强
enhance language --file=draft.md --techniques=metaphor,imagery,sensory
enhance language --file=flat.md --target=vivid --level=moderate

# 节奏优化
optimize pacing --file=chapter.md --action=adjust --target=suspense
optimize pacing --file=slow_section.md --action=speed_up --ratio=20%

# 对话优化
optimize dialogue --file=script.md --style=natural --subtext=true
optimize dialogue --file=stiff_dialogue.md --character_voice=true

# 描写增强
enhance description --file=scene.md --type=sensory --detail_level=high
enhance description --file=flat_scene.md --target=immersive --techniques=all

# 开头优化
optimize opening --file=chapter.md --target=hook --type=question_mystery
optimize opening --file=essay.md --type=compelling --technique=contrast
```

### 风格转换命令

```bash
# 风格转换
transform style --from=casual --to=formal --file=blog.md --preserve_meaning=true
transform style --from=dry --to=engaging --file=technical.md --examples=true

# 语气调整
adjust tone --file=email.md --tone=professional --level=moderate
adjust tone --file=article.md --tone=humorous --preservation=meaning

# 篇幅调整
adjust length --file=long.md --target=short --method=condense --ratio=30%
adjust length --file=short.md --target=expanded --method=elaborate --ratio=50%
```

### 批处理命令

```bash
# 批量文件检查
batch check --pattern="chapters/*.md" --types=typos,grammar,logic

# 批量润色
batch polish --pattern="drafts/*.md" --level=light --output=polished/

# 全文一致性检查
consistency check --file=novel.md --aspects=characters,locations,timeline

# 生成润色报告
report polish --file=manuscript.md --format=detailed --output=polish_report.md
```

### 内容生成联动

```bash
# 联动 auto-content-creator 生成内容
generate content --source=polish_notes --type=missing_section --context=manuscript

# 根据润色建议生成改写
rewrite --based_on=suggestions --style=improved --file=flat_paragraph.md

# 扩展不足章节
expand section --file=weak_chapter.md --target_length=3000 --style=consistent

# 补全遗漏情节
fill gap --file=plot.md --missing=scene --context=before_after --style=author_voice
```

## 配置说明

### 配置文件位置

```
~/.openclaw/config/content-editor.yaml
```

### 基础配置

```yaml
# 基础设置
output:
  base_path: ~/content-output
  polished_folder: polished
  reports_folder: reports
  backup_folder: backups

# 默认设置
defaults:
  language: zh
  polish_level: standard
  auto_fix_typos: false
  preserve_style: true
```

### 润色配置

```yaml
polishing:
  # 润色级别
  levels:
    light:
      focus: [grammar, typos]
      preserve: [voice, style]
      enhancement: minimal
    standard:
      focus: [grammar, typos, style, flow]
      preserve: [voice]
      enhancement: moderate
    deep:
      focus: [all]
      preserve: []
      enhancement: comprehensive
  
  # 润色选项
  options:
    vocabulary_upgrade: true
    sentence_variety: true
    redundancy_removal: true
    transition_improvement: true
    dialogue_naturalization: true
```

### 检查配置

```yaml
checking:
  # 错别字检查
  typos:
    enabled: true
    auto_fix: false
    types:
      homophone: true
      visual: true
      missing_char: true
  
  # 语法检查
  grammar:
    enabled: true
    categories:
      syntax: true
      punctuation: true
      formatting: true
  
  # 逻辑检查
  logic:
    enabled: true
    aspects:
      causality: true
      consistency: true
      coherence: true
    severity: warning
  
  # 风格检查
  style:
    enabled: true
    guide: literary
    deviations: report
```

### 风格配置

```yaml
style:
  # 预设风格
  presets:
    literary:
      vocabulary: elevated
      sentence: varied
      tone: formal
      imagery: rich
    casual:
      vocabulary: accessible
      sentence: short
      tone: friendly
      imagery: light
    technical:
      vocabulary: precise
      sentence: clear
      tone: objective
      imagery: minimal
  
  # 自定义风格
  custom:
    author_voice:
      vocabulary: [specific_words]
      phrases: [characteristic_expressions]
      rhythm: [pattern]
```

### 生成联动配置

```yaml
generation:
 联动:
    auto_content_creator:
      enabled: true
      template: polish_expansion
      style_match: true
    detail_painter:
      enabled: true
      techniques: sensory,emotional
```

## 使用示例

### 示例 1：小说章节润色

```bash
# 章节全文润色
polish full --file=chapters/chapter_5.md --level=deep --output=chapters/chapter_5_polished.md

# 对话优化
polish --file=chapters/chapter_5.md --focus=dialogue --subtext=true --output=dialogue_polished.md

# 场景描写增强
enhance description --file=chapters/chapter_5.md --type=sensory --detail_level=high

# 逻辑检查
check logic --file=chapters/chapter_5.md --aspects=character_consistency,timeline

# 错别字检查
check typos --file=chapters/chapter_5.md --auto_fix=true
```

### 示例 2：营销文案优化

```bash
# 标题优化
enhance title --file=headlines.txt --target=click_rate --variations=5

# 正文润色
polish --file=ad_copy.md --focus=persuasive --tone=urgent --output=ad_copy_polished.md

# 卖点提炼
extract selling_points --file=product_desc.md --count=3 --style=compelling

# 转化优化
optimize cta --file=landing_page.md --button_text=true --urgency=true
```

### 示例 3：技术文档规范化

```bash
# 专业术语检查
check terminology --file=tech_doc.md --glossary=./tech_terms.yaml

# 逻辑清晰度
optimize clarity --file=technical.md --target=beginner --explanations=true

# 格式规范化
format document --file=tech_doc.md --style=technical --toc=true --numbering=true

# 一致性检查
consistency check --file=tech_doc.md --aspects=terminology,formatting,abbreviations
```

### 示例 4：长篇小说全局检查

```bash
# 全文错别字扫描
batch check --pattern="chapters/*.md" --types=typos --output=typos_all.yaml

# 人物一致性检查
check character_consistency --file=novel.md --aspects=name,traits,backstory

# 时间线检查
check timeline --file=novel.md --format=linear --conflicts=true

# 风格统一检查
check style --file=novel.md --aspects=voice,tense,perspective

# 生成润色报告
report polish --file=novel.md --format=comprehensive --output=polish_plan.yaml
```

### 示例 5：风格转换

```bash
# 学术→通俗
transform style --from=academic --to=accessible --file=thesis_intro.md --examples=true

# 严肃→轻松
adjust tone --file=press_release.md --tone=casual --level=moderate --preserve_key_points

# 篇幅压缩
adjust length --file=long_article.md --target=short --method=condense --ratio=40%
```

## 与其他 Skills 的配合

| 场景 | 使用 Skill |
|------|-----------|
| 润色前审稿 | `blade-of-logic` (逻辑分析) |
| 细节描写增强 | `detail-painter` |
| 基于设定生成内容 | `auto-content-creator` |
| 素材收集参考 | `material-collector` |
| 浏览器查证 | `browser-automation` |
| 创作前规划 | `story-architect` |

## 注意事项

1. **保留原意**：润色不改变文章核心观点和情节
2. **风格一致**：改写要符合原文风格和作者声音
3. **人工审核**：自动润色结果建议人工复核
4. **备份原文**：润色前先备份原文
5. **适度原则**：不是所有文章都需要深度润色
6. **场景匹配**：不同类型文章润色标准不同

## 输出位置

所有润色内容保存在 `~/content-output/` 目录：
- 润色后文件：`polished/`
- 检查报告：`reports/`
- 原文备份：`backups/`
- 润色配置：`config/`
- 日志：`logs/content-editor.log`
