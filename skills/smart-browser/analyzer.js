/**
 * 页面结构分析器 - AI驱动
 * 将DOM发送给LLM，识别页面结构
 */

const { execSync } = require('child_process');
const path = require('path');

class PageAnalyzer {
  constructor() {
    this.agentBrowser = 'agent-browser';
  }

  /**
   * 获取页面DOM和截图
   */
  async capturePage(session = 'main') {
    try {
      // 获取交互元素快照
      const snapshot = execSync(
        `${this.agentBrowser} --session ${session} snapshot -i --json`,
        { encoding: 'utf-8', timeout: 10000 }
      );
      
      // 获取页面标题
      const title = execSync(
        `${this.agentBrowser} --session ${session} get title --json`,
        { encoding: 'utf-8', timeout: 5000 }
      );

      return {
        snapshot: JSON.parse(snapshot),
        title: JSON.parse(title).result
      };
    } catch (error) {
      console.error('Capture error:', error.message);
      return null;
    }
  }

  /**
   * AI分析页面结构
   * @param {Object} pageData - 页面快照数据
   * @param {string} intent - 用户意图
   */
  async analyzeStructure(pageData, intent) {
    const prompt = `
分析这个网页结构。

用户意图: ${intent}

页面标题: ${pageData.title}

页面元素:
${JSON.stringify(pageData.snapshot.elements?.slice(0, 50) || [], null, 2)}

请返回JSON格式的分析结果:
{
  "dataContainer": "数据列表的选择器",
  "itemSelector": "每个数据项的选择器",
  "fields": [
    {"name": "字段名", "selector": "选择器", "type": "text|datetime|attr"}
  ],
  "pagination": {
    "type": "none|button|scroll|infinite",
    "selector": "分页按钮选择器",
    "nextText": "下一页按钮文字"
  },
  "tabs": ["Tab切换按钮选择器"],
  "confidence": 0.0-1.0
}
`;

    // TODO: 调用LLM API分析
    // 这里先返回模拟结果，实际使用时接入LLM
    return this.mockAnalyzeResult(intent);
  }

  /**
   * 模拟分析结果（临时）
   */
  mockAnalyzeResult(intent) {
    return {
      dataContainer: '.content, .list, main',
      itemSelector: '.item, .card, tr',
      fields: [
        { name: 'title', selector: 'h2, h3, .title', type: 'text' },
        { name: 'link', selector: 'a', type: 'attr:href' }
      ],
      pagination: { type: 'button', selector: '.next, .pagination a', nextText: '下一页' },
      tabs: [],
      confidence: 0.7
    };
  }

  /**
   * 等待动态内容加载
   */
  async waitForDynamic(session, strategy = 'networkidle') {
    try {
      execSync(
        `${this.agentBrowser} --session ${session} wait --load ${strategy}`,
        { encoding: 'utf-8', timeout: 15000 }
      );
      return true;
    } catch (error) {
      console.log('Wait timeout, continuing...');
      return false;
    }
  }
}

module.exports = { PageAnalyzer };
