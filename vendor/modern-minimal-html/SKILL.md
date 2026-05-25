---
name: modern-minimal-html
description: 现代极简风格HTML文档模板。游戏立项/产品BP/商业计划/系统设计方案。单文件HTML+纯CSS，极细边框，无阴影，信息密度高。
trigger: 用户说「现代极简」「极简风」「做个HTML文档」「用现代极简风格」「white-doc style」「modern minimal」
---

# Modern Minimal HTML · 现代极简风文档模板

## 触发条件

用户说：
- 「按现代极简风格做一份HTML」
- 「做个极简风文档」
- 「white-doc style」
- 「modern minimal」
- 「做成像上次那个需求文档的样式」

> v2.2 已融合 `china_mobile_game_market_2026.html` 和 `survival_theme_comparison_producer.html` 两套实践，组件数扩充至 19 种，覆盖数据指标、排行评分、趋势分析、对比表格、图片+提示词卡片等场景。
>
> v2.3 新增 `--color-background-body` CSS 变量和 `templates/base.html` 完整起始模板，body 背景不再依赖浏览器默认白。
>
> v2.4 (2026-05-26) 组件 19 shot card 重构：区分横竖版布局（280px/400px），新增排版约束表和占位框规范。

## 模板框架

### HTML 基本结构

```html
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--color-text-primary:#1A1A1A;--color-text-secondary:#6B6B6B;--color-text-tertiary:#9A9A9A;--color-background-body:#F5F0EB;--color-background-primary:#FFFFFF;--color-background-secondary:#F4F3F1;--color-border-tertiary:#E4E2DF;--font-sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;--border-radius-lg:8px;--border-radius-md:6px}
body{font-family:var(--font-sans);color:var(--color-text-primary);background:var(--color-background-body)}
.wrap{padding:1rem 0}
.sec-label{font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.07em;padding-bottom:.5rem;border-bottom:.5px solid var(--color-border-tertiary);margin-bottom:1.1rem}
.section-title{font-size:16px;font-weight:600;color:var(--color-text-primary);padding-bottom:.5rem;border-bottom:.5px solid var(--color-border-tertiary);margin-bottom:1.1rem;letter-spacing:.02em}
.section{margin-bottom:2.2rem}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.card{background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:14px 16px}
.card-title{font-size:13px;font-weight:500;color:var(--color-text-primary);margin-bottom:7px}
.card-body{font-size:12px;color:var(--color-text-secondary);line-height:1.7}
.tag{display:inline-block;font-size:10px;font-weight:500;padding:2px 6px;border-radius:3px;margin:2px}
.tb{background:#E6F1FB;color:#0C447C}
.tt{background:#E1F5EE;color:#085041}
.ta{background:#FAEEDA;color:#633806}
.tc{background:#FAECE7;color:#4A1B0C}
.tp{background:#EEEDFE;color:#26215C}
.tg{background:#F2F2F0;color:#555}
</style>
```

### 核心设计原则

| 原则 | 说明 |
|------|------|
| **信息密度优先** | 字号偏小(9-20px)，行高给够(1.3-1.7)，可读性不丢 |
| **零装饰冗余** | 无投影、渐变、动效。纯靠边框+颜色区分层级 |
| **标题层级分明** | section-title(16px/600) 是段落级标题，用粗字重+细边分隔区块。区内子标题用 sec-label(11px/500 大写) 形成主次落差。**不要用 11px 做段落标题**——用户会嫌小 |
| **CSS变量驱动** | `var(--color-text/background/border-*)` 可一键换肤色 |
| **body 背景显式化** | body 必须设 `background: var(--color-background-body)`，不依赖浏览器默认白。`--color-background-body` 与卡片纯白 `--color-background-primary` 可错开形成层次感（推荐 body 暖白、卡片纯白） |
| **纯flex/grid** | 无框架依赖，任何浏览器直接跑 |
| **自文档化** | HTML注释标记每个区块用途 `<!-- SECTION: XXX -->` |

### 字号梯度

```
9px  — 日历标签/极简脚注
10px — 标签/徽章/脚注
11px — 区块标签/表格相位/阶段名
12px — 正文/卡片内容
13px — 卡片标题/条目标题
14px — 副标题
16px — 大区段标题（section-title）
20px — 主标题
22px — 指标数值（metric-value，仅指标卡用）
```

### 调色板（CSS变量）

