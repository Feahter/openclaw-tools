---
name: story-architect
title: Story Architect - Novel Worldbuilding & Character Design
version: 1.0.0
description: 融合世界观设定、情节大纲、人物设计的创作系统，支持多种题材（科幻/奇幻/都市/历史）和素材库联动
tags: ["故事创作", "worldbuilding", "character-design", "novel-writing", "plot-architecture", "故事架构", "人物设计", "世界观", "创意写作"]
metadata:
  author_name: "OpenClaw System"
  author_role: "Creative Writing Assistant"
  supported_platforms:
    - "通用文本"
    - "Markdown"
    - "协作平台"
  supported_content_types:
    - "世界观设定"
    - "人物小传"
    - "情节大纲"
    - "故事线规划"
    - "冲突高潮设计"
  features:
    - "多题材世界观生成"
    - "情节架构设计"
    - "人物系统设计"
    - "冲突高潮规划"
    - "主题隐喻提取"
    - "素材库联动"
---

# 故事架构师 (Story Architect)

融合世界观设定、情节大纲与人物设计的全能创作系统，帮助作者从构思到落笔的系统化创作工具。

## 适用场景

- **小说创作**：长篇/短篇小说的世界观、人物、情节一体化设计
- **剧本编写**：影视/戏剧的故事架构、场景规划、人物动机
- **游戏策划**：游戏世界观、NPC设计、剧情线规划
- **同人创作**：基于原作的角色延展和新故事线设计
- **商业写作**：品牌故事、产品叙事、营销剧本
- **教学示例**：写作课程的故事范例和结构分析

## 核心功能

### 1. 世界观/背景设定生成

| 题材类型 | 核心要素 | 生成深度 |
|---------|---------|---------|
| **科幻** | 科技水平、文明形态、星际政治、时间线 | 硬科幻/软科幻可调 |
| **奇幻** | 魔法体系、种族设定、神祇体系、异世界 | 魔法/神学/低魔可调 |
| **都市** | 现代背景、行业设定、社会阶层、隐世规则 | 当代/近未来可调 |
| **历史** | 时代背景、社会制度、文化风俗、真实事件 | 古代/近代/架空 |
| **悬疑** | 背景氛围、案件设定、隐秘组织、线索布局 | 社会派/本格可调 |
| **言情** | 社交圈层、情感关系、职业背景、冲突设置 | 现代/民国/跨时空 |

### 2. 情节大纲架构

```
故事结构模型：
├── 三幕式结构
│   ├── 第一幕：建置（铺垫-触发-转折）
│   ├── 第二幕：对抗（发展-危机-高潮1）
│   └── 第三幕：解决（高潮2-结局-余韵）
├── 七点式结构
│   ├── 开场-铺垫-第二机会-高潮-结局
├── 英雄之旅
│   ├── 平凡世界-冒险召唤-拒绝召唤-导师出现-跨过门槛
└── 雪花模型
    ├── 核心句-段落扩写-角色扩展-场景卡片
```

### 3. 人物设计系统

```
人物档案结构：
├── 基础信息
│   ├── 姓名、年龄、外貌特征、职业
├── 性格维度
│   ├── MBTI/大五人格/九型人格
├── 内在驱动
│   ├── 核心动机、深层恐惧、价值观
├── 背景故事
│   ├── 成长经历、关键事件、秘密
├── 关系网络
│   ├── 亲人/爱人/敌人/盟友
└── 角色弧光
    ├── 起点-转折-终点
```

### 4. 冲突与高潮设计

- **内外冲突**：内心矛盾 vs 外部阻力
- **多线交织**：主线/副线/暗线的节奏把控
- **高潮设计**：情绪峰值点、转折设计、意外反转
- **节奏控制**：张弛有度、悬念铺垫、释放节奏

### 5. 主题与隐喻提取

- **核心主题**：故事要传达的思想/情感
- **象征体系**：意象、隐喻、预言、伏笔
- **多层解读**：表层叙事 vs 深层含义
- **一致性检查**：确保元素服务主题

## 核心工具/命令

### 世界观生成命令

