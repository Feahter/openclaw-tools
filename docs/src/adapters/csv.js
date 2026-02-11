/**
 * CSV Adapter - CSV 导入/导出适配器
 */

export class CSVAdapter {
  constructor(datalake = null) {
    this.datalake = datalake;
    this.type = 'csv';
    this.delimiter = ',';
  }

  /**
   * 读取 CSV 文件
   */
  async read(file, options = {}) {
    const text = await this.readFile(file);
    return this.parse(text, options);
  }

  /**
   * 解析 CSV 文本
   */
  parse(text, options = {}) {
    const lines = text.split(/\r?\n/);
    if (lines.length === 0) return [];

    // 检测分隔符
    if (options.detectDelimiter !== false) {
      const firstLine = lines[0];
      const delimiters = [',', ';', '\t', '|'];
      let maxCount = 0;
      let detectedDelim = ',';

      for (const delim of delimiters) {
        const count = firstLine.split(delim).length;
        if (count > maxCount) {
          maxCount = count;
          detectedDelim = delim;
        }
      }
      this.delimiter = detectedDelim;
    }

    // 解析头部
    const header = this.parseLine(lines[0]);
    const hasHeader = options.hasHeader !== false;

    // 解析数据行
    const data = [];
    const startRow = hasHeader ? 1 : 0;

    for (let i = startRow; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      
      const values = this.parseLine(lines[i]);
      const row = {};
      
      for (let j = 0; j < header.length; j++) {
        const key = hasHeader ? header[j] : `column_${j}`;
        row[key] = this.convertValue(values[j], options);
      }

      data.push(row);
    }

    return data;
  }

  /**
   * 解析单行（处理引号）
   */
  parseLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === this.delimiter && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    result.push(current.trim());
    return result;
  }

  /**
   * 类型转换
   */
  convertValue(value, options = {}) {
    if (value === '' || value === null || value === undefined) {
      return options.nullValue !== undefined ? options.nullValue : null;
    }

    // 尝试数字
    if (options.autoType !== false) {
      if (/^-?\d+$/.test(value)) {
        return parseInt(value, 10);
      }
      if (/^-?\d+\.\d+$/.test(value)) {
        return parseFloat(value);
      }
      if (value.toLowerCase() === 'true') return true;
      if (value.toLowerCase() === 'false') return false;
    }

    return value;
  }

  /**
   * 读取文件
   */
  readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;
      
      if (file instanceof Blob) {
        reader.readAsText(file, options?.encoding || 'UTF-8');
      } else if (typeof file === 'string') {
        resolve(file);
      } else {
        reader.readAsText(file);
      }
    });
  }

  /**
   * 写入 CSV
   */
  async write(data, options = {}) {
    if (!Array.isArray(data) || data.length === 0) {
      return '';
    }

    const headers = Object.keys(data[0]);
    const delimiter = options.delimiter || this.delimiter;

    // 构建 CSV
    const lines = [];

    // 头部
    lines.push(headers.map(h => this.escapeField(h, delimiter)).join(delimiter));

    // 数据行
    for (const row of data) {
      const values = headers.map(h => this.escapeField(row[h], delimiter));
      lines.push(values.join(delimiter));
    }

    return lines.join('\n');
  }

  /**
   * 转义字段
   */
  escapeField(value, delimiter) {
    if (value === null || value === undefined) {
      return '';
    }
    
    const str = String(value);
    
    // 需要引号的情况：包含分隔符、换行或引号
    if (str.includes(delimiter) || str.includes('\n') || str.includes('"')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    
    return str;
  }

  /**
   * 生成下载链接
   */
  createDownload(data, filename = 'export.csv') {
    const csv = this.write(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    return URL.createObjectURL(blob);
  }
}

/**
 * CSV 工具函数
 */
export function csvToJSON(csvText, options = {}) {
  const adapter = new CSVAdapter();
  return adapter.parse(csvText, options);
}

export function jsonToCSV(jsonData, options = {}) {
  const adapter = new CSVAdapter();
  return adapter.write(jsonData, options);
}