- `--color-text-primary` — 主文字色
- `--color-text-secondary` — 次级文字色
- `--color-text-tertiary` — 弱化文字色
- `--color-background-body` — 页面整体背景色（body 背景，默认暖白 `#F5F0EB`，与卡片纯白错开层次）
- `--color-background-primary` — 卡片/主体背景
- `--color-background-secondary` — 次要背景（表格表头/高亮区）
- `--color-border-tertiary` — 边框色
- `--font-sans` — 字体
- `--border-radius-lg` / `--border-radius-md` — 圆角

### 6种标签色（用于.tag）

| 类名 | 背景 | 文字 | 用途 |
|------|------|------|------|
| `.tb` | #E6F1FB | #0C447C | 蓝色 — 一般/信息 |
| `.tt` | #E1F5EE | #085041 | 绿色 — 正面/收益 |
| `.ta` | #FAEEDA | #633806 | 琥珀 — 警告/中优先级 |
| `.tc` | #FAECE7 | #4A1B0C | 珊瑚 — 高风险/紧急 |
| `.tp` | #EEEDFE | #26215C | 紫色 — 特殊/高端 |
| `.tg` | #F2F2F0 | #555 | 灰色 — 中性/通用 |

### 4种阶段色（直接style内联）

| 色值 | 用途 |
|------|------|
| #D85A30 (橙) | 早期/启动/高风险 |
| #BA7517 (金/琥珀) | 中期/习惯形成 |
| #1D9E75 (绿) | 深度/稳定期 |
| #3266ad (蓝) | 长期/最大规模 |

### 6种图标底色（用于 trend-card / integrate-card 的 icon 圈）

| 色值 | 用途 |
|------|------|
| #E6F1FB | 蓝色 — 信息/技术 |
| #EEEDFE | 紫色 — AI/创新 |
| #E1F5EE | 绿色 — 增长/自然 |
| #FAEEDA | 琥珀 — 运营/变现 |
| #FAECE7 | 珊瑚 — 风险/热度 |
| #FBEAF0 | 粉 — 趋势/社会 |

## 19种组件模块

### 1. 大区段标题 (section-title)
```html
<div class="section-title">1. 方向摘要</div>
```
16px + 600字重 + 底部细边。**每个 section 顶部的首要标题**，视觉权重最高，与后面 11px 的 sec-label 形成主次层级。

### 2. 区块标签 (sec-label)
```html
<div class="sec-label">Section title — description</div>
```
11px 大写 + 底部细边框。**次一级标题**，用于区内小标题或 English sub-label，与 section-title 配合使用。

### 3. 标题区 (Title block)
```html
<div style="margin-bottom:1.8rem">
  <div style="font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px">Kicker line</div>
  <div style="font-size:20px;font-weight:500;line-height:1.3;margin-bottom:5px">🎮 Main Title<br><span style="font-size:14px;font-weight:400;color:var(--color-text-secondary)">Subtitle description</span></div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
    <span class="tag tb">Tag 1</span>
    <span class="tag tt">Tag 2</span>
  </div>
</div>
```

### 4. 流程弧 (Loop arc)
```html
<div style="background:var(--color-background-secondary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:14px 16px">
  <div class="loop-row" style="gap:4px">
    <div style="flex:1"><div class="loop-node-bg"><div class="loop-icon">🎣</div><div class="loop-label">Step 1</div><div class="loop-sub">Description</div></div></div>
    <div style="display:flex;align-items:center;padding:0 4px;color:var(--color-text-tertiary);font-size:14px">→</div>
    <div style="flex:1"><div class="loop-node-bg"><div class="loop-icon">🏗️</div><div class="loop-label">Step 2</div><div class="loop-sub">Description</div></div></div>
  </div>
</div>
```
CSS:
```css
.loop-row{display:flex;gap:0;margin-bottom:0}
.loop-node-bg{border-radius:var(--border-radius-md);padding:10px 6px;background:var(--color-background-secondary);border:.5px solid var(--color-border-tertiary)}
.loop-icon{font-size:18px;display:block;margin-bottom:4px;text-align:center}
.loop-label{font-size:11px;font-weight:500;color:var(--color-text-primary);line-height:1.3;text-align:center}
.loop-sub{font-size:10px;color:var(--color-text-secondary);margin-top:2px;line-height:1.4;text-align:center}
```