```bash
# 生成科幻世界观
generate world --type=sci-fi --tech_level=hard --era=2300 --scope=galactic
generate world --type=sci-fi --ftl=true --ai_level=strong --society=utopia

# 生成奇幻世界观
generate world --type=fantasy --magic_system=hard --races=6 --pantheon=true
generate world --type=fantasy --magic=elemental --world_size=continent --history=3000

# 生成都市世界观
generate world --type=urban --setting=modern_china --hidden_society=true
generate world --type=urban --era=2020s --industry=tech --tension=class

# 生成历史世界观
generate world --type=historical --era=tang_dynasty --region=china --detail=culture
generate world --type=historical --era=ww2 --region=europe --aspect=military

# 扩展世界观细节
expand world --depth=geography --output=map_notes
expand world --depth=politics --output=factions
expand world --depth=economics --output=trade_routes
expand world --depth=culture --output=customs_religion
```

### 情节大纲命令

```bash
# 生成基础大纲
generate outline --type=novel --structure=three_act --chapters=30 --words=100000
generate outline --type=short_story --structure=hero_journey --sections=5

# 生成详细章节
outline chapter --chapter=5 --scenes=4 --points=conflict,revelation
outline chapter --chapter=12 --scenes=3 --points=betrayal,climax

# 生成故事线
generate storyline --main=primary --subplots=3 --timing=interweave
generate storyline --type=romance --arc=will_they_wont_they --episodes=10

# 冲突设计
design conflict --type=external --antagonist=organization --stakes=world
design conflict --type=internal --trigger=trauma --arc=redemption
design conflict --type=relationship --dynamic=estrangement --resolution=reunion

# 高潮设计
design climax --type=action --scale=epic --location=ruins
design climax --type=emotional --scene=catharsis --trigger=sacrifice
design climax --type=revelation --secret=identity --impact=high
```

### 人物设计命令

```bash
# ⚠️ 必须指定小说名（目录隔离）
# 参数: --novel=小说名

# 生成主角
create character --novel=重生带AI夯爆了 --role=protagonist --type=complex
create character --novel=重生之我是亿万富翁 --role=protagonist --archetype=everyman

# 人物校验（按小说隔离）
validate character --novel=重生带AI夯爆了 --chapter=17 --characters=陈默,林清雅
validate character --novel=重生之我是亿万富翁 --chapter=24 --characters=陈默,赵建国
```

# 生成配角
create character --role=sidekick --function=comic_relief --relationship=best_friend
create character --role=villain --motivation=revenge --method=manipulation
create character --role=mentor --ability=combat --personality=stern

# 人物详细设计
character design --name=林雨 --full_profile=true --tags=主角,成长型
character design --name=墨轩 --full_profile=true --tags=神秘,亦正亦邪

# 关系网络
network create --characters=林雨,墨轩,苏晚 --type=love_triangle
network create --characters=主角团队 --type=allies --bond_strength=strong

# 角色弧光
arc design --character=林雨 --arc=transformation --start=coward --end=hero --midpoint=betrayal
```

### 主题隐喻命令

```bash
# 主题提取
analyze theme --text=manuscript --output=core_themes
theme extract --symbolic_elements=true --hidden_meanings=true

# 隐喻设计
metaphor design --base=winter --correlates=despair,death,purification
metaphor design --base=journey --correlates=growth,change,quest

# 伏笔布局
foreshadowing plan --method=subtle --placement=chapters --frequency=every_5
foreshadowing plan --method=obvious --placement=prologue --callback=climax

# 一致性检查
consistency check --elements=theme,symbol,character --strict=true
```

### 素材库联动命令

```bash
# 从素材库获取参考
素材 select --source=material-collector --tags=参考,同类型 --type=text --limit=20

# 收集灵感素材
素材 collect --topic=魔法体系 --search=true --platform=web

# 存储创作素材
素材 save --type=character --name=墨轩 --metadata=profile.yaml
素材 save --type=world --name=青云大陆 --metadata=geography.yaml

# 获取同类作品参考
素材 reference --type=novel --tags=仙侠,玄幻 --count=5 --aspect=worldbuilding
```

## 配置说明

### 配置文件位置

```
~/.openclaw/config/story-architect.yaml
```

### 基础配置

```yaml
# 基础设置
output:
  base_path: ~/story-output
  templates_folder: templates
  characters_folder: characters
  worlds_folder: worlds
  outlines_folder: outlines

# 默认设置
defaults:
  language: zh
  genre: fantasy
  perspective: third_limited
  tense: past
```

### 世界观配置

```yaml
worldbuilding:
  # 默认世界观类型
  genre_defaults:
    sci-fi:
      tech_level: mid
      magic_enabled: false
      realism: high
    fantasy:
      magic_enabled: true
      magic_system: soft
      races: 5
    urban:
      hidden_society: true
      realism: medium
  
  # 详细度设置
  detail_level:
    geography: high
    politics: medium
    economics: low
    culture: high
