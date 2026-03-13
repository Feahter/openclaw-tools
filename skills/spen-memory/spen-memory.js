// spen-memory.js - 动态按需记忆系统 v1.1.0
// SPEN-inspired memory system with lazy loading

class SPENMemory {
    constructor(options = {}) {
        this.options = {
            // 压缩配置
            maxMemorySize: options.maxMemorySize || 1000,
            compressionRatio: options.compressionRatio || 0.3,
            importanceThreshold: options.importanceThreshold || 0.3,
            
            // 时间衰减
            timeDecayFactor: options.timeDecayFactor || 0.95,
            recentWindow: options.recentWindow || 10,
            
            // 检索配置
            maxRetrieve: options.maxRetrieve || 5,
            semanticWeight: options.semanticWeight || 0.5,
            temporalWeight: options.temporalWeight || 0.3,
            importanceWeight: options.importanceWeight || 0.2,
            
            // 持久化
            storageKey: options.storageKey || 'spen_memory',
            persist: options.persist || false,
            
            // 增强功能
            enableArchive: options.enableArchive || true,    // 归档
            enableEmbedding: options.enableEmbedding || false, // 向量语义
            embeddingAPI: options.embeddingAPI || null,       // embedding API
            embeddingProvider: options.embeddingProvider || 'openai', // openai/cohere/local
            embeddingModel: options.embeddingModel || 'text-embedding-3-small',
            embeddingKey: options.embeddingKey || null,        // API key
            embeddingDim: options.embeddingDim || 1536,         // 向量维度
            
            // 本地 embedding (无需 API)
            useLocalEmbedding: options.useLocalEmbedding || false,
            
            ...options
        };
        
        // 核心存储
        this.events = [];
        this.archive = [];        // 归档存储
        this.indices = {
            temporal: new Map(),
            semantic: new Map(),
            importance: []
        };
        
        // 向量存储
        this.embeddings = new Map();
        
        this.stats = {
            totalEvents: 0,
            retrievalCount: 0,
            cacheHits: 0,
            archiveSize: 0
        };
        
        if (this.options.persist) {
            this.loadFromStorage();
        }
    }
    
    // ============================================================
    // 核心1: 添加记忆 (时空联合编码)
    // ============================================================
    
    addEvent(event) {
        const now = Date.now();
        
        const memoryUnit = {
            id: this._generateId(),
            type: event.type || 'general',
            content: event.content,
            timestamp: now,
            metadata: event.metadata || {},
            
            // 时空编码
            temporalPos: this._encodeTemporalPos(now),
            spatialPos: this._encodeSpatialPos(event),
            
            importance: event.importance || this._calcImportance(event),
            accessCount: 0,
            lastAccess: now
        };
        
        this.events.push(memoryUnit);
        this.stats.totalEvents++;
        this._buildIndices(memoryUnit);
        
        // 生成 embedding (如果启用)
        if (this.options.useLocalEmbedding) {
            this._generateEmbedding(memoryUnit);
        } else if (this.options.enableEmbedding && this.options.embeddingAPI) {
            this._generateEmbedding(memoryUnit);
        }
        
        // 压缩
        if (this.events.length > this.options.maxMemorySize) {
            this._compress();
        }
        
        if (this.options.persist) {
            this.saveToStorage();
        }
        
        return memoryUnit.id;
    }
    
    _encodeTemporalPos(timestamp) {
        const date = new Date(timestamp);
        const hour = date.getHours();
        const dayOfWeek = date.getDay();
        
        return {
            timestamp,
            hourSin: Math.sin(2 * Math.PI * hour / 24),
            hourCos: Math.cos(2 * Math.PI * hour / 24),
            daySin: Math.sin(2 * Math.PI * dayOfWeek / 7),
            dayCos: Math.cos(2 * Math.PI * dayOfWeek / 7),
            hour,
            isWorkingHours: hour >= 9 && hour <= 18,
            isWeekend: dayOfWeek === 0 || dayOfWeek === 6
        };
    }
    
