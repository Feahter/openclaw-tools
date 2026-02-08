#!/usr/bin/env python3
"""
Download AI prompts from waytoagi.com - Optimized Version

Usage:
    python download-waytoagi-prompts.py --author "李继刚"
    python download-waytoagi-prompts.py --test
    python download-waytoagi-prompts.py --discover-authors
"""

import re
import html
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import urllib.request
import urllib.error


def fetch_url(url, timeout=15):
    """Fetch URL with timeout and error handling"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except Exception:
        return None


def get_author_from_page(url):
    """Extract author from a prompt page"""
    html_content = fetch_url(url)
    if not html_content:
        return None
    match = re.search(r';; 作者: ([^\n]+)', html_content)
    return match.group(1).strip() if match else None


def get_title_from_page(url):
    """Extract title from a prompt page"""
    html_content = fetch_url(url)
    if not html_content:
        return None
    match = re.search(r'<title>([^<]+)</title>', html_content)
    if match:
        title = match.group(1).split(' - ')[0].strip()
        return re.sub(r'[<>:"/\\|?*]', '', title)
    return None


def download_prompt_content(url, filename):
    """Download prompt content - handles both direct HTML and Next.js JSON"""
    html_content = fetch_url(url)
    if not html_content:
        return False
    
    # Method 1: Try direct HTML extraction first
    match = re.search(r';; ━━━━━━━━━━━━━━\n;;; Attention: 运行规则!', html_content, re.DOTALL)
    if match:
        start_idx = html_content.find(";; 作者:")
        if start_idx != -1:
            content = html_content[start_idx:match.start()].strip()
            content = re.sub(r';;; ━━━━━━━━━━━━━━.*$', '', content, flags=re.DOTALL).strip()
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    
    # Method 2: Extract from Next.js JSON data
    json_pattern = r'"text":"(;; [^\"]+)"'
    matches = re.findall(json_pattern, html_content)
    
    for match_text in matches:
        if ';; 作者:' in match_text and ';; ━━━━━━━━━━━━━━' in match_text:
            # Clean up JSON escaping
            content = match_text.replace('\\n', '\n').replace('\\"', '"')
            content = re.sub(r';;; ━━━━━━━━━━━━━━.*$', '', content, flags=re.DOTALL).strip()
            content = re.sub(r';;; 使用说明.*$', '', content, flags=re.DOTALL).strip()
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    
    return False


def discover_all_prompts(max_pages=10, workers=10):
    """Discover ALL prompts with their authors - optimized version"""
    print(f"\n🔍 Discovering all prompts (checking {max_pages} pages)...")
    
    all_pids = []
    
    # Step 1: Get all prompt IDs from list pages
    for page in range(1, max_pages + 1):
        url = f"https://www.waytoagi.com/zh/prompts?page={page}"
        html_content = fetch_url(url)
        if html_content:
            pids = re.findall(r'/prompts/(\d+)', html_content)
            all_pids.extend(pids)
        print(f"  Page {page}: {len(pids)} prompts", flush=True)
    
    # Deduplicate and sort
    all_pids = sorted(set(all_pids))
    print(f"\n  Total unique prompts: {len(all_pids)}")
    
    # Step 2: Parallel fetch authors for all prompts
    print(f"\n📋 Fetching author info ({len(all_pids)} prompts, {workers} workers)...")
    
    authors = {}
    pid_to_title = {}
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(get_author_from_page, f"https://www.waytoagi.com/zh/prompts/{pid}"): pid 
                   for pid in all_pids}
        
        for future in tqdm(as_completed(futures), total=len(all_pids), desc="Checking"):
            pid = futures[future]
            author = future.result()
            if author:
                if author not in authors:
                    authors[author] = []
                if pid not in authors[author]:
                    authors[author].append(pid)
    
    return authors


def download_by_author(author_name, output_dir, max_workers=5):
    """Download all prompts by an author"""
    print(f"\n📥 Downloading {author_name}'s prompts...")
    
    # Get all prompts with authors
    authors = discover_all_prompts(max_pages=10, workers=10)
    
    # Find matching author
    if author_name not in authors:
        matches = [a for a in authors.keys() if author_name in a]
        if not matches:
            print(f"⚠️ Author '{author_name}' not found")
            return 0
        author_name = matches[0]
        print(f"  Using: {author_name}")
    
    prompt_ids = authors[author_name]
    print(f"  Found {len(prompt_ids)} prompts\n")
    
    # Get titles and download in parallel
    print("📖 Fetching titles...")
    tasks = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_title_from_page, f"https://www.waytoagi.com/zh/prompts/{pid}"): pid 
                   for pid in prompt_ids}
        
        for future in as_completed(futures):
            pid = futures[future]
            title = future.result()
            if title:
                filename = os.path.join(output_dir, f"{title}.md")
                tasks.append((pid, title, filename))
    
    print(f"\n⬇️  Downloading {len(tasks)} prompts...")
    
    # Download prompts
    success = 0
    failed = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_prompt_content, 
                                   f"https://www.waytoagi.com/zh/prompts/{pid}", 
                                   filename): (pid, title) 
                   for pid, title, filename in tasks}
        
        for future in tqdm(as_completed(futures), total=len(tasks), desc="Downloading"):
            pid, title = futures[future]
            if future.result():
                success += 1
            else:
                failed.append((pid, title))
    
    # Report
    print(f"\n✓ Downloaded {success}/{len(tasks)} prompts")
    if failed:
        print(f"✗ Failed {len(failed)}:")
        for pid, title in failed:
            print(f"  - {title} ({pid})")
    
    return success


def main():
    parser = argparse.ArgumentParser(
        description='Download AI prompts from waytoagi.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download-waytoagi-prompts.py --author "李继刚"
  python download-waytoagi-prompts.py --discover-authors
  python download-waytoagi-prompts.py --author "卡兹克" --workers 5
        """
    )
    
    parser.add_argument('--author', type=str, help='Download prompts by author name')
    parser.add_argument('--discover-authors', action='store_true', help='List all authors')
    parser.add_argument('--output', type=str, default='assets/prompts', help='Output directory')
    parser.add_argument('--workers', type=int, default=5, help='Parallel workers')
    parser.add_argument('--pages', type=int, default=10, help='Max pages to scan')
    
    args = parser.parse_args()
    
    if args.discover_authors:
        authors = discover_all_prompts(max_pages=args.pages, workers=10)
        print("\n📋 Available Authors:")
        print("-" * 50)
        for author, pids in sorted(authors.items(), key=lambda x: -len(x[1])):
            print(f"  • {author}: {len(pids)} prompts")
    elif args.author:
        download_by_author(args.author, args.output, args.workers)
    else:
        print(__doc__)
        print("\nUsage: python download-waytoagi-prompts.py --author 李继刚")


if __name__ == '__main__':
    main()
