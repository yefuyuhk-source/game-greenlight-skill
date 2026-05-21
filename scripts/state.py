#!/usr/bin/env python3
"""project_state.json 读写工具。"""

from __future__ import annotations

import argparse
import json
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_VERSION = "0.3.1"
VALID_STEPS = {f"M{i}" for i in range(1, 9)}
VALID_STATUS = {"in_progress", "paused", "done", "error"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def default_state(project_id: str, workspace: str) -> dict[str, Any]:
    timestamp = now_iso()
    return {
        "project_id": project_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "workspace": workspace,
        "current_step": "M1",
        "status": "in_progress",
        "skill_version": SKILL_VERSION,
        "inputs": {
            "theme": None,
            "gameplay": [],
            "art_style": None,
            "background": None,
            "platforms": [],
            "audience": None,
            "research_keywords": {
                "primary_keywords": [],
                "competitor_keywords": [],
                "player_need_keywords": [],
                "negative_keywords": [],
            },
        },
        "research": {
            "sources_path": "research/sources.jsonl",
            "findings_path": "research/findings.md",
            "direction_path": "research/direction.md",
            "source_count": 0,
            "high_reliability_count": 0,
            "medium_reliability_count": 0,
            "low_reliability_count": 0,
        },
        "direction_judgment": {
            "light": None,
            "summary": None,
            "evidence_strength": None,
            "axes": {
                "market_opportunity": {"label": None, "summary": None, "sources": []},
                "player_need_signal": {"label": None, "summary": None, "sources": []},
                "competitor_gap": {"label": None, "summary": None, "sources": []},
            },
            "assumptions_to_validate": [],
            "notes": [],
        },
        "candidates": [],
        "selected_candidate_id": None,
        "concept": {
            "concept_path": "concept.md",
            "shotlist_path": "shotlist.md",
            "direction_hypotheses": {
                "target_players": None,
                "pain_or_thrill": None,
                "competitor_gap": None,
                "viral_hook": None,
            },
            "shotlist": [],
        },
        "art": {
            "prompts_path": "images/prompts.jsonl",
            "engine_provider": None,
            "generated_images": [],
            "iterations": [],
        },
        "video": {
            "storyboard_path": "video/storyboard.md",
            "provider": None,
            "final_video_path": None,
        },
        "report": {
            "md_path": "report/report.md",
            "html_path": "report/report.html",
            "design_style": "auto",
        },
        "claim_labels": {"green": [], "yellow": [], "red": []},
        "errors": [],
        "history": [],
    }


def project_dir(workspace: Path, project_id: str) -> Path:
    return workspace / "outputs" / project_id


def state_path(workspace: Path, project_id: str) -> Path:
    return project_dir(workspace, project_id) / "project_state.json"


def read_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: dict[str, Any], backup: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    state["updated_at"] = now_iso()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_project_dirs(root: Path) -> None:
    for child in ["research", "images", "video", "report"]:
        (root / child).mkdir(parents=True, exist_ok=True)


def merge_patch(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        result = deepcopy(base)
        for key, value in patch.items():
            result[key] = merge_patch(result.get(key), value)
        return result
    return deepcopy(patch)


def append_history(state: dict[str, Any], step: str, event: str, note: str = "") -> None:
    state.setdefault("history", []).append({"time": now_iso(), "step": step, "event": event, "note": note})


def validate_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("current_step") not in VALID_STEPS:
        errors.append("current_step 必须是 M1..M8")
    if state.get("status") not in VALID_STATUS:
        errors.append("status 必须是 in_progress | paused | done | error")
    for key in ["inputs", "research", "direction_judgment", "candidates", "concept", "art", "video", "report", "claim_labels", "errors", "history"]:
        if key not in state:
            errors.append(f"缺少字段: {key}")
    return errors


def summarize(state: dict[str, Any]) -> str:
    direction = state.get("direction_judgment") or {}
    candidates = state.get("candidates") or []
    selected = state.get("selected_candidate_id")
    top = next((item for item in candidates if item.get("id") == selected), candidates[0] if candidates else None)
    lines = [
        f"项目: {state.get('project_id')}",
        f"状态: {state.get('status')} / 当前步骤: {state.get('current_step')}",
        f"方向灯号: {direction.get('light') or '未生成'}",
        f"证据充分度: {direction.get('evidence_strength') or '未生成'}",
        f"Top 候选: {top.get('id') + '｜' + top.get('title') if top else '未生成'}",
        f"下一步建议: 从 {state.get('current_step')} 继续，先读取 project_state.json 与对应产出文件。",
    ]
    return "\n".join(lines)


def cmd_init(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace).expanduser().resolve()
    root = project_dir(workspace, args.project_id)
    ensure_project_dirs(root)
    target = root / "project_state.json"
    if target.exists() and not args.force:
        raise SystemExit(f"状态文件已存在: {target}")
    state = default_state(args.project_id, str(workspace))
    append_history(state, "M1", "project_created", "初始化项目状态")
    write_state(target, state, backup=False)
    print(target)


def cmd_summary(args: argparse.Namespace) -> None:
    print(summarize(read_state(Path(args.state).expanduser().resolve())))


def cmd_validate(args: argparse.Namespace) -> None:
    errors = validate_state(read_state(Path(args.state).expanduser().resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("OK")


def cmd_patch(args: argparse.Namespace) -> None:
    target = Path(args.state).expanduser().resolve()
    state = read_state(target)
    patch = json.loads(args.patch)
    state = merge_patch(state, patch)
    append_history(state, args.step, "state_patch", args.note)
    write_state(target, state)
    print(target)


def cmd_error(args: argparse.Namespace) -> None:
    target = Path(args.state).expanduser().resolve()
    state = read_state(target)
    state["status"] = "error"
    state.setdefault("errors", []).append(
        {"step": args.step, "time": now_iso(), "message": args.message, "retryable": args.retryable}
    )
    append_history(state, args.step, "error", args.message)
    write_state(target, state)
    print(target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="game-greenlight project_state.json 工具")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="创建项目状态")
    init.add_argument("--workspace", default="~/game-greenlight-workspace")
    init.add_argument("--project-id", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    summary = sub.add_parser("summary", help="输出恢复摘要")
    summary.add_argument("state")
    summary.set_defaults(func=cmd_summary)

    validate = sub.add_parser("validate", help="校验状态结构")
    validate.add_argument("state")
    validate.set_defaults(func=cmd_validate)

    patch = sub.add_parser("patch", help="合并 JSON patch")
    patch.add_argument("state")
    patch.add_argument("--patch", required=True, help="JSON 对象字符串")
    patch.add_argument("--step", default="M1")
    patch.add_argument("--note", default="")
    patch.set_defaults(func=cmd_patch)

    error = sub.add_parser("error", help="记录错误")
    error.add_argument("state")
    error.add_argument("--step", required=True)
    error.add_argument("--message", required=True)
    error.add_argument("--retryable", action="store_true")
    error.set_defaults(func=cmd_error)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
