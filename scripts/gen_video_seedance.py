#!/usr/bin/env python3
"""视频 provider 入口占位。

PRD 将实际视频生成列为可选 D6。本脚本在未配置 provider 时返回降级信息，
避免影响 M1-M7 文字闭环。
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seedance / video provider 入口")
    parser.add_argument("--storyboard", required=True)
    parser.add_argument("--provider", default=os.environ.get("VIDEO_PROVIDER", "seedance"))
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storyboard = Path(args.storyboard)
    if not storyboard.exists():
        raise SystemExit(f"分镜文件不存在: {storyboard}")

    if args.dry_run or not os.environ.get("VIDEO_PROVIDER"):
        print(
            json.dumps(
                {
                    "ok": False,
                    "degraded": True,
                    "reason": "未配置视频 provider，已保留 storyboard.md 交付物",
                    "provider": args.provider,
                    "storyboard": str(storyboard),
                    "output": args.output,
                    "time": now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    raise SystemExit(
        f"provider '{args.provider}' 尚未安装 adapter。v1 主链路不依赖实际视频生成，请先使用 storyboard.md。"
    )


if __name__ == "__main__":
    main()
