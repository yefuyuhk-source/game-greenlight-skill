# M7 HTML 报告生成指南

## 标准流程（强制决策树）

> ⚠️ **铁律**：此决策树不可跳过。agent 必须按顺序执行每一步，禁止以"省事"为由跳过分支 A 直接使用 `md_to_html.py`。

### 入口：检测设计后端

```bash
python scripts/check_design_backend.py --json
```

读取输出的 `backend` 和 `modern_minimal_available` 字段，走向对应分支。

---

### ◆ 分支 A：modern-minimal-html 可用

#### A-1：加载 modern-minimal-html skill

```bash
skill_view('modern-minimal-html')
```

读取 SKILL.md 中的 19 种组件 HTML/CSS 模板全文。**禁止跳过此步**——不加载 skill 就不知道组件的确切 HTML 结构和 CSS 类名。

#### A-2：生成设计 Brief

```bash
python scripts/build_html_brief.py /path/to/project --output /path/to/project/report/html_design_brief.md
```

输出文件包含：
- 项目上下文（题材、玩法、美术风格、目标用户）
- 灯号和证据充分度
- 关键画面的完整提示词 JSON
- 设计目标约束

#### A-3：手写 HTML（禁止调用 md_to_html.py）

根据 `html_design_brief.md` + `report/report.md` + modern-minimal-html 的 19 种组件，**手写**完整的 `report/report.html`。

**关键约束**：
- 标题只写项目名称（如"小妖的洞天"），不加"游戏立项方向内部讨论报告"后缀
- 使用 modern-minimal-html 的 CSS 变量体系和 19 种组件模块
- 白底、0.5px 细边框、无阴影、高密度排版
- **Shot card 排版**：竖版图(9:16)用 `.shot-img` 280px，横版图(16:9)用 `.shot-img-wide` 400px，根据 prompts.jsonl 的 aspect_ratio 自动区分
- 所有关键画面均为占位时，展示清晰占位框 + 完整提示词 + 复制按钮
- HTML 内联 CSS/JS，不依赖外部资源
- 表格优先，不做无意义图表

#### A-4：更新 project_state.json

```json
{
  "report": {
    "md_path": "report/report.md",
    "html_path": "report/report.html",
    "design_style": "modern-minimal",
    "html_method": "modern-minimal-html (high-fidelity)",
    "html_regeneration": "2026-05-28T14:00+08:00"
  }
}
```

#### A-5：验证清单

- [ ] 确认 `report.html` 中使用了 `--color-text-primary` 等 CSS 变量（而非硬编码色值）
- [ ] 确认至少使用了以下组件：标题区(3) + 关键指标卡(12) + 趋势卡片(14) + 对比表格(18) + 进度网格表(5) + 风险矩阵(9) + 流程弧(4) + Shot card(19)
- [ ] Shot card div 平衡验证：每个 card 的 `<div>` 数 == `</div>` 数
- [ ] Shot card 数量 == 9（或实际 shot 数量），用 `grep -n "shot-card" report.html` 确认
- [ ] 竖版图用 `.shot-img`(280px)，横版图用 `.shot-img-wide`(400px)
- [ ] 无生成图时用 `.shot-placeholder` 占位框 + 完整提示词 + Copy 按钮
- [ ] `m7-html-generation.md` 的 8 条 Pitfall 全部过一遍

---

### ◆ 分支 B：modern-minimal-html 不可用

#### B-1：走兜底

```bash
python scripts/md_to_html.py /path/to/project/report/report.md /path/to/project/report/report.html --prompts /path/to/project/images/prompts.jsonl
```

#### B-2：更新 project_state.json

```json
{
  "report": {
    "md_path": "report/report.md",
    "html_path": "report/report.html",
    "design_style": "structured-card",
    "html_method": "md_to_html.py (fallback)"
  }
}
```

## 设计风格（modern-minimal-html 体系）

modern-minimal-html 是单一风格体系（白底 + 细框 + 高密度），通过调色板和字体适配不同题材：

| 题材关键词 | 文字色 | 强调色 | 字体 |
|-----------|--------|--------|------|
| 国风/水墨/仙侠 | #1a1a1a | #8B4513（棕） | Noto Serif SC |
| 科幻/赛博 | #e6edf3 (深底) | #58a6ff（蓝） | Inter |
| 休闲/治愈 | #1a1a1a | #4a9e6b（绿） | Noto Sans SC |
| 二次元/动漫 | #1a1a1a | #e04080（粉） | Noto Sans SC |
| 默认通用 | #1a1a1a | #3266ad（蓝） | -apple-system |

> 所有主题共用 modern-minimal-html 的 CSS 变量体系和组件模块，仅调色板和字体不同。

## 组件选用指南

modern-minimal-html 提供 19 种组件，立项报告常用：

| 组件 | 编号 | 用途 |
|------|------|------|
| 标题区 | 3 | 报告首屏主标题 |
| 大区段标题 | 1 | 各章节分隔 |
| 进度网格表 | 5 | 候选评分对比、系统架构 |
| 对比表格 | 18 | 竞品对比、假设验证方法 |
| 关键指标卡 | 12 | 市场信号、核心数据 |
| 趋势卡片 | 14 | 趋势分析、方向信号 |
| 评分点阵 | 16 | 维度评分可视化 |
| 风险矩阵 | 9 | 注意事项、待验证假设 |
| 流程弧 | 4 | 核心玩法循环 |
| 双列卡片 | 6 | 并列对比内容 |
| **图片+提示词卡片** | **19** | **关键画面展示，横竖版自适应** |

