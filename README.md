# game-greenlight-skill

**Internal direction-screening assistant for game ops/designers — 游戏立项方向筛选辅助工具**

## 定位

这是一个"方向筛选辅助器"，不是"立项决策器"。帮助运营和策划从模糊想法收敛到一个值得继续讨论验证的方向，并写清楚"为什么可能成立"和"还要验证什么"。

### 硬约束
- 不做立项决策、制作成本评估、团队能力评估、政策风险定性、商业模式或 ROI 测算
- 制作成本、团队能力、政策风险、商业模式风险不参与评分，只能作为注意事项
- 默认产出是 Markdown / HTML 文件，不做 Web 应用、按钮、画廊或交互组件
- 所有项目产出写入 workspace，不写入 Skill 包

## 工作流程 (M1→M8)

| 里程碑 | 内容 | 产出 |
|--------|------|------|
| **M1** | 需求采集 | 需求文档 |
| **M2** | 证据调研 | 联网调研笔记 |
| **M3** | 选题推荐 | 加权评分矩阵 |
| **M4** | 立项初案 | 立项方向说明书 |
| **M5** | 画面提示词 | 出图 prompt 包 |
| **M6** | 视频分镜 | 分镜脚本 + 视频 |
| **M7** | 内部报告 | HTML 简报 |
| **M8** | 风格迭代 | 风格变体集 |

## 项目结构

```
game-greenlight-skill/
├── SKILL.md                  # 核心定义：流程、规则、约束
├── references/               # 参考文档（9份）
│   ├── workflow.md           #   流程总述
│   ├── research_protocol.md  #   调研协议
│   ├── scoring_rubric.md     #   评分准则
│   ├── state_schema.md       #   状态契约
│   ├── report_template.md    #   报告模板
│   ├── genre_taxonomy.md     #   品类分类
│   ├── design_styles.md      #   美术风格库
│   ├── image_prompt_library.md  # 提示词库
│   └── storyboard_patterns.md   # 分镜模式
├── scripts/                  # 可用脚本（10个）
│   ├── state.py              #   状态管理
│   ├── search_web.py         #   联网搜索（Tavily）
│   ├── fetch_url.py          #   网页抓取
│   ├── md_to_html.py         #   Markdown → HTML
│   ├── build_process_report.py   # 过程报告
│   ├── list_outputs.py       #   产物路径列表
│   ├── asset_index.py        #   资产索引
│   ├── gen_image.py          #   出图
│   ├── gen_video_seedance.py #   视频生成
│   └── ffmpeg_concat.py      #   视频拼接
├── assets/                   # 资源文件
│   ├── prompt_snippets/      #   提示词片段
│   └── style_presets/        #   风格预设
├── agents/                   # Agent 配置
│   └── openai.yaml           #   OpenAI GPT 配置
├── tests/                    # 测试套件
│   └── test_scripts.py       #   核心脚本测试（6/6通过）
└── .gitignore
```

## 使用方式

1. 在 AI Agent（Claude Code / OpenAI Codex / Hermes）中加载此 Skill
2. 首次启动时确认 workspace 路径，默认 `~/game-greenlight-workspace`
3. 项目产出写入 `{workspace}/outputs/{project_id}/`
4. 每步开始前读取 `project_state.json`，结束后写回
5. 联网搜索依赖 Tavily API key

### 依赖
- Python 3.10+
- Tavily API Key（搜索脚本使用）
- 可选：ffmpeg（视频拼接）、ComfyUI / Seedance（视频生成）

## 设计原则

- **证据驱动**：每个方向必须有可追溯的市场/用户数据支撑
- **边界收敛**：从 3-5 个方向逐步收敛到 1 个主推方向
- **状态持久化**：使用 `state.py` 管理项目状态，支持中断恢复
- **可验证**：每步产出明确，支持回溯和审查

## 创建背景

由游戏营销策划 yefuyuhk-source 设计，面向游戏运营/策划团队的日常立项方向筛选场景。2026年5月完成初始版本开发。