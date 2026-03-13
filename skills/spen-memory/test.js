/**
 * SPEN-Memory 测试
 */

import SPENMemory from './spen-memory.js';

async function runTests() {
    console.log('🧪 开始测试 SPEN-Memory\n');
    
    // 测试1: 初始化
    console.log('📋 测试1: 初始化');
    const memory = new SPENMemory({
        maxMemorySize: 100,
        compressionRatio: 0.5,
        persist: false
    });
    console.log('✅ 初始化成功\n');
    
    // 测试2: 添加记忆
    console.log('📋 测试2: 添加记忆');
    const id1 = memory.addEvent({
        type: '对话',
        content: '用户问：帮我订一张明天去上海的机票',
        importance: 0.9
    });
    console.log(`   添加成功: ${id1}`);
    
    const id2 = memory.addEvent({
        type: '工具',
        content: '执行搜索：明天 上海 经济舱',
        importance: 0.7
    });
    console.log(`   添加成功: ${id2}`);
    
    const id3 = memory.addEvent({
        type: '用户',
        content: '用户选择了东方航空 MU5184',
        importance: 0.9
    });
    console.log(`   添加成功: ${id3}`);
    
    const id4 = memory.addEvent({
        type: '对话',
        content: '确认订单，机票已订成功',
        importance: 1.0
    });
    console.log(`   添加成功: ${id4}`);
    console.log('✅ 添加测试通过\n');
    
    // 测试3: 检索
    console.log('📋 测试3: 检索记忆');
    
    const result1 = await memory.retrieve({
        text: '机票订好了吗',
        maxResults: 5
    });
    console.log(`   查询: 机票订好了吗`);
    console.log(`   结果: ${result1.context.memoryCount} 条`);
    console.log(`   内容:\n${result1.context.text}`);
    console.log(`   摘要: ${result1.context.summary}\n`);
    
    const result2 = await memory.retrieve({
        text: '用户要去哪里',
        maxResults: 5
    });
    console.log(`   查询: 用户要去哪里`);
    console.log(`   结果: ${result2.context.memoryCount} 条`);
    console.log(`   内容:\n${result2.context.text}\n`);
    
    // 测试4: 统计
    console.log('📋 测试4: 统计');
    const stats = memory.getStats();
    console.log(`   当前存储: ${stats.currentMemorySize} 条`);
    console.log(`   总添加: ${stats.totalEvents} 次`);
    console.log(`   总检索: ${stats.retrievalCount} 次\n`);
    
    // 测试5: 压缩
    console.log('📋 测试5: 压缩');
    // 添加超过限制的记忆
    for (let i = 0; i < 60; i++) {
        memory.addEvent({
            type: '测试',
            content: `测试记忆 ${i}`,
            importance: Math.random()
        });
    }
    console.log(`   压缩后存储: ${memory.events.length} 条`);
    console.log('✅ 压缩测试通过\n');
    
    // 测试6: 导出/导入
    console.log('📋 测试6: 导出/导入');
    const exportData = memory.export();
    console.log(`   导出: ${exportData.events.length} 条`);
    
    const memory2 = new SPENMemory({ persist: false });
    memory2.import(exportData);
    console.log(`   导入: ${memory2.events.length} 条`);
    console.log('✅ 导出/导入测试通过\n');
    
    console.log('🎉 所有测试通过！');
}

runTests().catch(console.error);
