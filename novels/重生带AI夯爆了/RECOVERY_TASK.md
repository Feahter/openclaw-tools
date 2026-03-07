# 小说章节恢复任务

## 目标
根据现有摘要重新生成丢失的章节内容。

## 源文件位置
- 小说目录: `novels/重生带AI夯爆了/`
- 摘要目录: `novels/重生带AI夯爆了/chapter_summaries/`
- 元数据: `novels/重生带AI夯爆了/progress.json`
- 大纲: `novels/重生带AI夯爆了/大纲.md`
- 人物档案: `novels/重生带AI夯爆了/人物档案.md`

## 输出目录（必须遵守）
- 第一卷: `novels/重生带AI夯爆了/chapters/volume1/ch001_标题.md`
- 第二卷: `novels/重生带AI夯爆了/chapters/volume2/ch031_标题.md`

## 目录结构规范
```
chapters/volume1/  → ch001-ch030
chapters/volume2/  → ch031开始
```

## 需要生成的章节
### 第一卷 (ch001-ch030)
| 章节 | 摘要文件 | 状态 |
|------|---------|------|
| ch001 | ch001_summary.md | 待生成 |
| ch002 | ch002_summary.md | 待生成 |
| ch003 | ch003_summary.md | 待生成 |
| ... | ... | ... |
| ch030 | ch030_summary.md | 待生成 |

### 第二卷 (ch031-ch056)
| 章节 | 摘要文件 | 状态 |
|------|---------|------|
| ch031 | ch031_summary.md | 待生成 |
| ch032 | ch032_summary.md | 待生成 |
| ... | ... | ... |
| ch056 | ch056_summary.md | 待生成 |

## 已有内容（保留）
- ch039_危机.md ✅
- ch057_神秘礼物.md ✅

## 执行要求
1. 先读取摘要文件理解剧情
2. 按照摘要风格生成完整章节
3. 每章保存到正确目录
4. 更新 progress.json 状态
