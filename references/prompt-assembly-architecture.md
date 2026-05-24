# 三层组合式提示词系统架构

## 设计动机

M5 需要为每款游戏生成 6-10 条高质量图片生成提示词。手工拼接提示词存在三个问题：

1. 不一致 — 不同 agent 写出来的提示词在风格、长度、细节密度上差异很大
2. 遗漏 — 品类特定的画风参数、UI 描述、负面词容易被忘记
3. 品质不均匀 — S1/S2/S5（对外展示图）需要二次润色，手工步骤容易被跳过

三层组合式系统解决了这三个问题：用 YAML 配置固化知识，用代码组装保证一致性，用 --polish 自动化润色保证品质。

## 架构分层

```
prompt_base.yaml ─────────────────────────────────────────
  │  全局锚点（with_ui_true/false 前置词）
  │  全局负面词（注入所有图）
  │  LLM 润色指令模板
  │  变量占位符规范
  │  兜底策略
  ├── category_prompts.yaml ──────────────────────────────
  │    13 品类，每品类：
  │    ├─ art_style（画风描述）
  │    ├─ default_camera（默认机位）
  │    ├─ color_palette（色调）
  │    ├─ ui_aesthetic（UI 风格）
  │    ├─ model_route（primary/fallback/cfg）
  │    ├─ negative_extra（品类负面词）
  │    ├─ default_subject（兜底主体）
  │    └─ replacement_shots（S7-S9 品类替换槽位）
  ├── slot_prompts.yaml ─────────────────────────────────
  │    6 固定槽位 + 1 可选社交：
  │    ├─ composition（构图描述）
  │    ├─ subject_template（主体模板，含 {var} 占位符）
  │    ├─ camera_override（槽位定制机位）
  │    ├─ ui_layout（UI 布局详细说明，S3-S6 专用）
  │    ├─ llm_polish（是否需 LLM 润色）
  │    ├─ must_include / must_exclude（强制元素约束）
  │    └─ detail_checklist（QA 检查清单）
  └── project_state.concept ──────────────────────────────
        × 变量注入：game_name, main_character, key_scene 等
        × shotlist：定义每条图的 id、name、purpose
        × fields：具体游戏信息
```

## 核心设计决策

1. 品类替换槽位（S7-S9）在 category_prompts.yaml 而非 slot_prompts.yaml 中定义，因为不同品类的替换槽位数和内容差异大，随品类而非槽位固定。

2. 只有对外展示的图才需要 LLM 润色（S1 主视觉、S2 场景图、S5 Boss战），S3-S6（主界面、战斗、养成）用结构化拼接即可。润色指令声明为 llm_polish: true，通过 --polish 自动触发。

3. 模型路由走品类层配置。每品类定义 primary/fallback provider + CFG scale + denoising strength，gen_image.py 通过 --category 参数读取，不再 hardcode。

4. 负面词三层累加去重：base negative_global + category negative_extra + slot must_exclude，按关键词 set 去重而非简单拼串。

5. 变量兜底链：{var} 占位符 + category default_subject（品类默认主体）+ built-in fallback（prompt_base 层），防止缺失变量导致空输出。

## 使用示例

```bash
# 基础组装
python scripts/build_prompts.py --project outputs/my_game/ --category 模拟经营

# 组装+自动润色（S1/S2/S5 调用 LLM）
python scripts/build_prompts.py --project outputs/my_game/ --category 模拟经营 --polish

# dry-run 预览
python scripts/build_prompts.py --project outputs/my_game/ --category 模拟经营 --dry-run

# 出图（自动读取 prompt_v2 优先）
python scripts/gen_image.py --prompts outputs/my_game/images/prompts.jsonl --provider toapis --output-dir outputs/my_game/images --category 模拟经营
```

## 版本历史

- v1.0 (2026-05-23)：初始发布，三层 YAML + --polish + 模型路由