### 5. 进度网格表 (Progression table)
```html
<div style="background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);overflow:hidden">
  <div class="prog-header">
    <div class="prog-header-cell">Phase</div>
    <div class="prog-header-cell">Column 1</div>
    <div class="prog-header-cell">Column 2</div>
    <div class="prog-header-cell">Column 3</div>
  </div>
  <div class="prog-row">
    <div class="prog-phase" style="color:#D85A30">Phase name<br><span style="font-weight:400;font-size:10px">Sub</span></div>
    <div class="prog-cell">Content</div>
    <div class="prog-cell">Content</div>
    <div class="prog-cell">Content</div>
  </div>
</div>
```
基础 CSS：
```css
.prog-table{background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);overflow:hidden}
.prog-header{background:var(--color-background-secondary);border-bottom:.5px solid var(--color-border-tertiary);display:grid;gap:0}
.prog-header-cell{font-size:10px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.05em;padding:6px 10px}
.prog-row{display:grid;gap:0;border-bottom:.5px solid var(--color-border-tertiary);padding:8px 10px;align-items:start}
.prog-row:last-child{border-bottom:none}
.prog-phase{font-size:11px;font-weight:500;color:var(--color-text-secondary);padding:0 10px}
.prog-phase strong{color:var(--color-text-primary)}
.prog-cell{font-size:11px;color:var(--color-text-secondary);line-height:1.5;padding:0 10px}
.prog-cell strong{color:var(--color-text-primary)}
```
⚠️ **铁律：prog-phase 必须有 padding。** 务必与 `prog-cell` 保持一致 `padding:0 10px`。缺了会导致：
- 第一列正文紧贴单元格左边缘（与其他列有 6px 左内边距不对齐）
- 表头 `prog-header-cell(padding:6px 10px)` 与数据第一列的文本起始位置错位，表头和数据对不上
- 列间距仅靠 prog-cell 左内边距 6px，视觉上太挤

#### 对齐验证清单（交付前自检） — 详细排查步骤见 `references/prog-table-troubleshooting.md`

用户抱怨「表头正文对不上」「列间距太挤」「歪的」时，按此排查：

```
[ ] 所有 prog-header-cell 的 padding-x 一致？（基准：10px）
[ ] prog-phase 的 padding-x == prog-cell 的 padding-x？（必须相等）
[ ] 数据行第一列的 padding-x == 表头第一列的 padding-x？（否则表头和数据的文本起始位错位）
[ ] 没有对单独列加 text-align:center？（会破坏表头/数据横排对齐）
[ ] grid-template-columns 没有用不合理的固定 px？（数据变长就挤）
```

**真实案例（踩坑过程）：**

| 轮次 | 做了什么 | 用户反馈 | 原因 |
|------|---------|---------|------|
| 1 | 候选列 `60px` 固定宽度 | 候选名被挤压换行 | 内容宽度远超 60px |
| 2 | 改为 `auto 64px 64px 52px 1fr`，中间列居中 | 表头正文对不上，列间距太挤 | ① 居中破坏了横排对齐 ② 定宽太死 ③ prog-phase 无 padding 导致错位 |
| 3 | 去掉居中，`auto 1fr 1fr 1fr 1fr`，只加 `padding-right:12px` 到 prog-phase | 完全没有变 | 根因没解决：全局 prog-phase 和 prog-cell 的 padding 不一致 |
| 4 | 统一 `prog-phase` 和 `prog-cell` 为 `padding:0 10px` | 对齐 | 表头/数据水平 padding 完全匹配 |

**教训**：对齐问题 90% 是 padding 不一致引起的。不要先怀疑列宽或居中——先用清单查 padding。

#### 列宽策略

通过 `.prog-c2` / `.prog-c3` / `.prog-c4` / `.prog-c5` class 控制栅格列数。在 HTML 中用 `<div class="prog-table prog-cN">`。

| variant | 列数 | 典型场景 | 推荐 grid-template-columns |
|---------|------|---------|---------------------------|
| `prog-c2` | 2 | 键值对照 | `1fr 1.6fr` |
| `prog-c3` | 3 | 三等分数据 | `1fr 1fr 1fr` |
| `prog-c4` | 4 | 阶段名+三列 | `90px 1fr 1fr 1fr` |
| `prog-c5` | 5 | 评分表/多维度 | 见下方 |

