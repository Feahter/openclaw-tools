# Interactive Tools Reference

Templates for interactive calculators and simulators.

---

## Compound Interest Calculator (复利计算器)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 500px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .form-group { margin-bottom: 16px; }
  label { display: block; font-size: 14px; margin-bottom: 6px; color: #666; }
  input[type="number"], input[type="range"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
  input[type="range"] { padding: 0; }
  .range-value { float: right; font-weight: 600; color: #3b82f6; }
  .result { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-top: 20px; }
  .result-label { font-size: 14px; opacity: 0.9; }
  .result-value { font-size: 32px; font-weight: 700; margin: 8px 0; }
  .result-detail { font-size: 13px; opacity: 0.8; }
</style>
</head>
<body>
<div class="container">
  <h3>复利计算器</h3>
  <div class="form-group">
    <label>初始金额 <span class="range-value" id="principalVal">¥10000</span></label>
    <input type="range" id="principal" min="1000" max="1000000" step="1000" value="10000" oninput="calculate()">
  </div>
  <div class="form-group">
    <label>年化收益率 <span class="range-value" id="rateVal">5%</span></label>
    <input type="range" id="rate" min="1" max="20" step="0.5" value="5" oninput="calculate()">
  </div>
  <div class="form-group">
    <label>投资年限 <span class="range-value" id="yearsVal">10年</span></label>
    <input type="range" id="years" min="1" max="30" step="1" value="10" oninput="calculate()">
  </div>
  <div class="form-group">
    <label>每月定投 <span class="range-value" id="monthlyVal">¥0</span></label>
    <input type="range" id="monthly" min="0" max="10000" step="100" value="0" oninput="calculate()">
  </div>
  <div class="result">
    <div class="result-label">最终金额</div>
    <div class="result-value" id="finalAmount">¥16,289</div>
    <div class="result-detail" id="detail">本金: ¥10,000 | 收益: ¥6,289</div>
  </div>
</div>
<script>
function formatMoney(n) {
  return '¥' + n.toLocaleString('zh-CN', { maximumFractionDigits: 0 });
}
function calculate() {
  const P = +document.getElementById('principal').value;
  const r = +document.getElementById('rate').value / 100;
  const t = +document.getElementById('years').value;
  const M = +document.getElementById('monthly').value;
  
  document.getElementById('principalVal').textContent = formatMoney(P);
  document.getElementById('rateVal').textContent = (r*100).toFixed(1) + '%';
  document.getElementById('yearsVal').textContent = t + '年';
  document.getElementById('monthlyVal').textContent = formatMoney(M);
  
  const compoundPrincipal = P * Math.pow(1 + r, t);
  let compoundMonthly = 0;
  if (M > 0) {
    const monthlyRate = r / 12;
    const months = t * 12;
    compoundMonthly = M * (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate * (1 + monthlyRate);
  }
  const total = compoundPrincipal + compoundMonthly;
  const totalInvested = P + M * t * 12;
  const profit = total - totalInvested;
  
  document.getElementById('finalAmount').textContent = formatMoney(total);
  document.getElementById('detail').textContent = `本金: ${formatMoney(totalInvested)} | 收益: ${formatMoney(profit)}`;
}
calculate();
</script>
</body>
</html>
```

---

## Unit Converter (单位换算器)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 400px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .converter { background: #f8fafc; padding: 20px; border-radius: 12px; }
  .form-group { margin-bottom: 16px; }
  label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
  input, select { width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 15px; }
  .equals { text-align: center; font-size: 24px; color: #94a3b8; margin: 12px 0; }
  .result { background: #3b82f6; color: white; padding: 16px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: 600; }
</style>
</head>
<body>
<div class="container">
  <h3>长度单位换算</h3>
  <div class="converter">
    <div class="form-group">
      <label>输入值</label>
      <input type="number" id="input" value="1" oninput="convert()">
    </div>
    <div class="form-group">
      <label>从</label>
      <select id="from" onchange="convert()">
        <option value="m">米 (m)</option>
        <option value="km">千米 (km)</option>
        <option value="cm">厘米 (cm)</option>
        <option value="mm">毫米 (mm)</option>
        <option value="ft">英尺 (ft)</option>
        <option value="in">英寸 (in)</option>
      </select>
    </div>
    <div class="equals">↓</div>
    <div class="form-group">
      <label>到</label>
      <select id="to" onchange="convert()">
        <option value="ft">英尺 (ft)</option>
        <option value="m" selected>米 (m)</option>
        <option value="km">千米 (km)</option>
        <option value="cm">厘米 (cm)</option>
        <option value="mm">毫米 (mm)</option>
        <option value="in">英寸 (in)</option>
      </select>
    </div>
    <div class="result" id="result">3.28 ft</div>
  </div>
</div>
<script>
const rates = { m: 1, km: 1000, cm: 0.01, mm: 0.001, ft: 0.3048, in: 0.0254 };
function convert() {
  const val = +document.getElementById('input').value;
  const from = document.getElementById('from').value;
  const to = document.getElementById('to').value;
  const result = val * rates[from] / rates[to];
  const labels = { m: 'm', km: 'km', cm: 'cm', mm: 'mm', ft: 'ft', in: 'in' };
  document.getElementById('result').textContent = result.toFixed(2) + ' ' + labels[to];
}
convert();
</script>
</body>
</html>
```

---

## Loan Calculator (贷款计算器)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 500px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .form-group { margin-bottom: 16px; }
  label { display: block; font-size: 14px; margin-bottom: 6px; color: #666; }
  input[type="range"] { width: 100%; }
  .range-value { float: right; font-weight: 600; color: #3b82f6; }
  .summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; }
  .summary-item { background: #f8fafc; padding: 16px; border-radius: 10px; text-align: center; }
  .summary-label { font-size: 12px; color: #666; margin-bottom: 4px; }
  .summary-value { font-size: 18px; font-weight: 700; color: #1f2937; }
  .highlight { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; }
  .highlight .summary-label { color: rgba(255,255,255,0.8); }
  .highlight .summary-value { color: white; }
</style>
</head>
<body>
<div class="container">
  <h3>房贷计算器</h3>
  <div class="form-group">
    <label>贷款金额 <span class="range-value" id="amountVal">100万</span></label>
    <input type="range" id="amount" min="10" max="1000" step="10" value="100" oninput="calculate()">
  </div>
  <div class="form-group">
    <label>贷款年限 <span class="range-value" id="yearsVal">30年</span></label>
    <input type="range" id="years" min="5" max="30" step="1" value="30" oninput="calculate()">
  </div>
  <div class="form-group">
    <label>年利率 <span class="range-value" id="rateVal">4.2%</span></label>
    <input type="range" id="rate" min="2" max="8" step="0.1" value="4.2" oninput="calculate()">
  </div>
  <div class="summary">
    <div class="summary-item highlight">
      <div class="summary-label">月供</div>
      <div class="summary-value" id="monthly">¥4,890</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">总利息</div>
      <div class="summary-value" id="totalInterest">¥76万</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">还款总额</div>
      <div class="summary-value" id="totalPayment">¥176万</div>
    </div>
  </div>
</div>
<script>
function calculate() {
  const amount = +document.getElementById('amount').value * 10000;
  const years = +document.getElementById('years').value;
  const rate = +document.getElementById('rate').value / 100;
  
  document.getElementById('amountVal').textContent = (amount/10000) + '万';
  document.getElementById('yearsVal').textContent = years + '年';
  document.getElementById('rateVal').textContent = (rate*100).toFixed(1) + '%';
  
  const monthlyRate = rate / 12;
  const months = years * 12;
  const monthly = amount * monthlyRate * Math.pow(1 + monthlyRate, months) / (Math.pow(1 + monthlyRate, months) - 1);
  const totalPayment = monthly * months;
  const totalInterest = totalPayment - amount;
  
  document.getElementById('monthly').textContent = '¥' + (monthly/10000).toFixed(2) + '万';
  document.getElementById('totalInterest').textContent = '¥' + (totalInterest/10000).toFixed(0) + '万';
  document.getElementById('totalPayment').textContent = '¥' + (totalPayment/10000).toFixed(0) + '万';
}
calculate();
</script>
</body>
</html>
```

---

## Tips

- Always provide sensible default values
- Use sliders for ranges where users want to explore "what if" scenarios
- Show results immediately (no submit button needed)
- Format numbers with appropriate units and separators
- Add visual hierarchy to highlight the most important result
