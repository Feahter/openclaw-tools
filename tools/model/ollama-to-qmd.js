#!/usr/bin/env node
/**
 * Ollama Embedding to QMD Vector Store (Node.js version)
 * 使用 Ollama 生成向量，写入 qmd 的 SQLite vec 表
 * 
 * 用法:
 *   node ollama-to-qmd.js              # 嵌入所有未向量化的文档
 *   node ollama-to-qmd.js --force     # 强制重新嵌入所有文档
 *   node ollama-to-qmd.js --dry-run   # 只显示要处理的文档
 */

const Database = require('better-sqlite3');
const { load } = require('sqlite-vec');
const fs = require('fs');
const path = require('path');
const http = require('http');
const { promisify } = require('util');

// 配置
const QMD_INDEX = path.join(process.env.HOME, '.cache/qmd/index.sqlite');
const OLLAMA_MODEL = 'nomic-embed-text';
const BATCH_SIZE = 10;
const MAX_CONTENT_LENGTH = 8000;

// promisify http request
const httpPost = promisify((options, data, callback) => {
  const req = http.request(options, (res) => {
    let body = '';
    res.on('data', chunk => body += chunk);
    res.on('end', () => callback(null, body));
  });
  req.on('error', callback);
  req.write(JSON.stringify(data));
  req.end();
});

async function getOllamaEmbedding(text) {
  try {
    const result = await httpPost({
      hostname: 'localhost',
      port: 11434,
      path: '/api/embeddings',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      model: OLLAMA_MODEL,
      prompt: text.slice(0, MAX_CONTENT_LENGTH)
    });
    
    const data = JSON.parse(result);
    return data.embedding;
  } catch (e) {
    console.error('Ollama error:', e.message);
    return null;
  }
}

function checkStatus(db) {
  const total = db.prepare('SELECT COUNT(DISTINCT hash) FROM documents WHERE active = 1').get()[0];
  const embedded = db.prepare('SELECT COUNT(DISTINCT hash) FROM content_vectors').get()[0];
  return { total, embedded, pending: total - embedded };
}

function getDocsNeedingEmbedding(db, force = false) {
  if (force) {
    return db.prepare(`
      SELECT d.path, c.doc, d.hash
      FROM documents d
      JOIN content c ON d.hash = c.hash
      WHERE d.active = 1
      GROUP BY d.hash
    `).all();
  }
  
  return db.prepare(`
    SELECT d.path, c.doc, d.hash
    FROM documents d
    JOIN content c ON d.hash = c.hash
    LEFT JOIN content_vectors cv ON d.hash = cv.hash
    WHERE d.active = 1 AND cv.hash IS NULL
    GROUP BY d.hash
  `).all();
}

async function embedDocuments(args) {
  console.log(`🤖 使用模型: ${OLLAMA_MODEL}`);
  console.log(`📁 QMD 索引: ${QMD_INDEX}\n`);
  
  // 打开数据库并加载 sqlite-vec
  const db = new Database(QMD_INDEX);
  await load(db);
  console.log('✅ sqlite-vec 扩展已加载\n');
  
  // 检查状态
  const status = checkStatus(db);
  console.log(`📊 向量状态: ${status.embedded}/${status.total} 已嵌入, ${status.pending} 待处理`);
  
  if (status.pending === 0 && !args.force) {
    console.log('✅ 所有文档已向量完成!');
    db.close();
    return;
  }
  
  // 获取待处理文档
  const docs = getDocsNeedingEmbedding(db, args.force);
  console.log(`📄 将处理 ${docs.length} 个文档...\n`);
  
  if (args.dryRun) {
    console.log('📝 Dry Run - 以下文档将被向量化:');
    docs.slice(0, 10).forEach((d, i) => console.log(`  ${i+1}. ${d.path}`));
    if (docs.length > 10) console.log(`  ... 还有 ${docs.length - 10} 个`);
    db.close();
    return;
  }
  
  if (!docs.length) {
    console.log('✅ 没有需要处理的文档');
    db.close();
    return;
  }
  
  // 批量嵌入
  let success = 0, error = 0;
  
  for (let i = 0; i < docs.length; i++) {
    const { path: docPath, doc, hash } = docs[i];
    process.stdout.write(`🔄 [${i+1}/${docs.length}] 处理: ${docPath.slice(0,40)}... `);
    
    const embedding = await getOllamaEmbedding(doc);
    
    if (!embedding) {
      console.log('❌ 获取向量失败');
      error++;
      await new Promise(r => setTimeout(r, 1000));
      continue;
    }
    
    try {
      const hashSeq = `${hash}|0`;
      
      // 写入 vectors_vec
      db.prepare('INSERT OR REPLACE INTO vectors_vec (hash_seq, embedding) VALUES (?, ?)').run(
        hashSeq,
        JSON.stringify(embedding)
      );
      
      // 更新 content_vectors 追踪表
      const now = new Date().toISOString();
      db.prepare('INSERT OR REPLACE INTO content_vectors (hash, seq, pos, model, embedded_at) VALUES (?, 0, 0, ?, ?)').run(
        hash,
        OLLAMA_MODEL.replace(/-/g, ''),
        now
      );
      
      success++;
      console.log('✅');
      
    } catch (e) {
      console.log(`❌ 写入失败: ${e.message}`);
      error++;
    }
    
    // 批量提交
    if ((i + 1) % BATCH_SIZE === 0) {
      console.log(`\n📦 批量提交 (${i+1}/${docs.length})`);
    }
    
    await new Promise(r => setTimeout(r, 50));
  }
  
  db.close();
  
  const finalStatus = checkStatus(db);
  console.log(`\n🎉 完成!`);
  console.log(`   成功: ${success}`);
  console.log(`   失败: ${error}`);
  console.log(`   总计: ${finalStatus.embedded}/${finalStatus.total} 已嵌入`);
}

// 解析参数
const args = {
  force: process.argv.includes('--force') || process.argv.includes('-f'),
  dryRun: process.argv.includes('--dry-run') || process.argv.includes('-n')
};

embedDocuments(args).catch(console.error);