**列宽选型原则**（按优先级）：
1. **短内容用固定 px**：候选名、分数、标签等已知宽度的列，直接给 px 值（如 `150px 80px 60px`）。这比 `auto` 更可预测——读者和开发者都能预期列的位置
2. **等宽均分用 `1fr`**：正文列文字长短不一，均分最稳。不要用 `auto` 做长文列——它会根据内容抖动，每次数据变化都重排
3. **长文撑满用 `1fr`**：最右侧的备注/判断列始终用 `1fr` 吃剩余空间
4. **`auto` 仅当内容宽度无法预测**：如动态数据、用户生成的文本。此时必须加 `white-space:nowrap` 防止换行，且接受列宽会随内容变化

**prog-c5 实战案例**（评分对比表）：
```css
/* 候选(150px) | 原始分(80px) | 折算分(80px) | 标签(60px) | 判断(撑满) */
.prog-c5 .prog-header{grid-template-columns:150px 80px 80px 60px 1fr}
.prog-c5 .prog-row{grid-template-columns:150px 80px 80px 60px 1fr}
.prog-c5 .prog-phase{white-space:nowrap}
```
- 候选列 `150px` 固定宽，足够容纳 "C1 大奉打更人"。`white-space:nowrap` 兜底防换行
- 分数列 `80px` 固定宽，短数字居中不拥挤
- 标签列 `60px` 仅够 emoji+tag
- 判断列 `1fr` 吃剩余空间，长文本不换行
- 所有单元格 `padding:0 10px` 一致，表头/数据精确对齐
- **不要给中间列加 `text-align:center`**——会破坏表头/数据对齐一致性
- **不要用 `auto` 做第一列**——内容长度不可控时看似灵活，实际每次数据变化列宽都会重新计算，容易挤到相邻列

### 6. 双列解说 (grid2 + card)
```html
<div class="grid2">
  <div class="card">
    <div class="card-title">Title</div>
    <div class="card-body">Body content...</div>
  </div>
  <div class="card">
    <div class="card-title">Title</div>
    <div class="card-body">Body content...</div>
  </div>
</div>
```

### 7. 三列角色卡 (grid3 + char-card)
```html
<div class="grid3">
  <div class="char-card">
    <span class="char-icon">⛵</span>
    <div class="char-name">Name</div>
    <div class="char-role">Role</div>
    <div class="char-skill">Description</div>
  </div>
</div>
```
CSS:
```css
.char-card{background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);padding:12px}
.char-icon{font-size:24px;margin-bottom:6px;display:block}
.char-name{font-size:12px;font-weight:500;color:var(--color-text-primary);margin-bottom:2px}
.char-role{font-size:10px;color:var(--color-text-secondary);margin-bottom:6px}
.char-skill{font-size:11px;color:var(--color-text-secondary);line-height:1.5}
```

### 8. 营收比例条 (Monetization bar)
```html
<div class="mono-row">
  <div class="mono-type">Label</div>
  <div class="mono-bar-wrap"><div class="mono-bar" style="width:42%;background:#3266ad"></div></div>
  <div class="mono-pct">~42%</div>
  <div class="mono-desc">Description</div>
</div>
```
CSS:
```css
.mono-row{display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:.5px solid var(--color-border-tertiary)}
.mono-row:last-child{border-bottom:none}
.mono-type{font-size:12px;font-weight:500;color:var(--color-text-primary);min-width:110px}
.mono-bar-wrap{flex:1;background:var(--color-background-secondary);border-radius:4px;height:8px;overflow:hidden}
.mono-bar{height:100%;border-radius:4px}
.mono-pct{font-size:12px;font-weight:500;color:var(--color-text-secondary);min-width:36px;text-align:right}
.mono-desc{font-size:11px;color:var(--color-text-tertiary);min-width:180px}
```

### 9. 风险矩阵 (Risk matrix)
```html
<div class="risk-row">
  <div class="risk-lv rl-h">High</div>
  <div><div class="risk-title">Title</div><div class="risk-body">Description</div></div>
</div>
```
CSS:
```css
.risk-row{display:flex;gap:10px;padding:8px 0;border-bottom:.5px solid var(--color-border-tertiary);align-items:flex-start}
.risk-row:last-child{border-bottom:none}
.risk-lv{font-size:10px;font-weight:500;padding:2px 7px;border-radius:10px;white-space:nowrap;flex-shrink:0;margin-top:1px}
.rl-h{background:#FAECE7;color:#4A1B0C}
.rl-m{background:#FAEEDA;color:#633806}
.rl-l{background:#E1F5EE;color:#085041}
.risk-title{font-size:12px;font-weight:500;color:var(--color-text-primary);margin-bottom:2px}
.risk-body{font-size:11px;color:var(--color-text-secondary);line-height:1.6}
```

