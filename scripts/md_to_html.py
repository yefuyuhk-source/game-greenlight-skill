#!/usr/bin/env python3
"""Markdown 到 HTML 报告转换器。

根据游戏类型匹配 huashu-design 设计风格，动态生成 CSS。
使用 --style <name> 选择风格，默认 pentagram。
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


# ── 设计风格 CSS 变量定义 ──────────────────────────────────────────
# 每种风格只定义 :root 变量，结构 CSS 通过 var() 引用实现风格切换。

STYLE_ROOTS: dict[str, str] = {
    "ash-thorp": """
:root {
  --bg: #0d1117;
  --bg-soft: #161b22;
  --card: rgba(22, 27, 34, 0.94);
  --card-solid: #161b22;
  --ink: #e6edf3;
  --muted: #8b949e;
  --line: #21262d;
  --accent: #f0883e;
  --accent-2: #58a6ff;
  --accent-soft: rgba(240, 136, 62, 0.12);
  --accent-glow: rgba(240, 136, 62, 0.18);
  --yellow: #f59e0b;
  --red: #ef4444;
  --shadow: 0 18px 60px rgba(0, 0, 0, 0.40);
  --shadow-sm: 0 10px 30px rgba(0, 0, 0, 0.25);
  --radius-card: 12px;
  --radius-section: 16px;
  --radius-hero: 20px;
  --font-display: "Orbitron", ui-sans-serif;
  --font-body: "IBM Plex Sans", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, var(--bg) 0%, #111820 100%);
  --hero-gradient: linear-gradient(135deg, rgba(22,27,34,0.95), rgba(13,17,23,0.92));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(240,136,62,0.12), transparent 24rem);
  --topbar-bg: rgba(13, 17, 23, 0.84);
  --topbar-border: rgba(33, 38, 45, 0.78);
}
""",
    "territory-studio": """
:root {
  --bg: #0a0e14;
  --bg-soft: #10161e;
  --card: rgba(16, 22, 30, 0.95);
  --card-solid: #10161e;
  --ink: #c9d1d9;
  --muted: #6e7681;
  --line: #1c2333;
  --accent: #e6b450;
  --accent-2: #39d353;
  --accent-soft: rgba(230, 180, 80, 0.10);
  --accent-glow: rgba(230, 180, 80, 0.14);
  --yellow: #e6b450;
  --red: #ef4444;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.50);
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.40);
  --radius-card: 4px;
  --radius-section: 8px;
  --radius-hero: 8px;
  --font-display: "Share Tech Mono", monospace;
  --font-body: "IBM Plex Mono", monospace;
  --body-gradient: linear-gradient(180deg, var(--bg) 0%, #0d1117 100%);
  --hero-gradient: linear-gradient(135deg, rgba(16,22,30,0.95), rgba(10,14,20,0.92));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(57,211,83,0.08), transparent 24rem);
  --topbar-bg: rgba(10, 14, 20, 0.88);
  --topbar-border: rgba(28, 35, 51, 0.78);
}
""",
    "neo-shen": """
:root {
  --bg: #f7f4f0;
  --bg-soft: #f0ece5;
  --card: rgba(255, 255, 255, 0.88);
  --card-solid: #ffffff;
  --ink: #1a1a1a;
  --muted: #78716c;
  --line: #e7e0d8;
  --accent: #c04a1a;
  --accent-2: #1e3a5f;
  --accent-soft: rgba(192, 74, 26, 0.08);
  --accent-glow: rgba(192, 74, 26, 0.12);
  --yellow: #d97706;
  --red: #dc2626;
  --shadow: 0 12px 48px rgba(0, 0, 0, 0.06);
  --shadow-sm: 0 6px 24px rgba(0, 0, 0, 0.04);
  --radius-card: 16px;
  --radius-section: 24px;
  --radius-hero: 28px;
  --font-display: "Noto Serif SC", serif;
  --font-body: "Noto Sans SC", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, #fbfaf7 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(247,244,240,0.88));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(192,74,26,0.10), transparent 24rem);
  --topbar-bg: rgba(247, 244, 240, 0.84);
  --topbar-border: rgba(231, 224, 216, 0.78);
}
""",
    "sagmeister": """
