# MCP Filesystem Server

A local filesystem MCP server providing secure file operations as MCP tools.

## Status

✅ Working - tested with mcporter 0.7.3, MCP Python SDK 1.26.0

## Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read text file (with offset/limit) |
| `write_file` | Write or append to file |
| `list_directory` | List directory contents |
| `file_stats` | Get file/directory statistics |
| `search_files` | Search by name or content |
| `create_directory` | Create directory (with `parents` option) |
| `delete_file` | Delete file or directory |

## Usage

### With mcporter (CLI)

```bash
# List directory
mcporter call --stdio "python3 scripts/mcp-filesystem/server.py" list_directory path="/tmp" limit=10

# Read file
mcporter call --stdio "python3 scripts/mcp-filesystem/server.py" read_file path="~/.openclaw/workspace/MEMORY.md" limit=500

# Search files
mcporter call --stdio "python3 scripts/mcp-filesystem/server.py" search_files root="/tmp" pattern="*.py" limit=20

# Write file
mcporter call --stdio "python3 scripts/mcp-filesystem/server.py" write_file path="/tmp/test.txt" content="hello world"

# File stats
mcporter call --stdio "python3 scripts/mcp-filesystem/server.py" file_stats path="~/.openclaw/workspace/MEMORY.md"
```

### With OpenClaw MCP Config

Add to `~/.openclaw/openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "filesystem": {
        "command": "python3",
        "args": ["/Users/fuzhuo/.openclaw/workspace/scripts/mcp-filesystem/server.py"]
      }
    }
  }
}
```

## Security

Sandbox mode restricts operations to:
- `~/` (home directory)
- `/tmp/`
- `~/.openclaw/workspace`

Can be disabled with `MCP_FS_SANDBOX=false` env var (not recommended).

## Architecture

```
mcporter --stdio → python3 server.py → FastMCP → stdio transport
                     ↓
              Tool Handlers
                     ↓
              os.path (sandboxed)
```

## Key Insights

1. **mcporter works with --stdio servers**: Tool name is just the function name (e.g., `list_directory`), not the server-prefixed name
2. **FastMCP is the simplest way** to build MCP servers in Python - just decorate functions with `@mcp.tool()`
3. **Security is important**: Always sandbox filesystem operations with allowlist
4. **MCP protocol is transport-agnostic**: The same server works over stdio (local) or HTTP (remote)

## Tested

- ✅ `list_directory` - works
- ✅ `read_file` - works
- ✅ `file_stats` - works  
- ✅ `write_file` - works
- ✅ `search_files` - works
- ✅ `create_directory` - works
- ✅ `delete_file` - works