### 10. 时间线 (Timeline)
```html
<div class="timeline">
  <div class="tl-item">
    <div class="tl-dot" style="background:#D85A30"></div>
    <div class="tl-label">Phase label</div>
    <div class="tl-title">Phase title</div>
    <div class="tl-body">Description...</div>
  </div>
</div>
```
CSS:
```css
.timeline{position:relative;padding-left:28px}
.timeline::before{content:'';position:absolute;left:10px;top:0;bottom:0;width:1.5px;background:var(--color-border-tertiary)}
.tl-item{position:relative;margin-bottom:16px}
.tl-dot{position:absolute;left:-22px;top:3px;width:10px;height:10px;border-radius:50%;border:2px solid var(--color-background-primary)}
.tl-label{font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}
.tl-title{font-size:13px;font-weight:500;color:var(--color-text-primary);margin-bottom:4px}
.tl-body{font-size:12px;color:var(--color-text-secondary);line-height:1.65}
```

### 11. 日历网格 (Calendar grid)
```html
<div class="cal-grid">
  <div class="cal-month">
    <div class="cal-m-label">Jan</div>
    <div class="cal-block" style="background:#E6F1FB;color:#0C447C">Event<br>Name</div>
  </div>
</div>
```
CSS:
```css
.cal-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:3px}
.cal-month{text-align:center}
.cal-m-label{font-size:9px;color:var(--color-text-tertiary);text-align:center;margin-bottom:3px}
.cal-block{border-radius:3px;height:36px;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:500;text-align:center;line-height:1.3;padding:2px}
```

### 12. 关键指标卡 (Metric card)
用于展示核心数据指标——大号数字 + 标签 + 副文本。

```html
<div class="grid-4">
  <div class="metric-card">
    <div class="metric-label">China annual revenue</div>
    <div class="metric-value">$43B</div>
    <div class="metric-sub">Top globally in 2026</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Top genre by revenue</div>
    <div class="metric-value">RPG</div>
    <div class="metric-sub">$24B worldwide</div>
  </div>
</div>
```
CSS:
```css
.grid-4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.metric-card{background:var(--color-background-secondary);border-radius:var(--border-radius-md);padding:12px 14px}
.metric-label{font-size:12px;color:var(--color-text-secondary);margin-bottom:4px}
.metric-value{font-size:22px;font-weight:500;color:var(--color-text-primary)}
.metric-sub{font-size:11px;color:var(--color-text-tertiary);margin-top:2px}
```
`grid-4` 与 `grid2`/`grid3` 同理，4 等分栅格。指标卡可单独使用，不一定要套 grid-4。大号数字(22px)是全文最大字号，仅在指标卡中使用。

### 13. 排行进度条行 (Rank row)
带排名、名称、分类、进度条的排行行。用于产品排名榜单。

```html
<div class="card">
  <div style="font-size:12px;font-weight:500;color:var(--color-text-secondary);margin-bottom:10px">iOS App Store top grossing</div>
  <div class="rank-row">
    <div class="rank-num">#1</div>
    <div><div class="rank-name">Honor of Kings 王者荣耀</div><div class="rank-tag">MOBA · Tencent</div></div>
    <div class="rank-bar"><div class="bar" style="width:100%;background:#3266ad"></div></div>
  </div>
  <div class="rank-row">
    <div class="rank-num">#2</div>
    <div><div class="rank-name">Peacekeeper Elite 和平精英</div><div class="rank-tag">Shooter · Tencent</div></div>
    <div class="rank-bar"><div class="bar" style="width:85%;background:#3266ad"></div></div>
  </div>
</div>
```
CSS:
```css
.rank-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:.5px solid var(--color-border-tertiary)}
.rank-row:last-child{border-bottom:none}
.rank-num{font-size:12px;font-weight:500;color:var(--color-text-secondary);min-width:24px;text-align:right}
.rank-name{font-size:13px;font-weight:500;color:var(--color-text-primary)}
.rank-tag{font-size:11px;color:var(--color-text-secondary);margin-top:2px}
.rank-bar{flex-shrink:0;width:90px;background:var(--color-background-secondary);border-radius:4px;height:8px;overflow:hidden}
.rank-bar .bar{height:100%;border-radius:4px}
```
排行行是 flex 布局，三部分：排名(定宽24px) + 名称+分类(flex:1) + 进度条(90px)。`gap:10px`分隔。`rank-num`支持文字（#1、#2）或徽章（`<span class="badge up">↑ new</span>`）。

