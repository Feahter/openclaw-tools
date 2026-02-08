#!/usr/bin/env python3
"""
文章提取器 - 从网页提取文章内容和元数据
用于知识库建设
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# 尝试导入 web_fetch，如果不可用则使用模拟实现
try:
    from tools import web_fetch
except ImportError:
    from openclaw.tools import web_fetch


class ArticleExtractor:
    """文章提取器类"""
    
    def __init__(self, default_output_dir: str = "./extracted_articles"):
        """
        初始化文章提取器
        
        Args:
            default_output_dir: 默认输出目录
        """
        self.default_output_dir = default_output_dir
        
    def extract_article(self, url: str, extract_mode: str = "markdown") -> Dict:
        """
        提取文章完整内容和元数据
        
        Args:
            url: 文章 URL
            extract_mode: 提取模式，"markdown" 或 "text"
            
        Returns:
            包含文章内容和元数据的字典
        """
        # 提取网页内容
        content = web_fetch(url=url, extractMode=extract_mode)
        
        # 提取元数据
        metadata = self.extract_metadata(url, content)
        
        return {
            "url": url,
            "content": content,
            "metadata": metadata,
            "extracted_at": datetime.now().isoformat()
        }
    
    def extract_metadata(self, url: str, content: str) -> Dict:
        """
        提取文章元数据
        
        Args:
            url: 文章 URL
            content: 文章内容
            
        Returns:
            元数据字典
        """
        metadata = {
            "title": self._extract_title(content),
            "author": self._extract_author(content),
            "publish_date": self._extract_publish_date(content),
            "tags": self._extract_tags(content),
            "categories": self._extract_categories(content),
            "description": self._extract_description(content),
            "word_count": self._count_words(content),
            "url_domain": self._get_domain(url)
        }
        
        return metadata
    
    def save_to_markdown(self, article_data: Dict, output_path: str = None) -> str:
        """
        保存文章为 Markdown 格式
        
        Args:
            article_data: 文章数据字典
            output_path: 输出文件路径（可选，自动生成）
            
        Returns:
            保存的文件路径
        """
        metadata = article_data.get("metadata", {})
        content = article_data.get("content", "")
        
        # 构建 Markdown 文件
        markdown_lines = []
        
        # 标题
        title = metadata.get("title", "Untitled Article")
        markdown_lines.append(f"# {title}\n")
        
        # 元数据
        markdown_lines.append("---")
        markdown_lines.append(f"**URL**: {article_data.get('url', '')}")
        
        if metadata.get("author"):
            markdown_lines.append(f"**Author**: {metadata['author']}")
        
        if metadata.get("publish_date"):
            markdown_lines.append(f"**Published**: {metadata['publish_date']}")
        
        if metadata.get("categories"):
            markdown_lines.append(f"**Categories**: {', '.join(metadata['categories'])}")
        
        if metadata.get("tags"):
            markdown_lines.append(f"**Tags**: {', '.join(metadata['tags'])}")
        
        if metadata.get("description"):
            markdown_lines.append(f"**Description**: {metadata['description']}")
        
        markdown_lines.append(f"**Extracted**: {article_data.get('extracted_at', '')}")
        markdown_lines.append("---\n")
        
        # 正文内容
        markdown_lines.append(content)
        
        # 合并内容
        markdown_content = "\n".join(markdown_lines)
        
        # 确定输出路径
        if not output_path:
            title_slug = self._slugify(title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{title_slug}_{timestamp}.md"
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
    
    def batch_extract(self, urls: List[str], output_dir: str = None, 
                      format: str = "markdown") -> List[Dict]:
        """
        批量提取多个文章
        
        Args:
            urls: URL 列表
            output_dir: 输出目录
            format: 输出格式
            
        Returns:
            提取结果列表
        """
        if output_dir is None:
            output_dir = self.default_output_dir
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = []
        
        for i, url in enumerate(urls):
            try:
                print(f"Extracting [{i+1}/{len(urls)}]: {url}")
                
                # 提取文章
                article_data = self.extract_article(url, extract_mode=format)
                results.append(article_data)
                
                # 保存为 Markdown
                output_path = os.path.join(output_dir, f"article_{i+1}.md")
                self.save_to_markdown(article_data, output_path)
                
            except Exception as e:
                print(f"Error extracting {url}: {str(e)}")
                results.append({
                    "url": url,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    # 私有辅助方法
    
    def _extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        # 尝试匹配 Markdown 标题格式
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_author(self, content: str) -> str:
        """从内容中提取作者"""
        # 常见作者标记模式
        patterns = [
            r'Author[:：]\s*(.+)',
            r'By[:：]?\s*(.+)',
            r'作者[:：]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_publish_date(self, content: str) -> str:
        """从内容中提取发布日期"""
        # 常见日期格式
        patterns = [
            r'Published[:：]?\s*(.+)',
            r'发布时间[:：]?\s*(.+)',
            r'Date[:：]?\s*(.+)',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1).strip()
                # 尝试标准化日期格式
                try:
                    parsed_date = datetime.strptime(date_str.split()[0], 
                                                     "%Y-%m-%d" if '-' in date_str else "%Y/%m/%d")
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
                return date_str
        
        return ""
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容中提取标签"""
        patterns = [
            r'Tags?[:：]\s*(.+)',
            r'标签[:：]?\s*(.+)',
            r'Keywords?[:：]?\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tags_str = match.group(1).strip()
                # 分割标签
                tags = [tag.strip() for tag in re.split(r'[,，;；\s]+', tags_str) if tag.strip()]
                return tags
        
        return []
    
    def _extract_categories(self, content: str) -> List[str]:
        """从内容中提取分类"""
        patterns = [
            r'Categor(?:y|ies)[:：]\s*(.+)',
            r'分类[:：]?\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                cats_str = match.group(1).strip()
                cats = [cat.strip() for cat in re.split(r'[,，;；\s]+', cats_str) if cat.strip()]
                return cats
        
        return []
    
    def _extract_description(self, content: str) -> str:
        """从内容中提取描述"""
        patterns = [
            r'Description[:：]?\s*(.+)',
            r'描述[:：]?\s*(.+)',
            r'Excerpt[:：]?\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _count_words(self, content: str) -> int:
        """统计字数"""
        # 移除 Markdown 标记后统计
        clean_text = re.sub(r'[#*`_~\[\]]', '', content)
        words = clean_text.split()
        return len(words)
    
    def _get_domain(self, url: str) -> str:
        """获取 URL 域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def _slugify(self, text: str) -> str:
        """将文本转换为 URL 友好的 slug 格式"""
        # 移除非字母数字字符
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        # 转换为小写并用连字符替换空格
        slug = re.sub(r'\s+', '-', slug.strip().lower())
        # 移除连续连字符
        slug = re.sub(r'-+', '-', slug)
        return slug[:100]  # 限制长度


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Article Extractor - Extract articles from web pages")
    
    parser.add_argument("--url", help="URL of the article to extract")
    parser.add_argument("--batch", help="File containing list of URLs to extract")
    parser.add_argument("--output", default="./extracted_articles", 
                        help="Output directory (default: ./extracted_articles)")
    parser.add_argument("--format", default="markdown", choices=["markdown", "text"],
                        help="Output format (default: markdown)")
    
    args = parser.parse_args()
    
    extractor = ArticleExtractor()
    
    if args.url:
        # 单个文章提取
        article_data = extractor.extract_article(args.url, args.format)
        output_path = extractor.save_to_markdown(article_data, None)
        print(f"Article extracted and saved to: {output_path}")
        
    elif args.batch:
        # 批量提取
        if not os.path.exists(args.batch):
            print(f"Error: URL file not found: {args.batch}")
            return
        
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        results = extractor.batch_extract(urls, args.output, args.format)
        print(f"\nBatch extraction complete. {len(results)} articles processed.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
