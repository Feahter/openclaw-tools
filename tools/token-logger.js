#!/usr/bin/env node3
/**
 * Token Usage Logger for OpenClaw
 * 集成到 OpenClaw 的 API 调用监控
 * 
 * 使用方式:
 * 在 OpenClaw 配置中设置环境变量或在 agent 初始化时引入
 */

import { spawn } from 'node:child_process';
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const TOKEN_MONITOR_PY = "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py";
const LOG_DIR = "/Users/fuzhuo/.openclaw/workspace/data";
const LOG_FILE = join(LOG_DIR, "openclaw-token-log.jsonl");

// 确保目录存在
if (!existsSync(LOG_DIR)) {
  mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * 记录 API 调用
 * @param {Object} params
 * @param {string} params.provider - Provider 名称 (如 minimax, openai, anthropic)
 * @param {string} params.model - 模型名称
 * @param {number} params.promptTokens - Prompt tokens
 * @param {number} params.completionTokens - Completion tokens
 * @param {number} [params.cost=0] - 费用
 * @param {string} [params.sessionKey] - 会话 key
 */
export function logTokenUsage(params) {
  const { provider, model, promptTokens, completionTokens, cost = 0, sessionKey } = params;
  
  const totalTokens = promptTokens + completionTokens;
  
  // 记录到本地文件
  const record = {
    timestamp: new Date().toISOString(),
    provider,
    model,
    promptTokens,
    completionTokens,
    totalTokens,
    cost,
    sessionKey
  };
  
  writeFileSync(LOG_FILE, JSON.stringify(record) + '\n', { flag: 'a' });
  
  // 调用 Python 监控器
  try {
    const proc = spawn('python3', [
      TOKEN_MONITOR_PY, 'log',
      provider,
      model,
      String(promptTokens),
      String(completionTokens),
      String(cost),
      sessionKey || ''
    ], {
      detached: true,
      stdio: 'ignore'
    });
    
    proc.unref();
  } catch (err) {
    console.error('Failed to log token usage:', err.message);
  }
  
  // 如果 token 过多，打印警告
  if (totalTokens > 100000) {
    console.warn(`⚠️ High token usage: ${provider}/${model} - ${totalTokens.toLocaleString()} tokens`);
  }
  
  return record;
}

/**
 * 检查上下文大小
 * @param {Array} messages - 消息数组
 * @param {string} [sessionKey] - 会话 key
 * @returns {Object} 检查结果
 */
export function checkContextSize(messages, sessionKey) {
  const content = JSON.stringify(messages);
  const estimatedTokens = Math.ceil(content.length / 4);
  
  const MAX_TOKENS = 100000;
  const MAX_MESSAGES = 20;
  
  const result = {
    estimatedTokens,
    messageCount: messages.length,
    status: 'ok',
    suggestions: []
  };
  
  if (estimatedTokens > MAX_TOKENS) {
    result.status = 'warning';
    result.suggestions.push(`Context too large (${estimatedTokens.toLocaleString()} tokens). Consider reducing history.`);
  }
  
  if (messages.length > MAX_MESSAGES) {
    result.status = 'warning';
    result.suggestions.push(`Too many messages (${messages.length}). Keep last ${MAX_MESSAGES} messages.`);
  }
  
  return result;
}

/**
 * 优化消息历史
 * @param {Array} messages - 原始消息
 * @param {number} [keepLast=20] - 保留最近 N 条
 * @returns {Array} 优化后的消息
 */
export function optimizeHistory(messages, keepLast = 20) {
  if (messages.length <= keepLast) {
    return messages;
  }
  
  // 保留系统消息 + 最近 N 条
  let optimized;
  if (messages[0]?.role === 'system') {
    optimized = [messages[0], ...messages.slice(-keepLast + 1)];
  } else {
    optimized = messages.slice(-keepLast);
  }
  
  return optimized;
}

/**
 * 获取今日统计
 */
export async function getDailyStats() {
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', [TOKEN_MONITOR_PY, 'daily'], {
      stdout: 'pipe',
      stderr: 'pipe'
    });
    
    let stdout = '';
    proc.stdout.on('data', (d) => stdout += d.toString());
    proc.on('close', () => resolve(stdout));
    proc.on('error', reject);
  });
}

/**
 * 获取最近消耗报告
 * @param {number} [hours=24] - 最近几小时
 */
export async function getRecentUsage(hours = 24) {
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', [TOKEN_MONITOR_PY, 'recent', String(hours)], {
      stdout: 'pipe',
      stderr: 'pipe'
    });
    
    let stdout = '';
    proc.stdout.on('data', (d) => stdout += d.toString());
    proc.on('close', () => resolve(stdout));
    proc.on('error', reject);
  });
}

// 自动检查脚本
if (process.argv[1]?.includes('token-logger')) {
  const command = process.argv[2];
  
  switch (command) {
    case 'stats':
      getDailyStats().then(console.log).catch(console.error);
      break;
    case 'recent':
      getRecentUsage(parseInt(process.argv[3]) || 24).then(console.log).catch(console.error);
      break;
    default:
      console.log('OpenClaw Token Logger');
      console.log('');
      console.log('Usage:');
      console.log('  node token-logger.js stats      # 今日统计');
      console.log('  node token-logger.js recent [h] # 最近消耗');
  }
}

export default {
  logTokenUsage,
  checkContextSize,
  optimizeHistory,
  getDailyStats,
  getRecentUsage
};
