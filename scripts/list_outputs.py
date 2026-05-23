#!/usr/bin/env python3
"""列出项目产出文件，便于在对话中保留可打开路径。"""

from __future__ import annotations

import argparse
from pathlib import Path


STEP_FILES = {
    "M1": ["inputs.md", "project_state.json"],
    "M2": ["research/sources.jsonl", "research/findings.md", "research/direction.md", "project_state.json"],
    "M3": ["candidates.md", "project_state.json"],
    "M4": ["concept.md", "shotlist.md", "project_state.json"],
    "M5": ["images/prompts.jsonl", "project_state.json"],
    "M6": ["video/storyboard.md", "video/final.mp4", "project_state.json"],
    "M7": ["report/report.md", "report/report.html", "report/html_design_brief.md", "project_state.json"],
    "M8": ["images/prompts.jsonl", "project_state.json"],
}


def existing_outputs(project_dir: Path, step: str | None) -> list[Path]:
    candidates: list[str]
    if step:
        candidates = STEP_FILES.get(step, [])
    else:
        candidates = sorted({item for items in STEP_FILES.values() for item in items})
    paths = []
    for item in candidates:
        path = project_dir / item
        if path.exists():
            paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="列出 game-greenlight 项目产出")
    parser.add_argument("project_dir", help="workspace/outputs/{project_id}")
    parser.add_argument("--step", choices=sorted(STEP_FILES), default=None)
    parser.add_argument("--markdown", action="store_true", help="输出 Markdown 列表")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        raise SystemExit(f"项目目录不存在: {project_dir}")
    paths = existing_outputs(project_dir, args.step)
    if args.markdown:
        if not paths:
            print("- 暂无已生成产物")
        for path in paths:
            print(f"- `{path}`")
    else:
        for path in paths:
            print(path)


if __name__ == "__main__":
    main()
