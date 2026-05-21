#!/usr/bin/env python3
"""抓取网页正文和基础元数据。"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = False
        self.parts: list[str] = []
        self.title: str | None = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = True
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text or self.skip:
            return
        if self._in_title and not self.title:
            self.title = text
        self.parts.append(text)

    def text(self) -> str:
        compact = " ".join(self.parts)
        return re.sub(r"\s+", " ", html.unescape(compact)).strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def fetch(url: str, timeout: int, max_chars: int) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "game-greenlight-skill/0.3.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(max_chars * 4)
            content_type = response.headers.get("content-type")
            final_url = response.geturl()
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"url": url, "ok": False, "error": str(exc), "fetched_at": now_iso()}

    encoding = "utf-8"
    match = re.search(r"charset=([^;]+)", content_type or "", re.I)
    if match:
        encoding = match.group(1).strip()
    markup = raw.decode(encoding, errors="replace")
    parser = TextExtractor()
    parser.feed(markup)
    text = parser.text()[:max_chars]
    return {
        "url": final_url,
        "ok": True,
        "title": parser.title,
        "content_type": content_type,
        "published_at": None,
        "fetched_at": now_iso(),
        "text": text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取 URL 正文")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=8000)
    args = parser.parse_args()
    print(json.dumps(fetch(args.url, args.timeout, args.max_chars), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
