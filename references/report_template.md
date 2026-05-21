# M7 内部讨论报告模板

报告固定 tagline：

> 本报告用于内部方向讨论，不替代立项决策。

## 三标签规则

|位置|是否强制标签|
|---|---|
|评分表每个维度|必须|
|章节结论句|必须|
|direction.md 三轴判断|必须|
|direction_hypotheses 四条|必须|
|普通描述、铺垫、上下文|不强制|

标签是给读者快速分级，不要给每句话贴标签。

## 单报告输出

M7 固定输出一份报告：

- `report/report.md` 和 `report/report.html`：立项报告。

## 立项报告结构

```markdown
# {项目名}

> 本报告用于内部方向讨论，不替代立项决策。

## 1. 方向摘要
🟡【AI 推断】一句话总结方向灯号、核心机会和最大待验证假设。

## 2. 为什么值得继续验证
🟢/🟡/🔴【标签】本方向可能成立的最短论证。

### 目标玩家
……

### 玩家吸引点
……

### 竞品没满足的切口
……

### 传播钩子
……

## 3. 调研要点
按 `supports` 分块：market、player_preference、competitor、trend、art_style、monetization。

## 4. 选题对比与选定理由
放 M3 横向表、Top1 选择理由、备选方向。

## 5. 立项初案 + 关键画面清单
放 M4 概念说明和 6-8 张 shotlist。

## 6. 关键画面与提示词

使用 `{{SHOT_CARDS}}` 占位符，由 `md_to_html.py --prompts` 自动注入为图片+提示词双栏卡片：

- 左侧展示已生成图片或占位提示
- 右侧展示完整提示词文本
- 附带「复制提示词」按钮，方便手动复制去跑图

```markdown
## 6. 关键画面与提示词

{{SHOT_CARDS}}
```

若未提供 `--prompts`，占位符原样保留。

## 7. 待验证假设
列出后续人工调研、demo、玩家访谈要验证的问题。

## 8. 注意事项
不影响评分，但供讨论参考。

## 9. 附录
来源清单、所有提示词、备选选题。
```

## HTML 输出

HTML 报告必须由 huashu-design 执行设计，不使用固定版式模板。

推荐流程：

1. 先生成 `report/report.md`。
2. 运行 `scripts/build_huashu_brief.py {project_dir}`，生成 `report/huashu_design_brief.md`。
3. 调用 huashu-design skill，读取该 brief、`report/report.md`、`images/prompts.jsonl` 和已生成图片，产出最终 `report/report.html`。
4. 只有无法调用 huashu-design 时，才用 `scripts/md_to_html.py` 作为兜底转换器。

报告内容组织规则：

- 候选方案对比、评分、来源等级、待验证假设优先用表格。
- 只要能用表格清晰表达，不要写成长段落。
- 不要默认把所有数值表格做成图表；只有当图表能显著减少理解成本时，才设计专门的图表模块。
- HTML 设计可以重排内容、做卡片、做导航、做重点摘要，但不能丢失核心结论。
