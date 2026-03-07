/**
 * 数据提取器
 * 根据AI分析结果提取结构化数据
 */

const { execSync } = require('child_process');

class DataExtractor {
  constructor() {
    this.agentBrowser = 'agent-browser';
  }

  /**
   * 提取单页数据
   */
  async extract(session, plan) {
    const results = [];

    try {
      // 获取页面HTML用于详细提取
      const html = execSync(
        `${this.agentBrowser} --session ${session} get html body --json`,
        { encoding: 'utf-8', timeout: 10000 }
      );

      // 使用选择器提取数据
      const items = await this.queryAll(session, plan.itemSelector);
      
      for (const item of items) {
        const record = {};
        
        for (const field of plan.fields) {
          record[field.name] = await this.extractField(session, item.ref, field);
        }
        
        results.push(record);
      }
    } catch (error) {
      console.error('Extract error:', error.message);
    }

    return results;
  }

  /**
   * 查询所有匹配元素
   */
  async queryAll(session, selector) {
    try {
      // 使用get count获取数量
      const countResult = execSync(
        `${this.agentBrowser} --session ${session} get count "${selector}" --json`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      const count = JSON.parse(countResult).result;
      
      // 收集元素引用（通过snapshot）
      const snapshot = execSync(
        `${this.agentBrowser} --session ${session} snapshot -i --json`,
        { encoding: 'utf-8', timeout: 10000 }
      );
      
      const data = JSON.parse(snapshot);
      // 过滤出数据相关的元素
      const elements = (data.elements || []).filter(el => 
        el.role && ['link', 'heading', 'textbox', 'cell'].includes(el.role)
      );
      
      return elements.slice(0, count).map((el, i) => ({
        ref: `@e${i + 1}`,
        ...el
      }));
    } catch (error) {
      console.error('Query error:', error.message);
      return [];
    }
  }

  /**
   * 提取单个字段
   */
  async extractField(session, ref, field) {
    try {
      if (field.type === 'text') {
        const result = execSync(
          `${this.agentBrowser} --session ${session} get text ${ref} --json`,
          { encoding: 'utf-8', timeout: 5000 }
        );
        return JSON.parse(result).result?.trim() || '';
      }
      
      if (field.type === 'attr:href') {
        const result = execSync(
          `${this.agentBrowser} --session ${session} get attr ${ref} href --json`,
          { encoding: 'utf-8', timeout: 5000 }
        );
        return JSON.parse(result).result || '';
      }
      
      return '';
    } catch (error) {
      return '';
    }
  }

  /**
   * 滚动加载更多内容
   */
  async scrollToLoad(session, maxScrolls = 5) {
    for (let i = 0; i < maxScrolls; i++) {
      try {
        execSync(
          `${this.agentBrowser} --session ${session} scroll down 500`,
          { encoding: 'utf-8', timeout: 5000 }
        );
        
        // 等待新内容加载
        execSync(
          `${this.agentBrowser} --session ${session} wait 1000`,
          { encoding: 'utf-8', timeout: 2000 }
        );
      } catch (error) {
        break;
      }
    }
  }
}

module.exports = { DataExtractor };