    _encodeSpatialPos(event) {
        const keywords = this._extractKeywords(event.content);
        
        return {
            type: event.type || 'general',
            keywords,
            semanticHash: this._hashKeywords(keywords),
            entities: this._extractEntities(event.content),
            intent: this._inferIntent(event.content, event.type)
        };
    }
    
    // ============================================================
    // 核心2: 按需检索 (智能重建)
    // ============================================================
    
    async retrieve(query) {
        const startTime = Date.now();
        
        const queryEncoding = this._encodeQuery(query);
        
        // 多路检索
        const useEmbedding = this.options.enableEmbedding || this.options.useLocalEmbedding;
        const [temporalResults, semanticResults, importanceResults, embeddingResults] = 
            await Promise.all([
                this._retrieveByTemporal(query, queryEncoding),
                this._retrieveBySemantic(query, queryEncoding),
                this._retrieveByImportance(query),
                useEmbedding ? this._retrieveByEmbedding(query, queryEncoding) : Promise.resolve([])
            ]);
        
        // 融合
        const fusedResults = this._fuseResults(
            temporalResults, 
            semanticResults, 
            importanceResults,
            embeddingResults,
            query
        );
        
        // 懒加载
        const loadedResults = await this._lazyLoad(fusedResults, query);
        
        // 上下文组装
        const context = this._assembleContext(loadedResults, query);
        
        this.stats.retrievalCount++;
        
        return {
            context,
            results: loadedResults,
            metadata: {
                queryTime: Date.now() - startTime,
                totalScanned: this.events.length,
                loadedCount: loadedResults.length,
                sources: {
                    temporal: temporalResults.length,
                    semantic: semanticResults.length,
                    importance: importanceResults.length,
                    embedding: embeddingResults.length
                }
            }
        };
    }
    
    _encodeQuery(query) {
        return {
            text: query.text,
            type: query.type,
            keywords: this._extractKeywords(query.text),
            temporalPos: this._encodeTemporalPos(Date.now()),
            temporalConstraint: query.timeRange,
            embedding: query.embedding || null
        };
    }
    
