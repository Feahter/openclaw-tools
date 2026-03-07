/**
 * 输出格式化器
 */

class OutputFormatter {
  /**
   * 格式化为Markdown表格
   */
  toMarkdown(data) {
    if (!data.pages || data.pages.length === 0) {
      return 'No data extracted.';
    }

    let md = `# 爬取结果\n\n`;
    md += `- **目标**: ${data.url}\n`;
    md += `- **意图**: ${data.intent}\n`;
    md += `- **总条目**: ${data.totalItems}\n`;
    md += `- **时间**: ${data.timestamp}\n\n`;

    for (const page of data.pages) {
      md += `## ${page.page ? `Page ${page.page}` : `Tab ${page.tab}`}\n\n`;
      
      if (page.items && page.items.length > 0) {
        // 表头
        const fields = Object.keys(page.items[0]);
        md += `| ${fields.join(' | ')} |\n`;
        md += `| ${fields.map(() => '---').join(' | ')} |\n`;
        
        // 数据行
        for (const item of page.items) {
          const values = fields.map(f => {
            const val = item[f] || '';
            return val.toString().substring(0, 100); // 截断长文本
          });
          md += `| ${values.join(' | ')} |\n`;
        }
      }
      
      md += '\n';
    }

    return md;
  }

  /**
   * 格式化为JSON
   */
  toJSON(data) {
    return JSON.stringify({
      metadata: {
        url: data.url,
        intent: data.intent,
        totalItems: data.totalItems,
        timestamp: data.timestamp
      },
      pages: data.pages
    }, null, 2);
  }

  /**
   * 格式化为简洁文本
   */
  toText(data) {
    let text = `爬取结果: ${data.url}\n`;
    text += `总条目: ${data.totalItems}\n\n`;

    for (const page of data.pages) {
      const pageLabel = page.page ? `Page ${page.page}` : `Tab ${page.tab}`;
      text += `--- ${pageLabel} ---\n`;
      
      for (const item of page.items) {
        const firstField = Object.values(item)[0];
        text += `• ${firstField}\n`;
      }
      text += '\n';
    }

    return text;
  }
}

module.exports = { OutputFormatter };
