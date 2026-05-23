# Changelog

## v0.5.1 (2026-05-23)

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