#!/usr/bin/env python3
"""ffmpeg 拼接入口。

仅在用户显式生成视频并已有片段时使用。脚本不下载或生成视频。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def escape_ffmpeg_path(path: Path) -> str:
    """转义 ffmpeg concat 列表中路径的单引号。"""
    return str(path.resolve()).replace("'", "'\\''")


def main() -> None:
    parser = argparse.ArgumentParser(description="拼接视频片段")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    inputs = [Path(item) for item in args.inputs]
    missing = [str(item) for item in inputs if not item.exists()]
    if missing:
        raise SystemExit("视频片段不存在: " + ", ".join(missing))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(f"file '{escape_ffmpeg_path(item)}'" for item in inputs) + "\n"
    if args.dry_run:
        print(content)
        return

    list_file = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
            handle.write(content)
            list_file = handle.name
        subprocess.run(
            [args.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", str(output)],
            check=True,
        )
    finally:
        if list_file and os.path.exists(list_file):
            os.unlink(list_file)
    print(output)


if __name__ == "__main__":
    main()
