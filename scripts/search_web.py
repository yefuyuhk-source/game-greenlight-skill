#!/usr/bin/env python3
"""联网搜索 provider 入口。v1 实现 Tavily，缺 key 时输出降级结果。

API Key 读取优先级：
  1. TAVILY_API_KEY 环境变量（由 hermes() wrapper 从 Keychain 加载）
  2. macOS Keychain（execute_code 沙箱中 env var 不可用时）
  3. 降级返回空结果
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _load_api_key() -> str | None:
    """Load TAVILY_API_KEY from env var or macOS Keychain."""
    # 1. Environment variable (set by hermes() wrapper from Keychain)
    key = os.environ.get("TAVILY_API_KEY")
    if key and key.strip():
        return key.strip()

    # 2. macOS Keychain fallback (execute_code sandbox doesn't inherit env vars)
    try:
        result = subprocess.run(
            ["security", "find-generic-password",
             "-a", os.environ.get("USER", os.environ.get("LOGNAME", "yip")),
             "-s", "hermes:TAVILY_API_KEY",
             "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass  # security CLI not available (non-macOS or permission denied)

    return None


def tavily_search(query: str, max_results: int) -> dict[str, Any]:
    api_key = _load_api_key()
    if not api_key:
        return {
            "query": query,
            "provider": "tavily",
            "degraded": True,
            "error": "TAVILY_API_KEY 未配置",
            "fetched_at": now_iso(),
            "results": [],
        }
    payload = json.dumps(
        {
            "query": query,
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        # 安全：屏蔽 Authorization 头中的 API Key
        msg = str(exc).replace(f"Bearer {api_key}", "Bearer ***")
        return {
            "query": query,
            "provider": "tavily",
            "degraded": True,
            "error": msg,
            "fetched_at": now_iso(),
            "results": [],
        }
    results = []
    for item in data.get("results", []):
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "score": item.get("score"),
            }
        )
    return {
        "query": query,
        "provider": "tavily",
        "degraded": False,
        "error": None,
        "fetched_at": now_iso(),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="game-greenlight 搜索入口")
    parser.add_argument("query")
    parser.add_argument("--provider", default=os.environ.get("SEARCH_PROVIDER", "tavily"))
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--jsonl", action="store_true", help="逐行输出结果")
    args = parser.parse_args()

    if args.provider != "tavily":
        raise SystemExit(f"暂不支持搜索 provider: {args.provider}")

    result = tavily_search(args.query, args.max_results)
    if args.jsonl:
        for item in result["results"]:
            print(json.dumps({**item, "query": args.query, "fetched_at": result["fetched_at"]}, ensure_ascii=False))
        if result["degraded"]:
            print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
