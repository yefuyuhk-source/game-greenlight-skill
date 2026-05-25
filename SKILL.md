---
name: game-greenlight
description: Internal direction-screening assistant for game ops/designers. Use when users ask for 游戏立项, 方向筛选, 选题分析, greenlight, or 立项报告. Helps narrow vague game ideas to one direction worth deeper validation in 20-30 minutes; does not produce production feasibility, team-fit, policy-risk, commercial-model, or ROI verdicts.
---

# 工具定位

这是一个“方向筛选辅助器”，不是“立项决策器”。它帮助运营和策划从模糊想法收敛到一个值得继续讨论验证的方向，并写清楚“为什么可能成立”和“还要验证什么”。

硬约束：

- 不做立项决策、制作成本评估、团队能力评估、政策风险定性、商业模式或 ROI 测算。
- 制作成本、团队能力、政策风险、商业模式风险不参与 M3 评分，只能作为注意事项。
- 默认产出是 Markdown / HTML 文件，不做 Web 应用、按钮、画廊或交互组件。
- 所有项目产出写入 workspace，不写入 Skill 包。

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
3. M3 选题推荐：必须遵守 `references/scoring_rubric.md`。
4. M4 立项初案：生成 `concept.md`，按 `references/shot_taxonomy.md` 槽位规则生成 `shotlist.md`（6 固定核心 + 2~3 品类替换 + 1 可选社交），填写四条 `direction_hypotheses`。
5. M5 关键画面提示词：
   - **推荐路径**（LLM 原生生成）：
     a. 运行 `python scripts/build_prompts.py --project {project_dir} --category <品类名> --context-only`
        → 加载三层 YAML 知识库 + project_state 变量 → 为每条 shot 生成结构化上下文卡片
        → `prompt_v1` 字段存储上下文卡片（供 concept-prompt-architecture skill 消费），metadata + negative 照常生成
        → 输出 `images/prompts.jsonl`
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
   - 用户显式说"开始出图"或配置 `TOAPIS_API_KEY` 后调用：
     ```
     python scripts/gen_image.py --prompts <project>/images/prompts.jsonl --provider toapis --output-dir <project>/images --category <品类名>
     ```
     出图时优先使用 `prompt_v2`（如有），否则用 `prompt_v1`
   - 对话中返回 `images/prompts.jsonl` 与 `project_state.json` 的路径
6. M6 演示视频分镜：默认只生成 `video/storyboard.md`。
7. M7 内部讨论报告：按 `references/report_template.md` 汇总为一份 Markdown 立项报告；HTML 输出先检测设计后端（`modern-minimal-html`），有则调用它定制排版，没有时使用内置结构化卡片式 HTML 兜底（`scripts/md_to_html.py`）。
8. **产物汇总**：M7 完成后运行以下命令展示所有最终产物，包含中文标题与路径：
   ```bash
   python scripts/list_outputs.py {workspace}/outputs/{project_id} --step M7 --markdown
   ```
   输出示例：
   - **立项报告（Markdown）**：`~/game-greenlight-workspace/outputs/xxx/report/report.md`
   - **立项报告（HTML）**：`~/game-greenlight-workspace/outputs/xxx/report/report.html`
   对话回复中保留所有最终产物的绝对路径，供用户直接打开。
9. M8 风格迭代：只在用户对 M5 不满意时进入。

# 判断标签

报告和评分中使用三标签：

- 🟢 已证据支持：至少 1 条来源支持。
- 🟡 AI 推断：基于已知信息合理推演，无直接来源。
- 🔴 待人工验证：关键判断但证据不足。

标签用于评分维度、章节结论、三轴判断和四条 `direction_hypotheses`；不要给每句话贴标签。

# 脚本调用

- 状态：`scripts/state.py`
- 搜索：`scripts/search_web.py`
- 抓取：`scripts/fetch_url.py`
- HTML 后端检测：`scripts/check_design_backend.py` — 检测 `modern-minimal-html` skill 是否可用
- HTML 设计 brief：`scripts/build_html_brief.py` — 生成 modern-minimal-html 设计输入
- HTML 兜底转换：`scripts/md_to_html.py`（无 modern-minimal-html 时使用，输出现代极简风结构化卡片布局）
- 产物路径：`scripts/list_outputs.py`
- 资产索引：`scripts/asset_index.py`
- 可选出图：`scripts/gen_image.py` — 支持 `--provider toapis`（Gemini 2.5 Flash）或 `--provider banana`
- 可选视频：`scripts/gen_video_seedance.py`、`scripts/ffmpeg_concat.py`

# 失败与降级

当搜索或抓取连续失败 3 次以上：

- `evidence_strength` 强制为 `weak`。
- 禁止绿灯，禁止 8 分以上候选。
- 报告封面提示“本次未能完成联网调研，结论基于模型已知信息”。
- 所有关键判断默认标为 🟡 或 🔴。

# 暂停 / 回退 / 恢复

- 用户说“暂停”：设置 `status = paused`。
- 用户说“回到 Mx”：读取状态并从该步骤重跑，提醒后续产出需要刷新。
- 新会话恢复：输出当前灯号、Top1 候选、下一步建议。**M5 前须确认 `project_state.concept.fields` 已填写完整（name, main_character, key_scene, theme_keywords 等），否则 world_context 世界锚点会丢失主题上下文。**
- 任何步骤失败：写入 `errors[]`，不静默继续。
