#!/usr/bin/env python3
"""抓取网页正文和基础元数据。"""

from __future__ import annotations

import argparse
import html
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse


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


# ── URL 安全校验 ──────────────────────────────────────────────────────

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def validate_url(url: str) -> str | None:
    """校验 URL 安全性，返回错误信息或 None（通过）。"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"不允许的 URL scheme: {parsed.scheme}（仅允许 http/https）"
    hostname = parsed.hostname
    if not hostname:
        return "URL 缺少 hostname"
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            addr = ipaddress.ip_address(info[4][0])
            for net in BLOCKED_NETWORKS:
                if addr in net:
                    return f"禁止访问内网地址: {hostname} -> {addr}"
    except (socket.gaierror, ValueError):
        # DNS 解析失败时允许继续（由后续 urlopen 报错）
        pass
    return None


def fetch(url: str, timeout: int, max_chars: int) -> dict[str, object]:
    # URL 安全校验
    url_error = validate_url(url)
    if url_error:
        return {"url": url, "ok": False, "error": url_error, "fetched_at": now_iso()}

    request = urllib.request.Request(url, headers={"User-Agent": "game-greenlight-skill/0.8.5"})
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
