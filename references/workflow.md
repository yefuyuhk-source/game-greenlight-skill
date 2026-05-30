# 主流程 SOP

## 总原则

- 这是方向筛选辅助器，不是立项决策器。
- 每步开始前读取 `project_state.json`。
- 每步结束后写回状态，并询问用户是否进入下一步。
- 每步结束后的对话回复必须列出本步产物路径；使用 `scripts/list_outputs.py {project_dir} --step Mx --markdown` 可辅助生成。
- 项目产出只写入 workspace，不写入 Skill 包。
- 图像和视频默认只生成提示词；只有用户显式要求才调用 provider。

## M1 需求采集与关键词生成

1. 从用户自然语言中抽取 `theme`、`gameplay`、`art_style`、`background`、`platforms`、`audience`。
2. 若可用字段少于 2 个，继续追问。
3. **模拟经营/RPG 等重度设定依赖品类**：即使已有 3+ 字段，若 `background`（具体经营什么/世界观）缺失，应在 M1 末尾追问。这类品类的竞品对标和用户画像高度依赖设定细节，「模拟经营」本身太宽。
3. 生成四组关键词：
   - `primary_keywords`: 3-5 个，中英文混合。
   - `competitor_keywords`: 3-8 个。
   - `player_need_keywords`: 3-5 个。
   - `negative_keywords`: 2-5 个。
4. 写入 `inputs.md` 与 `project_state.inputs`。
5. 对话中返回 `inputs.md` 与 `project_state.json` 的路径。

## M2 证据驱动调研

0. **前置检查**：确认 `TAVILY_API_KEY` 可用。
   - `search_web.py` 按优先级读取：环境变量 → macOS Keychain → 降级（详见 `references/tavily-setup.md`）。
   - execute_code 沙箱中会自动从 Keychain 回退，无需手动设置。
   - 无 key 时所有搜索降级返回空结果，触发 `evidence_strength = weak`。
1. 使用 `scripts/search_web.py` 搜索关键词。
2. 使用 `scripts/fetch_url.py` 抽取页面正文与元数据。
3. 写入 `research/sources.jsonl`。
4. 按 `references/research_protocol.md` 生成 `findings.md` 与 `direction.md`。
5. 写回 `project_state.research` 与 `project_state.direction_judgment`。
6. 对话中返回 `sources.jsonl`、`findings.md`、`direction.md` 与 `project_state.json` 的路径。

## M3 选题推荐

1. 基于 `direction_judgment` 和 `findings.md` 生成 3-5 个候选。
2. 按 `references/scoring_rubric.md` 打分。
3. 写入 `candidates.md`。
4. 选择折算分最高的候选为 `selected_candidate_id`。
5. 对话中返回 `candidates.md` 与 `project_state.json` 的路径。

## M4 立项初案

1. 基于 Top1 生成 `concept.md`。
2. 强制填写 `direction_hypotheses` 四问。
3. 按 `references/shot_taxonomy.md` 槽位规则生成关键画面 `shotlist.md`：
   - 固定核心槽位 6 张：主视觉 KV（S1）、标志性场景图（S2）、主界面（S3）、战斗/核心玩法（S4）、Boss战/高潮（S5）、角色养成/成长（S6）。
   - 品类替换槽位 2-3 张：查品类映射表，按项目品类补充（S7-S9）。
   - 可选社交槽位 1 张：当品类命中社交驱动标签时启用（S10）。
   - 总数约束：最少 6 张，最多 10 张。
4. 对话中返回 `concept.md`、`shotlist.md` 与 `project_state.json` 的路径。

## M5 关键画面提示词

1. 推荐路径：运行 `python scripts/build_prompts.py --project <project_dir> --category <品类名> --context-only`
   自动完成：三层 YAML 加载 → 为每条 shot 生成结构化上下文卡片 → 输出 `images/prompts.jsonl`
   （`prompt_v1` = 上下文卡片，metadata + negative 照常生成）。
   然后调用 `concept-prompt-architecture` skill 逐条生成英文 prompt 写入 `prompt_v2`。
   **主题一致性**：上下文卡片包含 world_context anchor，concept-prompt-architecture 的自检第 7 条强化跨 shot 视觉锚点共享。
