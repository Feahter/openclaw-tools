/**
 * UUID Generator - 简单 UUID 生成器
 */

export function v4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export function v4Short() {
  return 'xxxxxxxx'.replace(/[x]/g, function(c) {
    return Math.random().toString(16).substr(2, 1);
  });
}

export function generateId(prefix = '') {
  return prefix ? `${prefix}_${v4Short()}` : v4Short();
}
