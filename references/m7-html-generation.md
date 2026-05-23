# M7 HTML 报告生成指南

## 标准流程

### 步骤 1：检测设计后端

```bash
python scripts/check_design_backend.py --json
```

返回值 `modern_minimal_available` 为 `true` 时走定制流程，否则走兜底。

### 步骤 2：生成设计 Brief（有 modern-minimal-html 时）

```bash
python scripts/build_html_brief.py /path/to/project --output /path/to/project/report/html_design_brief.md
```

输出文件包含：
- 项目上下文（题材、玩法、美术风格、目标用户）
- 灯号和证据充分度
- 关键画面的完整提示词 JSON
- 设计目标约束

### 步骤 3：调用 modern-minimal-html 生成 HTML

**关键约束**：
- 标题只写项目名称（如"小妖的洞天"），不加"游戏立项方向内部讨论报告"后缀
- 使用 modern-minimal-html 的 CSS 变量体系和 18 种组件模块
- 白底、0.5px 细边框、无阴影、高密度排版
- 所有关键画面均为占位时，展示清晰占位框 + 完整提示词 + 复制按钮
- HTML 内联 CSS/JS，不依赖外部资源
- 表格优先，不做无意义图表

### 步骤 4：更新 project_state.json

```json
{
  "report": {
    "md_path": "report/report.md",
    "html_path": "report/report.html",
    "design_style": "modern-minimal",
    "html_method": "modern-minimal-html (high-fidelity)",
    "html_regeneration": "2026-05-23T14:00+08:00"
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

modern-minimal-html 提供 18 种组件，立项报告常用：

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
- 每张画面展示占位框 + "图片待生成"文字
- 下方展示完整提示词
- 提示词区域带"复制"按钮，支持一键复制到剪贴板
- 不要编造图片

### 4. 同步多环境 Skill

更新 game-greenlight 时，需同步到：
- Hermes: `~/.hermes/skills/game-greenlight/`
- Claude Code: `~/.claude/skills/game-greenlight/`

同步内容：`SKILL.md` + `references/` 目录下所有文件 + `scripts/` 目录下所有文件。
