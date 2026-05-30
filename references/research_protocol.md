# M2 证据驱动调研协议

本协议用于快速判断“方向是否值得继续讨论验证”，不是立项决策、成本评估、团队评估、政策定性或 ROI 测算。

## 输入

- `project_state.inputs`
- `project_state.inputs.research_keywords`
- `research/sources.jsonl` 中已有来源（恢复或补充调研时）

## 输出

- `research/sources.jsonl`
- `research/findings.md`
- `research/direction.md`
- `project_state.research`
- `project_state.direction_judgment`

## sources.jsonl 证据原子

每行一条 JSON，字段如下：

```json
{
  "id": "S001",
  "claim": "可被引用的一句话主张",
  "url": "https://example.com",
  "supports": ["market", "competitor"],
  "source_type": "industry_report",
  "publisher": "发布方",
  "published_at": "2025-08-15",
  "fetched_at": "2026-05-19T16:10:00+08:00",
  "excerpt": "原文片段，不超过 200 字",
  "data_type": "quantitative",
  "reliability": "high",
  "notes": "口径说明"
}
```

`supports` 可选值：`market`、`player_preference`、`competitor`、`trend`、`art_style`、`monetization`。

## 来源可靠性

|级别|适用|
|---|---|
|high|厂商财报、官方应用商店数据、付费数据机构、知名媒体一手报道|
|medium|行业自媒体二手转引、研究机构免费报告、官方采访、可追溯平台页|
|low|社区帖、不署名博客、不可追溯转载|

## 三轴判断

|轴|判断问题|
|---|---|
|市场机会|赛道体量、增长信号、新兴变种是否存在|
|玩家需求信号|玩家痛点/爽点是否能被解释，现有产品是否未完全满足|
|竞品差异空间|是否还有清晰的切口，而不是只复制头部产品|

## 灯号规则

绿灯：三轴均出现正向信号，且关键判断证据强度为 `strong` 或 `medium`。

黄灯：默认档位。有可挖掘空间，但存在待验证假设。绝大多数方向应落在黄灯。

红灯仅两种触发：

- R1 玩家需求信号完全缺失：未找到任何可解释的玩家需求信号，且无法从相邻品类合理迁移。
- R2 赛道拥挤且无清晰差异切口：头部产品话语权明显且至少 2 条 medium 以上来源支撑，同时本次输入未提出差异点，调研也未发现新切口。

证据不足时 `evidence_strength = weak`：禁止出绿灯，禁止出红灯，最高黄灯。

小众创新方向：默认黄灯 + 待验证假设，不因缺少大市场数据红灯。

## 证据强度

- `strong`: 关键判断有 3 条以上 high 来源，且核心数据在 12 个月内。
- `medium`: 关键判断有 2 条以上 medium 及以上来源，或有可追溯平台页 + 社区讨论互相印证。
- `weak`: 低于上述标准，或联网/抓取失败进入降级模式。

## 写作硬规则

- 每个定量结论末尾必须挂 `[Sxxx]` 引用，否则不写入。
- 无 high/medium 来源时，用“未获取到可靠来源支撑该数据，列为待验证假设”。
- 来源时间超过 18 个月，标注“数据较旧，仅作参考”。
- 来源互相冲突时，并列展示并标注分歧。
- 定性判断允许综合，但需区分“广泛共识”和“个别声音”。
- 任何风险、政策、平台限制默认放到“注意事项”，不参与 M3 评分。

## 注意事项上升机制

注意事项默认不影响评分，但触发以下条件时必须上升为三轴评估项：

- 直接破坏需求信号：写入“玩家需求信号”轴并扣分。
- 直接消除差异空间：写入“竞品差异空间”轴并扣分。
- 方向因外部约束不可成立：触发红灯 R2 的扩展解释。

如命中上升条件，`direction.md` 必须写明“已上升为三轴评估项”。

## direction.md 模板

```markdown
# 方向判断：🟡 黄灯 — 值得继续验证

## 一句话结论
🟡【AI 推断】这个方向有 X 信号 / 缺 Y 证据 / 建议下一步做 Z。

## 三轴信号
- 市场机会：…… 🟢 [S003][S007]
- 玩家需求信号：…… 🟡 [S005][S008]
- 竞品差异空间：…… 🟢 [S001][S004][S010]

## 证据充分度：medium
- 关键来源：medium 级 X 条 / high 级 Y 条
- 数据时间窗：YYYY-MM ~ YYYY-MM

## 待验证假设
1. ……

## 注意事项（不影响评分，供讨论参考）
- 题材层面：……
- 平台层面：……
- 玩法层面：……

## 建议下一步
- 进入选题推荐 / 调整输入重跑 / 暂不推进
- 若继续，建议在 demo 阶段优先验证：……
```

## 实操注意事项

### 批量搜索模式（推荐）

使用 `execute_code` 可在单次脚本中串行跑多组 `search_web.py`，每轮 5-6 个关键词，比逐个 terminal 调用更高效。注意：

- 每个 `execute_code` 调用中无需手动获取 `TAVILY_API_KEY`——`search_web.py` 内置了 Keychain 回退机制，在 `execute_code` 沙箱中会自动从 macOS Keychain 读取。
- 收集 JSONL 输出时优先在 Python 内解析 `result["output"]` 后直接 `write_file`，避免依赖 shell 重定向 `>>`（execute_code 中 shell 重定向行为不稳定）
- 搜索参数用 `--max-results 3`（非 `--limit`）；JSONL 输出用 `--jsonl`

### fetch_url.py 的 JS 页面限制

`fetch_url.py` 基于 HTTP 请求 + BeautifulSoup，对 JS 重度渲染页面（Steam 商店页、腾讯新闻、知乎专栏等）通常只提取到导航/框架文本，正文缺失。遇到以下情况时降级处理：

- 提取文本 < 500 字符且无实质信息 → 仍可写入 sources.jsonl，但 `excerpt` 从 Tavily 搜索摘要中提取，`reliability` 降一档
- 需要完整正文的关键来源（如行业报告）→ 考虑用 `scrapling-web-fetch` skill（支持现代 JS 页面和微信公众号）
- 知乎返回 403 属正常反爬 → 直接用搜索摘要，标注"页面受限无法抓取"

## 降级模式

当搜索或抓取连续失败 3 次以上：

- `direction_judgment.evidence_strength = weak`
- 报告封面加入"本次未能完成联网调研，结论基于模型已知信息"
- 所有判断默认打 🟡 或 🔴
- 禁止绿灯，禁止 8 分以上候选
- 报告末尾列出人工补充调研问题
