#!/usr/bin/env python3
"""
Fetch GitHub repository information.
Usage: python fetch_github_info.py <repo_url>
"""

import sys
import json
import subprocess
import re
from urllib.request import urlopen
from urllib.error import URLError

def get_repo_info(repo_url):
    """Extract owner/repo from URL"""
    # Handle both https://github.com/owner/repo and git@github.com:owner/repo
    if repo_url.startswith('git@'):
        match = re.search(r'github\.com[:/](.+?)/(.+?)(?:\.git)?$', repo_url)
    else:
        match = re.search(r'github\.com/(.+?)/(.+?)(?:\.git)?/?$', repo_url)
    
    if not match:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    return match.group(1), match.group(2)

def fetch_readme(owner, repo):
    """Fetch README content from GitHub API"""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    try:
        with urlopen(api_url, timeout=10) as response:
            import base64
            data = json.loads(response.read().decode())
            return data.get('content', '')
    except Exception as e:
        return f"# {repo}\n\nFailed to fetch README: {e}"

def get_latest_commit(owner, repo):
    """Get latest commit hash"""
    try:
        result = subprocess.run(
            ['git', 'ls-remote', f'https://github.com/{owner}/{repo}.git', 'HEAD'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception as e:
        pass
    return "unknown"

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_github_info.py <repo_url>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    owner, repo = get_repo_info(repo_url)
    
    print(f"Fetching info for {owner}/{repo}...")
    
    readme = fetch_readme(owner, repo)
    commit_hash = get_latest_commit(owner, repo)
    
    result = {
        "owner": owner,
        "repo": repo,
        "url": f"https://github.com/{owner}/{repo}",
        "github_hash": commit_hash,
        "readme_preview": readme[:500] + "..." if len(readme) > 500 else readme
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
