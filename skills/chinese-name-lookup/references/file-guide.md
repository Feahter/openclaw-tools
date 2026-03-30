# 脚本文件说明

## 主入口

| 文件 | 用途 |
|------|------|
| `scripts/name_generator.py` | **主入口**：整合所有模块，提供 `quick_generate`、`generate_name_recommendations`、`analyze_existing_name` |

## 核心引擎

| 文件 | 用途 |
|------|------|
| `scripts/bazi_engine.py` | 八字排盘 + 十神 + 十二长生（1050行） |
| `scripts/lunar_calendar.py` | 农历转换（1900-2100年） |
| `scripts/xiyongshen_v2.py` | 本地喜用神 v2（调候优先 + 格局已成） |
| `scripts/rizhu_strength_v2.py` | 日主强弱 v2（权重法 + 计数法 + `determine_primary_method`） |
| `scripts/pattern_method.py` | 格局取用法 + 成败判定 + 破格分析 |
| `scripts/poge_analyzer.py` | 破格原因识别（6种破格类型） |

## 调候与藏干

| 文件 | 用途 |
|------|------|
| `scripts/tiao_hou.py` | 穷通宝鉴120格调候喜忌表 |
| `scripts/tiao_hou_judge.py` | 调候优先级判定 |
| `scripts/yueling_canggan.py` | 月令藏干表 |
| `scripts/shier_changsheng.py` | 十二长生表 |

## 姓名评分

| 文件 | 用途 |
|------|------|
| `scripts/name_scorer_v3.py` | 三维评分引擎（喜用神40% + 生肖30% + 十神20% + 字义10%） |
| `scripts/zodiac_preferences.py` | 十二生肖用字宜忌 |
| `scripts/liushen_xinxing.py` | 六神心性速查（性格/职业/六亲） |
| `scripts/wuge_calculator.py` | 五格计算（仅供参考） |
| `scripts/wuxing_power.py` | 五行力量计算 |

## 大运神煞

| 文件 | 用途 |
|------|------|
| `scripts/dayun_liunian.py` | 大运流年推算（1005行） |
| `scripts/shen_sha.py` | 神煞查询系统（15个神煞） |

## 报告输出

| 文件 | 用途 |
|------|------|
| `scripts/report_formatter.py` | Phase 9 完整报告格式化器（900行） |
| `scripts/bazi_api.py` | 可选：外部八字 API 集成 |

## 测试文件

| 文件 | 用途 |
|------|------|
| `scripts/test_bazi_engine_day.py` | 日柱计算测试 |
| `scripts/wuxing_power_test.py` | 五行力量测试 |
| `scripts/test_*.py`（其余9个） | 各模块端到端测试 |

## 数据文件

| 文件 | 用途 |
|------|------|
| `references/stroke_table.json` | 汉字笔画数表（25,653行） |
| `references/wuge_rules.json` | 五格数理吉凶（19,823行，仅供参考） |
| `data/sample_output.json` | 参考输出样本（用于测试对比） |

---

## 已知 Bug

### JDN 公式误差（2000年后日期）

**影响**：日柱、时柱可能有 5-8 天误差（尤其 2000 年后日期）

**根因**：`bazi_engine.py` 中 `_julian_day_number` 的 Gregorian century correction 计算有误

**修复方向**：
- 改用 `ephem` 库
- 或用甲子反推 BASE_JDN
- 或验证公式：`y//100 - y//400` 部分

**状态**：已知，待修复
