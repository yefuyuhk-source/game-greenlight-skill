#!/usr/bin/env python3
"""本地 JSONL 资产索引工具。"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def append_jsonl(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record.setdefault("created_at", now_iso())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> Iterable[dict[str, object]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="资产库 JSONL 索引")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("index")
    add.add_argument("--record", required=True, help="JSON 对象字符串")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("index")
    list_cmd.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    index = Path(args.index).expanduser()
    if args.command == "add":
        record = json.loads(args.record)
        append_jsonl(index, record)
        print(index)
    elif args.command == "list":
        rows = list(read_jsonl(index))[: args.limit]
        print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
