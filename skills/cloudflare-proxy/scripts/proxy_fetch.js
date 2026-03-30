#!/usr/bin/env node
/**
 * Cloudflare Worker Proxy — Fetch 模式（Node.js 实现）
 *
 * macOS 的 Python ssl 模块不支持 Cloudflare Workers 的 TLS 版本，
 * 所以改用 Node.js（使用自己的 crypto，完美支持 TLS 1.3）。
 */

const https = require('https');

const args = process.argv.slice(2);
const maxChars = 50000;

if (!args[0] || args[0] === '--help') {
  console.log('用法: node proxy_fetch.js <目标URL> [maxChars] [--proxy <代理URL>]');
  console.log('示例: node proxy_fetch.js https://github.com 30000');
  process.exit(0);
}

let targetUrl = args[0];
let proxy = 'https://arthur-proxy.frankfeahter.workers.dev';
let maxCharsOverride = maxChars;

// Parse flags
const remainingArgs = args.slice(1);
for (let i = 0; i < remainingArgs.length; i++) {
  if (remainingArgs[i] === '--proxy' && remainingArgs[i + 1]) {
    proxy = remainingArgs[i + 1];
    i++;
  } else if (!isNaN(parseInt(remainingArgs[i]))) {
    maxCharsOverride = parseInt(remainingArgs[i]);
  }
}

const encodedTarget = encodeURIComponent(targetUrl);
const proxyFetchUrl = `${proxy.replace(/\/$/, '')}/?url=${encodedTarget}&_raw=1`;

const req = https.get(proxyFetchUrl, {
  headers: {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
    'Connection': 'keep-alive',
  },
  timeout: 30000,
}, (res) => {
  if (res.statusCode >= 400) {
    console.error(`HTTP ${res.statusCode}`);
    process.exit(1);
  }

  const chunks = [];
  res.on('data', chunk => chunks.push(chunk));
  res.on('end', () => {
    let content = Buffer.concat(chunks).toString('utf8');

    // Cloudflare challenge detection
    if (content.includes('cf-challenge') || content.includes('turnstile') ||
        content.includes('_cf_translation') || content.includes('cloudflare')) {
      // Check if it's actually the challenge page
      if (content.includes('Ray ID') || content.includes('的人机验证')) {
        console.error('ERROR: CF验证墙拦截 — 自建 Worker 可避免此问题');
        process.exit(1);
      }
    }

    // Check if we got the homepage instead of target content
    if (content.includes('CF Proxy') && !content.includes(targetUrl)) {
      // We got the proxy homepage — target wasn't fetched correctly
      const errMsg = `Proxy returned homepage instead of target content. URL: ${targetUrl}`;
      console.error('ERROR:', errMsg);
      process.exit(1);
    }

    if (content.length > maxCharsOverride) {
      content = content.slice(0, maxCharsOverride) +
        `\n\n[Output truncated at ${maxCharsOverride} chars, full: ${content.length} chars]`;
    }
    process.stdout.write(content);
  });
});

req.on('error', (e) => {
  console.error('Network error:', e.message);
  process.exit(1);
});

req.on('timeout', () => {
  req.destroy();
  console.error('Request timeout');
  process.exit(1);
});
