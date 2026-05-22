# 兜底 HTML 报告设计风格库

本文件只用于当前环境没有 `huashu-design` skill 时的结构化 HTML 兜底输出。

M7 HTML 的主路径是：检测到 `huashu-design` 时，直接调用该 skill 读取 `report/huashu_design_brief.md`、`report/report.md`、`images/prompts.jsonl` 和已生成图片，完成定制排版并产出 `report/report.html`。

若当前环境没有 `huashu-design`，才使用 `scripts/md_to_html.py` 的内置卡片式布局。本文件从 huashu-design 的 20 种设计哲学中精选 8 种，作为兜底 HTML 的 CSS 变量库，按游戏类型自动匹配报告视觉风格。

## 游戏类型 → 设计风格映射

| 游戏题材/美术风格 | 设计风格 | 设计师/机构 | 流派 |
|---|---|---|---|
| 赛博朋克 / 科幻 / 近未来 | ash-thorp | Ash Thorp 赛博诗意 | 实验先锋派 |
| 废土 / 末日 / 末世生存 | territory-studio | Territory Studio FUI | 实验先锋派 |
| 国风 / 武侠 / 仙侠 / 东方 | neo-shen | Neo Shen 东方光影诗 | 东方哲学派 |
| 二次元 / 动漫 / 卡通 | sagmeister | Sagmeister & Walsh 快乐极简 | 极简主义派 |
| 中世纪 / 魔幻 / 暗黑 | irma-boom | Irma Boom 书籍建筑 | 东方哲学派 |
| 极简 / 休闲 / 治愈 | kenya-hara | Kenya Hara 空的设计 | 东方哲学派 |
| 经营 / 模拟 / 策略 / 数据 | fathom | Fathom 科学叙事 | 信息建筑派 |
| 恐怖 / 微恐 / 悬疑 | muller-brockmann | Müller-Brockmann 瑞士网格 | 极简主义派 |
| **默认回退** | pentagram | Pentagram 信息建筑 | 信息建筑派 |

## 风格 CSS 变量定义

### ash-thorp — 赛博诗意

```
:root {
  --bg: #0d1117;
  --bg-soft: #161b22;
  --card: rgba(22, 27, 34, 0.94);
  --card-solid: #161b22;
  --ink: #e6edf3;
  --muted: #8b949e;
  --line: #21262d;
  --accent: #f0883e;
  --accent-2: #58a6ff;
  --accent-soft: rgba(240, 136, 62, 0.12);
  --shadow: 0 18px 60px rgba(0, 0, 0, 0.40);
  --font-display: "Orbitron", ui-sans-serif;
  --font-body: "IBM Plex Sans", ui-sans-serif;
  --radius-card: 12px;
  --radius-section: 16px;
}
```

### territory-studio — FUI 工业美学

```
:root {
  --bg: #0a0e14;
  --bg-soft: #10161e;
  --card: rgba(16, 22, 30, 0.95);
  --card-solid: #10161e;
  --ink: #c9d1d9;
  --muted: #6e7681;
  --line: #1c2333;
  --accent: #e6b450;
  --accent-2: #39d353;
  --accent-soft: rgba(230, 180, 80, 0.10);
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.50);
  --font-display: "Share Tech Mono", monospace;
  --font-body: "IBM Plex Mono", monospace;
  --radius-card: 4px;
  --radius-section: 8px;
}
```

### neo-shen — 东方光影诗

```
:root {
  --bg: #f7f4f0;
  --bg-soft: #f0ece5;
  --card: rgba(255, 255, 255, 0.88);
  --card-solid: #ffffff;
  --ink: #1a1a1a;
  --muted: #78716c;
  --line: #e7e0d8;
  --accent: #c04a1a;
  --accent-2: #1e3a5f;
  --accent-soft: rgba(192, 74, 26, 0.08);
  --shadow: 0 12px 48px rgba(0, 0, 0, 0.06);
  --font-display: "Noto Serif SC", serif;
  --font-body: "Noto Sans SC", ui-sans-serif;
  --radius-card: 16px;
  --radius-section: 24px;
}
```

### sagmeister — 快乐极简

```
:root {
  --bg: #faf8ff;
  --bg-soft: #f3f0ff;
  --card: rgba(255, 255, 255, 0.90);
  --card-solid: #ffffff;
  --ink: #1a1523;
  --muted: #6e6480;
  --line: #e4dff0;
  --accent: #ff4d6a;
  --accent-2: #7c3aed;
  --accent-soft: rgba(255, 77, 106, 0.08);
  --shadow: 0 16px 48px rgba(0, 0, 0, 0.06);
  --font-display: "Fraunces", serif;
  --font-body: "Inter", ui-sans-serif;
  --radius-card: 20px;
  --radius-section: 28px;
}
```

