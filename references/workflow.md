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
3. 生成四组关键词：
   - `primary_keywords`: 3-5 个，中英文混合。
   - `competitor_keywords`: 3-8 个。
   - `player_need_keywords`: 3-5 个。
   - `negative_keywords`: 2-5 个。
4. 写入 `inputs.md` 与 `project_state.inputs`。
5. 对话中返回 `inputs.md` 与 `project_state.json` 的路径。

## M2 证据驱动调研

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

1. 默认只生成 `images/prompts.jsonl`。
2. 默认目标是”手游实际画面截图”，用于验证玩法、UI、战斗可读性和项目可行性。
3. 只有主视觉、宣传图、纯氛围场景允许使用概念图 / key visual / scene concept 表达。
4. 每张图包含用途、`render_mode`、构图、视觉关键词、provider 建议、正向 prompt、negative prompt。
5. 用户显式说”开始出图”或配置 `BANANA_API_KEY` + `BANANA_MODEL_KEY` 后调用：
   ```bash
   python scripts/gen_image.py --prompts <project>/images/prompts.jsonl --provider banana --output-dir <project>/images
   ```
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
3. 如果检测到 huashu-design，运行 `scripts/build_huashu_brief.py` 生成 HTML 设计 brief：
   ```bash
   python scripts/build_huashu_brief.py <project_dir>
   ```
4. 调用 huashu-design skill 读取 `report/huashu_design_brief.md`、`report/report.md`、`images/prompts.jsonl` 和已生成图片，设计并产出 `report/report.html`。
5. 如果当前环境没有 huashu-design，使用内置兜底转换：
   ```bash
   python scripts/md_to_html.py report/report.md report/report.html \
     --style auto \
     --state project_state.json \
     --prompts images/prompts.jsonl
   ```
   兜底 HTML 必须使用结构化卡片式布局，尽量把长文本拆成可读模块，并在对话中说明“HTML 为结构化兜底版，非 huashu-design 定制版”。
6. 若联网失败降级，报告封面必须提示证据不足。
7. 对话中返回 `report/report.md`、`report/report.html`、可选 `report/huashu_design_brief.md` 与 `project_state.json` 的路径。

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
