#!/usr/bin/env python3
"""
MCP Filesystem Server - Provides file operations as MCP tools
Based on MCP Python SDK 1.26.0
"""

import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="filesystem",
    instructions="Local filesystem operations: read, write, list, search, stats. "
    "All paths are resolved relative to allowed directories for security.",
)

# Security: whitelist allowed directories
ALLOWED_DIRS = [
    os.path.expanduser("~/"),
    "/tmp/",
    "/Users/fuzhuo/.openclaw/workspace",
]

SANDBOX_MODE = os.environ.get("MCP_FS_SANDBOX", "true").lower() == "true"


def _safe_path(path: str) -> Optional[str]:
    """Resolve and validate path is within allowed directories."""
    if not SANDBOX_MODE:
        return path
    
    try:
        resolved = Path(path).expanduser().resolve()
        for allowed in ALLOWED_DIRS:
            allowed_resolved = Path(allowed).resolve()
            try:
                resolved.relative_to(allowed_resolved)
                return str(resolved)
            except ValueError:
                continue
        return None
    except Exception:
        return None


@mcp.tool()
def read_file(path: str, offset: int = 0, limit: int = 10000) -> str:
    """
    Read contents of a text file.
    
    Args:
        path: Absolute or relative path to the file
        offset: Character offset to start reading from (default: 0)
        limit: Maximum characters to read (default: 10000)
    
    Returns:
        File contents (truncated if large)
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        with open(safe, "r", encoding="utf-8", errors="replace") as f:
            f.seek(offset)
            content = f.read(limit)
            remaining = f.read()  # Check if there's more
        suffix = f"\n... [truncated, {len(remaining)} more characters]" if remaining else ""
        return content + suffix
    except IsADirectoryError:
        return f"Error: '{path}' is a directory, not a file"
    except PermissionError:
        return f"Error: Permission denied reading '{path}'"
    except FileNotFoundError:
        return f"Error: File '{path}' not found"
    except Exception as e:
        return f"Error reading '{path}': {e}"


@mcp.tool()
def write_file(path: str, content: str, append: bool = False) -> str:
    """
    Write content to a file.
    
    Args:
        path: Absolute or relative path to the file
        content: Text content to write
        append: If True, append to existing file instead of overwriting
    
    Returns:
        Success or error message
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        mode = "a" if append else "w"
        with open(safe, mode, encoding="utf-8") as f:
            f.write(content)
        action = "Appended to" if append else "Written to"
        return f"{action} '{path}' ({len(content)} characters)"
    except PermissionError:
        return f"Error: Permission denied writing '{path}'"
    except Exception as e:
        return f"Error writing '{path}': {e}"


@mcp.tool()
def list_directory(path: str = ".", include_hidden: bool = False, limit: int = 100) -> str:
    """
    List contents of a directory.
    
    Args:
        path: Directory path (default: current directory)
        include_hidden: Include hidden files starting with dot
        limit: Maximum number of entries to return
    
    Returns:
        Formatted directory listing
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        entries = os.listdir(safe)
        if not include_hidden:
            entries = [e for e in entries if not e.startswith(".")]
        
        entries.sort()
        entries = entries[:limit]
        
        lines = []
        for name in entries:
            full = os.path.join(safe, name)
            try:
                st = os.stat(full)
                if stat.S_ISDIR(st.st_mode):
                    lines.append(f"  📁 {name}/")
                else:
                    size = st.st_size
                    size_str = _format_size(size)
                    lines.append(f"  📄 {name} ({size_str})")
            except OSError:
                lines.append(f"  ? {name}")
        
        suffix = f"\n... [{len(entries)} entries, truncated]" if len(entries) == limit else ""
        return "Directory listing:\n" + "\n".join(lines) + suffix
    except NotADirectoryError:
        return f"Error: '{path}' is not a directory"
    except PermissionError:
        return f"Error: Permission denied listing '{path}'"
    except Exception as e:
        return f"Error listing '{path}': {e}"


@mcp.tool()
def file_stats(path: str) -> str:
    """
    Get detailed file/directory statistics.
    
    Args:
        path: File or directory path
    
    Returns:
        Formatted file statistics
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        st = os.stat(safe)
        mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        ctime = datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        
        mode = stat.filemode(st.st_mode)
        is_dir = stat.S_ISDIR(st.st_mode)
        is_file = stat.S_ISREG(st.st_mode)
        
        lines = [
            f"Path: {path}",
            f"Type: {'Directory' if is_dir else 'File' if is_file else 'Other'}",
            f"Mode: {mode}",
            f"Size: {_format_size(st.st_size)} ({st.st_size} bytes)",
            f"Modified: {mtime}",
            f"Changed: {ctime}",
        ]
        
        if is_file and st.st_size > 0:
            try:
                with open(safe, "rb") as f:
                    header = f.read(20)
                lines.append(f"Magic: {header.hex()[:40]}")
            except Exception:
                pass
        
        return "\n".join(lines)
    except FileNotFoundError:
        return f"Error: '{path}' not found"
    except PermissionError:
        return f"Error: Permission denied accessing '{path}'"
    except Exception as e:
        return f"Error accessing '{path}': {e}"