```

### 人物配置

```yaml
characters:
  # 人物模板
  templates:
    protagonist:
      required_fields: [name, age, motivation, flaw]
      optional_fields: [backstory, secrets]
    villain:
      required_fields: [name, motivation, method]
    
  # 关系类型
  relationship_types:
    - family
    - romance
    - rivalry
    - mentor
    - ally
```

### 情节配置

```yaml
plotting:
  # 故事结构
  structures:
    three_act:
      ratio: [25%, 50%, 25%]
    hero_journey:
      stages: [12, 12, 6]
    seven_point:
      ratio: [15%, 15%, 15%, 10%, 15%, 15%, 15%]
  
  # 节奏设置
  pacing:
    chapters_per_arc: 5
    scenes_per_chapter: 3
    conflict_frequency: every_chapter
```

### 模板配置

```yaml
templates:
  folder: ~/story-output/templates
  
  # 模板变量
  variables:
    world:
      - name: world_name
      - name: era
      - name: magic_system
    
    character:
      - name: char_name
      - name: role
      - name: arc_type
    
    outline:
      - name: story_title
      - name: genre
      - name: word_count
```

## 使用示例

### 示例 1：创建奇幻小说世界观

```bash
# 生成基础世界观
generate world --type=fantasy --magic_system=hard --pantheon=true --races=8

# 扩展详细设定
expand world --depth=all --output=青云大陆/

# 设计魔法体系
expand world --depth=magic --system=五行+血脉 --rules=3 --cost=记忆

# 设计种族
expand world --depth=races --include=人族,龙族,精灵,矮人 --history=5000

# 生成时间线
expand world --depth=history --start_date=-3000 --events=major --format=timeline
```

### 示例 2：设计悬疑小说人物

```bash
# 创建主角
create character --role=protagonist --template=detective --name=秦风 --age=32

# 创建嫌疑人
create character --role=suspect --name=林雨 --secrets=3
create character --role=suspect --name=墨轩 --motive=inheritance
create character --role=suspect --name=苏晚 --hidden_agenda=true

# 创建反派
create character --role=villain --name=X --method=orchestration --identity=twist

# 设计关系网络
network create --characters=秦风,林雨,墨轩,苏晚 --type=mystery_web
```

### 示例 3：规划都市言情大纲

```bash
# 生成都市言情大纲
generate outline --type=romance --structure=three_act --chapters=20

# 设计主线
outline storyline --main=office_romance --couple=上司x下属 --obstacles=3

# 设计副线
outline subplot --type=career --character=女主 --arc=升职记
outline subplot --type=friendship --characters=闺蜜团 --conflict=误会

# 冲突高潮
design conflict --type=relationship --event=身份暴露 --intensity=high
design climax --type=emotional --scene=雨中告白 --type=romantic
```

### 示例 4：创作科幻短篇

```bash
# 快速生成短篇设定
generate world --type=sci-fi --era=2150 --scope=solar --tech=realistic

# 创建人物
create character --role=protagonist --name=叶轩 --job=宇航员 --arc=exploration

# 生成短篇大纲
generate outline --type=short_story --structure=twist --scenes=6 --words=8000

# 设计高潮
design climax --type=revelation --secret=simulation --impact=existential
```

## 与其他 Skills 的配合

| 场景 | 使用 Skill |
|------|-----------|
| 收集创作素材 | `material-collector` |
| 基于设定生成内容 | `auto-content-creator` |
| 润色文稿 | `content-editor` |
| 详细描写增强 | `detail-painter` |
| 浏览器查资料 | `browser-automation` |
| 思维导图整理 | `canvas-design` |

## 注意事项

1. **前后一致**：人物设定和世界观需要保持逻辑自洽
2. **详略得当**：大纲和设定不需要一次完成，可以迭代扩展
3. **灵活调整**：故事结构是指导原则，不是死规则
4. **素材引用**：收集的参考素材要注意版权
5. **备份保存**：重要的设定文件要定期备份

## 输出位置

所有创作内容保存在 `~/story-output/` 目录：
- 世界观设定：`worlds/`
- 人物档案：`characters/`
- 故事大纲：`outlines/`
- 模板库：`templates/`
- 素材库联动：`materials/`
- 日志：`logs/story-architect.log`
