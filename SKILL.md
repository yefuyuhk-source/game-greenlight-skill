---
name: game-greenlight
description: Internal direction-screening assistant for game ops/designers. Use when users ask for 游戏立项, 方向筛选, 选题分析, greenlight, or 立项报告. Helps narrow vague game ideas to one direction worth deeper validation in 20-30 minutes; does not produce production feasibility, team-fit, policy-risk, commercial-model, or ROI verdicts.
---

# 工具定位

> **v0.9.0** · 2026-05-28

## Changelog

### v0.9.0 (2026-05-28)
- **M7 决策树重构**：将 HTML 生成的铁律从描述+警告改为强制序列化步骤。agent 必须先运行 `check_design_backend.py --json`、读取结果、按分支执行显式步骤——加载 modern-minimal-html skill → 读取 19 种组件 → 手写 HTML。`md_to_html.py` 仅在分支 B 中自动触发。禁止跳过 skill 加载或自行捏造组件。
- **vendor 补齐**：`vendor/modern-minimal-html/` 补齐 `references/` 和 `templates/` 目录，支持无 Hermes 安装时的 skill 加载（通过 `read_file('vendor/modern-minimal-html/SKILL.md')` 兜底）
- **分支 A 增加 vendor 兜底路径**：`skill_view` 失败时从仓库 vendor 读取 SKILL.md

### v0.8.9 (2026-05-27)
- **m7-html-generation.md**：新增 Pitfall 7「Shot card 生成后必须验证 div 结构」（含 div 平衡验证 + grep 检查清单）和 Pitfall 8「固定品类 art style 并不安全」（即使是 14 个固定品类，默认 art style 也可能与项目实际方向冲突，必须逐条检查）

### v0.8.8 (2026-05-27)
- **M7 HTML 生成铁律**：`references/m7-html-generation.md` 新增 Pitfall 5「modern-minimal-html 可用时禁止走兜底」。`md_to_html.py` 仅在后端检测返回 `structured-html` 时才使用——检测到 `modern-minimal-html` 时必须读取 `html_design_brief.md` + 调用 modern-minimal-html skill 原生构建，不允许以省事为由走兜底。
- **M2 Tavily 快速来源**：`references/tavily-setup.md` 新增一键 source 命令，当 key 仅存在于 `~/.tavily/config.json` 时可直接执行
- **M5 concept.fields 必填清单**：`references/workflow.md` 新增 M5 前置检查表，列出 `concept.fields` 必须填写的 8 个字段（name, name_en, main_character, key_scene, theme_keywords, art_style, world_context, target_audience），缺一则 world_context anchor 断裂

### v0.8.7 (2026-05-27)
- **M3 受众分析陷阱**：`references/scoring_rubric.md` 新增「受众分析陷阱」章节，禁止将品类惯例受众直接映射到具体方向。品类 × 题材 × 平台三者受众交叉需来自 M2 来源数据，不可凭 stereotype 推断。

### v0.8.6 (2026-05-26)
- **逻辑修正**：`fill_template` 仅在所有占位符缺失时才使用 fallback，修复部分变量有值时被整体替换的 bug
- **逻辑修正**：`state.py` SKILL_VERSION 从 `0.3.1` 更新为 `0.8.5`
- **逻辑修正**：`gen_video_seedance.py` 降级判断改用 `args.provider`，使显式传参行为一致
- **安全修复**：`fetch_url.py` 新增 URL scheme 白名单 + 内网 IP 过滤（防 SSRF）
- **安全修复**：`gen_image.py` banana provider 异常信息中过滤 API Key 明文
- **安全修复**：`ffmpeg_concat.py` 路径单引号转义 + 临时文件清理
- **健壮性**：`build_html_brief.py` 空报告不再 IndexError；`asset_index.py` 非法 JSON 友好提示
- **维护**：品类数量注释 13→14 全项目同步；CI 增加 Python 3.14 矩阵
- **测试**：新增 `test_safety_fixes.py`（12 测试），覆盖所有修复点

