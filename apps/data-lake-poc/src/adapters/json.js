/**
 * JSON Adapter - JSON 导入/导出适配器
 */

export class JSONAdapter {
  constructor(datalake = null) {
    this.datalake =    this.type = datalake;
 'json';
  }

  /**
   * 读取 JSON 文件
   */
  async read(file, options = {}) {
    const text = await this.readFile(file);
    return this.parse(text, options);
  }

  /**
   * 解析 JSON 文本
   */
  parse(text, options = {}) {
    let data;

    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(`Invalid JSON: ${e.message}`);
    }

    // 处理不同 JSON 结构
    if (options.arrayPath) {
      // 从深层结构提取数组
      const paths = options.arrayPath.split('.');
      for (const path of paths) {
        if (data && typeof data === 'object') {
          data = data[path];
        }
      }
    }

    if (!Array.isArray(data)) {
      // 尝试转换为数组
      if (options.wrapSingle !== false && data && typeof data === 'object') {
        data = [data];
      } else {
        throw new Error('JSON does not contain an array');
      }
    }

    return data;
  }

  /**
   * 读取文件
   */
  readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;

      if (typeof file === 'string') {
        resolve(file);
      } else {
        reader.readAsText(file);
      }
    });
  }

  /**
   * 写入 JSON
   */
  write(data, options = {}) {
    const pretty = options.pretty !== false;
    const space = pretty ? 2 : 0;

    if (data && typeof data === 'object' && !Array.isArray(data)) {
      // 包装为对象结构
      const output = {
        exported_at: new Date().toISOString(),
        count: Object.keys(data).length,
        data
      };
      return JSON.stringify(output, null, space);
    }

    return JSON.stringify(data, null, space);
  }

  /**
   * 生成下载
   */
  createDownload(data, filename = 'export.json') {
    const json = this.write(data);
    const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
    return URL.createObjectURL(blob);
  }

  /**
   * NDJSON (Newline Delimited JSON) 支持
   */
  async readNDJSON(file, options = {}) {
    const text = await this.readFile(file);
    const lines = text.split('\n').filter(l => l.trim());
    
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(Boolean);
  }

  writeNDJSON(data, options = {}) {
    return data.map(row => JSON.stringify(row)).join('\n');
  }
}

/**
 * JSON Lines (JSONL) 格式
 */
export class JSONLinesAdapter extends JSONAdapter {
  constructor(datalake = null) {
    super(datalake);
    this.type = 'jsonl';
  }

  async read(file, options = {}) {
    return this.readNDJSON(file, options);
  }

  write(data, options = {}) {
    return this.writeNDJSON(data, options);
  }
}