### 14. 趋势卡片 (Trend card)
带图标、标题、正文、标签行的信息卡片。用于展示趋势、方向、方案。

```html
<div class="grid-3">
  <div class="trend-card">
    <div class="trend-hd">
      <div class="trend-ic" style="background:#E6F1FB">🎯</div>
      <div class="trend-title">Shooter surge</div>
    </div>
    <div class="trend-body">5G-enabled smooth gameplay and competitive esports ecosystems drive shooter growth.</div>
    <div class="tag-row">
      <span class="tag tb">FPS/TPS</span>
      <span class="tag tb">Esports</span>
    </div>
  </div>
  <div class="trend-card">
    <div class="trend-hd">
      <div class="trend-ic" style="background:#EEEDFE">🧩</div>
      <div class="trend-title">Hybrid-casual rise</div>
    </div>
    <div class="trend-body">Hybrid-casual IAP revenue grew 37% in 2024, replacing pure hyper-casual.</div>
    <div class="tag-row">
      <span class="tag tp">SLG+</span>
      <span class="tag tp">Merge</span>
    </div>
  </div>
</div>
```
CSS:
```css
.trend-card{background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:14px 16px}
.trend-hd{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.trend-ic{width:28px;height:28px;border-radius:var(--border-radius-md);display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0}
.trend-title{font-size:14px;font-weight:500;color:var(--color-text-primary)}
.trend-body{font-size:12px;color:var(--color-text-secondary);line-height:1.6}
.tag-row{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
```
图标底色按「6种图标底色」表取色，标题14px稍大于普通卡片(13px)，正文12px。标签行 `tag-row` 用 flex wrap 避免溢出。

### 15. 标记徽章 (Badge)
用于排行行或列表中的状态标记。

```html
<div class="rank-num">
  <span class="badge up">↑ new</span>
</div>
<span class="badge hot">🔥 hot</span>
<span class="badge done">✓ done</span>
```
CSS:
```css
.badge{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:500;padding:3px 8px;border-radius:20px}
.badge.up{background:#EAF3DE;color:#3B6D11}
.badge.hot{background:#FAECE7;color:#714B13}
```
|常用变体：`up`（涨/新增/绿色）、`hot`（热门/珊瑚色）。需要更多色值按 6 种标签色体系扩展。

### 16. 评分点阵 (Score dots)
5 分制点阵评分——实心点 + 空心点，用于维度评分/能力值可视化。

```html
<div class="score-row">
  <div class="score-lbl">Visual distinction</div>
  <div class="score-dots">
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-e"></span>
  </div>
</div>
<div class="score-row">
  <div class="score-lbl">Female audience appeal</div>
  <div class="score-dots">
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-f" style="background:#1A5FAD"></span>
    <span class="dot-e"></span>
    <span class="dot-e"></span>
    <span class="dot-e"></span>
  </div>
</div>
```
CSS:
```css
.score-row{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:.5px solid var(--color-border-tertiary)}
.score-row:last-child{border-bottom:none}
.score-lbl{font-size:11px;color:var(--color-text-secondary);flex:1;line-height:1.3}
.score-dots{display:flex;gap:3px;flex-shrink:0}
.dot-f{width:9px;height:9px;border-radius:50%}
.dot-e{width:9px;height:9px;border-radius:50%;border:.5px solid var(--color-border-tertiary)}
```
- `score-row` 是 flex 行：左侧标签 `flex:1` 撑满，右侧点阵 `flex-shrink:0` 定宽
- `dot-f`（filled）= 实心圆，通过 `style="background:#色值"` 设颜色
- `dot-e`（empty）= 空心圆，自动使用边框色
- 常用于主题评分卡（theme-card）、能力雷达、竞品评分

### 17. 分析区块 (Factor block)
带彩色左边框的正文分析块。用于长文分析、因素拆解。

