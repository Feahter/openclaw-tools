/**
 * 爬虫核心 - 处理多Tab和分页
 */

const { execSync } = require('child_process');

class SmartCrawler {
  constructor(analyzer, extractor) {
    this.analyzer = analyzer;
    this.extractor = extractor;
    this.agentBrowser = 'agent-browser';
  }

  /**
   * 爬取单个URL
   */
  async crawl(url, intent, session = 'main') {
    const results = {
      url,
      intent,
      pages: [],
      totalItems: 0,
      timestamp: new Date().toISOString()
    };

    try {
      // 1. 打开页面
      console.log(`Opening ${url}...`);
      execSync(
        `${this.agentBrowser} --session ${session} open ${url}`,
        { encoding: 'utf-8', timeout: 30000 }
      );

      // 2. 等待动态内容
      await this.analyzer.waitForDynamic(session);

      // 3. 获取页面结构
      const pageData = await this.analyzer.capturePage(session);
      if (!pageData) {
        throw new Error('Failed to capture page');
      }

      // 4. AI分析页面结构
      const plan = await this.analyzer.analyzeStructure(pageData, intent);
      console.log('Analysis plan:', JSON.stringify(plan, null, 2));

      // 5. 处理分页/滚动
      if (plan.pagination?.type === 'scroll' || plan.pagination?.type === 'infinite') {
        await this.extractor.scrollToLoad(session, 10);
      }

      // 6. 提取数据
      const pageDataResult = await this.extractor.extract(session, plan);
      results.pages.push({
        page: 1,
        items: pageDataResult
      });
      results.totalItems += pageDataResult.length;

      // 7. 处理分页
      if (plan.pagination?.type === 'button') {
        const morePages = await this.crawlPagination(session, plan, intent);
        results.pages.push(...morePages);
      }

      // 8. 处理多Tab
      const tabResults = await this.crawlTabs(session, intent);
      results.pages.push(...tabResults);

    } catch (error) {
      results.error = error.message;
    }

    return results;
  }

  /**
   * 分页爬取
   */
  async crawlPagination(session, plan, intent, maxPages = 10) {
    const pages = [];
    let pageNum = 2;

    while (pageNum <= maxPages) {
      try {
        // 查找下一页按钮
        const selector = plan.pagination.selector;
        
        // 点击下一页
        execSync(
          `${this.agentBrowser} --session ${session} click "${selector}"`,
          { encoding: 'utf-8', timeout: 10000 }
        );

        await this.analyzer.waitForDynamic(session);

        // 提取数据
        const data = await this.extractor.extract(session, plan);
        pages.push({ page: pageNum, items: data });
        
        pageNum++;
      } catch (error) {
        console.log(`No more pages at ${pageNum}`);
        break;
      }
    }

    return pages;
  }

  /**
   * 多Tab爬取
   */
  async crawlTabs(session, intent) {
    const pages = [];

    try {
      // 获取所有Tab
      const tabs = execSync(
        `${this.agentBrowser} --session ${session} tab --json`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      const tabList = JSON.parse(tabs).result;
      
      // 遍历每个Tab（跳过第一个，因为已经在主页面）
      for (let i = 1; i < tabList.length; i++) {
        execSync(
          `${this.agentBrowser} --session ${session} tab ${i}`,
          { encoding: 'utf-8', timeout: 5000 }
        );

        await this.analyzer.waitForDynamic(session);

        const pageData = await this.analyzer.capturePage(session);
        const plan = await this.analyzer.analyzeStructure(pageData, intent);
        const data = await this.extractor.extract(session, plan);

        pages.push({ tab: i, items: data });
      }
    } catch (error) {
      console.error('Tab crawl error:', error.message);
    }

    return pages;
  }
}

module.exports = { SmartCrawler };
