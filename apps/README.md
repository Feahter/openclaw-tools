# Apps - 开源应用集合

本目录包含所有独立的应用和项目级开源内容。

## 项目列表

### 📦 Data Lake POC

**路径**: `apps/data-lake-poc/`

**描述**: 浏览器端 SQLite + ETL 数据基座

**功能**:
- 统一 ETL 管道引擎
- SQL 查询 (数据模型
-sql.js)
- 多格式导入导出 (CSV/JSON/SQLite)
- 性能优化 (虚拟滚动/分页)
- IndexedDB 持久化

**状态**: ✅ 完成
- 文件数: 20
- 测试通过: 25/25
- 代码行数: ~5500

**快速开始**:
```bash
cd apps/data-lake-poc
python3 -m http.server 8080
# 访问 http://localhost:8080/src/index.html
```

---

## 项目结构

```
apps/
├── data-lake-poc/          # 浏览器端数据湖 POC
│   ├── src/
│   │   ├── core/          # 核心引擎
│   │   ├── adapters/       # 格式适配器
│   │   ├── storage/       # 持久化层
│   │   └── ui/           # 用户界面
│   ├── test/              # 测试
│   └── SKILL.md          # OpenClaw Skill
```

## 添加新项目

1. 在 `apps/` 下创建项目目录
2. 包含 `README.md` 说明文档
3. 包含 `SKILL.md` (可选，用于 OpenClaw)
4. 包含测试用例

## License

各项目独立 license，详见各项目目录。