```html
<div class="fblock" style="border-left:3px solid #3266ad">
  <div class="fblock-title" style="color:#185FA5">① Competitive landscape</div>
  <div class="fblock-body">
    <strong>Ocean:</strong> Near-zero direct competition on WeChat mini-games...<br><br>
    <strong>Zombie:</strong> The most crowded theme...
  </div>
  <div class="pill-row">
    <span class="tag tb">Ocean: open</span>
    <span class="tag tc">Zombie: saturated</span>
  </div>
</div>
```
CSS:
```css
.fblock{border-radius:var(--border-radius-md);padding:12px 14px;margin-bottom:10px;border:.5px solid var(--color-border-tertiary)}
.fblock-title{font-size:12px;font-weight:500;margin-bottom:5px;display:flex;align-items:center;gap:6px}
.fblock-body{font-size:12px;color:var(--color-text-secondary);line-height:1.7}
```
- 左边框通过 `style="border-left:3px solid #色值"` 控制，颜色按阶段色体系取（#3266ad 蓝 / #534AB7 紫 / #1D9E75 绿 / #BA7517 琥珀 / #D85A30 珊瑚）
- `fblock-title` 的文字色建议与左边框同色
- 比 `risk-row` 更适合长文本分析，因为 body 不需要压缩在短行内

### 18. 对比表格 (Comparison table)
独立 `<table>` 元素，支持行高亮和单元格颜色标记。适合多维度交叉对比。

```html
<table class="ctable">
  <thead>
    <tr><th>Factor</th><th>🌊 Ocean</th><th>🧟 Zombie</th><th>🌾 Ancient CN</th></tr>
  </thead>
  <tbody>
    <tr><td>WeChat whitespace</td><td class="good">Fully open</td><td class="bad">Saturated</td><td class="mid">Partially open</td></tr>
    <tr class="hl"><td>Female retention</td><td class="good">Strong</td><td class="bad">Weak</td><td class="good">Strongest</td></tr>
  </tbody>
</table>
```
CSS:
```css
.ctable{width:100%;border-collapse:collapse;font-size:12px}
.ctable th{padding:7px 10px;text-align:left;font-weight:500;color:var(--color-text-secondary);font-size:11px;border-bottom:.5px solid var(--color-border-tertiary);background:var(--color-background-secondary)}
.ctable td{padding:7px 10px;border-bottom:.5px solid var(--color-border-tertiary);color:var(--color-text-secondary);vertical-align:top;line-height:1.5}
.ctable tr:last-child td{border-bottom:none}
.ctable tr:nth-child(even) td{background:rgba(128,128,128,.03)}
.hl td{background:rgba(22,140,95,.04)!important;color:var(--color-text-primary)}
.good{color:#1D9E75;font-weight:500}
.mid{color:#BA7517;font-weight:500}
.bad{color:#D85A30;font-weight:500}
```
- 与 `prog-table` 的差别：原生 `<table>` 支持 `colspan`/`rowspan`/表头分组，`prog-table` 的 CSS grid 不支持
- `hl` 行高亮（绿色底色），`good`/`mid`/`bad` 单元格级颜色编码
- `nth-child(even)` 斑马纹辅助阅读
- 适合多列对比表，当列数 ≥ 4 时优先用此组件

### 19. 图片+提示词卡片 (Shot card with image + copy button)

用于展示游戏/产品画面截图、提示词、提供复制按钮的复合卡片。左图右文布局，图片区固定 280px 宽，文字区自适应撑满。**排版约束：图片和提示词区必须视觉对称，左右比例约 35:65，整体美观易读。**

#### HTML 结构

```html
<div class="shot-card">
  <div class="shot-img">
    <img src="images/s1.png" alt="S1 主视觉" loading="lazy">
  </div>
  <div class="shot-body">
    <div class="shot-hd">
      <span class="shot-tag">S1</span>
      <span class="shot-name">主视觉 KV</span>
    </div>
    <div class="shot-prompt-wrap">
      <div class="shot-prompt" id="prompt-S1">image generation prompt text here...</div>
      <button class="copy-btn" id="copy-S1" onclick="copyPrompt('S1')">📋 Copy</button>
    </div>
  </div>
</div>
```

#### 无图片时的占位框

```html
<div class="shot-img">
  <div class="shot-placeholder">
    <div class="ph-icon">🖼️</div>
    <div class="ph-label">S1</div>
    <div class="ph-name">主视觉 KV</div>
  </div>
</div>
```

#### CSS（含图片+占位两套样式，区分横竖版）