:root {
  --bg: #faf8ff;
  --bg-soft: #f3f0ff;
  --card: rgba(255, 255, 255, 0.90);
  --card-solid: #ffffff;
  --ink: #1a1523;
  --muted: #6e6480;
  --line: #e4dff0;
  --accent: #ff4d6a;
  --accent-2: #7c3aed;
  --accent-soft: rgba(255, 77, 106, 0.08);
  --accent-glow: rgba(255, 77, 106, 0.14);
  --yellow: #f59e0b;
  --red: #ef4444;
  --shadow: 0 16px 48px rgba(0, 0, 0, 0.06);
  --shadow-sm: 0 8px 24px rgba(0, 0, 0, 0.04);
  --radius-card: 20px;
  --radius-section: 28px;
  --radius-hero: 32px;
  --font-display: "Fraunces", serif;
  --font-body: "Inter", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, #fdfbff 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(250,248,255,0.90));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(124,58,237,0.10), transparent 24rem);
  --topbar-bg: rgba(250, 248, 255, 0.84);
  --topbar-border: rgba(228, 223, 240, 0.78);
}
""",
    "irma-boom": """
:root {
  --bg: #f5f0e8;
  --bg-soft: #ede4d6;
  --card: rgba(255, 255, 255, 0.85);
  --card-solid: #ffffff;
  --ink: #1c1814;
  --muted: #6b5e4e;
  --line: #d9ccb8;
  --accent: #b5343a;
  --accent-2: #d4843a;
  --accent-soft: rgba(181, 52, 58, 0.08);
  --accent-glow: rgba(181, 52, 58, 0.10);
  --yellow: #d4843a;
  --red: #b5343a;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.05);
  --radius-card: 8px;
  --radius-section: 12px;
  --radius-hero: 16px;
  --font-display: "Playfair Display", serif;
  --font-body: "Source Serif 4", serif;
  --body-gradient: linear-gradient(180deg, #f8f4ed 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(245,240,232,0.84));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(181,52,58,0.08), transparent 24rem);
  --topbar-bg: rgba(245, 240, 232, 0.84);
  --topbar-border: rgba(217, 204, 184, 0.78);
}
""",
    "kenya-hara": """
:root {
  --bg: #fbfaf8;
  --bg-soft: #f5f3ef;
  --card: rgba(255, 255, 255, 0.92);
  --card-solid: #ffffff;
  --ink: #1a1a1a;
  --muted: #9ca3af;
  --line: #e8e5e0;
  --accent: #78716c;
  --accent-2: #a8a29e;
  --accent-soft: rgba(120, 113, 108, 0.06);
  --accent-glow: rgba(120, 113, 108, 0.08);
  --yellow: #a16207;
  --red: #dc2626;
  --shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
  --shadow-sm: 0 1px 8px rgba(0, 0, 0, 0.03);
  --radius-card: 0px;
  --radius-section: 0px;
  --radius-hero: 0px;
  --font-display: "Noto Serif JP", serif;
  --font-body: "Noto Sans JP", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, #fefdfb 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(251,250,248,0.90));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(120,113,108,0.04), transparent 24rem);
  --topbar-bg: rgba(251, 250, 248, 0.84);
  --topbar-border: rgba(232, 229, 224, 0.78);
}
""",
    "fathom": """
:root {
  --bg: #f8fafc;
  --bg-soft: #f1f5f9;
  --card: rgba(255, 255, 255, 0.94);
  --card-solid: #ffffff;
  --ink: #0f172a;
  --muted: #64748b;
  --line: #e2e8f0;
  --accent: #2563eb;
  --accent-2: #0891b2;
  --accent-soft: rgba(37, 99, 235, 0.08);
  --accent-glow: rgba(37, 99, 235, 0.12);
  --yellow: #f59e0b;
  --red: #ef4444;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  --shadow-sm: 0 4px 16px rgba(0, 0, 0, 0.04);
  --radius-card: 12px;
  --radius-section: 16px;
  --radius-hero: 20px;
  --font-display: "Inter Tight", ui-sans-serif;
  --font-body: "Inter", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, #fafcfe 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.92));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(37,99,235,0.10), transparent 24rem);
  --topbar-bg: rgba(248, 250, 252, 0.84);
  --topbar-border: rgba(226, 232, 240, 0.78);
}
""",
    "muller-brockmann": """
:root {
  --bg: #1a1a1a;
  --bg-soft: #242424;
  --card: rgba(36, 36, 36, 0.94);
  --card-solid: #242424;
  --ink: #e5e5e5;
  --muted: #737373;
  --line: #333333;
  --accent: #ef4444;
  --accent-2: #a3a3a3;
  --accent-soft: rgba(239, 68, 68, 0.08);
  --accent-glow: rgba(239, 68, 68, 0.10);
  --yellow: #eab308;
  --red: #ef4444;
  --shadow: 0 4px 20px rgba(0, 0, 0, 0.30);
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.20);
  --radius-card: 0px;
  --radius-section: 0px;
  --radius-hero: 0px;
  --font-display: "Helvetica Neue", ui-sans-serif;
  --font-body: "Helvetica Neue", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, var(--bg) 0%, #1e1e1e 100%);
  --hero-gradient: linear-gradient(135deg, rgba(36,36,36,0.95), rgba(26,26,26,0.92));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(239,68,68,0.06), transparent 24rem);
  --topbar-bg: rgba(26, 26, 26, 0.88);
  --topbar-border: rgba(51, 51, 51, 0.78);
}
""",
    "pentagram": """
