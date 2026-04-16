#!/usr/bin/env python3
"""
WeChat Article Parser - 直接从微信公众号 HTML 源码提取正文
原理：正文在 rich_media_content div 里，不需要 CDP
"""
import re
import html
from typing import Optional


def parse_wechat_article(html_content: str) -> Optional[str]:
    """
    从微信文章 HTML 中提取正文内容
    
    Args:
        html_content: 微信公众号页面的 HTML 源码
    
    Returns:
        提取的纯文本内容，失败返回 None
    """
    # 方法1: 提取 rich_media_content div
    pattern1 = r'<div[^>]*id=["\']rich_media_content["\'][^>]*>(.*?)</div>'
    match = re.search(pattern1, html_content, re.DOTALL)
    
    if match:
        content = match.group(1)
    else:
        # 方法2: 尝试直接找正文区域
        pattern2 = r'<section[^>]*class=["\'][^"\']*rich_media_content[^"\']*["\'][^>]*>(.*?)</section>'
        match = re.search(pattern2, html_content, re.DOTALL)
        if match:
            content = match.group(1)
        else:
            return None
    
    # 清理 HTML 标签，保留文本
    text = strip_html_tags(content)
    
    # 清理多余空白
    text = clean_whitespace(text)
    
    return text if text.strip() else None


def strip_html_tags(html_str: str) -> str:
    """去除 HTML 标签，保留内部文本"""
    # 处理 <p> 标签，替换为换行
    html_str = re.sub(r'<p[^>]*>', '\n', html_str)
    html_str = re.sub(r'</p>', '\n', html_str)
    
    # 处理 <br>
    html_str = re.sub(r'<br\s*/?>', '\n', html_str)
    
    # 处理 <section>
    html_str = re.sub(r'<section[^>]*>', '\n', html_str)
    html_str = re.sub(r'</section>', '\n', html_str)
    
    # 处理 <div>
    html_str = re.sub(r'<div[^>]*>', '\n', html_str)
    html_str = re.sub(r'</div>', '\n', html_str)
    
    # 去除所有其他标签
    html_str = re.sub(r'<[^>]+>', '', html_str)
    
    # 解码 HTML 实体
    html_str = html.unescape(html_str)
    
    return html_str


def clean_whitespace(text: str) -> str:
    """清理多余空白，保留段落结构"""
    # 将多个空白字符替换为单个空格
    text = re.sub(r'[ \t]+', ' ', text)
    # 将多个连续换行压缩为两个
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 去除行首行尾空白
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(line for line in lines if line)


def is_wechat_url(url: str) -> bool:
    """判断是否为微信文章 URL"""
    return 'mp.weixin.qq.com' in url


if __name__ == '__main__':
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            html = f.read()
        
        text = parse_wechat_article(html)
        if text:
            print(text[:2000])
        else:
            print("提取失败")
