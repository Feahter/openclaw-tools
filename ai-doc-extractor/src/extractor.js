/**
 * AI 文档提取器 - 核心逻辑
 * 功能：从 OCR 文本中提取关键字段
 */

const fs = require('fs');
const path = require('path');

/**
 * 从文本中提取发票信息
 * @param {string} text - OCR 识别的文本
 * @returns {Object} 提取的结构化数据
 */
function extractInvoiceInfo(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(l => l);
  
  const result = {
    invoiceNumber: null,    // 发票号
    date: null,              // 开票日期
    amount: null,            // 金额
    taxAmount: null,         // 税额
    totalAmount: null,       // 价税合计
    sellerName: null,        // 销售方名称
    sellerTaxId: null,       // 销售方税号
    buyerName: null,         // 购买方名称
    buyerTaxId: null,        // 购买方税号
    rawText: text
  };

  // 发票号码pattern (常见格式)
  const invoiceNumPattern = /(?:发票号|发票号码|No|no|第)\s*[A-Z0-9]{10,20}/i;
  // 日期 pattern
  const datePattern = /(\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}[日]?)/;
  // 金额 pattern
  const amountPattern = /[¥$￥]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/;
  // 税号 pattern (15位或18位)
  const taxIdPattern = /[0-9A-Z]{15,20}/;

  for (const line of lines) {
    // 提取发票号
    if (!result.invoiceNumber) {
      const match = line.match(invoiceNumPattern);
      if (match) {
        result.invoiceNumber = match[0].replace(/发票号|发票号码|No|no|第/gi, '').trim();
      }
    }

    // 提取日期
    if (!result.date) {
      const match = line.match(datePattern);
      if (match) {
        result.date = match[1].replace(/[年月日]/g, '-').replace(/-$/, '');
      }
    }

    // 提取金额 (找最大的数字通常是总额)
    const amountMatch = line.match(amountPattern);
    if (amountMatch) {
      const num = parseFloat(amountMatch[1].replace(/,/g, ''));
      if (!result.totalAmount || num > result.totalAmount) {
        result.totalAmount = num;
      }
    }

    // 提取税号
    const taxIdMatch = line.match(taxIdPattern);
    if (taxIdMatch && taxIdMatch[0].length >= 15) {
      if (!result.sellerTaxId) {
        result.sellerTaxId = taxIdMatch[0];
      } else if (!result.buyerTaxId && taxIdMatch[0] !== result.sellerTaxId) {
        result.buyerTaxId = taxIdMatch[0];
      }
    }
  }

  // 尝试从非结构化文本中推断买卖方
  // 通常销售方在前，购买方在后
  if (lines.length > 2) {
    result.sellerName = lines[0] || null;
    result.buyerName = lines[1] || null;
  }

  return result;
}

/**
 * 验证提取结果的完整性
 * @param {Object} info - 提取的信息
 * @returns {Object} 验证结果
 */
function validateInvoiceInfo(info) {
  const issues = [];
  
  if (!info.invoiceNumber) issues.push('缺少发票号');
  if (!info.date) issues.push('缺少日期');
  if (!info.totalAmount) issues.push('缺少金额');
  
  return {
    isValid: issues.length === 0,
    issues
  };
}

// 测试
function test() {
  const sampleText = `
    增值税专用发票
    发票号码：1234567890
    开票日期：2026-01-15
    销售方名称：北京科技有限公司
    销售方税号：91110000123456789X
    购买方名称：上海贸易有限公司
    购买方税号：91310000987654321Y
    金额：1,000.00
    税额：130.00
    价税合计：1,130.00
  `;

  const result = extractInvoiceInfo(sampleText);
  console.log('提取结果:', JSON.stringify(result, null, 2));
  
  const validation = validateInvoiceInfo(result);
  console.log('验证结果:', validation);
}

module.exports = { extractInvoiceInfo, validateInvoiceInfo };

if (require.main === module) {
  test();
}