### v0.8.5 (2026-05-27)
- **安全修复**：所有参考文件删除 `export KEY=xxx`/`KEY=sk-xxx` 等含 key 配置示例，改为仅描述「从环境变量读取」
- **安全修复**：`gen_image.py` / `search_web.py` 异常输出中过滤 Authorization 头（替换 `Bearer {key}` → `Bearer ***`）
- **SKILL.md**：新增硬约束「禁止打印/回显/命令行传递 API Key」

### v0.8.4 (2026-05-27)
- **测试修复**：品类计数 13→14（v0.8.0 新增「RPG养成」后未同步）、vendor 降级测试适配
- **CHANGELOG.md**：补全 v0.8.0–v0.8.3 历史记录
- **check_design_backend.py**：新增 vendor fallback 逻辑——优先使用系统全局安装的 modern-minimal-html，找不到时自动从仓库 `vendor/` 加载
- **m7-html-generation.md**：Pitfall 4 "Shot card 排版失衡" 排查指南

### v0.8.2 (2026-05-26)
- **Shot card 排版**：关联 modern-minimal-html 组件 19 更新，横版图(16:9)用 `.shot-img-wide` 400px，竖版图(9:16)用 `.shot-img` 280px，根据 ASPECT RATIO 自动区分
- **m7-html-generation.md**：Pitfall 4 新增 "Shot card 排版失衡" 排查指南，占位框区分横竖版尺寸
- **hybrid-category-mapping.md**：新增实例二「RPG养成+地府探索」+ M5 修正流程（通用），覆盖杂交品类 ART STYLE 全量替换、S7-S9 槽位名修正、验证清单
- **chinese-folklore-minigame-landscape.md**：新增「Q版微恐方向」章节，귀판오분전 案例 + 平台合规注意事项
- **build_html_brief.py**：传递 aspect_ratio 到 design brief，确保 HTML 生成时正确选类

### v0.8.1 (2026-05-26)
- **M7 补图流程**：用户手动补充生成图片后，需更新 report.html 中 shot card 的占位框为 `<img src="../images/sN.png">`，见本步末尾新增的补图说明

### v0.8.0 (2026-05-26)
- **新增品类**：`RPG养成` 加入 category_prompts.yaml（第14个品类），含装备/技能系统、关卡/副本选择、角色属性面板三张替换槽位
- **品类映射表**：shot_taxonomy.md 追加 RPG / ARPG（养成向）条目
- **修复**：category_prompts.yaml 末尾补充换行符

### v0.7.0 (2026-05-25)
- M5 新增双路径 `--context-only`（推荐）和 `--legacy`
- gen_image.py 新增 toapis31 provider（Gemini 3.1 Flash）
- toapis-image-api.md 合并为统一参考

这是一个"方向筛选辅助器"，不是"立项决策器"。它帮助运营和策划从模糊想法收敛到一个值得继续讨论验证的方向，并写清楚“为什么可能成立”和“还要验证什么”。

硬约束：

- 不做立项决策、制作成本评估、团队能力评估、政策风险定性、商业模式或 ROI 测算。
- 制作成本、团队能力、政策风险、商业模式风险不参与 M3 评分，只能作为注意事项。
- 默认产出是 Markdown / HTML 文件，不做 Web 应用、按钮、画廊或交互组件。
- 所有项目产出写入 workspace，不写入 Skill 包。
- **API Key 安全**：禁止打印、回显、或通过命令行参数传递 `TOAPIS_API_KEY`、`TAVILY_API_KEY` 等敏感环境变量值。仅通过 `os.environ` 读取，且异常输出中必须替换 `Bearer {key}` 为 `Bearer ***`。

# 工作区

首次启动时确认 workspace 路径，默认 `~/game-greenlight-workspace`。项目产出路径：

`{workspace}/outputs/{project_id}/`