    _retrieveByTemporal(query, queryEncoding) {
        const results = [];
        const now = Date.now();
        
        for (const event of this.events) {
            let score = 0;
            
            if (queryEncoding.temporalConstraint) {
                const { start, end } = queryEncoding.temporalConstraint;
                if (event.timestamp >= start && event.timestamp <= end) {
                    score = 1.0;
                }
            } else {
                const timeDiff = now - event.timestamp;
                const daysAgo = timeDiff / (1000 * 60 * 60 * 24);
                score = Math.pow(this.options.timeDecayFactor, daysAgo);
                
                if (daysAgo <= 1) score *= 1.5;
            }
            
            if (score > 0.1) {
                results.push({ event, score, matchType: 'temporal' });
            }
        }
        
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, this.options.maxRetrieve * 2);
    }
    
    _retrieveBySemantic(query, queryEncoding) {
        const results = [];
        const queryKeywords = queryEncoding.keywords;
        
        for (const event of this.events) {
            const eventKeywords = event.spatialPos.keywords;
            
            const overlap = queryKeywords.filter(k => 
                eventKeywords.includes(k)
            ).length;
            
            const score = overlap / Math.max(
                queryKeywords.length, 
                eventKeywords.length
            );
            
            if (score > 0) {
                results.push({ event, score, matchType: 'semantic' });
            }
        }
        
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, this.options.maxRetrieve * 2);
    }
    
    _retrieveByImportance(query) {
        return this.events
            .filter(e => e.importance >= this.options.importanceThreshold)
            .sort((a, b) => b.importance - a.importance)
            .slice(0, this.options.maxRetrieve * 2)
            .map(event => ({ event, score: event.importance, matchType: 'importance' }));
    }
    
    async _retrieveByEmbedding(query, queryEncoding) {
        // 如果是本地 embedding，直接生成
        if (this.options.useLocalEmbedding && !queryEncoding.embedding) {
            queryEncoding.embedding = this._localEmbedding(query.text || query);
        } else if (!queryEncoding.embedding && this.options.enableEmbedding && this.options.embeddingAPI) {
            // 调用 API
            queryEncoding.embedding = await this._callEmbeddingAPI(query.text || query);
        }
        
        if (!queryEncoding.embedding) {
            return [];
        }
        
        const results = [];
        
        for (const [eventId, embedding] of this.embeddings) {
            const event = this.events.find(e => e.id === eventId);
            if (!event) continue;
            
            // 余弦相似度
            const score = this._cosineSimilarity(
                queryEncoding.embedding,
                embedding
            );
            
            if (score > 0.5) {
                results.push({ event, score, matchType: 'embedding' });
            }
        }
        
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, this.options.maxRetrieve * 2);
    }
    
    async _callEmbeddingAPI(text) {
        if (!this.options.embeddingAPI && !this.options.embeddingProvider) return null;
        
        const provider = this.options.embeddingProvider || 'openai';
        const apiKey = this.options.embeddingKey || process.env.EMBEDDING_API_KEY;
        
        try {
            let response;
            
            switch (provider) {
                case 'openai':
                    response = await fetch(this.options.embeddingAPI || 'https://api.openai.com/v1/embeddings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: JSON.stringify({
                            model: this.options.embeddingModel || 'text-embedding-3-small',
                            input: text
                        })
                    });
                    const openaiData = await response.json();
                    return openaiData.data?.[0]?.embedding;
                    
                case 'cohere':
                    response = await fetch(this.options.embeddingAPI || 'https://api.cohere.ai/v1/embed', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${apiKey}`
                        },
                        body: JSON.stringify({
                            model: this.options.embeddingModel || 'embed-english-v3.0',
                            texts: [text]
                        })
                    });
                    const cohereData = await response.json();
                    return cohereData.embeddings?.[0];
                    
                case 'local':
                    // 本地 embedding 服务
                    response = await fetch(this.options.embeddingAPI || 'http://localhost:11434/api/embeddings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            model: this.options.embeddingModel || 'nomic-embed-text',
                            prompt: text
                        })
                    });
                    const localData = await response.json();
                    return localData.embedding;
                    
                default:
                    return null;
            }
        } catch (e) {
            console.error('[SPENMemory] Embedding API error:', e.message);
            return null;
        }
    }
    
    /**
     * 本地简单 embedding (无需 API)
     * 使用词向量累加 + TF-IDF 权重
     */
    _localEmbedding(text) {
        // 简单 hash-based embedding
        const words = this._extractKeywords(text);
        const embedding = new Array(this.options.embeddingDim || 1536).fill(0);
        
        for (const word of words) {
            let hash = 0;
            for (let i = 0; i < word.length; i++) {
                hash = ((hash << 5) - hash) + word.charCodeAt(i);
                hash |= 0;
            }
            
            // 基于 hash 填充向量
            for (let i = 0; i < embedding.length; i++) {
                embedding[i] += Math.sin((hash + i) % 1000) * 0.1;
            }
        }
        
        // 归一化
        const norm = Math.sqrt(embedding.reduce((sum, v) => sum + v * v, 0));
        if (norm > 0) {
            for (let i = 0; i < embedding.length; i++) {
                embedding[i] /= norm;
            }
        }
        
        return embedding;
    }
    
    /**
     * 生成 embedding
     */
    _generateEmbedding(memoryUnit) {
        if (this.options.useLocalEmbedding) {
            // 本地 embedding
            const embedding = this._localEmbedding(memoryUnit.content);
            this.embeddings.set(memoryUnit.id, embedding);
        } else if (this.options.enableEmbedding && this.options.embeddingAPI) {
            // 异步调用 API
            this._callEmbeddingAPI(memoryUnit.content).then(embedding => {
                if (embedding) {
                    this.embeddings.set(memoryUnit.id, embedding);
                }
            });
        }
    }
    
    _cosineSimilarity(a, b) {
        if (!a || !b || a.length !== b.length) return 0;
        
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
    
    _fuseResults(temporal, semantic, importance, embedding, query) {
        const scoreMap = new Map();
        
        const addScore = (eventId, item, weight) => {
            const existing = scoreMap.get(eventId) || { 
                event: null, score: 0, matches: [] 
            };
            existing.event = item.event;
            existing.score += item.score * weight;
            existing.matches.push(item.matchType);
            scoreMap.set(eventId, existing);
        };
        
        temporal.forEach(r => addScore(r.event.id, r, this.options.temporalWeight));
        semantic.forEach(r => addScore(r.event.id, r, this.options.semanticWeight));
        importance.forEach(r => addScore(r.event.id, r, this.options.importanceWeight));
        
        if (embedding.length > 0) {
            const embeddingWeight = 0.3; // embedding 权重
            embedding.forEach(r => addScore(r.event.id, r, embeddingWeight));
        }
        
        return Array.from(scoreMap.values())
            .sort((a, b) => b.score - a.score)
            .slice(0, this.options.maxRetrieve);
    }
    
    async _lazyLoad(fusedResults, query) {
        const loaded = [];
        
        for (const item of fusedResults) {
            const event = item.event;
            event.accessCount++;
            event.lastAccess = Date.now();
            
            loaded.push({
                ...event,
                loadedAt: Date.now()
            });
        }
        
        return loaded;
    }
    
    _assembleContext(results, query) {
        if (results.length === 0) {
            return { 
                text: '', 
                memoryCount: 0, 
                summary: '无相关记忆',
                suggestions: this._generateSuggestions(query)
            };
        }
        
        const sorted = [...results].sort((a, b) => a.timestamp - b.timestamp);
        
        const contextParts = sorted.map(event => {
            const time = this._formatTime(event.timestamp);
            return `[${time}] [${event.type}] ${event.content}`;
        });
        
        return {
            text: contextParts.join('\n'),
            memoryCount: results.length,
            timeRange: {
                earliest: sorted[0].timestamp,
                latest: sorted[sorted.length - 1].timestamp
            },
            types: [...new Set(results.map(r => r.type))],
            summary: this._generateSummary(results, query),
            suggestions: this._generateSuggestions(query, results)
        };
    }
    
    // ============================================================
    // 核心3: 压缩 + 归档
    // ============================================================
    
    _compress() {
        const targetSize = Math.floor(
            this.options.maxMemorySize * this.options.compressionRatio
        );
        
        if (this.events.length <= targetSize) return;
        
        const scored = this.events.map(event => {
            const recentBonus = event.lastAccess > Date.now() - 24 * 60 * 60 * 1000 ? 0.2 : 0;
            const accessBonus = Math.min(event.accessCount / 10, 0.3);
            return {
                event,
                score: event.importance + recentBonus + accessBonus
            };
        });
        
        scored.sort((a, b) => b.score - a.score);
        
        const kept = scored.slice(0, targetSize);
        const archived = scored.slice(targetSize);
        
        // 归档保留元信息
        if (this.options.enableArchive) {
            archived.forEach(item => {
                this.archive.push({
                    id: item.event.id,
                    type: item.event.type,
                    content: item.event.content.substring(0, 100), // 只保留前100字符
                    timestamp: item.event.timestamp,
                    importance: item.event.importance,
                    archivedAt: Date.now()
                });
            });
            this.stats.archiveSize = this.archive.length;
        }
        
        this.events = kept.map(s => s.event);
        this._rebuildIndices();
        
        console.log(`[SPENMemory] 压缩: ${archived.length} 事件已归档`);
    }
    
    /**
     * 归档检索 (从压缩归档中检索)
     */
    retrieveArchive(query) {
        if (!this.options.enableArchive || this.archive.length === 0) {
            return { results: [], summary: '无归档' };
        }
        
        const queryKeywords = this._extractKeywords(query.text || query);
        const results = [];
        
        for (const item of this.archive) {
            const archiveKeywords = this._extractKeywords(item.content);
            
            const overlap = queryKeywords.filter(k => 
                archiveKeywords.includes(k)
            ).length;
            
            const score = overlap / Math.max(queryKeywords.length, archiveKeywords.length);
            
            if (score > 0) {
                results.push({ ...item, score, fromArchive: true });
            }
        }
        
        return {
            results: results.sort((a, b) => b.score - a.score).slice(0, 10),
            summary: `从归档中找到 ${results.length} 条相关记忆`
        };
    }
    
    // ============================================================
    // 增强功能: 智能建议
    // ============================================================
    
    _generateSuggestions(query, results = []) {
        const suggestions = [];
        
        // 基于检索结果类型
        const types = {};
        results.forEach(r => {
            types[r.type] = (types[r.type] || 0) + 1;
        });
        
        // 如果没有工具调用记忆，建议添加
        if (!types['工具'] && results.length > 0) {
            suggestions.push('建议记录工具调用过程以便追溯');
        }
        
        // 如果记忆太少
        if (this.events.length < 10) {
            suggestions.push('记忆库较空，可以添加更多关键信息');
        }
        
        // 基于查询类型
        const queryLower = (query.text || query).toLowerCase();
        if (queryLower.includes('什么') || queryLower.includes('?')) {
            suggestions.push('可能需要查询外部知识库补充信息');
        }
        
        return suggestions;
    }
    
    // ============================================================
    // 辅助方法
    // ============================================================
    
    _generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    _calcImportance(event) {
        if (event.importance !== undefined) return event.importance;
        
        let importance = 0.5;
        const typeWeights = { '对话': 0.6, '工具': 0.7, '用户': 0.9, '系统': 0.3, '错误': 0.8 };
        
        if (typeWeights[event.type]) {
            importance = typeWeights[event.type];
        }
        
        if (event.content && event.content.length > 200) {
            importance += 0.1;
        }
        
        return Math.min(importance, 1.0);
    }
    
    _extractKeywords(text) {
        if (!text) return [];
        
        // 清理文本
        const cleaned = text.toLowerCase()
            .replace(/[^\w\s\u4e00-\u9fa5]/g, ' ');
        
        // 提取英文单词
        const englishWords = cleaned
            .replace(/[\u4e00-\u9fa5]/g, ' ')
            .split(/\s+/)
            .filter(w => w.length > 1)
            .slice(0, 5);
        
        // 提取中文字符 (每个字 + 每2-4个连续字符)
        const chineseChars = cleaned.match(/[\u4e00-\u9fa5]/g) || [];
        const chineseWords = [];
        
        // 提取2-4个连续汉字
        for (let i = 0; i < chineseChars.length - 1; i++) {
            if (i + 1 < chineseChars.length) chineseWords.push(chineseChars[i] + chineseChars[i + 1]);
            if (i + 2 < chineseChars.length) chineseWords.push(chineseChars[i] + chineseChars[i + 1] + chineseChars[i + 2]);
        }
        
        // 合并去重
        const allKeywords = [...englishWords, ...chineseWords];
        return [...new Set(allKeywords)].slice(0, 10);
    }
    
    _hashKeywords(keywords) {
        const str = keywords.sort().join('|');
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0;
        }
        return hash;
    }
    
    _extractEntities(text) {
        return {
            urls: (text.match(/https?:\/\/[^\s]+/g) || []),
            emails: (text.match(/[\w.-]+@[\w.-]+\.\w+/g) || []),
            numbers: (text.match(/\d+/g) || [])
        };
    }
    
    _inferIntent(content, type) {
        const intentPatterns = {
            '查询': ['查', '找', '搜索', '什么', '?'],
            '执行': ['做', '执行', '运行', '完成', '帮'],
            '确认': ['确认', '是不是', '对不对', '同意'],
            '修改': ['改', '更新', '修改', '编辑'],
            '删除': ['删', '移除', '去掉', '不要']
        };
        
        for (const [intent, patterns] of Object.entries(intentPatterns)) {
            if (patterns.some(p => content.includes(p))) {
                return intent;
            }
        }
        return 'unknown';
    }
    
    _buildIndices(memoryUnit) {
        const timeKey = new Date(memoryUnit.timestamp).toDateString();
        if (!this.indices.temporal.has(timeKey)) {
            this.indices.temporal.set(timeKey, []);
        }
        this.indices.temporal.get(timeKey).push(memoryUnit.id);
        
        for (const keyword of memoryUnit.spatialPos.keywords) {
            if (!this.indices.semantic.has(keyword)) {
                this.indices.semantic.set(keyword, []);
            }
            this.indices.semantic.get(keyword).push(memoryUnit.id);
        }
        
        this.indices.importance.push({
            id: memoryUnit.id,
            importance: memoryUnit.importance,
            timestamp: memoryUnit.timestamp
        });
    }
    
    _rebuildIndices() {
        this.indices.temporal.clear();
        this.indices.semantic.clear();
        this.indices.importance = [];
        
        for (const event of this.events) {
            this._buildIndices(event);
        }
    }
    
    _formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN', {
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    _generateSummary(results, query) {
        if (results.length === 0) return '无记忆';
        
        const types = {};
        results.forEach(r => {
            types[r.type] = (types[r.type] || 0) + 1;
        });
        
        const topType = Object.entries(types).sort((a, b) => b[1] - a[1])[0];
        return `找到 ${results.length} 条相关记忆，最新为 ${topType[0]} 类型`;
    }
    
    // ============================================================
    // 持久化
    // ============================================================
    
    saveToStorage() {
        try {
            const data = {
                events: this.events,
                archive: this.archive,
                embeddings: Array.from(this.embeddings),
                stats: this.stats,
                options: this.options
            };
            localStorage.setItem(this.options.storageKey, JSON.stringify(data));
        } catch (e) {
            console.error('[SPENMemory] 保存失败:', e);
        }
    }
    
    loadFromStorage() {
        try {
            const data = localStorage.getItem(this.options.storageKey);
            if (data) {
                const parsed = JSON.parse(data);
                this.events = parsed.events || [];
                this.archive = parsed.archive || [];
                this.embeddings = new Map(parsed.embeddings || []);
                this.stats = parsed.stats || this.stats;
                this._rebuildIndices();
                console.log(`[SPENMemory] 加载了 ${this.events.length} 条记忆`);
            }
        } catch (e) {
            console.error('[SPENMemory] 加载失败:', e);
        }
    }
    
    clear() {
        this.events = [];
        this.archive = [];
        this.embeddings.clear();
        this.indices.temporal.clear();
        this.indices.semantic.clear();
        this.indices.importance = [];
        this.stats = { totalEvents: 0, retrievalCount: 0, cacheHits: 0, archiveSize: 0 };
        
        if (this.options.persist) {
            localStorage.removeItem(this.options.storageKey);
        }
    }
    
    getStats() {
        return {
            ...this.stats,
            currentMemorySize: this.events.length,
            archiveSize: this.archive.length,
            maxMemorySize: this.options.maxMemorySize,
            compressionRatio: this.events.length / this.options.maxMemorySize
        };
    }
    
    export() {
        return {
            events: this.events,
            archive: this.archive,
            stats: this.stats
        };
    }
    
    import(data) {
        this.events = data.events || [];
        this.archive = data.archive || [];
        this.stats = data.stats || this.stats;
        this._rebuildIndices();
    }
}

export default SPENMemory;