```css
/* Shot card — left image + right prompt */
.shot-card{display:flex;gap:16px;padding:14px 16px;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);background:var(--color-background-primary);margin-bottom:12px;align-items:flex-start}
/* 竖版图 (9:16) — 280px 宽 */
.shot-img{flex-shrink:0;width:280px;align-self:stretch;display:flex;align-items:center}
/* 横版图 (16:9) — 400px 宽，给概念图/KV更多展示空间 */
.shot-img-wide{flex-shrink:0;width:400px;align-self:stretch;display:flex;align-items:center}
.shot-img img,.shot-img-wide img{width:100%;height:auto;display:block;border-radius:var(--border-radius-md);border:.5px solid var(--color-border-tertiary);object-fit:contain;max-height:360px}
.shot-body{flex:1;min-width:0;display:flex;flex-direction:column}
.shot-hd{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.shot-tag{font-size:10px;font-weight:500;padding:1px 5px;border-radius:3px;background:var(--color-background-secondary);color:var(--color-text-secondary)}
.shot-name{font-size:13px;font-weight:500;color:var(--color-text-primary)}
.shot-prompt-wrap{position:relative;flex:1;display:flex;flex-direction:column}
.shot-prompt{font-size:10px;color:var(--color-text-tertiary);background:var(--color-background-secondary);padding:8px 10px;border-radius:var(--border-radius-md);line-height:1.6;font-family:SFMono-Regular,Consolas,monospace;word-break:break-word;max-height:140px;overflow-y:auto;margin-bottom:6px;white-space:pre-wrap;flex:1}
.copy-btn{font-size:10px;padding:4px 10px;border-radius:3px;border:.5px solid var(--color-border-tertiary);background:var(--color-background-primary);color:var(--color-text-secondary);cursor:pointer;font-family:inherit;align-self:flex-start}
.copy-btn:hover{background:var(--color-background-secondary);color:var(--color-text-primary)}
.copy-btn.copied{background:#E1F5EE;color:#085041;border-color:#1D9E75}

/* Shot placeholder — same dimensions as image area */
.shot-placeholder{width:280px;height:180px;background:var(--color-background-secondary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.ph-icon{font-size:28px}
.ph-label{font-size:10px;font-weight:500;color:var(--color-accent)}
.ph-name{font-size:11px;color:var(--color-text-secondary)}
```

#### 排版约束（生成 HTML 时强制遵守）

| 约束 | 说明 |
|------|------|
| **竖版图 (9:16)** | 使用 `.shot-img`，固定 280px 宽，适用于手游截图 |
| **横版图 (16:9)** | 使用 `.shot-img-wide`，固定 400px 宽，适用于 KV/概念图/场景图 |
| **自动判断** | 根据 `prompts.jsonl` 中每条 shot 的 aspect_ratio 或 `ASPECT RATIO: 16:9` 标记判断横竖 |
| **图片区高度** | 由图片比例自适应，`max-height:360px` 防止过高 |
| **占位框** | 竖版 `.shot-placeholder`(280×180)，横版 `.shot-placeholder-wide`(400×225) |
| **手动补图** | 补图后检查各图片高度是否一致，不一致时用 CSS 约束或 crop |
| **对称性** | 图片区和提示词区视觉平衡，竖版约 35:65，横版约 40:60 |

#### JavaScript (放在 `</body>` 前)

```html
<script>
function copyPrompt(id) {
  var el = document.getElementById('prompt-' + id);
  var btn = document.getElementById('copy-' + id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(function() {
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(function() {
      btn.textContent = '📋 Copy';
      btn.classList.remove('copied');
    }, 2000);
  }).catch(function() {
    btn.textContent = '✗ Failed';
  });
}
</script>
```

**使用场景**：游戏立项报告的画面槽位展示、设计稿评审、提示词库展示。每个卡片需一个唯一 id（如 `prompt-S1`、`copy-S1`）。

**图片路径**：相对于 HTML 文件的相对路径（如 `../images/s1.png`）。懒加载 `loading="lazy"` 优化多图页面性能。无真实图片时用 `.shot-placeholder` 占位框。

## 输出要求

- 有 `templates/base.html` 作为完整起始模板，可直接复制修改，含 CSS 变量预设（body 暖白 `#FAFAF8`、卡片纯白 `#FFFFFF`）和骨架组件
- 输出 **单文件完整HTML**，可直接在浏览器打开
- CSS放在 `<style>` 标签内，放在HTML顶部
- 所有组件CSS一次性声明完，后续直接复用类名
- 区块用 `<!-- SECTION: XXX -->` 注释分隔
- 每个 section 结构：`section-title`（大区段标题）→ 组件内容 → (可选) 用 `sec-label` 做区内小副标题 → (可选) `grid-4`/`grid2`/`grid3` 补充细节
- grid-4（四等分指标卡）、grid2（双列卡片）、grid3（三列卡片/趋势卡）是标准栅格，优先使用
- 字号不做响应式（桌面文档优先），如需自适应加 `clamp()` 即可