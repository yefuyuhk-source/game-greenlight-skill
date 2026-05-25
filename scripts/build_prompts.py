#!/usr/bin/env python3
"""M5 提示词组装引擎 - 三层组合式提示词生成。

读取 project_state.json + 三层 YAML 配置，输出 images/prompts.jsonl。

用法:
  python scripts/build_prompts.py --project <project_dir> --category <品类名>
  python scripts/build_prompts.py --project <project_dir> --category 模拟经营 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


# ── 路径解析 ──────────────────────────────────────────────────────────

def find_project_dir(project_arg: str) -> Path:
    """解析 --project 参数为绝对路径。"""
    p = Path(project_arg)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        raise SystemExit(f"项目目录不存在: {p}")
    return p.resolve()


def find_skill_root() -> Path:
    """向上寻找包含 references/ 目录的 skill 根目录。"""
    start = Path(__file__).resolve().parent.parent  # scripts/..
    for candidate in [start, start.parent]:
        ref_dir = candidate / "references"
        if ref_dir.is_dir():
            return candidate
    # 兜底：脚本同级的 references/
    ref_dir = start / "references"
    if ref_dir.is_dir():
        return start
    raise SystemExit("无法定位 references/ 目录")


# ── 配置加载 ──────────────────────────────────────────────────────────

def load_yaml(path: Path) -> dict[str, Any]:
    """安全加载 YAML 文件。"""
    if not path.exists():
        raise SystemExit(f"YAML 文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"YAML 格式错误（期望 dict）: {path}")
    return data


def load_project_state(project_dir: Path) -> dict[str, Any]:
    """加载 project_state.json。"""
    state_path = project_dir / "project_state.json"
    if not state_path.exists():
        raise SystemExit(f"project_state.json 不存在: {state_path}")
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── 变量注入 ──────────────────────────────────────────────────────────

def fill_template(template: str, variables: dict[str, str], fallback: str = "") -> str:
    """填充 {var} 占位符，缺失时用 fallback。

    当所有占位符都找不到变量且 fallback 有值时，整体用 fallback 替换。
    """
    # 找出所有占位符
    placeholders = re.findall(r"\{(\w+)\}", template)
    if not placeholders:
        return template.strip()

    # 检查是否有变量缺失
    missing = [p for p in placeholders if not variables.get(p, "")]
    if missing and fallback:
        # 所有占位符都缺失时整体替换为 fallback
        return fallback

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        val = variables.get(key, "")
        if val:
            return val
        return ""  # 单个缺失时留空

    result = re.sub(r"\{(\w+)\}", replacer, template)
    # 清理多余空格和逗号
    result = re.sub(r"[,，]+\s*[,，]+", ", ", result)
    result = re.sub(r"\s{2,}", " ", result)
    result = re.sub(r"[,，]+\s*$", "", result)
    return result.strip()


def extract_variables(state: dict[str, Any]) -> dict[str, str]:
    """从 project_state.concept.fields 提取变量字典。"""
    fields = state.get("concept", {}).get("fields", {})
    if not fields:
        print("[build_prompts] ⚠️ 警告: project_state.concept.fields 为空，世界锚点将缺少主题上下文！", file=sys.stderr)
        print("[build_prompts]   请确保 M4 已正确填写 fields（name, main_character, key_scene, theme_keywords 等）", file=sys.stderr)
        fields = {}

    def safe_str(val: Any) -> str:
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            return ", ".join(str(v) for v in val[:3])
        return str(val) if val else ""

    # 从 theme_keywords 取首项作为 atmosphere_keyword
    theme_kws = fields.get("theme_keywords", [])
    atmosphere_kw = safe_str(theme_kws[0]) if isinstance(theme_kws, list) and theme_kws else ""

    # enemies 取首项
    enemies = fields.get("enemies", [])
    enemy_type = safe_str(enemies[0]) if isinstance(enemies, list) and enemies else "generic enemy"

    # featured_character 缺省 = main_character
    fc = safe_str(fields.get("featured_character", ""))
    mc = safe_str(fields.get("main_character", ""))
    featured = fc or mc

    return {
        "game_name": safe_str(fields.get("name", "")),
        "main_character": mc,
        "characters": safe_str(fields.get("characters", [])),
        "key_scene": safe_str(fields.get("key_scene", "")),
        "atmosphere_keyword": atmosphere_kw,
        "enemy_type": enemy_type,
        "boss_description": safe_str(fields.get("boss_description", "")),
        "landmark_scene": safe_str(fields.get("landmark_scene", "")),
        "featured_character": featured,
        "color_preference": safe_str(fields.get("color_preference", "")),
    }


# ── 槽位解析 ──────────────────────────────────────────────────────────

def resolve_slot(
    shot: dict[str, Any],
    slot_configs: dict[str, Any],
    category_config: dict[str, Any],
) -> dict[str, Any]:
    """确定槽位的配置来源。

    S1-S6: 从 slot_prompts.yaml 读取
    S7-S9: 从 category_prompts.yaml 的 replacement_shots 读取
    S10:   从 slot_prompts.yaml 读取（条件启用）
    """
    shot_id = shot.get("id", "")
    shot_name = shot.get("name", "")

    # S1-S6 固定槽位
    if shot_id.startswith("S") and not shot_id.startswith("S10"):
        if shot_id in slot_configs:
            return slot_configs[shot_id]

    # S10 可选社交槽位
    if shot_id == "S10" and shot_id in slot_configs:
        return slot_configs[shot_id]

    # S7-S9 品类替换槽位：按 name 或 id 匹配 replacement_shots
    replacements = category_config.get("replacement_shots", [])
    for r in replacements:
        if r["id"] == shot_id or r.get("name", "") == shot_name:
            return {**r, "slot_type": "replacement"}

    # 兜底：返回空配置
    return {
        "name": shot_name,
        "slot_type": "replacement",
        "with_ui": True,
        "llm_polish": False,
        "composition": "standard gameplay screen",
        "subject_template": "gameplay screenshot of {game_name}",
        "camera_override": "",
        "subject_template_features": "",
        "must_include": [],
        "must_exclude": [],
        "detail_checklist": ["视角与构图", "UI层级", "玩法状态"],
        "reference_match": [],
    }


# ── 提示词组装 ────────────────────────────────────────────────────────

def assemble_prompt(
    shot: dict[str, Any],
    slot: dict[str, Any],
    cat: dict[str, Any],
    base: dict[str, Any],
    variables: dict[str, str],
) -> str:
    """组装单条正向提示词。"""
    with_ui = slot.get("with_ui", True)

    # 0. 世界观锚点（保证所有提示词主题一致）
    world_tmpl = base.get("world_context", {}).get("template", "")
    world_anchor = fill_template(world_tmpl, variables, fallback="") if world_tmpl else ""
    world_anchor = world_anchor.rstrip(";,.，；、")

    # 1. 锚点词
    anchor = base.get("anchors", {})
    anchor_text = anchor.get("with_ui_true", "") if with_ui else anchor.get("with_ui_false", "")

    # 2. 碎片列表（世界锚点放在第一位，确保每条都统一开篇）
    fragments = [
        world_anchor,
        anchor_text,
        cat.get("art_style", ""),
        slot.get("composition", ""),
        fill_template(
            slot.get("subject_template", ""),
            variables,
            fallback=cat.get("default_subject", ""),
        ),
        slot.get("camera_override", "") or cat.get("default_camera", ""),
        variables.get("color_preference", "")
        and f"{variables['color_preference']} color palette, "
        or "",
        cat.get("color_palette", ""),
    ]

    # 3. UI 相关
    if with_ui:
        ui_aesthetic = cat.get("ui_aesthetic", "")
        ui_layout = slot.get("ui_layout", "")
        if ui_aesthetic:
            fragments.append(ui_aesthetic)
        if ui_layout:
            fragments.append(ui_layout)

    # 4. must_include 指令
    must_include = slot.get("must_include", [])
    if must_include:
        fragments.append("must include: " + "; ".join(must_include))

    # 5. 去重、去除空值、组合
    seen = set()
    clean = []
    for f in fragments:
        f_stripped = f.strip()
        if not f_stripped:
            continue
        # 简单去重（去掉完全相同的片段）
        key = f_stripped.lower()[:80]
        if key in seen:
            # 跳过重复
            continue
        seen.add(key)
        # 去掉尾部逗号/分号再加逗号
        f_stripped = f_stripped.rstrip(";,，；")
        clean.append(f_stripped)

    return ", ".join(clean)


def assemble_negative(
    shot: dict[str, Any],
    slot: dict[str, Any],
    cat: dict[str, Any],
    base: dict[str, Any],
) -> str:
    """组装负向提示词。"""
    with_ui = slot.get("with_ui", True)

    parts = [
        base.get("negative_global", ""),
    ]
    if with_ui:
        parts.append(base.get("negative_ui_extra", ""))
    parts.append(cat.get("negative_extra", ""))
    slot_exclude = slot.get("must_exclude", [])
    if slot_exclude:
        parts.append(", ".join(slot_exclude))

    # 去重
    seen = set()
    clean = []
    for p in parts:
        for item in [x.strip() for x in p.split(",") if x.strip()]:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                clean.append(item)

    return ", ".join(clean)


# ── concept-prompt-architecture 上下文卡片 ──────────────────────────────

def derive_zone_strategy(shot_id: str, shot_name: str, with_ui: bool, purpose: str, slot: dict[str, Any]) -> str:
    """根据 shot 用途推导 concept-prompt-architecture 的 7 种分区策略。

    优先使用 slot 中预定义的 zone_strategy 字段，
    否则根据 shot_id、with_ui、purpose 推断。
    """
    # 优先用 YAML 中预定义的 zone_strategy
    if slot.get("zone_strategy"):
        return slot["zone_strategy"]

    # 按 shot_id 固定映射
    strategies = {
        "S1": "营销引流",     # 叙事+构图分区
        "S2": "世界观展示",   # 空间层次分区
        "S3": "主场景展示",   # 场景+UI混合分区
        "S4": "玩法展示",     # 功能逻辑分区
        "S5": "高潮爽感",     # 叙事张力分区
        "S6": "收集欲望",     # 信息层级分区
        "S10": "功能说明",    # 屏幕区域分区
    }
    if shot_id in strategies:
        return strategies[shot_id]

    # S7-S9: 根据 purpose/name 推断
    purpose_lower = (purpose + shot_name).lower()
    if any(kw in purpose_lower for kw in ["战斗", "combat", "玩法", "gameplay", "副本", "对局", "关卡", "节奏"]):
        return "玩法展示"
    if any(kw in purpose_lower for kw in ["角色", "character", "养成", "收集", "装备", "英雄", "卡牌", "武器", "好感"]):
        return "收集欲望"
    if any(kw in purpose_lower for kw in ["场景", "全景", "世界", "scene", "landscape", "world", "剧情", "cg"]):
        return "世界观展示"
    if any(kw in purpose_lower for kw in ["kv", "视觉", "海报", "poster", "合影", "演出", "舞台"]):
        return "营销引流"
    if any(kw in purpose_lower for kw in ["boss", "高潮", "climax", "危机", "night"]):
        return "高潮爽感"
    if any(kw in purpose_lower for kw in ["界面", "地图", "map", "系统", "社交", "ui", "menu", "建造", "合成", "制作", "订单", "选", "进度"]):
        return "功能说明"

    return "主场景展示"  # 兜底


def build_context_card(
    shot: dict[str, Any],
    slot: dict[str, Any],
    cat: dict[str, Any],
    base: dict[str, Any],
    variables: dict[str, str],
    shot_index: int,
    total_shots: int,
) -> str:
    """生成结构化英文上下文卡片，供 concept-prompt-architecture skill 消费。"""
    with_ui = slot.get("with_ui", True)
    zone_strategy = derive_zone_strategy(
        shot.get("id", ""), shot.get("name", ""), with_ui, shot.get("purpose", ""), slot,
    )

    # 画幅
    aspect_ratio = slot.get("aspect_ratio", "9:16" if with_ui else "16:9")

    # 渲染模式
    if not with_ui:
        render_mode = "concept_allowed — pure illustration, no UI elements"
    else:
        render_mode = shot.get("render_mode", "mobile_screenshot")

    # 图像类型推断
    image_type_map = {
        "营销引流": "key art poster",
        "世界观展示": "establishing shot / scene concept",
        "主场景展示": "screen mockup with scene + UI overlay",
        "玩法展示": "gameplay screen capture",
        "高潮爽感": "boss battle / climax screen",
        "收集欲望": "character progression / collection screen",
        "功能说明": "UI interface screenshot",
    }
    image_type = image_type_map.get(zone_strategy, "game screenshot")

    # 世界锚点
    world_tmpl = base.get("world_context", {}).get("template", "")
    world_anchor = fill_template(world_tmpl, variables, fallback="") if world_tmpl else ""

    # 系列上下文
    series_tmpl = base.get("concept_prompt_architecture_series_context", "")
    if series_tmpl:
        series_context = series_tmpl.format(
            shot_index=shot_index,
            total_shots=total_shots,
            game_name=variables.get("game_name", "this game"),
        )
    else:
        series_context = (
            f"This is shot {shot_index} of {total_shots} concept images for "
            f"{variables.get('game_name', 'this game')}. "
            "Share 1-2 visual anchor elements with other shots in the series."
        )

    # 组装 must_include / must_exclude
    must_include = slot.get("must_include", [])
    must_exclude = slot.get("must_exclude", [])

    # 组装上下文卡片
    lines = []
    lines.append(f"=== SHOT CONTEXT: {shot.get('id', 'S?')} - {slot.get('name', '')} ===")
    lines.append(f"GAME: {variables.get('game_name', 'Unknown')}")
    if world_anchor:
        lines.append(f"WORLD ANCHOR: {world_anchor}")
    lines.append(f"MAIN CHARACTER: {variables.get('main_character', 'N/A')}")
    lines.append(f"FEATURED CHARACTER: {variables.get('featured_character', 'N/A')}")
    lines.append(f"LANDMARK SCENE: {variables.get('landmark_scene', 'N/A')}")
    lines.append(f"COLOR PREFERENCE: {variables.get('color_preference', 'N/A')}")
    lines.append("")
    lines.append(f"IMAGE TYPE: {image_type}")
    lines.append(f"FIRST PURPOSE: {zone_strategy}")
    lines.append(f"ZONE STRATEGY: {zone_strategy}")
    lines.append(f"ASPECT RATIO: {aspect_ratio}")
    lines.append(f"WITH UI: {str(with_ui).lower()}")
    lines.append(f"RENDER MODE: {render_mode}")
    lines.append(f"PURPOSE: {shot.get('purpose', '')}")
    lines.append("")
    lines.append(f"ART STYLE: {cat.get('art_style', '')}")
    lines.append(f"COLOR PALETTE: {cat.get('color_palette', '')}")
    lines.append(f"DEFAULT CAMERA: {cat.get('default_camera', '')}")
    if with_ui:
        lines.append(f"UI AESTHETIC: {cat.get('ui_aesthetic', '')}")
    lines.append("")
    lines.append(f"COMPOSITION GUIDANCE: {slot.get('composition', '')}")
    lines.append(f"SUBJECT DESCRIPTION: {fill_template(slot.get('subject_template', ''), variables, fallback=cat.get('default_subject', ''))}")
    camera = slot.get('camera_override', '') or cat.get('default_camera', '')
    if camera:
        lines.append(f"CAMERA: {camera}")
    if with_ui and slot.get('ui_layout'):
        lines.append(f"UI LAYOUT: {slot.get('ui_layout', '')}")
    lines.append("")
    if must_include:
        lines.append("MUST INCLUDE:")
        for item in must_include:
            lines.append(f"  - {item}")
    if must_exclude:
        lines.append("MUST EXCLUDE:")
        for item in must_exclude:
            lines.append(f"  - {item}")
    detail_checklist = slot.get("detail_checklist", [])
    if detail_checklist:
        lines.append("DETAIL CHECKLIST:")
        for item in detail_checklist:
            lines.append(f"  - {item}")
    lines.append("")
    lines.append(f"SERIES CONTEXT: {series_context}")

    return "\n".join(lines)


# ── 主流程 ────────────────────────────────────────────────────────────

def build_prompts(
    project_dir: Path,
    category_name: str,
    skill_root: Path,
    dry_run: bool = False,
    context_only: bool = False,
) -> list[dict[str, Any]]:
    """组装所有提示词。"""
    # 加载配置
    base = load_yaml(skill_root / "references" / "prompt_base.yaml")
    cat = load_yaml(skill_root / "references" / "category_prompts.yaml")
    slot_configs = load_yaml(skill_root / "references" / "slot_prompts.yaml")

    # 品类配置
    # 尝试精确匹配，再尝试模糊匹配（去掉空格/斜杠）
    category_config = cat.get(category_name)
    if not category_config:
        # 模糊匹配（大小写不敏感）
        normalized_cat = category_name.replace("/", "").replace(" ", "").lower()
        for key, val in cat.items():
            if key.replace("/", "").replace(" ", "").lower() == normalized_cat:
                category_config = val
                break
    if not category_config:
        # 兜底品类：跳过低版本/日期等非 dict 值
        first_category = None
        for key, val in cat.items():
            if isinstance(val, dict):
                first_category = val
                break
        if first_category is None:
            raise SystemExit(f"[build_prompts] 品类配置为空或格式错误")
        print(f"[build_prompts] 未找到品类 '{category_name}'，使用通用配置", file=sys.stderr)
        category_config = first_category

    # 加载 project state
    state = load_project_state(project_dir)

    # 步骤前置检查：M5 需在 M4 完成后运行
    current_step = state.get("current_step", "")
    valid_steps = ["M4", "M5", "M6", "M7", "M8"]
    if current_step not in valid_steps:
        raise SystemExit(
            f"[build_prompts] 错误: 当前步骤 {current_step}，M5 提示词生成需在 M4 完成后运行。\n"
            f"          请先完成 M4 立项初案（需包含 concept.fields 和 shotlist）。\n"
            f"          可通过 `python scripts/state.py patch <project> --step M4 --patch ...` 手动设置。"
        )

    variables = extract_variables(state)

    # 加载 shotlist
    shotlist = state.get("concept", {}).get("shotlist", [])
    if not shotlist:
        print("[build_prompts] 警告: shotlist 为空，检查 project_state.json", file=sys.stderr)
        return []

    # 组装每条提示词
    prompts = []
    total_shots = len(shotlist)
    for idx, shot in enumerate(shotlist):
        shot_id = shot.get("id", "S?")
        shot_name = shot.get("name", "")

        slot = resolve_slot(shot, slot_configs, category_config)
        with_ui = slot.get("with_ui", True)
        llm_polish = slot.get("llm_polish", False)

        if context_only:
            prompt_text = build_context_card(
                shot, slot, category_config, base, variables, idx + 1, total_shots,
            )
            llm_polish = True  # context-only 下所有 shot 都需要 LLM 生成
        else:
            prompt_text = assemble_prompt(shot, slot, category_config, base, variables)
        negative_text = assemble_negative(shot, slot, category_config, base)

        # 提取 render_mode
        render_mode = "mobile_screenshot"
        if not with_ui:
            render_mode = "concept_allowed"
        elif slot.get("slot_type") == "fixed":
            # 从 shot 中读取 M4 设置的 render_mode，缺省用 mobile_screenshot
            render_mode = shot.get("render_mode", "mobile_screenshot")

        # detail_checklist
        detail_checklist = slot.get("detail_checklist", [
            "视角与构图",
            "UI层级",
            "关键角色",
            "玩法状态",
            "反馈特效",
            "环境细节",
        ])

        entry = {
            "shot_id": shot_id,
            "name": slot.get("name", shot_name),
            "slot_type": slot.get("slot_type", "fixed"),
            "render_mode": render_mode,
            "exception_reason": shot.get("exception_reason", None),
            "purpose": shot.get("purpose", ""),
            "composition": slot.get("composition", ""),
            "detail_checklist": detail_checklist,
            "visual_keywords": shot.get("visual_keywords", []),
            "engine_suggestion": "configured-image-provider",
            "prompt_v1": prompt_text,
            "negative": negative_text,
            "reference_assets": shot.get("reference_assets", []),
            "generated_image": shot.get("generated_image", None),
            "iteration_tag": "v1",
            "llm_polish": llm_polish,
            "with_ui": with_ui,
        }
        prompts.append(entry)

    return prompts


def write_prompts(prompts_path: Path, prompts: list[dict[str, Any]]) -> None:
    """写入 prompts.jsonl。"""
    prompts_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(p, ensure_ascii=False) for p in prompts]
    prompts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[build_prompts] 写入 {len(prompts)} 条提示词 -> {prompts_path}")


def print_json(obj: Any) -> None:
    """打印 JSON 到 stdout。"""
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="M5 三层组合式提示词生成器")
    parser.add_argument("--project", required=True, help="项目目录（含 project_state.json）")
    parser.add_argument("--category", required=True, help="品类名（如 模拟经营、SLG策略战争）")
    parser.add_argument("--output", default=None, help="prompts.jsonl 输出路径，缺省为 project/images/prompts.jsonl")
    parser.add_argument("--polish", action="store_true", help="输出全部提示词的润色清单（由 AI 助手在会话中完成润色，无需外部 API key）")
    parser.add_argument("--context-only", action="store_true", help="生成上下文卡片（prompt_v1）供 concept-prompt-architecture skill 消费，而非碎片拼接")
    parser.add_argument("--legacy", action="store_true", help="使用原有碎片拼接模式（显式开关，与 --context-only 互斥）")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入文件")
    args = parser.parse_args()

    project_dir = find_project_dir(args.project)
    skill_root = find_skill_root()

    context_only = args.context_only

    prompts = build_prompts(
        project_dir, args.category, skill_root,
        dry_run=args.dry_run, context_only=context_only,
    )

    if args.dry_run:
        print_json({
            "ok": True,
            "dry_run": True,
            "category": args.category,
            "mode": "context-only" if context_only else "legacy",
            "prompt_count": len(prompts),
            "prompts": prompts,
        })
        return

    output_path = Path(args.output) if args.output else project_dir / "images" / "prompts.jsonl"
    write_prompts(output_path, prompts)

    # context-only 模式：提示用户在会话中调用 concept-prompt-architecture skill
    if context_only:
        if prompts:
            print("[build_prompts] ════════════════════════════════════════════")
            print(f"[build_prompts] context-only 模式：已生成 {len(prompts)} 条上下文卡片 -> prompt_v1")
            print("[build_prompts]")
            print("[build_prompts] 下一步：调用 concept-prompt-architecture skill")
            print("[build_prompts]   逐条读取 JSONL 中每个 shot 的 prompt_v1（上下文卡片）")
            print("[build_prompts]   → 按 4 层写作法 + 分区策略 + 8 条自检生成英文 prompt")
            print("[build_prompts]   → 写入 prompt_v2 字段，标记 iteration_tag: 'v2'")
            print("[build_prompts]")
            for p in prompts:
                print(f"[build_prompts]   {p['shot_id']} «{p.get('name', '')}» — zone: {derive_zone_strategy(p['shot_id'], p.get('name', ''), p.get('with_ui', True), p.get('purpose', ''), {})}")
            print("[build_prompts] ════════════════════════════════════════════")
        else:
            print("[build_prompts] 没有需要处理的槽位")
    elif args.polish:
        # legacy 模式下 --polish 的原有行为
        if prompts:
            print("[build_prompts] ════════════════════════════════════════════")
            print(f"[build_prompts] 全部 {len(prompts)} 个槽位需 LLM 二次润色（由 AI 助手处理）：")
            for p in prompts:
                print(f"[build_prompts]   {p['shot_id']} «{p.get('name', '')}»")
                if p.get("llm_polish"):
                    print(f"[build_prompts]     ⭐ S1/S2/S5 精细润色（原 llm_polish 标记槽位）")
                print(f"[build_prompts]     用途: {p.get('purpose', '')}")
                print(f"[build_prompts]     原文: {p.get('prompt_v1', '')[:120]}...")
                print()
            print("[build_prompts] 全部润色完成后写入 prompt_v2 字段即可。")
            print("[build_prompts] ════════════════════════════════════════════")
        else:
            print("[build_prompts] 没有需要润色的槽位")

    print_json({
        "ok": True,
        "category": args.category,
        "mode": "context-only" if context_only else "legacy",
        "prompt_count": len(prompts),
        "output": str(output_path),
    })

    # 列出全部需 LLM 处理的槽位
    if args.polish and prompts:
        slot_ids = ", ".join(p["shot_id"] for p in prompts)
        print(f"[build_prompts] 全部槽位 ({slot_ids}) 已列入润色清单")


if __name__ == "__main__":
    main()