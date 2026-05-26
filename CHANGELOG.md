# Changelog

## v0.8.6 (2026-05-26)

**安全加固与健壮性修复（无功能变更）**

### 逻辑修正
- `build_prompts.py`：`fill_template` 仅在所有占位符都缺失时才使用 fallback，修复部分变量有值时被 fallback 整体替换的 bug
- `state.py`：`SKILL_VERSION` 从 `0.3.1` 更新为 `0.8.5`，与 SKILL.md 实际版本对齐
- `gen_video_seedance.py`：降级判断从检查 `os.environ.get("VIDEO_PROVIDER")` 改为检查 `args.provider`，使 `--provider` 显式传参时行为一致

### 安全
- `fetch_url.py`：新增 URL scheme 白名单（仅允许 http/https）+ 内网 IP 段过滤（127/10/172.16/192.168/169.254），防止 SSRF
- `gen_image.py`：banana provider 异常信息中过滤 API Key 明文（替换 `apiKey` 值为 `***`）
- `ffmpeg_concat.py`：concat 列表中文件路径单引号转义，防止特殊文件名破坏格式

### 健壮性
- `build_html_brief.py`：空 report.md 不再触发 `IndexError`，使用 project_id 兜底标题
- `asset_index.py`：`--record` 参数 JSON 解析失败时输出友好错误信息而非 traceback
- `ffmpeg_concat.py`：临时 concat 列表文件在 ffmpeg 执行后清理（`try/finally + os.unlink`）

### 维护
- 品类数量注释全项目同步：13 → 14（`category_prompts.yaml`、`test_category_schema.py`、`test_build_prompts.py`、`SKILL.md`）
- CI workflow：Python 版本矩阵 3.12 + 3.14；依赖改为读取 `requirements.txt`
- 新增 `tests/test_safety_fixes.py`（12 个测试用例），覆盖本次所有修复点

---

## v0.8.5 (2026-05-27)

**安全修复：API Key 泄露防护**

### 安全
- 所有参考文件删除 `export KEY=xxx` 等含 key 配置示例，改为仅描述「从环境变量读取」
- `gen_image.py` / `search_web.py` 异常输出中过滤 Authorization 头（替换 `Bearer {key}` → `Bearer ***`）

### 文档
- SKILL.md 新增硬约束「禁止打印/回显/命令行传递 API Key」

---

## v0.8.4 (2026-05-27)

**测试同步 v0.8 系列变更**

### 修复
- 品类计数测试硬编码 13→14（v0.8.0 新增「RPG养成」品类后未同步）
- vendor 降级测试更新，适配仓库自带 `vendor/modern-minimal-html/` 兜底逻辑

---

## v0.8.3 (2026-05-26)

**vendor fallback + bugfix**

### 新增
- `check_design_backend.py` vendor fallback 逻辑——优先系统全局安装，找不到时从仓库 `vendor/` 加载
- `vendor/` 目录打包 modern-minimal-html SKILL.md，clone 后无需额外安装

### 修复
- M7 Shot card 排版：横竖图自动区分尺寸（16:9 ↔ 9:16）

---

## v0.8.2 (2026-05-26)

**Shot card 排版 + 杂交品类修正**

### 改进
- Shot card 横版图(16:9)用 `.shot-img-wide` 400px，竖版图(9:16)用 `.shot-img` 280px
- `hybrid-category-mapping.md` 新增实例二「RPG养成+地府探索」
- M5 杂交品类完整修正流程（ART STYLE 全量替换、S7-S9 槽位名修正、验证清单）
- `chinese-folklore-minigame-landscape.md` 新增「Q版微恐方向」章节

---

## v0.8.1 (2026-05-26)

**M7 补图流程**

### 新增
- M7 后补图说明：用户手动放入图片后更新 report.html 中 shot card 占位框为 `<img>` 标签

---

## v0.8.0 (2026-05-26)

**新增「RPG养成」品类**

### 新增
- 第 14 个品类 `RPG养成` 加入 `category_prompts.yaml`（装备/技能系统、关卡/副本选择、角色属性面板三张替换槽位）
- `shot_taxonomy.md` 追加 RPG / ARPG（养成向）条目

### 修复
- `category_prompts.yaml` 末尾补充换行符

---

## v0.7.0 (2026-05-25)

