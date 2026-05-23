#!/usr/bin/env python3
"""检测 M7 HTML 设计后端。

优先使用 modern-minimal-html；不可用时回退到内置结构化卡片 HTML。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_SKILL_ROOTS = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".codex" / "skills",
    Path.home() / ".agents" / "skills",
]


def find_modern_minimal(extra_roots: list[Path] | None = None) -> Path | None:
    roots = [*DEFAULT_SKILL_ROOTS, *(extra_roots or [])]
    for root in roots:
        candidate = root / "modern-minimal-html" / "SKILL.md"
        if candidate.exists():
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="检测 HTML 设计后端")
    parser.add_argument("--root", action="append", default=[], help="额外 skill 根目录")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    extra_roots = [Path(item).expanduser() for item in args.root]
    skill = find_modern_minimal(extra_roots)
    result = {
        "backend": "modern-minimal-html" if skill else "structured-html",
        "modern_minimal_available": bool(skill),
        "skill_path": str(skill) if skill else None,
        "fallback": None if skill else "scripts/md_to_html.py",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if skill:
            print(f"modern-minimal-html available: {skill}")
        else:
            print("modern-minimal-html unavailable; use structured HTML fallback via scripts/md_to_html.py")


if __name__ == "__main__":
    main()
