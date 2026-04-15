#!/usr/local/opt/node@24/bin/node
/**
 * openclaw-control-cli
 * CLI tool for OpenClaw gateway control and proxy connection
 * 
 * Usage:
 *   node openclaw-control-cli.js <command> [options]
 * 
 * Commands:
 *   connect      Connect to gateway with optional proxy
 *   status       Show gateway status
 *   config       Get/set gateway configuration
 *   proxy        Configure proxy settings
 *   channels     List channel status
 *   sessions     List active sessions
 */

import { WebSocket } from 'ws';

const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || 'ws://127.0.0.1:28789';
const DEFAULT_TIMEOUT = 10000;

// ──────────────────────────────────────────────────────────────────────────────
// Gateway Client
// ──────────────────────────────────────────────────────────────────────────────

class GatewayClient {
  constructor(url, options = {}) {
    this.url = url;
    this.token = options.token || process.env.OPENCLAW_TOKEN || '';
    this.password = options.password || process.env.OPENCLAW_PASSWORD || '';
    this.timeout = options.timeout || DEFAULT_TIMEOUT;
    this.ws = null;
    this.pending = new Map();
    this.seq = 0;
    this.connected = false;
    this.hello = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Connection timeout')), this.timeout);
      
      this.ws = new WebSocket(this.url);
      
      this.ws.on('open', () => {
        clearTimeout(timer);
        this.sendConnect();
      });
      
      this.ws.on('message', (data) => {
        try {
          const msg = JSON.parse(String(data));
          this.handleMessage(msg, resolve, reject);
        } catch (e) {
          console.error('Parse error:', e.message);
        }
      });
      
      this.ws.on('error', (err) => {
        clearTimeout(timer);
        reject(new Error(`WebSocket error: ${err.message}`));
      });
      
      this.ws.on('close', (code, reason) => {
        this.connected = false;
        if (!this.hello) {
          reject(new Error(`Connection closed: ${code} ${reason}`));
        }
      });
    });
  }

  sendConnect() {
    const payload = {
      minProtocol: 3,
      maxProtocol: 3,
      client: {
        id: 'openclaw-control-cli',
        version: '1.0.0',
        platform: process.platform,
        mode: 'cli',
      },
      role: 'operator',
      scopes: ['operator.admin', 'operator.approvals', 'operator.pairing'],
      auth: this.token ? { token: this.token } : this.password ? { password: this.password } : undefined,
      userAgent: 'openclaw-control-cli/1.0.0',
      locale: process.env.LANG || 'en-US',
    };
    
    this.request('connect', payload);
  }

  handleMessage(msg, resolve, reject) {
    if (msg.type === 'res') {
      const pending = this.pending.get(msg.id);
      if (pending) {
        this.pending.delete(msg.id);
        if (msg.ok) {
          pending.resolve(msg.payload);
        } else {
          pending.reject(new Error(msg.error?.message || 'Request failed'));
        }
      }
      return;
    }
    
    if (msg.type === 'event') {
      if (msg.event === 'connect.hello') {
        this.hello = msg.payload;
        this.connected = true;
        resolve(msg.payload);
      }
      // Handle other events as needed
      return;
    }
  }

  request(method, params = {}) {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('Not connected'));
        return;
      }
      
      const id = `cli-${++this.seq}`;
      const msg = { type: 'req', id, method, params };
      
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, this.timeout);
      
      this.pending.set(id, {
        resolve: (payload) => {
          clearTimeout(timer);
          resolve(payload);
        },
        reject: (err) => {
          clearTimeout(timer);
          reject(err);
        },
      });
      
      this.ws.send(JSON.stringify(msg));
    });
  }

  close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Commands
// ──────────────────────────────────────────────────────────────────────────────

