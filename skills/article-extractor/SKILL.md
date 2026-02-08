# article-extractor

文章提取技能，从网页提取完整文本、标题、作者、标签等元数据。

## 功能

- **网页内容提取**：使用 web_fetch 从任意 URL 提取页面内容
- **元数据收集**：提取标题、作者、发布时间、标签、分类等
- **格式转换**：支持转换为 Markdown 或纯文本格式
- **本地保存**：自动保存到本地文件，便于知识库建设

## 使用方法

```bash
# 提取单个文章
python scripts/article_extract.py --url "https://example.com/article"

# 批量提取
python scripts/article_extract.py --batch urls.txt --output ./articles

# 指定输出格式
python scripts/article_extract.py --url "https://example.com/article" --format markdown
```

## 命令行参数

- `--url`: 要提取的网页 URL（单个模式）
- `--batch`: URL 列表文件（批量模式）
- `--output`: 输出目录（默认: ./extracted_articles）
- `--format`: 输出格式，可选 `markdown` 或 `text`（默认: markdown）
- `--include-metadata`: 是否在输出中包含元数据

## Python API

```python
from article_extract import ArticleExtractor

# 创建提取器
extractor = ArticleExtractor()

# 提取文章
result = extractor.extract_article("https://example.com/article")

# 提取元数据
metadata = extractor.extract_metadata("https://example.com/article")

# 保存为 Markdown
extractor.save_to_markdown(result, "output/article.md")

# 批量提取
extractor.batch_extract(["url1", "url2"], "./output_dir")
```

## 依赖

- web_fetch（OpenClaw 内置工具）
- Python 3.7+
