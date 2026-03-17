# CSV 数据分析与可视化所需 Skills

## 输入数据

```csv
name,value
a,10
b,20
c,30
```

## 基础分析（无需特殊 Skill）

基于通用知识，对该数据的简单分析：

| 指标 | 值 |
|------|-----|
| 记录数 | 3 |
| 总和 (sum) | 60 |
| 平均值 (mean) | 20 |
| 最小值 (min) | 10 (a) |
| 最大值 (max) | 30 (c) |
| 中位数 (median) | 20 (b) |

---

## 完整分析与可视化所需 Skills

### 1. 数据分析类 Skills

- **data-analysis / pandas-skill**
  - 用途：加载 CSV、计算统计量（均值、方差、分布等）、数据清洗
  - 工具：Python + pandas / numpy

- **statistics-skill**
  - 用途：描述性统计、相关性分析、异常值检测

### 2. 数据可视化类 Skills

- **data-visualization / chart-skill**
  - 用途：生成柱状图、饼图、折线图等
  - 工具：Python matplotlib / seaborn / plotly

- **interactive-chart-skill**
  - 用途：生成可交互图表（如 Plotly Dash、ECharts）

### 3. 代码执行类 Skills

- **python-runner / code-executor**
  - 用途：在沙箱中执行 Python 代码，输出图表或统计结果

- **jupyter-skill**
  - 用途：在 Notebook 环境中完成探索性数据分析（EDA）

### 4. 文件处理类 Skills

- **csv-reader / file-skill**
  - 用途：解析 CSV 文件，支持大文件流式读取

### 5. 报告生成类 Skills

- **agency-document-generator**
  - 用途：将分析结果和图表导出为 PDF / DOCX / XLSX 报告

---

## 推荐执行流程

```
CSV 输入
  → csv-reader（解析数据）
  → data-analysis（统计分析）
  → data-visualization（生成图表）
  → agency-document-generator（输出报告）
```

---

## 结论

对于当前这份简单的 3 行 CSV 数据，**无需特殊 Skill** 即可完成基础统计分析。
若需要完整的可视化和报告输出，最关键的 Skills 是：

1. **data-visualization**（图表生成）
2. **python-runner**（代码执行）
3. **agency-document-generator**（报告导出）