async function cmdStatus(client) {
  const health = await client.request('health', {});
  const sessions = await client.request('sessions.list', {});
  
  console.log('\n📊 Gateway Status\n');
  console.log('  Status:', health.ok ? '✅ OK' : '❌ Error');
  console.log('  Version:', health.serverVersion || 'unknown');
  console.log('  Uptime:', health.uptime ? formatUptime(health.uptime) : 'unknown');
  console.log('  Active Sessions:', sessions.sessions?.length || 0);
  
  if (sessions.sessions?.length > 0) {
    console.log('\n  Recent Sessions:');
    sessions.sessions.slice(0, 5).forEach(s => {
      console.log(`    - ${s.key} (${s.agentId || 'main'})`);
    });
  }
  
  return { health, sessions };
}

async function cmdConfig(client, args) {
  if (args.length === 0) {
    const config = await client.request('config.get', {});
    console.log('\n⚙️  Current Configuration\n');
    console.log(JSON.stringify(config.config, null, 2));
    return config;
  }
  
  const [action, path, value] = args;
  
  if (action === 'get') {
    const result = await client.request('config.get', {});
    const value = path?.split('.').reduce((obj, key) => obj?.[key], result.config);
    console.log(value !== undefined ? JSON.stringify(value, null, 2) : 'Path not found');
    return result;
  }
  
  if (action === 'set' && path && value !== undefined) {
    const config = await client.request('config.get', {});
    const parsedValue = tryParseValue(value);
    setNestedValue(config.config, path.split('.'), parsedValue);
    
    const result = await client.request('config.set', {
      raw: JSON.stringify(config.config, null, 2),
      baseHash: config.hash,
    });
    
    console.log('✅ Configuration updated');
    return result;
  }
  
  console.log('Usage: config [get <path> | set <path> <value>]');
}

async function cmdProxy(client, args) {
  const [action, proxyUrl] = args;
  
  if (action === 'show' || !action) {
    const config = await client.request('config.get', {});
    const proxy = config.config?.gateway?.proxy;
    
    console.log('\n🌐 Proxy Configuration\n');
    console.log('  HTTP Proxy:', proxy?.http || 'not set');
    console.log('  HTTPS Proxy:', proxy?.https || 'not set');
    console.log('  No Proxy:', proxy?.noProxy || 'not set');
    
    return { proxy };
  }
  
  if (action === 'set' && proxyUrl) {
    const config = await client.request('config.get', {});
    
    config.config = config.config || {};
    config.config.gateway = config.config.gateway || {};
    config.config.gateway.proxy = config.config.gateway.proxy || {};
    
    // Parse proxy URL
    const parsed = parseProxyUrl(proxyUrl);
    Object.assign(config.config.gateway.proxy, parsed);
    
    const result = await client.request('config.set', {
      raw: JSON.stringify(config.config, null, 2),
      baseHash: config.hash,
    });
    
    console.log('✅ Proxy configured:', proxyUrl);
    return result;
  }
  
  if (action === 'clear') {
    const config = await client.request('config.get', {});
    
    if (config.config?.gateway?.proxy) {
      delete config.config.gateway.proxy;
      
      const result = await client.request('config.set', {
        raw: JSON.stringify(config.config, null, 2),
        baseHash: config.hash,
      });
      
      console.log('✅ Proxy cleared');
      return result;
    }
    
    console.log('ℹ️  No proxy configured');
    return { cleared: false };
  }
  
  console.log('Usage: proxy [show | set <url> | clear]');
}

async function cmdChannels(client) {
  const result = await client.request('channels.status', { probe: false, timeoutMs: 5000 });
  
  console.log('\n📡 Channel Status\n');
  
  const channels = result.channels || {};
  for (const [name, status] of Object.entries(channels)) {
    const icon = status.enabled ? '✅' : '❌';
    console.log(`  ${icon} ${name}: ${status.status || 'unknown'}`);
  }
  
  return result;
}

async function cmdSessions(client) {
  const result = await client.request('sessions.list', {});
  
  console.log('\n💬 Active Sessions\n');
  
  const sessions = result.sessions || [];
  if (sessions.length === 0) {
    console.log('  No active sessions');
    return result;
  }
  
  sessions.forEach((s, i) => {
    const agent = s.agentId || 'main';
    const messages = s.messageCount || 0;
    console.log(`  ${i + 1}. ${s.key} [${agent}] (${messages} messages)`);
  });
  
  return result;
}