**M5 集成 concept-prompt-architecture skill + 默认 Gemini 3.1 Flash**

### 新增
- M5 `--context-only` 模式：生成结构化上下文卡片供 `concept-prompt-architecture` skill 消费
- `build_prompts.py` 新增 `--context-only` / `--legacy` 参数（`--legacy` 向后兼容原有碎片拼接）
- `gen_image.py` 新增 `--provider toapis31`（Gemini 3.1 Flash 图像生成）
- `--toapis-model` CLI 参数 + `TOAPIS_MODEL` 环境变量，支持模型名覆盖
- 所有 slot 新增 `zone_strategy` 和 `aspect_ratio` 字段，支持 7 种分区策略映射
- `references/structured-prompt-composition.md` — 4-Layer 手写提示词方法论手册

### 变更
- 默认出图模型从 `gemini-2.5-flash-image-preview` 改为 `gemini-3.1-flash-image-preview`
- 回退 2.5 Flash：`--toapis-model gemini-2.5-flash-image-preview`
- `references/toapis-gemini-image-api.md` 合并到 `references/toapis-image-api.md`

### 文档
- `references/prompt-assembly-architecture.md` 新增 v1.1 双模式架构说明
- `references/workflow.md` M5 流程更新为双路径说明

---

## v0.6.0 (2026-05-24)

**新增 12 个本地增强参考文件**

### 新增
- 12 个本地增强参考文件（品类映射、设计风格、提示词库等）
- 测试项目夹具 `tests/fixtures/test_project/`

### 改进
- 品类配置加载支持大小写不敏感模糊匹配

---

**三层提示词系统 + polish 改进 + 主题一致性 + 产物汇总中文标题**

### 新增
- 三层 YAML 提示词架构：`prompt_base.yaml`（基础层）、`category_prompts.yaml`（品类层）、`slot_prompts.yaml`（槽位层）
- `scripts/build_prompts.py` — 三层组装引擎，支持 13 品类自动匹配
- `scripts/polish_prompts.py` — 提示词润色工具（参考保留，不再自动调用）
- 世界观锚点（world_context）强制注入每条提示词，保证 S1-S10 主题一致
- `--polish` 参数：输出全部槽位的润色清单，由 AI 助手在会话中完成（无需外部 API key）

### 改进
- 润色阶段从外部 API 改为当前大模型自润色
- `scripts/gen_image.py` 新增 `load_category_config()` 和 `--category` 参数
- `scripts/list_outputs.py` 输出带中文标题 + 绝对路径
- 品类匹配支持大小写不敏感模糊匹配

### 修复
- 品类兜底不再返回 `version`/`last_updated` 等非 dict 字段
- `assets/prompt_snippets/common_negative.txt` 内容合并至 `prompt_base.yaml`

---

## v0.4.0 (2026-05-23)

**M5 槽位机制 + M7 modern-minimal + ToAPIs 生图**

### 新增
- M5 画面槽位分类机制（shot_taxonomy）：6 固定核心 + 2-3 品类替换 + 1 可选社交
- ToAPIs Gemini 2.5 Flash 图像生成 provider
- M7 HTML 输出后端检测（`scripts/check_design_backend.py`）
- M7 HTML 设计 brief 生成（`scripts/build_html_brief.py`）
- 现代极简风 HTML 兜底输出（`scripts/md_to_html.py`）

### 改进
- M7 输出替换 huashu-design 为 modern-minimal-html
- 出图路径取自 `prompt_v2`（如有）→ `prompt_v1` → `prompt`

### 修复
- ToAPIs provider 缺少 User-Agent 头导致 403
- ToAPIs 响应路径解析

---

## v0.3.0

**依赖管理 + CI**

- 添加 JSON schema 状态契约
- 完善 MIT LICENSE
- 添加 requirements.txt 依赖管理
- 添加 GitHub CI workflow
- 初始测试套件（6 tests）

---

## v0.2.0

**M7 HTML 输出**

- 添加 huashu-design 后端检测机制
- M7 报告生成流程

---

## v0.1.0 (2026-05-19)

**早期预览版**

- 初始立项方向筛选流程 M1→M8
- M2 证据驱动调研协议
- M3 加权评分矩阵
- M4 立项初案 + shotlist
- M5 关键画面提示词
- M6 视频分镜
- M7 内部讨论报告
- 基础搜索（Tavily）和抓取工具