每步开始前读取 `project_state.json`，结束后写回。恢复旧项目时，先运行或参考：

```bash
python scripts/state.py summary {workspace}/outputs/{project_id}/project_state.json
```

每步结束后，必须在对话回复中保留本步产出的文件路径，方便用户直接打开或定位。可运行：

```bash
python scripts/list_outputs.py {workspace}/outputs/{project_id} --step Mx --markdown
```

# 主流程

1. M1 需求采集与关键词生成：见 `references/workflow.md`。
2. M2 证据驱动调研：必须遵守 `references/research_protocol.md`。
3. M3 选题推荐：必须遵守 `references/scoring_rubric.md`。⚠️ 特别注意受众分析陷阱：禁止凭「品类=某性别」做推断，必须以 M2 平台级人口数据交叉验证。
4. M4 立项初案：生成 `concept.md`，按 `references/shot_taxonomy.md` 槽位规则生成 `shotlist.md`（6 固定核心 + 2~3 品类替换 + 1 可选社交），填写四条 `direction_hypotheses`。
5. M5 关键画面提示词：
   - **推荐路径**（LLM 原生生成）：
     a. 运行 `python scripts/build_prompts.py --project {project_dir} --category <品类名> --context-only`
        → 加载三层 YAML 知识库 + project_state 变量 → 为每条 shot 生成结构化上下文卡片
        → `prompt_v1` 字段存储上下文卡片（供 concept-prompt-architecture skill 消费），metadata + negative 照常生成
        → 输出 `images/prompts.jsonl`
   - **⚠️ ART STYLE 覆盖问题（所有品类）**：品类默认 `art_style`/`color_palette`/`ui_aesthetic` 可能完全不符合项目实际美术方向（如 模拟经营 默认 warm/cozy/田园 → 项目需要 dark Q版微恐）。即使是 14 个固定品类之一，也必须检查并用项目实际风格覆盖。流程：生成上下文卡片 → 检查 `ART STYLE`/`COLOR PALETTE`/`UI AESTHETIC` 是否匹配 → 不匹配则全部替换 → 再生成 prompt_v2。详见 `references/m5-hybrid-category-fix.md`（该文档对固定品类同样适用）。
   - **⚠️ 固定品类 art style 不匹配**：即使项目属于 14 个固定品类之一，若实际美术方向与品类默认风格差异显著
          （如 模拟经营 默认 warm/cozy/pastel，但项目是 Q版微恐暗黑风），`build_prompts.py --context-only` 生成的
          ART STYLE / COLOR PALETTE / UI AESTHETIC 仍会被品类默认值覆盖。必须在生成 prompt_v2 时用项目实际风格
          替换所有三个字段——不要信任品类默认值，始终以 concept.md 和 shotlist.md 中的美术描述为准。
     b. 调用 `concept-prompt-architecture` skill：
        → 逐条读取 JSONL 中每个 shot 的上下文卡片（prompt_v1）
        → 按 4 层写作法 + 分区策略 + 8 条自检生成高质量英文 prompt
        → 写入 `prompt_v2` 字段，标记 `iteration_tag: "v2"`
     c. 若会话中无法调用 skill，AI 助手可直接基于上下文卡片推理生成（效果略逊但仍优于碎片拼接）
   - **兼容路径**（原有碎片拼接）：
     运行 `python scripts/build_prompts.py --project {project_dir} --category <品类名> --legacy`
     → 完全等同于修改前的行为（碎片拼接 prompt_v1，--polish 输出润色清单）
   - **主题一致性**：
     - 上下文卡片包含 world_context anchor（来自 `prompt_base.yaml` 的 `world_context.template` 展开），保证 S1-S10 统一世界观
     - concept-prompt-architecture 的自检第 7 条（系列感）通过 SERIES CONTEXT 提示进一步强化跨 shot 视觉锚点共享
     - 负向提示词（negative）仍由 build_prompts.py 三层累加生成，不受影响
   - 默认目标是"手游实际画面截图"...
   - 只有主视觉、宣传图、纯氛围场景（`with_ui: false`）允许使用概念图表达
   - **手工写/润色高表现力提示词时**：见 `references/structured-prompt-composition.md`（4-Layer 结构法：Header → Scene Blocks → Detail Fill → MOOD）
   - 用户显式说"开始出图"或配置 `TOAPIS_API_KEY` 后调用：
     ```
     python scripts/gen_image.py --prompts <project>/images/prompts.jsonl --provider toapis --output-dir <project>/images --category <品类名>
     ```
    出图时优先使用 `prompt_v2`（如有），否则用 `prompt_v1`。默认使用 **Gemini 3.1 Flash**，如需回退到 2.5 Flash 用 `--toapis-model gemini-2.5-flash-image-preview`。
  - 对话中返回`images/prompts.jsonl` 与 `project_state.json` 的路径