async function cmdConnect(client, args) {
  const [proxyUrl] = args;
  
  console.log('\n🔗 Connecting to Gateway...\n');
  console.log('  URL:', client.url);
  console.log('  Auth:', client.token ? 'token' : client.password ? 'password' : 'none');
  
  try {
    const hello = await client.connect();
    console.log('\n✅ Connected!\n');
    console.log('  Server:', hello.snapshot?.serverVersion || 'unknown');
    console.log('  Sessions:', hello.snapshot?.sessions?.count || 0);
    
    if (proxyUrl) {
      console.log('\n🌐 Configuring proxy...');
      await cmdProxy(client, ['set', proxyUrl]);
    }
    
    return hello;
  } catch (err) {
    console.error('\n❌ Connection failed:', err.message);
    throw err;
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────────────────────────────────────

function formatUptime(seconds) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function tryParseValue(str) {
  try {
    return JSON.parse(str);
  } catch {
    return str;
  }
}

function setNestedValue(obj, path, value) {
  const last = path.pop();
  const target = path.reduce((obj, key) => {
    obj[key] = obj[key] || {};
    return obj[key];
  }, obj);
  target[last] = value;
}

function parseProxyUrl(url) {
  const parsed = new URL(url);
  const result = {};
  
  if (parsed.protocol === 'http:') {
    result.http = url;
    result.https = url; // Use same for HTTPS by default
  } else if (parsed.protocol === 'https:') {
    result.https = url;
  } else if (parsed.protocol === 'socks5:') {
    result.http = url;
    result.https = url;
  }
  
  // Handle no_proxy from URL query params
  const noProxy = parsed.searchParams.get('noProxy');
  if (noProxy) {
    result.noProxy = noProxy;
  }
  
  return result;
}

// ──────────────────────────────────────────────────────────────────────────────
// CLI Entry Point
// ──────────────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
OpenClaw Control CLI

Usage:
  node openclaw-control-cli.js <command> [options]

Commands:
  connect [proxy_url]  Connect to gateway, optionally configure proxy
  status               Show gateway status
  config [get|set]     Get/set gateway configuration
  proxy [show|set|clear]  Manage proxy settings
  channels             List channel status
  sessions             List active sessions

Environment Variables:
  OPENCLAW_GATEWAY_URL   Gateway WebSocket URL (default: ws://127.0.0.1:28789)
  OPENCLAW_TOKEN         Authentication token
  OPENCLAW_PASSWORD     Authentication password

Examples:
  # Connect and show status
  node openclaw-control-cli.js connect

  # Connect with proxy
  node openclaw-control-cli.js connect http://127.0.0.1:7890

  # Show proxy settings
  node openclaw-control-cli.js proxy show

  # Set proxy
  node openclaw-control-cli.js proxy set http://127.0.0.1:7890

  # Clear proxy
  node openclaw-control-cli.js proxy clear

  # Get config value
  node openclaw-control-cli.js config get gateway.port

  # Set config value
  node openclaw-control-cli.js config set gateway.port 28790
`);
    process.exit(0);
  }
  
  const [command, ...cmdArgs] = args;
  const client = new GatewayClient(GATEWAY_URL);
  
  try {
    // Commands that don't require connection
    if (command === 'connect') {
      await cmdConnect(client, cmdArgs);
    } else {
      // All other commands need connection
      await client.connect();
      
      switch (command) {
        case 'status':
          await cmdStatus(client);
          break;
        case 'config':
          await cmdConfig(client, cmdArgs);
          break;
        case 'proxy':
          await cmdProxy(client, cmdArgs);
          break;
        case 'channels':
          await cmdChannels(client);
          break;
        case 'sessions':
          await cmdSessions(client);
          break;
        default:
          console.error(`Unknown command: ${command}`);
          console.log('Run with --help for usage');
          process.exit(1);
      }
    }
  } catch (err) {
    console.error('\n❌ Error:', err.message);
    process.exit(1);
  } finally {
    client.close();
  }
}

main().catch(console.error);
