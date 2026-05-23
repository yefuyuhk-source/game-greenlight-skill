#!/usr/bin/env python3
"""列出项目产出文件，便于在对话中保留可打开路径。"""

from __future__ import annotations

import argparse
from pathlib import Path


STEP_FILES = {
    "M1": [
        ("inputs.md", "需求采集文档"),
        ("project_state.json", "项目状态文件"),
    ],
    "M2": [
        ("research/sources.jsonl", "调研数据源"),
        ("research/findings.md", "调研发现报告"),
        ("research/direction.md", "方向判断"),
        ("project_state.json", "项目状态文件"),
    ],
    "M3": [
        ("candidates.md", "选题候选清单"),
        ("project_state.json", "项目状态文件"),
    ],
    "M4": [
        ("concept.md", "立项概念文档"),
        ("shotlist.md", "画面槽位列表"),
        ("project_state.json", "项目状态文件"),
    ],
    "M5": [
        ("images/prompts.jsonl", "关键画面提示词"),
        ("project_state.json", "项目状态文件"),
    ],
    "M6": [
        ("video/storyboard.md", "演示视频分镜"),
        ("video/final.mp4", "演示视频成品"),
        ("project_state.json", "项目状态文件"),
    ],
    "M7": [
        ("report/report.md", "立项报告（Markdown）"),
        ("report/report.html", "立项报告（HTML）"),
        ("report/html_design_brief.md", "HTML 设计 Brief"),
        ("project_state.json", "项目状态文件"),
    ],
    "M8": [
        ("images/prompts.jsonl", "关键画面提示词（迭代版）"),
        ("project_state.json", "项目状态文件"),
    ],
}


def existing_outputs(project_dir: Path, step: str | None) -> list[tuple[str, str]]:
    """返回 (文件名, 中文描述) 列表。"""
    candidates: list[tuple[str, str]]
    if step:
        candidates = STEP_FILES.get(step, [])
    else:
        candidates = sorted(
            {item for items in STEP_FILES.values() for item in items},
            key=lambda x: x[0],
        )
    results = []
    for rel_path, desc in candidates:
        full_path = project_dir / rel_path
        if full_path.exists():
            results.append((str(full_path), desc))
    return results


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
        for full_path, desc in paths:
            print(f"- **{desc}**：`{full_path}`")
    else:
        for full_path, desc in paths:
            print(f"{desc}: {full_path}")


if __name__ == "__main__":
    main()
