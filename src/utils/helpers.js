// 工具函数 - 组合优于继承

// 缓存/Memoization
const memo = new Map();
export function memoize(key, fn) {
  if (memo.has(key)) return memo.get(key);
  const result = fn();
  memo.set(key, result);
  return result;
}

export function memoizeClear() {
  memo.clear();
}

// 防抖 - 高频事件优化
export function debounce(fn, delay = 300) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流 - 限制执行频率
export function throttle(fn, limit = 100) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ID生成
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
}

// 深拷贝
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// 表单验证
export function validate(data, rules) {
  const errors = [];
  for (const [field, rule] of Object.entries(rules)) {
    if (rule.required && !data[field]) {
      errors.push(`${field} 不能为空`);
    }
    if (rule.min && data[field]?.length < rule.min) {
      errors.push(`${field} 至少 ${rule.min} 个字符`);
    }
    if (rule.pattern && !rule.pattern.test(data[field])) {
      errors.push(`${field} 格式不正确`);
    }
  }
  return errors;
}

// 权限检查
export function hasPermission(role, action) {
  const permissions = {
    admin: ['create', 'read', 'update', 'delete'],
    editor: ['create', 'read', 'update'],
    viewer: ['read']
  };
  return permissions[role]?.includes(action) || false;
}

// 公式计算
export function calculateFormula(formula, data) {
  try {
    let expr = formula;
    for (const [key, val] of Object.entries(data)) {
      expr = expr.replace(new RegExp(`\\{${key}\\}`, 'g'), val);
    }
    return eval(expr);
  } catch (e) {
    return null;
  }
}

// 日期格式化
export function formatDate(timestamp, format = 'YYYY-MM-DD') {
  const d = new Date(timestamp);
  return format
    .replace('YYYY', d.getFullYear())
    .replace('MM', String(d.getMonth() + 1).padStart(2, '0'))
    .replace('DD', String(d.getDate()).padStart(2, '0'))
    .replace('HH', String(d.getHours()).padStart(2, '0'))
    .replace('mm', String(d.getMinutes()).padStart(2, '0'));
}

// 工具集合导出
export default {
  memoize, memoizeClear,
  debounce, throttle,
  generateId, deepClone,
  validate, hasPermission,
  calculateFormula, formatDate
};