:root {
  --bg: #f6faf8;
  --bg-soft: #eef8f3;
  --card: rgba(255, 255, 255, 0.92);
  --card-solid: #ffffff;
  --ink: #10201a;
  --muted: #607268;
  --line: #dbe9e2;
  --accent: #16c784;
  --accent-2: #35a7ff;
  --accent-soft: rgba(22, 199, 132, 0.10);
  --accent-glow: rgba(22, 199, 132, 0.14);
  --yellow: #f59e0b;
  --red: #ef4444;
  --shadow: 0 18px 60px rgba(20, 78, 55, 0.10);
  --shadow-sm: 0 10px 30px rgba(20, 78, 55, 0.06);
  --radius-card: 24px;
  --radius-section: 28px;
  --radius-hero: 32px;
  --font-display: "Inter Display", ui-sans-serif;
  --font-body: "Inter", ui-sans-serif;
  --body-gradient: linear-gradient(180deg, #f8fcfa 0%, var(--bg) 42%, #ffffff 100%);
  --hero-gradient: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(239,250,244,0.92));
  --hero-glow: radial-gradient(circle at 92% 10%, rgba(22,199,132,0.14), transparent 24rem);
  --topbar-bg: rgba(248, 252, 250, 0.84);
  --topbar-border: rgba(219, 233, 226, 0.78);
}
""",
}

# ── 结构 CSS（所有风格共用，通过 var() 引用变量） ──────────────

STYLE_BASE = """
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  font-family: var(--font-body), ui-sans-serif, system-ui, -apple-system, sans-serif;
  line-height: 1.68;
  background: var(--body-gradient);
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 14px clamp(18px, 4vw, 52px);
  border-bottom: 1px solid var(--topbar-border);
  background: var(--topbar-bg);
  backdrop-filter: blur(16px);
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 760;
  font-family: var(--font-display), ui-sans-serif;
}
.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 10px 24px var(--accent-glow);
}
.topbar-meta { color: var(--muted); font-size: 13px; }
.layout {
  display: grid;
  grid-template-columns: minmax(0, 220px) minmax(0, 1fr);
  gap: 28px;
  width: min(1320px, calc(100% - 36px));
  margin: 0 auto;
  padding: 34px 0 72px;
}
.toc {
  position: sticky;
  top: 76px;
  align-self: start;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  background: var(--card);
  box-shadow: var(--shadow);
}
.toc-title {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 760;
  text-transform: uppercase;
}
.toc a {
  display: block;
  padding: 8px 10px;
  border-radius: calc(var(--radius-card) * 0.5);
  color: var(--muted);
  text-decoration: none;
  font-size: 13px;
}
.toc a:hover { background: var(--accent-soft); color: var(--ink); }
.report-shell { min-width: 0; }
.hero {
  position: relative;
  overflow: hidden;
  padding: clamp(30px, 5vw, 58px);
  border: 1px solid var(--line);
  border-radius: var(--radius-hero);
  background: var(--hero-gradient), var(--hero-glow);
  box-shadow: var(--shadow);
}
.hero::after {
  content: "";
  position: absolute;
  inset: auto -8% -35% 52%;
  height: 280px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent-glow), rgba(53,167,255,0.08));
  transform: rotate(-8deg);
}
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding: 8px 12px;
  border: 1px solid var(--accent-soft);
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 13px;
  font-weight: 720;
}
h1 {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0;
  color: var(--ink);
  font-family: var(--font-display), ui-sans-serif;
  font-size: clamp(34px, 6vw, 72px);
  line-height: 1.03;
}
.section {
  margin-top: 22px;
  padding: clamp(20px, 3vw, 32px);
  border: 1px solid var(--line);
  border-radius: var(--radius-section);
  background: var(--card);
  box-shadow: var(--shadow-sm);
}
h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 16px;
  color: var(--ink);
  font-family: var(--font-display), ui-sans-serif;
  font-size: clamp(23px, 3vw, 34px);
  line-height: 1.18;
}
h2::before {
  content: "";
  flex: none;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 0 0 6px var(--accent-soft);
}
h3, h4, h5 { margin: 24px 0 10px; color: var(--ink); }
h3 { font-size: 20px; }
h4 { font-size: 17px; }
h5 { font-size: 15px; color: var(--muted); }
p { margin: 10px 0; color: var(--ink); opacity: 0.88; }
.bullet {
  margin: 8px 0;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--card);
  color: var(--ink);
}
.ordered { padding-left: 6px; }
blockquote {
  margin: 16px 0;
  padding: 16px 18px;
  border: 1px solid var(--accent-soft);
  border-left: 5px solid var(--accent);
  border-radius: 18px;
  background: var(--accent-soft);
  color: var(--ink);
}
code {
  background: var(--bg-soft);
  color: var(--accent);
  padding: 2px 6px;
  border-radius: 7px;
  font-size: 0.92em;
}
pre {
  margin: 16px 0;
  padding: 16px;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--bg-soft);
  color: var(--ink);
}
.table-card {
  margin: 18px 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  background: var(--card-solid);
  box-shadow: var(--shadow-sm);
}
.table-scroll { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 620px;
}
th, td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
th {
  background: var(--bg-soft);
  color: var(--muted);
  font-size: 12px;
  font-weight: 760;
  text-transform: uppercase;
}
tr:last-child td { border-bottom: 0; }
td { color: var(--ink); }
/* 关键画面卡片 */
.shot-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 20px;
  margin: 16px 0;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  background: var(--card);
}
.shot-image {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border: 1px dashed var(--line);
  border-radius: var(--radius-card);
  background: var(--bg-soft);
  overflow: hidden;
}
.shot-image img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}
.shot-image .placeholder {
  color: var(--muted);
  font-size: 13px;
  text-align: center;
  padding: 24px;
}
.shot-prompt {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.shot-prompt-label {
  color: var(--muted);
  font-size: 11px;
  font-weight: 760;
  text-transform: uppercase;
}
.shot-prompt-text {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--bg-soft);
  color: var(--ink);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.copy-btn {
  align-self: flex-end;
  padding: 6px 14px;
  border: 1px solid var(--accent);
  border-radius: 999px;
  background: transparent;
  color: var(--accent);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.copy-btn:hover { background: var(--accent); color: #fff; }
.tag-green, .tag-yellow, .tag-red {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.7em;
  min-height: 1.7em;
  margin: 0 2px;
  border-radius: 999px;
  font-size: 0.86em;
}
.tag-green { background: #d9fbe8; color: #087a52; }
.tag-yellow { background: #fff4d6; color: #96620d; }
.tag-red { background: #ffe1e1; color: #b42318; }
a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }
strong { color: var(--ink); }
.footer {
  margin-top: 26px;
  color: var(--muted);
  font-size: 12px;
  text-align: center;
}
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  .toc { position: static; }
  .shot-card { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .topbar { align-items: flex-start; flex-direction: column; }
  .layout { width: min(100% - 24px, 1320px); padding-top: 20px; }
  .hero, .section { border-radius: calc(var(--radius-section) * 0.75); }
}
"""


def style_for(name: str) -> str:
    """返回指定风格的完整 CSS。"""
    root = STYLE_ROOTS.get(name, STYLE_ROOTS["pentagram"])
    return root + STYLE_BASE


STYLE_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("ash-thorp", ("赛博", "科幻", "近未来", "cyber", "sci-fi", "scifi")),
    ("territory-studio", ("废土", "末日", "末世", "生存", "apocalypse", "wasteland")),
    ("neo-shen", ("国风", "武侠", "仙侠", "修仙", "东方", "中式", "民俗", "chinese")),
    ("sagmeister", ("二次元", "动漫", "卡通", "q版", "Q版", "anime", "cartoon")),
    ("irma-boom", ("中世纪", "魔幻", "暗黑", "奇幻", "fantasy", "dark")),
    ("kenya-hara", ("极简", "休闲", "治愈", "清新", "minimal", "cozy")),
    ("fathom", ("经营", "模拟", "策略", "数据", "slg", "strategy", "simulation")),
    ("muller-brockmann", ("恐怖", "微恐", "悬疑", "惊悚", "horror", "thriller")),
]


def style_from_state(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    inputs = state.get("inputs") or {}
    text = " ".join(
        [
            str(inputs.get("art_style") or ""),
            str(inputs.get("theme") or ""),
            str(inputs.get("gameplay") or ""),
            str(inputs.get("background") or ""),
        ]
    ).lower()
    for style, keywords in STYLE_KEYWORDS:
        if any(keyword.lower() in text for keyword in keywords):
            return style
    return None


def resolve_style(style_name: str, state_path: Path | None) -> str:
    if style_name != "auto":
        return style_name if style_name in STYLE_ROOTS else "pentagram"
    return style_from_state(state_path) or "pentagram"


def slugify(text: str, index: int) -> str:
    cleaned = re.sub(r"[^\w一-鿿-]+", "-", text).strip("-").lower()
    return cleaned or f"section-{index}"


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = escaped.replace("🟢", '<span class="tag-green">🟢</span>')
    escaped = escaped.replace("🟡", '<span class="tag-yellow">🟡</span>')
    escaped = escaped.replace("🔴", '<span class="tag-red">🔴</span>')
    return escaped


def parse_table(rows: list[str]) -> tuple[list[str], list[list[str]]]:
    parsed = [row.strip().strip("|").split("|") for row in rows if row.strip()]
    if not parsed:
        return [], []
    headers = [cell.strip() for cell in parsed[0]]
    body = []
    for index, cells in enumerate(parsed[1:], start=1):
        if index == 1 and all(set(cell.strip()) <= {"-", ":", " "} for cell in cells):
            continue
        body.append([cell.strip() for cell in cells])
    return headers, body


def table_to_html(rows: list[str]) -> str:
    headers, body = parse_table(rows)
    if not headers:
        return "\n".join(f"<p>{inline(row)}</p>" for row in rows)
    head = "<tr>" + "".join(f"<th>{inline(cell)}</th>" for cell in headers) + "</tr>"
    body_html = []
    for row in body:
        body_html.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
    table_html = '<div class="table-card"><div class="table-scroll"><table>\n' + head + "\n" + "\n".join(body_html) + "\n</table></div></div>"
    return table_html


def shot_card_to_html(shot_id: str, name: str, prompt: str, image_path: str = "") -> str:
    """渲染单张关键画面卡片：左侧图 + 右侧提示词 + 复制按钮。"""
    if image_path:
        image_html = f'<img src="{html.escape(image_path)}" alt="{html.escape(name)}" loading="lazy">'
    else:
        image_html = f'<div class="placeholder">[{html.escape(name)}]<br>图片待生成</div>'
    return (
        f'<div class="shot-card" id="shot-{html.escape(shot_id)}">'
        f'<div class="shot-image">{image_html}</div>'
        f'<div class="shot-prompt">'
        f'<span class="shot-prompt-label">{html.escape(shot_id)} · {html.escape(name)}</span>'
        f'<div class="shot-prompt-text">{html.escape(prompt)}</div>'
        f'<button class="copy-btn" onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent)">复制提示词</button>'
        f'</div>'
        f'</div>'
    )


def collect_toc(markdown: str) -> list[tuple[str, str]]:
    toc = []
    for index, line in enumerate(markdown.splitlines()):
        if line.startswith("## "):
            title = line[3:].strip()
            toc.append((slugify(title, index), title))
    return toc[:14]


def load_prompts(path: Path | None) -> list[dict]:
    """从 prompts.jsonl 加载关键画面数据。"""
    if not path or not path.exists():
        return []
    prompts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            prompts.append(json.loads(line))
    return prompts


def shot_cards_from_prompts(prompts: list[dict]) -> str:
    """从 prompts 数据生成 shot-cards HTML。"""
    if not prompts:
        return ""
    cards = []
    for item in prompts:
        shot_id = item.get("shot_id", "")
        name = item.get("name", shot_id)
        prompt = item.get("prompt_v1") or item.get("prompt") or ""
        image = item.get("generated_image") or ""
        cards.append(shot_card_to_html(shot_id, name, prompt, image))
    return "\n".join(cards)


def convert(markdown: str, style_name: str = "pentagram", prompts: list[dict] | None = None) -> str:
    lines = markdown.splitlines()
    toc = collect_toc(markdown)
    out: list[str] = []
    table: list[str] = []
    in_code = False
    code_lines: list[str] = []
    section_open = False

    def flush_table() -> None:
        nonlocal table
        if table:
            out.append(table_to_html(table))
            table = []

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            out.append("</section>")
            section_open = False

    for line_no, line in enumerate(lines):
        # 处理 {{SHOT_CARDS}} 占位符
        if line.strip() == "{{SHOT_CARDS}}" and prompts:
            flush_table()
            out.append(shot_cards_from_prompts(prompts))
            continue
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                flush_table()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("|"):
            table.append(line)
            continue
        flush_table()
        if not line.strip():
            continue
        if line.startswith("# "):
            close_section()
            out.append('<section class="hero">')
            out.append('<div class="eyebrow">game-greenlight report</div>')
            out.append(f"<h1>{inline(line[2:].strip())}</h1>")
            out.append("</section>")
        elif line.startswith("## "):
            close_section()
            title = line[3:].strip()
            out.append(f'<section class="section" id="{slugify(title, line_no)}">')
            section_open = True
            out.append(f"<h2>{inline(title)}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{inline(line[4:].strip())}</h3>")
        elif line.startswith("#### "):
            out.append(f"<h4>{inline(line[5:].strip())}</h4>")
        elif line.startswith("##### "):
            out.append(f"<h5>{inline(line[6:].strip())}</h5>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:].strip())}</blockquote>")
        elif line.startswith("- "):
            out.append(f'<div class="bullet">• {inline(line[2:].strip())}</div>')
        elif re.match(r"^\d+\.\s+", line):
            out.append(f'<div class="bullet ordered">{inline(line.strip())}</div>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    flush_table()
    close_section()

    toc_html = '<nav class="toc"><p class="toc-title">目录</p>' + "".join(
        f'<a href="#{anchor}">{inline(title)}</a>' for anchor, title in toc
    ) + "</nav>"
    html_body = (
        '<div class="topbar"><div class="brand"><span class="brand-mark"></span><span>game-greenlight</span></div>'
        '<div class="topbar-meta">Direction screening report</div></div>'
        f'<div class="layout">{toc_html}<main class="report-shell">'
        + "\n".join(out)
        + '<div class="footer">Generated by game-greenlight skill</div></main></div>'
    )
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<style>"
        + style_for(style_name)
        + "</style></head><body>\n"
        + html_body
        + "\n</body></html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown 转 HTML")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--style", default="auto",
                        choices=["auto", *STYLE_ROOTS.keys()],
                        help="设计风格名称；auto 会根据 project_state 匹配 huashu 子风格")
    parser.add_argument("--state", default=None,
                        help="project_state.json 路径；--style auto 时用于匹配设计风格")
    parser.add_argument("--prompts", default=None,
                        help="images/prompts.jsonl 路径，用于注入关键画面卡片")
    args = parser.parse_args()
    source = Path(args.input)
    target = Path(args.output)
    prompts = load_prompts(Path(args.prompts) if args.prompts else None)
    style_name = resolve_style(args.style, Path(args.state) if args.state else None)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(convert(source.read_text(encoding="utf-8"), style_name, prompts), encoding="utf-8")
    print(f"{target}\nstyle={style_name}")


if __name__ == "__main__":
    main()
