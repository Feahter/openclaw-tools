#!/usr/bin/env node
/**
 * Direct Vector Search with Ollama + SQLite
 * 不依赖 qmd 的查询模型，直接用 Ollama 做语义搜索
 * 
 * 用法:
 *   node ollama-vector-search.js "搜索内容"
 */

const Database = require('better-sqlite3');
const sqliteVec = require('sqlite-vec');
const http = require('http');

const QMD_INDEX = require('path').join(process.env.HOME, '.cache/qmd/index.sqlite');
const OLLAMA_MODEL = 'nomic-embed-text';

function httpPost(path, data) {
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: 'localhost',
      port: 11434,
      path: path,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(JSON.stringify(data));
    req.end();
  });
}

// 简单的余弦相似度计算
function cosineSimilarity(a, b) {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// 解析向量 Buffer (float array)
function parseVectorBuffer(buf) {
  const arr = new Float32Array(buf.length / 4);
  for (let i = 0; i < arr.length; i++) {
    arr[i] = buf.readFloatLE(i * 4);
  }
  return arr;
}

async function search(query, limit = 5) {
  console.log(`🔍 搜索: "${query}"\n`);
  
  // 1. 用 Ollama 生成查询向量
  console.log('📡 调用 Ollama 生成向量...');
  const { embedding } = await httpPost('/api/embeddings', {
    model: OLLAMA_MODEL,
    prompt: query
  });
  console.log('✅ 向量生成完成\n');
  
  // 2. 打开数据库并加载 sqlite-vec
  const db = new Database(QMD_INDEX, { readonly: true });
  await sqliteVec.load(db);
  
  // 3. 获取所有向量
  console.log('📊 搜索向量数据库...');
  const vectors = db.prepare(`
    SELECT v.hash_seq, v.embedding, d.path, c.doc
    FROM vectors_vec v
    JOIN documents d ON v.hash_seq = d.hash || '|0'
    JOIN content c ON d.hash = c.hash
    WHERE d.active = 1
  `).all();
  
  db.close();
  
  // 4. 计算相似度
  const results = vectors.map(v => ({
    path: v.path,
    doc: v.doc,
    similarity: cosineSimilarity(embedding, parseVectorBuffer(v.embedding))
  }));
  
  // 5. 排序并取 top N
  results.sort((a, b) => b.similarity - a.similarity);
  const topResults = results.slice(0, limit);
  
  // 6. 输出结果
  console.log(`📊 找到 ${vectors.length} 个向量，显示前 ${limit} 个:\n`);
  
  topResults.forEach((r, i) => {
    const score = r.similarity * 100;
    const snippet = r.doc.slice(0, 200).replace(/\n/g, ' ');
    console.log(`#${i+1} [${score.toFixed(1)}%] ${r.path}`);
    console.log(`   ${snippet}...\n`);
  });
}

const query = process.argv.slice(2).join(' ') || '小说创作';
search(query).catch(console.error);