2. 兼容路径：`python scripts/build_prompts.py --project <project_dir> --category <品类名> --legacy`
   使用原有碎片拼接生成 prompt_v1，保持完全向后兼容。
3. 默认目标是"手游实际画面截图"，用于验证玩法、UI、战斗可读性和项目可行性。
4. 只有主视觉、宣传图、纯氛围场景（`with_ui: false`）允许使用概念图 / key visual / scene concept 表达。
5. 用户显式说"开始出图"或配置 `TOAPIS_API_KEY` 后调用：
   ```bash
   python scripts/gen_image.py --prompts <project>/images/prompts.jsonl --provider toapis --output-dir <project>/images --category <品类名>
   ```
   出图时优先使用 `prompt_v2`（如有），否则用 `prompt_v1`。
   生成的图片路径写入 `prompts.jsonl` 的 `generated_image` 字段。
6. 对话中返回 `images/prompts.jsonl` 与 `project_state.json` 的路径。

## M6 演示视频分镜

1. 默认只生成 `video/storyboard.md`。
2. 每镜头包含时长、画面、动作、首帧提示词、尾帧提示词。
3. 用户显式说“生成视频”才调用视频 provider。
4. 对话中返回 `video/storyboard.md`、可选 `video/final.mp4` 与 `project_state.json` 的路径。

## M7 报告汇总

1. 汇总 M1-M6 关键结论到 `report/report.md`，作为立项报告。在「关键画面与提示词」章节使用 `{{SHOT_CARDS}}` 占位符。
2. 检测 HTML 设计后端：
   ```bash
   python scripts/check_design_backend.py --json
   ```
3. 如果检测到 modern-minimal-html，运行 `scripts/build_html_brief.py` 生成 HTML 设计 brief：
   ```bash
   python scripts/build_html_brief.py <project_dir>
   ```
4. 调用 modern-minimal-html skill 读取 `report/html_design_brief.md`、`report/report.md`、`images/prompts.jsonl` 和已生成图片，设计并产出 `report/report.html`。
5. 如果当前环境没有 modern-minimal-html，使用内置兜底转换：
   ```bash
   python scripts/md_to_html.py report/report.md report/report.html \
     --prompts images/prompts.jsonl
   ```
   兜底 HTML 使用 modern-minimal-html 的 CSS 变量体系 + 组件模块（白底细框高密度），并在对话中说明"HTML 为兜底版，非 modern-minimal-html 定制版"。
6. 若联网失败降级，报告封面必须提示证据不足。
7. 对话中返回 `report/report.md`、`report/report.html`、可选 `report/html_design_brief.md` 与 `project_state.json` 的路径。
8. **产物汇总**：M7 完成后运行以下命令展示所有最终产物，包含中文标题与路径：
   ```bash
   python scripts/list_outputs.py <project_dir> --step M7 --markdown
   ```
   输出示例：
   - **立项报告（Markdown）**：`<project_dir>/report/report.md`
   - **立项报告（HTML）**：`<project_dir>/report/report.html`
   - **关键画面提示词**：`<project_dir>/images/prompts.jsonl`
   对话回复中保留所有最终产物的绝对路径，供用户直接打开或定位。

## M8 风格迭代

用户对 M5 不满意时进入：

1. 推荐 3 个差异化风格方向。
2. 用户选择后更新 `art.iterations[]`。
3. 重新生成 prompts，视频仍默认不重跑。

## 暂停 / 回退 / 恢复

- 用户说“暂停”：设置 `status = paused`。
- 用户说“回到 Mx”：读取对应输入，重跑该步骤，并清理或标记后续产出需要刷新。
- 新会话恢复：用 `scripts/state.py summary project_state.json` 输出进度摘要。
- 任意失败：用 `scripts/state.py error` 记录到 `errors[]`。