@mcp.tool()
def search_files(
    root: str = ".",
    pattern: str = "",
    regex: bool = False,
    content_match: bool = False,
    case_sensitive: bool = False,
    limit: int = 50,
) -> str:
    """
    Search for files by name or content.
    
    Args:
        root: Root directory to search in
        pattern: Filename pattern or content to search for
        regex: Treat pattern as regular expression (name search)
        content_match: Search file contents instead of filenames
        case_sensitive: Case-sensitive matching
        limit: Maximum number of results
    
    Returns:
        Matching file paths
    """
    import fnmatch
    import re
    
    safe = _safe_path(root)
    if not safe:
        return f"Error: Path '{root}' is outside allowed directories"
    
    if not pattern:
        return "Error: pattern is required"
    
    results = []
    matcher = None
    if regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            matcher = re.compile(pattern, flags).search
        except re.error as e:
            return f"Error: Invalid regex: {e}"
    elif not content_match:
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = fnmatch.translate(pattern)
        try:
            matcher = re.compile(pattern, flags).search
        except re.error:
            matcher = None
    
    try:
        for dirpath, dirnames, filenames in os.walk(safe):
            # Prune hidden dirs for speed
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            
            if content_match:
                for filename in filenames:
                    full = os.path.join(dirpath, filename)
                    try:
                        with open(full, "r", encoding="utf-8", errors="replace") as f:
                            for lineno, line in enumerate(f, 1):
                                line_content = line if case_sensitive else line.lower()
                                pattern_lower = pattern if case_sensitive else pattern.lower()
                                if pattern_lower in line_content:
                                    rel = os.path.relpath(full, safe)
                                    results.append(f"{rel}:{lineno}: {line.rstrip()}")
                                    break  # One match per file
                    except Exception:
                        continue
            else:
                for filename in filenames:
                    if filename.startswith("."):
                        continue
                    if matcher and matcher(filename):
                        rel = os.path.relpath(os.path.join(dirpath, filename), safe)
                        results.append(rel)
                    elif not matcher and fnmatch.fnmatch(filename, pattern if case_sensitive else pattern.lower()):
                        rel = os.path.relpath(os.path.join(dirpath, filename), safe)
                        results.append(rel)
            
            if len(results) >= limit:
                break
        
        if not results:
            return f"No matches found for '{pattern}' in {root}"
        
        suffix = f"\n... [{len(results)} results, truncated]" if len(results) == limit else ""
        return f"Found {len(results)} matches:\n" + "\n".join(results[:limit]) + suffix
    
    except Exception as e:
        return f"Error searching '{root}': {e}"


@mcp.tool()
def create_directory(path: str, parents: bool = True) -> str:
    """
    Create a directory.
    
    Args:
        path: Directory path to create
        parents: Create parent directories as needed
    
    Returns:
        Success or error message
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        if parents:
            os.makedirs(safe, exist_ok=True)
        else:
            os.mkdir(safe)
        return f"Created directory '{path}'"
    except FileExistsError:
        return f"Error: '{path}' already exists"
    except PermissionError:
        return f"Error: Permission denied creating '{path}'"
    except Exception as e:
        return f"Error creating '{path}': {e}"


@mcp.tool()
def delete_file(path: str, recursive: bool = False) -> str:
    """
    Delete a file or directory.
    
    Args:
        path: File or directory path to delete
        recursive: Allow deleting non-empty directories
    
    Returns:
        Success or error message
    """
    safe = _safe_path(path)
    if not safe:
        return f"Error: Path '{path}' is outside allowed directories"
    
    try:
        if os.path.isdir(safe):
            if recursive:
                import shutil
                shutil.rmtree(safe)
            else:
                os.rmdir(safe)
        else:
            os.remove(safe)
        return f"Deleted '{path}'"
    except PermissionError:
        return f"Error: Permission denied deleting '{path}'"
    except OSError as e:
        return f"Error: Cannot delete '{path}': {e}"
    except Exception as e:
        return f"Error deleting '{path}': {e}"


def _format_size(size: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


if __name__ == "__main__":
    # Run with stdio transport
    mcp.run(transport="stdio")
