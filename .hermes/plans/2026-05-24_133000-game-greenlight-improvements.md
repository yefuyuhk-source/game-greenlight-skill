# 改进计划：game-greenlight-skill v0.5.2

## 目标

基于 v0.5.1，从代码质量、健壮性、可维护性三个维度识别并修复改进点，不做功能大改。

## 当前上下文

- 版本 v0.5.1，13 品类三层提示词系统，三条世界锚点，产物汇总中文标题
- 工作区 `~/game-greenlight-workspace/outputs/`，活跃项目 `20260523_chinese_folklore_mgmt_001`（M7 🟡）
- Hermes + Claude Code 双平台同步维护
- 用户数据中心 IP 被拦截，Tavily 搜索是唯一外部数据源

## 改进项清单

### P0 — 影响日常使用

| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| 1 | `requirements.txt` 缺失 `pyyaml` | 新环境 `pip install` 后 `build_prompts.py` 报 `ModuleNotFoundError` | 补齐所有运行时依赖 |
| 2 | `build_prompts.py` 不校验 `current_step >= M4` | M2 阶段误跑会产出无意义提示词 | 加上步骤前置检查 |
| 3 | 世界锚点 `fill_template()` 当 `fields` 为空时静默回退为空字符串 | 新项目或恢复项目未填写 fields 时，所有 prompt 失去世界锚点 | 加显式警告日志；在 SKILL.md 增加恢复时补填 fields 的检查步骤 |

### P1 — 质量保障

| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| 4 | 测试仅覆盖 state/md_to_html/gen_image 等 6 个脚本，未覆盖 `build_prompts.py`、`search_web.py` | 核心提示词组装无自动化回归 | 新增 `test_build_prompts.py`，测试三层 YAML 组装 + 世界锚点注入 + 品类配置加载 |
| 5 | `category_prompts.yaml` 13 品类缺少 schema 校验 | 新增品类时字段遗漏不会在 test 中暴露 | 新增 `test_category_schema.py`，校验每个品类必须有的字段 |
| 6 | `CI` 用 `unittest discover` 而非 `pytest` | 与本地开发方式不一致 | 升级 test.yml 使用 pytest + 品类 schema 校验脚本 |

### P2 — 文档与维护性

| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| 7 | `README.md` 文件结构过时（显示 v0.3 的结构） | 新开发者困惑 | 更新 README 目录树 |
| 8 | 缺少 `CHANGELOG.md` | 版本间变更无人能追溯 | 从 git log 生成初始 CHANGELOG，后续按 semver 维护 |
| 9 | `assets/style_presets/default.json` 不再被引用 | 死资产，误导 | 清理或标记废弃 |
| 10 | `agents/openai.yaml` 与三层 YAML 架构不匹配 | 可能误导使用者 | 更新或标记废弃 |

### P3 — 长远可优化（本次不执行）

| # | 问题 | 理由暂缓 |
|---|------|----------|
| 11 | `search_web.py` 仅支持 Tavily，无 fallback provider | 当前 Tavily 可用，适配多个 provider 需额外工作量 |
| 12 | `fetch_url.py` 用 HTMLParser 无法抓取 JS 渲染页 | 当前场景（行业报告、新闻）多数是静态页 |
| 13 | 缺少 End-to-End 集成测试（M1→M7 模拟跑通） | 需 mock Tavily + 大模型，开发成本高 |

## 预计变更文件

| 文件 | 变更类型 | 对应项 |
|------|----------|--------|
| `requirements.txt` | 修改 | P0-1 |
| `scripts/build_prompts.py` | 修改 | P0-2, P0-3 |
| `SKILL.md` | 修改 | P0-3 |
| `tests/test_build_prompts.py` | 新增 | P1-4 |
| `tests/test_category_schema.py` | 新增 | P1-5 |
| `.github/workflows/test.yml` | 修改 | P1-6 |
| `README.md` | 修改 | P2-7 |
| `CHANGELOG.md` | 新增 | P2-8 |
| `assets/style_presets/default.json` | 删除或标记 | P2-9 |
| `agents/openai.yaml` | 修改或标记废弃 | P2-10 |

## 验证方法

1. `python scripts/build_prompts.py --project <fixture> --category 模拟经营 --dry-run` 成功
2. 前置步骤检查：未完成 M4 时退出并报错
3. `python -m pytest tests/ -v` 全部通过（至少 10+ tests）
4. CI 在 GitHub 上通过
5. `pip install -r requirements.txt` 后所有脚本可运行

## 风险 / 开放问题

- P0-3（fields 空警告）：如果用户恢复旧项目，需要先补填 fields 再跑 M5。SKILL.md 中已有恢复检查，增加显式提示即可。
- P1-4 测试 build_prompts.py 需要 fixture 项目目录，用 `tmp_path` + 最小化 `project_state.json` 模拟即可，不需要真实 workspace。
- P2-8 CHANGELOG 内容从 git log `--pretty=format` 提取，需人工筛选关键变更。