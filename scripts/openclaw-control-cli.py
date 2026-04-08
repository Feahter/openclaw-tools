#!/usr/bin/env python3
"""
openclaw-control-cli
CLI tool for OpenClaw gateway configuration and proxy management

This tool directly modifies the gateway configuration file since
control-ui requires secure context device identity.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Try to load from qclaw config first
QCLAW_CONFIG = Path.home() / ".qclaw" / "openclaw.json"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

CONFIG_FILE = QCLAW_CONFIG if QCLAW_CONFIG.exists() else OPENCLAW_CONFIG


def load_config() -> Dict[str, Any]:
    """Load gateway configuration"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # QClaw outputs standard JSON
    return json.loads(content)


def save_config(config: Dict[str, Any], backup: bool = True):
    """Save gateway configuration"""
    if backup:
        backup_file = CONFIG_FILE.with_suffix(".json.bak")
        if CONFIG_FILE.exists():
            import shutil
            shutil.copy(CONFIG_FILE, backup_file)
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"✅ Configuration saved to {CONFIG_FILE}")
    print("ℹ️  Restart QClaw app to apply changes")


def get_nested_value(obj: dict, path: str) -> Any:
    """Get nested dictionary value"""
    keys = path.split(".")
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj


def set_nested_value(obj: dict, path: str, value: Any):
    """Set nested dictionary value"""
    keys = path.split(".")
    for key in keys[:-1]:
        obj = obj.setdefault(key, {})
    obj[keys[-1]] = value


def parse_value(value_str: str) -> Any:
    """Parse string value to appropriate type"""
    try:
        return json.loads(value_str)
    except:
        return value_str


# ──────────────────────────────────────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────────────────────────────────────

def cmd_status(args):
    """Show gateway status from config file"""
    config = load_config()
    
    print("\n📊 Gateway Configuration Summary\n")
    
    # Gateway
    gateway = config.get("gateway", {})
    print(f"  Port: {gateway.get('port', 'default')}")
    print(f"  Mode: {gateway.get('mode', 'local')}")
    print(f"  Auth: {gateway.get('auth', {}).get('mode', 'none')}")
    
    # Proxy
    proxy = gateway.get("proxy", {})
    if proxy:
        print("\n🌐 Proxy Settings\n")
        print(f"  HTTP: {proxy.get('http') or 'not set'}")
        print(f"  HTTPS: {proxy.get('https') or 'not set'}")
        print(f"  No Proxy: {proxy.get('noProxy') or 'not set'}")
    else:
        print("\n🌐 Proxy: not configured\n")
    
    # Channels
    channels = config.get("channels", {})
    if channels:
        print("\n📡 Channels\n")
        for name, cfg in channels.items():
            enabled = "✅" if cfg.get("enabled", False) else "❌"
            print(f"  {enabled} {name}")
    
    # Skills limit
    skills = config.get("skills", {})
    limits = skills.get("limits", {})
    if limits:
        print("\n📦 Skills Limits\n")
        print(f"  Max in Prompt: {limits.get('maxSkillsInPrompt', 'unlimited')}")
        print(f"  Max Prompt Chars: {limits.get('maxSkillsPromptChars', 'unlimited')}")
    
    return config


def cmd_config(args):
    """Get/set configuration values"""
    config = load_config()
    
    if not args.config_action:
        # Show full config
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return config
    
    if args.config_action == "get":
        value = get_nested_value(config, args.config_path) if args.config_path else config
        print(json.dumps(value, indent=2, ensure_ascii=False) if value is not None else "null")
        return value
    
    if args.config_action == "set":
        if not args.config_path or args.config_value is None:
            print("Error: --path and --value required for set")
            sys.exit(1)
        
        value = parse_value(args.config_value)
        set_nested_value(config, args.config_path, value)
        save_config(config)
        
        print(f"✅ Set {args.config_path} = {json.dumps(value)}")
        return config


def cmd_proxy(args):
    """Manage proxy settings"""
    config = load_config()
    
    # Ensure gateway.proxy exists
    config.setdefault("gateway", {}).setdefault("proxy", {})
    proxy = config["gateway"]["proxy"]
    
    if not args.proxy_action or args.proxy_action == "show":
        print("\n🌐 Proxy Configuration\n")
        print(f"  HTTP: {proxy.get('http') or 'not set'}")
        print(f"  HTTPS: {proxy.get('https') or 'not set'}")
        print(f"  No Proxy: {proxy.get('noProxy') or 'not set'}")
        return proxy
    
    if args.proxy_action == "set":
        if not args.proxy_url:
            print("Error: Proxy URL required")
            sys.exit(1)
        
        proxy_url = args.proxy_url
        
        # Parse proxy URL
        from urllib.parse import urlparse
        parsed = urlparse(proxy_url)
        
        # Set HTTP and HTTPS proxy
        proxy["http"] = proxy_url
        proxy["https"] = proxy_url
        
        # Handle no_proxy from query params
        if parsed.query:
            import urllib.parse as up
            params = dict(up.parse_qsl(parsed.query))
            if "noProxy" in params:
                proxy["noProxy"] = params["noProxy"]
        
        save_config(config)
        print(f"✅ Proxy configured: {proxy_url}")
        return proxy
    
    if args.proxy_action == "clear":
        if "proxy" in config.get("gateway", {}):
            del config["gateway"]["proxy"]
            save_config(config)
            print("✅ Proxy cleared")
        else:
            print("ℹ️  No proxy configured")
        
        return {"cleared": True}


def cmd_edit(args):
    """Open config file in editor"""
    editor = os.environ.get("EDITOR", "nano")
    os.system(f"{editor} {CONFIG_FILE}")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Control CLI - Gateway configuration and proxy management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Config File: {CONFIG_FILE}

Examples:
  # Show configuration summary
  %(prog)s status

  # Show proxy settings
  %(prog)s proxy show

  # Set proxy
  %(prog)s proxy set http://127.0.0.1:7890

  # Set proxy with no_proxy
  %(prog)s proxy set "http://127.0.0.1:7890?noProxy=localhost,127.0.0.1,.local"

  # Clear proxy
  %(prog)s proxy clear

  # Get config value
  %(prog)s config get gateway.port

  # Set config value
  %(prog)s config set gateway.port 28790

  # Open config in editor
  %(prog)s edit
""")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status
    subparsers.add_parser("status", help="Show gateway configuration summary")
    
    # Config
    p_config = subparsers.add_parser("config", help="Get/set configuration")
    p_config.add_argument("config_action", choices=["get", "set"], nargs="?", help="Action")
    p_config.add_argument("config_path", nargs="?", help="Config path (dot notation)")
    p_config.add_argument("config_value", nargs="?", help="Value to set (JSON or string)")
    
    # Proxy
    p_proxy = subparsers.add_parser("proxy", help="Manage proxy settings")
    p_proxy.add_argument("proxy_action", choices=["show", "set", "clear"], nargs="?", help="Action")
    p_proxy.add_argument("proxy_url", nargs="?", help="Proxy URL")
    
    # Edit
    subparsers.add_parser("edit", help="Open config file in editor")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "status":
            cmd_status(args)
        elif args.command == "config":
            cmd_config(args)
        elif args.command == "proxy":
            cmd_proxy(args)
        elif args.command == "edit":
            cmd_edit(args)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Make sure QClaw is running and {CONFIG_FILE} exists")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
