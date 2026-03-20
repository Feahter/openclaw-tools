# skill-tench-hunter 参考资料

## GitHub 搜索 Query 模板

```bash
# 基础搜索
gh search repos "$TOPIC" --sort=stars --order=desc --limit 10

# 精确匹配
gh search repos "topic:$TOPIC" --sort=stars --limit 10

# 组合搜索
gh search repos "$TOPIC implementation" --sort=stars --limit 5
gh search repos "$TOPIC javascript OR typescript" --sort=stars --limit 5
gh search repos "$TOPIC api OR sdk" --sort=stars --limit 5

# 元数据获取
curl -s "https://api.github.com/repos/{owner}/{repo}" | jq '{description, stars: .stargazers_count, language, updated_at, topics, forks_count, license: .license.spdx_id}'
```

## 并行抓取策略

```bash
# 并行抓取多个 URL（使用后台任务）
fetch_url() {
  local url="$1"
  local output="$2"
  curl -s "$url" -o "$output" &
}
# 等所有后台任务完成
wait
```

## 报告生成 Checkpoint

```markdown
## 报告生成 Checkpoint

- [ ] 标题：[技术名] 技术深度研究
- [ ] 副标题：Created: YYYY-MM-DD, Sources: [链接]
- [ ] Section 1: 概述（一句话定性 + 现状）
- [ ] Section 2: 核心机制（API + 竞品对比）
- [ ] Section 3: 生态现状（关键项目 + 工具链）
- [ ] Section 4: 应用场景（3+ 场景）
- [ ] Section 5: 局限性 / 风险
- [ ] Section 6: 对 OpenClaw 的意义
- [ ] Section 7: 总结（评分表）
- [ ] 参考资料（含链接）
```

## 最佳实践指南结构模板

```markdown
# [技术名] 最佳实践指南

## 目录
1. 快速入门
2. 核心设计原则
3. 实践示例
4. 安全 / 避坑
5. 检查清单
6. 参考资源
```