## Pitfalls

### 1. Subagent 可能只完成 Junior pass

**现象**：delegate_task 启动的 subagent 可能只输出设计假设，不生成完整 HTML。

**原因**：subagent 遵循 modern-minimal-html 的设计流程，默认先展示假设等确认。

**解决**：
- 时间敏感时，直接在主会话中生成 HTML，不要 delegate
- 如果 subagent 停在假设阶段，明确指令"请继续生成完整 HTML"

### 2. 标题冗余

HTML 首屏主标题只保留项目名称，不加后缀。

### 3. 关键画面无生成图

所有 `generated_image` 为 `null` 时：
- 竖版图 (9:16) 用 `.shot-placeholder`（280×180px）
- 横版图 (16:9) 用 `.shot-placeholder-wide`（400×225px）
- 下方展示完整提示词
- 提示词区域带"复制"按钮，支持一键复制到剪贴板
- 不要编造图片

### 4. Shot card 排版失衡

**现象**：手动补图或自动生图后，HTML 报告中的图片+提示词卡片排版不协调——图片过小、左右不对称、横竖版混合时高度参差。

**原因**：旧版 shot card CSS 图片区固定 200px，未区分横竖版。

**解决**：
- 竖版图 (9:16, mobile_screenshot) → `.shot-img`（280px）
- 横版图 (16:9, concept_allowed) → `.shot-img-wide`（400px）
- 根据 `prompts.jsonl` 中 `ASPECT RATIO: 16:9` 标记自动判断
- 重新生成 HTML 时检查 modern-minimal-html skill 组件 19 是否已更新到最新版

### 5. modern-minimal-html 可用时禁止走兜底（决策树强化）

**现象**：`check_design_backend.py --json` 返回 `modern-minimal-html` 可用，但 AI 助手为省事直接调用 `md_to_html.py` 兜底脚本，产出的 HTML 质量远低于 modern-minimal-html 原生构建。

**铁律**：检测到 `modern-minimal-html` 可用时，**禁止使用 `md_to_html.py`**。必须执行分支 A 的完整步骤：
1. `skill_view('modern-minimal-html')` 加载 skill
2. `python scripts/build_html_brief.py ...` 生成设计 brief
3. 根据 19 种组件的 HTML/CSS 模板手写 HTML

**根因**：agent 看到"检测后端→有则用它→没有则兜底"的描述时，倾向于选择路径最短的选项（兜底脚本一行命令）。决策树结构将分支 A 拆成 5 个显式子步骤，agent 无法跳过装载 skill + 手写 HTML 的环节。

`md_to_html.py` 仅在后端返回 `structured-html` 时使用（分支 B）。

### 6. 同步多环境 Skill

更新 game-greenlight 时，需同步到：
- Hermes: `~/.hermes/skills/game-greenlight/`
- Claude Code: `~/.claude/skills/game-greenlight/`

同步内容：`SKILL.md` + `references/` 目录下所有文件 + `scripts/` 目录下所有文件。

### 7. Shot card 生成后必须验证 div 结构

**现象**：用 Python f-string 或模板批量生成 shot card HTML 后，浏览器中图片与提示词区分离——
`shot-body` 被挤出 `shot-card` 之外，排版完全错乱。

**原因**：模板字符串中多余的 `</div>` 提前关闭了 `shot-card`。例如：

```html
<!-- 错误：第2行多了 </div>，shot-card 提前关闭 -->
<div class="shot-card">
  <div class="shot-img"><img src="s3.png"></div>
  </div>  <!-- ← 这个提前关闭了 shot-card -->
  <div class="shot-body">...</div>
```

**解决**：
1. 生成后立即对每个 card 做 div 平衡验证：`opens = card.count('<div')`, `closes = card.count('</div>')`，断言相等
2. 每个 card 应包含 1 个 `shot-card` + 1 个 `shot-img`/`shot-img-wide` + 1 个 `shot-body` + 1 个 `shot-hd` + 1 个 `shot-prompt-wrap`
3. 用 `grep -n "shot-card" report.html` 确认 card 数量 == 9（或实际 shot 数量）
4. 额外检查：`shot-body` 是否紧跟在 `shot-img`/`shot-img-wide` 的 `</div>` 之后（中间不应有其他闭合标签）

### 8. 固定品类 art style 并不安全

**现象**：项目属于 14 个固定品类之一（如「模拟经营」），`build_prompts.py --context-only` 生成的 `ART STYLE` / `COLOR PALETTE` / `UI AESTHETIC` 看似正确——
但实际是品类的**默认值**（如 warm/cozy/pastel/田园风），与项目 `concept.fields.art_style`（如 Q版微恐暗黑风）完全不同。

**原因**：`build_prompts.py` 从 `category_prompts.yaml` 加载品类默认 art style，不读取 `concept.fields`。即使是固定品类，默认值也可能与项目实际方向冲突。

**解决**：生成 prompts.jsonl 后**必须逐条检查**这三项是否匹配 `shotlist.md` 和 `concept.fields.art_style`。不匹配时按 `references/m5-hybrid-category-fix.md` §步骤 2 手动替换所有 shot 的这三个字段。不要因为项目在 14 个品类中就跳过检查。

