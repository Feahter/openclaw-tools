# 小说创作 SOP - 内容管理规范

## 📁 目录结构

```
novels/<小说名>/
├── 大纲.md                    # 小说大纲
├── 人物档案.md                # 人物设定
├── progress.json              # 进度追踪
├── chapters/
│   ├── volume1/              # 第一卷
│   │   ├── ch001_标题.md
│   │   ├── ch002_标题.md
│   │   └── ...
│   └── volume2/              # 第二卷
│       ├── ch031_标题.md
│       └── ...
├── chapter_summaries/        # 章节摘要
│   ├── ch001_summary.md
│   └── ...
└── 角色设定/                  # 角色详细设定
```

## ⚠️ 禁止事项

1. **禁止** 在根目录直接创建 `ch0*.md` 文件
2. **禁止** 在 `novel/` (非复数) 目录存放内容
3. **禁止** 创建独立子目录存放章节（如 `ch029_title/ch029_title.md`）
4. **禁止** 在 `chapters/` 下直接放文件，必须分卷

## ✅ 正确流程

1. 章节完成后 → 移动到 `chapters/volume<N>/`
2. 摘要生成 → 放到 `chapter_summaries/`
3. 进度更新 → 写入 `progress.json`

## 🔧 自动化检查

每次 Agent 完成章节后，检查：
- [ ] 文件是否在正确卷目录？
- [ ] 命名是否符合 `chXXX_标题.md`？
- [ ] progress.json 是否更新？
- [ ] 摘要是否生成？
