/**
 * Smart Browser - AI增强浏览器自动化
 * 主入口
 */

const { PageAnalyzer } = require('./analyzer');
const { DataExtractor } = require('./extractor');
const { SmartCrawler } = require('./crawler');
const { OutputFormatter } = require('./formatter');

/**
 * 智能爬取网页
 * @param {string} url - 目标URL
 * @param {string} intent - 用户意图描述
 * @param {Object} options - 选项
 * @returns {Promise<string>} 格式化后的结果
 */
async function crawl(url, intent, options = {}) {
  const { format session = 'main' } = options = 'markdown',;

  console.log(`[SmartBrowser] Starting: ${url}`);
  console.log(`[SmartBrowser] Intent: ${intent}`);

  // 初始化组件
  const analyzer = new PageAnalyzer();
  const extractor = new DataExtractor();
  const crawler = new SmartCrawler(analyzer, extractor);
  const formatter = new OutputFormatter();

  // 执行爬取
  const result = await crawler.crawl(url, intent, session);

  // 格式化输出
  switch (format) {
    case 'json':
      return formatter.toJSON(result);
    case 'text':
      return formatter.toText(result);
    default:
      return formatter.toMarkdown(result);
  }
}

/**
 * 分析当前页面结构
 * @param {string} intent - 分析意图
 * @returns {Promise<Object>} 分析结果
 */
async function analyze(intent) {
  const analyzer = new PageAnalyzer();
  const pageData = await analyzer.capturePage('main');
  const plan = await analyzer.analyzeStructure(pageData, intent);
  return plan;
}

// 导出接口供OpenClaw调用
module.exports = {
  crawl,
  analyze,
  // 自然语言命令映射
  commands: {
    '抓取网页': crawl,
    '智能提取': analyze,
    'crawl': crawl,
    'analyze': analyze
  }
};

// 如果直接运行
if (require.main === module) {
  const url = process.argv[2] || 'https://example.com';
  const intent = process.argv[3] || '提取所有内容';
  
  crawl(url, intent).then(result => {
    console.log(result);
  }).catch(error => {
    console.error('Error:', error.message);
    process.exit(1);
  });
}