6. M6 演示视频分镜：默认只生成 `video/storyboard.md`。
7. **M7 内部讨论报告**：按 `references/report_template.md` 汇总为一份 Markdown 立项报告。HTML 输出走以下强制决策树：

   **Step 1：检测后端**
   ```bash
   python scripts/check_design_backend.py --json
   ```
   读取输出中的 `backend` 字段。

   **Step 2：按分支执行**

   ┌─ **分支 A**（`backend = "modern-minimal-html"`）：
   │  1. 加载 modern-minimal-html skill：
   │     a. 优先：`skill_view('modern-minimal-html')`（Hermes 安装版）
   │     b. 兜底：`read_file('vendor/modern-minimal-html/SKILL.md')`（仓库自带的 vendor）
   │     → 读取 19 种组件的 HTML/CSS 模板全文，**禁止跳过**
   │  2. 生成设计 brief：`python scripts/build_html_brief.py <project_dir> --output <project_dir>/report/html_design_brief.md`
   │  3. 读取 `html_design_brief.md` 和 `report/report.md`
   │  4. **手写** `report/report.html`：使用 modern-minimal-html 的 CSS 变量体系 + 19 种组件原生构建，禁止使用 `md_to_html.py`
   │  5. 更新 project_state.json：`design_style: "modern-minimal"`, `html_method: "modern-minimal-html (high-fidelity)"`
   │
   └─ **分支 B**（`backend = "structured-html"`）：
      1. 运行兜底：`python scripts/md_to_html.py <project_dir>/report/report.md <project_dir>/report/report.html --prompts <project_dir>/images/prompts.jsonl`
      2. 更新 project_state.json：`design_style: "structured-card"`, `html_method: "md_to_html.py (fallback)"`

   **验证清单**：
   - [ ] 检查 `report.html` 是否使用了 modern-minimal-html 的 CSS 变量（`--color-text-primary` 等）
   - [ ] Shot card 的 div 平衡验证（`<div>` 数 == `</div>` 数）
   - [ ] 竖版图用 `.shot-img`(280px)，横版图用 `.shot-img-wide`(400px)
   - [ ] 无生成图时用 `.shot-placeholder` 占位框 + 完整提示词 + Copy 按钮
   - [ ] `m7-html-generation.md` 的 8 条 Pitfall 全部过一遍
8. **产物汇总**：M7 完成后运行以下命令展示所有最终产物，包含中文标题与路径：
   ```bash
   python scripts/list_outputs.py {workspace}/outputs/{project_id} --step M7 --markdown
   ```
   输出示例：
   - **立项报告（Markdown）**：`~/game-greenlight-workspace/outputs/xxx/report/report.md`
   - **立项报告（HTML）**：`~/game-greenlight-workspace/outputs/xxx/report/report.html`
   对话回复中保留所有最终产物的绝对路径，供用户直接打开。
   - **🖼️ M7 后补图**：如果用户在 M7 完成后手动将生成图片放入 `images/` 目录（如 `s1.png` ~ `s9.png`），需更新 `report.html` 中 shot card 的占位框为真实 `<img>` 标签。图片路径相对于 HTML 为 `../images/sN.png`。同时提示词卡片和 📋 Copy 按钮保持不变。