### irma-boom — 书籍建筑

```
:root {
  --bg: #f5f0e8;
  --bg-soft: #ede4d6;
  --card: rgba(255, 255, 255, 0.85);
  --card-solid: #ffffff;
  --ink: #1c1814;
  --muted: #6b5e4e;
  --line: #d9ccb8;
  --accent: #b5343a;
  --accent-2: #d4843a;
  --accent-soft: rgba(181, 52, 58, 0.08);
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  --font-display: "Playfair Display", serif;
  --font-body: "Source Serif 4", serif;
  --radius-card: 8px;
  --radius-section: 12px;
}
```

### kenya-hara — 空的设计

```
:root {
  --bg: #fbfaf8;
  --bg-soft: #f5f3ef;
  --card: rgba(255, 255, 255, 0.92);
  --card-solid: #ffffff;
  --ink: #1a1a1a;
  --muted: #9ca3af;
  --line: #e8e5e0;
  --accent: #78716c;
  --accent-2: #a8a29e;
  --accent-soft: rgba(120, 113, 108, 0.06);
  --shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
  --font-display: "Noto Serif JP", serif;
  --font-body: "Noto Sans JP", ui-sans-serif;
  --radius-card: 0px;
  --radius-section: 0px;
}
```

### fathom — 科学叙事

```
:root {
  --bg: #f8fafc;
  --bg-soft: #f1f5f9;
  --card: rgba(255, 255, 255, 0.94);
  --card-solid: #ffffff;
  --ink: #0f172a;
  --muted: #64748b;
  --line: #e2e8f0;
  --accent: #2563eb;
  --accent-2: #0891b2;
  --accent-soft: rgba(37, 99, 235, 0.08);
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  --font-display: "Inter Tight", ui-sans-serif;
  --font-body: "Inter", ui-sans-serif;
  --radius-card: 12px;
  --radius-section: 16px;
}
```

### muller-brockmann — 瑞士网格

```
:root {
  --bg: #1a1a1a;
  --bg-soft: #242424;
  --card: rgba(36, 36, 36, 0.94);
  --card-solid: #242424;
  --ink: #e5e5e5;
  --muted: #737373;
  --line: #333333;
  --accent: #ef4444;
  --accent-2: #a3a3a3;
  --accent-soft: rgba(239, 68, 68, 0.08);
  --shadow: 0 4px 20px rgba(0, 0, 0, 0.30);
  --font-display: "Helvetica Neue", ui-sans-serif;
  --font-body: "Helvetica Neue", ui-sans-serif;
  --radius-card: 0px;
  --radius-section: 0px;
}
```

### pentagram — 信息建筑（默认回退）

```
:root {
  --bg: #f6faf8;
  --bg-soft: #eef8f3;
  --card: rgba(255, 255, 255, 0.92);
  --card-solid: #ffffff;
  --ink: #10201a;
  --muted: #607268;
  --line: #dbe9e2;
  --accent: #16c784;
  --accent-2: #35a7ff;
  --accent-soft: rgba(22, 199, 132, 0.10);
  --shadow: 0 18px 60px rgba(20, 78, 55, 0.10);
  --font-display: "Inter Display", ui-sans-serif;
  --font-body: "Inter", ui-sans-serif;
  --radius-card: 24px;
  --radius-section: 28px;
}
```

## 兜底选择逻辑

1. 从 `project_state.inputs.art_style` 或 `project_state.inputs.theme` 提取游戏题材关键词
2. 按「游戏类型 → 设计风格映射」表匹配
3. 若匹配多个，优先选择 `art_style` 匹配项
4. 无匹配时回退为 `pentagram`
5. 调用 `scripts/md_to_html.py --style auto --state project_state.json ...`
6. 将脚本输出的风格名写入 `project_state.report.design_style`
7. 在对话中说明“HTML 为结构化兜底版，非 huashu-design 定制版”

## 图表策略

不要默认把所有数值表格都转成图表。只有当报告作者明确设计“图表模块”或专门可视化占位时，才生成图表。v1 HTML 转换器默认只把 Markdown 表格渲染为清晰表格卡片，避免无意义图表干扰阅读。

## 与 huashu-design 的关系

本文件不是 huashu-design 的替代实现，也不用于限制 huashu-design 的排版。它只保证没有 huashu-design 的环境仍能生成可读、结构化、卡片式的 HTML 报告。

完整设计方向顾问流程、版式选择、视觉语言和高保真 HTML 生成，仍通过 huashu-design skill 调用。
