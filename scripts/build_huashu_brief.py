#!/usr/bin/env python3
"""为 huashu-design 生成 M7 HTML 设计 brief。

这个脚本不负责设计 HTML。它把 game-greenlight 的报告内容、项目状态、
提示词/图片资产整理成设计输入，随后由 huashu-design skill 根据该 brief
执行真正的版式、美化和交互设计。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def rel(project_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_dir))
    except ValueError:
        return str(path)


def build_brief(project_dir: Path) -> str:
    state = read_json(project_dir / "project_state.json")
    report_md = project_dir / "report" / "report.md"
    prompts = read_jsonl(project_dir / "images" / "prompts.jsonl")
    inputs = state.get("inputs", {})
    direction = state.get("direction_judgment", {})
    report_title = report_md.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip() if report_md.exists() else state.get("project_id", project_dir.name)

    prompt_rows = []
    for item in prompts:
        image = item.get("generated_image")
        prompt_rows.append(
            {
                "shot_id": item.get("shot_id"),
                "name": item.get("name") or item.get("title"),
                "render_mode": item.get("render_mode"),
                "image": image,
                "image_path": rel(project_dir, project_dir / image) if image else None,
                "prompt": item.get("prompt_v1") or item.get("prompt"),
            }
        )

    return f"""# Huashu Design Brief｜{report_title}

## 任务

请使用 huashu-design 的高保真 HTML 设计流程，为 game-greenlight 的立项报告设计并产出最终 `report/report.html`。

这不是把 Markdown 套固定模板，也不是使用 `md_to_html.py` 的固定布局。请根据项目题材、美术风格、报告内容和素材状态，自主决定版式、信息层级、模块组织、视觉节奏和交互细节。

## 项目上下文

- 项目目录：`{project_dir}`
- Markdown 报告：`{rel(project_dir, report_md)}`
- 目标 HTML：`report/report.html`
- 项目 ID：`{state.get("project_id", project_dir.name)}`
- 题材：{inputs.get("theme")}
- 玩法：{inputs.get("gameplay")}
- 美术风格：{inputs.get("art_style")}
- 目标用户：{inputs.get("audience")}
- 当前灯号：{direction.get("light")}
- 证据充分度：{direction.get("evidence_strength")}

## 标题规则

HTML 首屏主标题只保留项目名称，不要追加“游戏立项方向内部讨论报告”等长后缀。

## 设计目标

- 面向内部运营和策划快速阅读。
- 第一屏让人知道项目名、方向判断、Top1 方案、最大待验证假设。
- 中段重点展示：为什么值得继续验证、候选对比、核心玩法循环、关键画面。
- 关键画面与提示词必须做成可读模块，方便手动复制提示词跑图。
- 有生成图时展示图片；无生成图时展示清晰占位和提示词。
- 不要无意义图表。只有评分对比、证据分布、验证优先级这类确实帮助理解的内容才做可视化。

## 关键画面素材

```json
{json.dumps(prompt_rows, ensure_ascii=False, indent=2)}
```

## 输出要求

- 直接生成一个可离线打开的 `report/report.html`。
- HTML 内联 CSS/JS，不依赖外部资源。
- 保留内容准确性，不改写核心结论。
- 可以重排内容、拆卡片、做导航、做高亮，但不要丢失报告中的关键章节。
- 移动端和桌面端都要可读。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 huashu-design HTML 设计 brief")
    parser.add_argument("project_dir")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not (project_dir / "project_state.json").exists():
        raise SystemExit(f"项目目录缺少 project_state.json: {project_dir}")
    output = Path(args.output).expanduser().resolve() if args.output else project_dir / "report" / "huashu_design_brief.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_brief(project_dir), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
