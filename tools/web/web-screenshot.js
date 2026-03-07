#!/usr/bin/env node
/**
 * Webpage Screenshot Tool - 网页截图工具
 */

const { chromium } = require('playwright');

async function screenshot(url, options = {}) {
  const output = options.output || `/tmp/screenshot_${Date.now()}.png`;
  const fullPage = options.full || false;
  
  console.log(`📸 开始截图...`);
  console.log(`   URL: ${url}`);
  console.log(`   输出: ${output}`);
  
  const browser = await chromium.launch({ headless: true });
  
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    
    await page.screenshot({ 
      path: output, 
      fullPage,
      type: 'png'
    });
    
    const fs = require('fs');
    const stats = fs.statSync(output);
    
    console.log(`✅ 截图完成!`);
    console.log(`   文件: ${output}`);
    console.log(`   大小: ${(stats.size / 1024).toFixed(2)} KB`);
    console.log(`MEDIA: ${output}`);
    
  } catch (e) {
    console.error(`❌ 截图失败: ${e.message}`);
    throw e;
  } finally {
    await browser.close();
  }
}

// 命令行参数
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
Webpage Screenshot Tool

用法:
  node tools/web-screenshot.js <url> [options]

选项:
  --full    截取整个页面

示例:
  node tools/web-screenshot.js http://localhost:8080
  node tools/web-screenshot.js http://localhost:8080 --full
`);
    process.exit(0);
  }
  
  const url = args[0];
  const fullPage = args.includes('--full');
  const output = args.find(a => !a.startsWith('-') && !a.startsWith('http')) || `/tmp/screenshot_${Date.now()}.png`;
  
  screenshot(url, { output, fullPage })
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
}

module.exports = { screenshot };