9. M8 风格迭代：只在用户对 M5 不满意时进入。

# 判断标签

报告和评分中使用三标签：

- 🟢 已证据支持：至少 1 条来源支持。
- 🟡 AI 推断：基于已知信息合理推演，无直接来源。
- 🔴 待人工验证：关键判断但证据不足。

标签用于评分维度、章节结论、三轴判断和四条 `direction_hypotheses`；不要给每句话贴标签。

# 脚本调用

- 状态：`scripts/state.py`
- 搜索：`scripts/search_web.py`（依赖 `TAVILY_API_KEY` 环境变量。若 key 仅存在于 `~/.tavily/config.json`，用以下命令 source：`export TAVILY_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.tavily/config.json'))['api_key'])")`）
- 抓取：`scripts/fetch_url.py`
- HTML 后端检测：`scripts/check_design_backend.py` — 检测 `modern-minimal-html` skill 是否可用
- HTML 设计 brief：`scripts/build_html_brief.py` — 生成 modern-minimal-html 设计输入
- HTML 兜底转换：`scripts/md_to_html.py`（无 modern-minimal-html 时使用，输出现代极简风结构化卡片布局）
- 产物路径：`scripts/list_outputs.py`
- 资产索引：`scripts/asset_index.py`
- 可选出图：`scripts/gen_image.py` — 支持 `--provider toapis`（Gemini 2.5 Flash）、`--provider toapis31`（Gemini 3.1 Flash）或 `--provider banana`
  - 模型优先级：`--toapis-model` 参数 > `TOAPIS_MODEL` 环境变量 > provider 默认模型
- 可选视频：`scripts/gen_video_seedance.py`、`scripts/ffmpeg_concat.py`

# 失败与降级

当搜索或抓取连续失败 3 次以上：

- `evidence_strength` 强制为 `weak`。
- 禁止绿灯，禁止 8 分以上候选。
- 报告封面提示“本次未能完成联网调研，结论基于模型已知信息”。
- 所有关键判断默认标为 🟡 或 🔴。

# 版本更新

此 skill 托管在 `https://github.com/yefuyuhk-source/game-greenlight-skill`，本地作为 git repo 维护。更新流程：

1. **本地有未提交改动时**：先 `git stash` → `git pull origin main` → `git stash pop`（直接 git pull 会报错 abort）
2. **feature 分支合并到 main**：`git checkout main && git merge origin/<branch> --no-ff` → push
3. **推送前展示改动**给用户确认后再 `git push origin main`
4. **同步其他 skill 目录**：`cd ~/.claude/skills/game-greenlight && git pull origin main`
5. **structured-prompt-composition.md 等参考文件**：如果本地有新增但未跟踪的文件，记得 `git add` 一起提交，不要在多个副本间手动复制

新增 provider（如 gen_image.py 的 `toapis31`）：在 `main()` 中添加 provider 分支，调用 `run_toapis(prompts_path, output_dir, model=...)` 复用同一异步轮询逻辑。模型优先级：`--toapis-model` 参数 > `TOAPIS_MODEL` 环境变量 > provider 默认。

# 暂停 / 回退 / 恢复

- 用户说“暂停”：设置 `status = paused`。
- 用户说“回到 Mx”：读取状态并从该步骤重跑，提醒后续产出需要刷新。
- **M5 前须确认 `project_state.concept.fields` 已填写完整**，必须包含以下 8 个字段，缺一则 `world_context` 世界锚点断裂：
  `name` `name_en` `main_character` `key_scene` `theme_keywords` `art_style` `world_context` `target_audience`
- 任何步骤失败：写入 `errors[]`，不静默继续。
