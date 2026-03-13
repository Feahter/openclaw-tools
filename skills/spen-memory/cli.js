#!/usr/bin/env node

/**
 * SPEN-Memory CLI v1.1.0
 * 动态按需记忆系统的命令行工具
 */

import SPENMemory from './spen-memory.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 解析命令行参数
function parseArgs(args) {
    const result = {
        command: args[2] || 'help',
        options: {}
    };
    
    for (let i = 3; i < args.length; i++) {
        const arg = args[i];
        const nextArg = args[i + 1];
        
        if (arg.startsWith('--')) {
            const key = arg.replace('--', '');
            
            if (['persist', 'help', 'version', 'archive', 'embedding', 'local-embedding'].includes(key)) {
                result.options[key] = true;
            } else if (nextArg && !nextArg.startsWith('--')) {
                if (!isNaN(nextArg)) {
                    result.options[key] = parseFloat(nextArg);
                } else {
                    result.options[key] = nextArg;
                }
                i++;
            }
        }
    }
    
    return result;
}

// 主命令处理
async function handleCommand(parsed) {
    const { command, options } = parsed;
    
    const storagePath = path.join(__dirname, 'memory-data.json');
    let memory;
    
    try {
        if (fs.existsSync(storagePath)) {
            const data = JSON.parse(fs.readFileSync(storagePath, 'utf-8'));
            memory = new SPENMemory({ ...options, persist: false });
            memory.import(data);
        } else {
            memory = new SPENMemory({ ...options, persist: false });
        }
    } catch (e) {
        memory = new SPENMemory({ ...options, persist: false });
    }
    
    const save = () => {
        const data = memory.export();
        fs.writeFileSync(storagePath, JSON.stringify(data, null, 2));
    };
    
    switch (command) {
        case 'init':
            console.log('✅ 初始化 SPEN-Memory v1.2.0');
            console.log(`   最大记忆数: ${options.maxSize || 1000}`);
            console.log(`   压缩比: ${options.compressRatio || 0.3}`);
            console.log(`   归档功能: ${options.archive ? '启用' : '关闭'}`);
            console.log(`   向量语义: ${options.embedding ? '启用' : '关闭'}`);
            if (options.localEmbedding) {
                console.log(`   本地向量: 启用 (无需 API)`);
            }
            save();
            break;
            
        case 'add':
            if (!options.type || !options.content) {
                console.error('❌ 请指定 --type 和 --content');
                process.exit(1);
            }
            const id = memory.addEvent({
                type: options.type,
                content: options.content,
                importance: options.importance || 0.5
            });
            console.log(`✅ 添加成功: ${id}`);
            save();
            break;
            
        case 'retrieve':
        case 'search':
            if (!options.query && !options.text) {
                console.error('❌ 请指定 --query 或 --text');
                process.exit(1);
            }
            const queryText = options.query || options.text;
            const maxResults = options.maxResults || options.maxRetrieve || 5;
            const result = await memory.retrieve({
                text: queryText,
                maxResults: maxResults
            });
            
            console.log(`\n📋 检索结果 (${result.context.memoryCount} 条记忆)`);
            console.log(`   耗时: ${result.metadata.queryTime}ms`);
            console.log(`   来源: 语义${result.metadata.sources.semantic} | 时间${result.metadata.sources.temporal} | 重要${result.metadata.sources.importance}\n`);
            console.log(result.context.text);
            console.log(`\n📝 ${result.context.summary}`);
            
            if (result.context.suggestions && result.context.suggestions.length > 0) {
                console.log('\n💡 建议:');
                result.context.suggestions.forEach(s => console.log(`   • ${s}`));
            }
            break;
            
        case 'archive':
            if (!options.query) {
                console.error('❌ 请指定 --query');
                process.exit(1);
            }
            const archiveResult = memory.retrieveArchive(options.query);
            console.log(`\n📦 归档检索: ${archiveResult.summary}`);
            archiveResult.results.forEach(r => {
                console.log(`   [${r.type}] ${r.content}...`);
            });
            break;
            
        case 'stats':
            const stats = memory.getStats();
            console.log('\n📊 记忆统计');
            console.log(`   当前存储: ${stats.currentMemorySize} 条`);
            console.log(`   归档数量: ${stats.archiveSize} 条`);
            console.log(`   最大容量: ${stats.maxMemorySize} 条`);
            console.log(`   压缩比: ${(stats.compressionRatio * 100).toFixed(1)}%`);
            console.log(`   总添加: ${stats.totalEvents} 次`);
            console.log(`   总检索: ${stats.retrievalCount} 次`);
            break;
            
        case 'export':
            const exportPath = options.file || 'spen-memory-export.json';
            const exportData = memory.export();
            fs.writeFileSync(exportPath, JSON.stringify(exportData, null, 2));
            console.log(`✅ 已导出到: ${exportPath}`);
            break;
            
        case 'import':
            if (!options.file) {
                console.error('❌ 请指定 --file');
                process.exit(1);
            }
            const importData = JSON.parse(fs.readFileSync(options.file, 'utf-8'));
            memory.import(importData);
            save();
            console.log(`✅ 已导入 ${importData.events.length} 条记忆`);
            break;
            
        case 'clear':
            memory.clear();
            if (fs.existsSync(storagePath)) {
                fs.unlinkSync(storagePath);
            }
            console.log('✅ 记忆已清空');
            break;
            
        case 'list':
            const list = memory.events.map(e => {
                const time = new Date(e.timestamp).toLocaleString('zh-CN');
                return `${time} [${e.type}] ${e.content.substring(0, 50)}...`;
            });
            console.log(`\n📚 共 ${list.length} 条记忆:\n`);
            list.forEach((item, i) => console.log(`${i + 1}. ${item}`));
            break;
            
        case 'help':
        default:
            console.log(`
🧠 SPEN-Memory CLI v1.2.0

用法:
  spen-memory <command> [options]

命令:
  init                  初始化记忆系统
  add                   添加记忆
  retrieve              检索记忆 (别名: search)
  archive               归档检索
  stats                 查看统计
  list                  列出所有记忆
  export                导出记忆
  import                导入记忆
  clear                  清空记忆
  help                  显示帮助

选项:
  --type <类型>         记忆类型 (对话/工具/用户/系统/错误)
  --content <内容>       记忆内容
  --importance <0-1>    重要性
  --query <文本>        检索关键词
  --max-size <数字>     最大记忆数 (默认: 1000)
  --compress-ratio <数字> 压缩比 (默认: 0.3)
  --max-results <数字>  最大检索数 (默认: 5)
  --file <路径>         文件路径
  --archive             启用归档功能
  --embedding           启用向量语义 (需要 API)
  --local-embedding     启用本地向量 (无需 API)
  --persist             启用持久化

向量语义配置:
  --provider <openai|cohere|local>  向量提供商
  --api-key <密钥>      API 密钥
  --model <模型>        模型名称

示例:
  # 基础用法
  spen-memory init --max-size 500 --archive
  spen-memory add --type "对话" --content "用户想订机票" --importance 0.9
  spen-memory retrieve --query "机票"

  # 启用本地向量 (无需 API)
  spen-memory init --max-size 500 --local-embedding

  # 启用 OpenAI 向量
  spen-memory init --max-size 500 --embedding --api-key sk-xxx

  # 归档检索
  spen-memory archive --query "机票"
  spen-memory stats
`);
            break;
    }
}

const parsed = parseArgs(process.argv);
handleCommand(parsed);
