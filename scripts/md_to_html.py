#!/usr/bin/env python3
"""Markdown 到 HTML 报告转换器（modern-minimal-html 兜底版）。

当环境没有 modern-minimal-html skill 时使用。
使用 modern-minimal-html 的 CSS 变量体系和组件模块，生成白底细框高密度 HTML。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path


# ── modern-minimal-html CSS 变量体系 ─────────────────────────────────

CSS_VARIABLES = """:root {
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #666;
  --color-text-tertiary: #999;
  --color-background-primary: #fff;
  --color-background-secondary: #f8f8f8;
  --color-border-tertiary: #e0e0e0;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
  --border-radius-lg: 8px;
  --border-radius-md: 4px;
}
"""

# ── modern-minimal-html 核心组件 CSS ─────────────────────────────────

CORE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font-sans);color:var(--color-text-primary);background:#fafafa;line-height:1.68;padding:2rem 1.5rem}
.wrap{max-width:960px;margin:0 auto;background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:2rem 2.5rem}

/* 标题区 */
.title-block{margin-bottom:1.8rem}
.title-kicker{font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px}
.title-main{font-size:20px;font-weight:500;line-height:1.3;margin-bottom:5px}
.title-sub{font-size:14px;font-weight:400;color:var(--color-text-secondary)}

/* 大区段标题 */
.section-title{font-size:16px;font-weight:600;color:var(--color-text-primary);padding-bottom:.5rem;border-bottom:.5px solid var(--color-border-tertiary);margin-bottom:1.1rem;margin-top:2rem;letter-spacing:.02em}

/* 区块标签 */
.sec-label{font-size:11px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:.07em;padding-bottom:.5rem;border-bottom:.5px solid var(--color-border-tertiary);margin-bottom:1.1rem}

/* 卡片 */
.card{background:var(--color-background-primary);border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:14px 16px;margin-bottom:10px}
.card-title{font-size:13px;font-weight:500;color:var(--color-text-primary);margin-bottom:7px}
.card-body{font-size:12px;color:var(--color-text-secondary);line-height:1.7}

/* 标签 */
.tag{display:inline-block;font-size:10px;font-weight:500;padding:2px 6px;border-radius:3px;margin:2px}
.tb{background:#E6F1FB;color:#0C447C}
.tt{background:#E1F5EE;color:#085041}
.ta{background:#FAEEDA;color:#633806}
.tc{background:#FAECE7;color:#4A1B0C}
.tp{background:#EEEDFE;color:#26215C}
.tg{background:#F2F2F0;color:#555}

/* 表格 */
.table-card{margin:16px 0;overflow:hidden;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);background:var(--color-background-primary)}
.table-scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:500px;font-size:12px}
th,td{padding:8px 10px;border-bottom:.5px solid var(--color-border-tertiary);text-align:left;vertical-align:top;line-height:1.5}
th{background:var(--color-background-secondary);color:var(--color-text-secondary);font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.05em}
tr:last-child td{border-bottom:none}
tr:nth-child(even) td{background:rgba(128,128,128,.02)}

/* 引用块 */
blockquote{margin:14px 0;padding:12px 14px;border-left:3px solid #3266ad;border-radius:var(--border-radius-md);background:var(--color-background-secondary);color:var(--color-text-secondary);font-size:0.95em}

/* 代码 */
code{background:#f0f0f0;color:#333;padding:2px 6px;border-radius:3px;font-size:0.9em;font-family:"SF Mono",monospace}
pre{margin:14px 0;padding:14px;overflow:auto;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);background:var(--color-background-secondary);font-size:12px;line-height:1.6}
pre code{background:none;padding:0}

/* 关键画面卡片 */
.shot-card{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin:14px 0;padding:16px;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);background:var(--color-background-primary)}
.shot-image{display:flex;align-items:center;justify-content:center;min-height:180px;border:.5px dashed var(--color-border-tertiary);border-radius:var(--border-radius-md);background:var(--color-background-secondary);overflow:hidden}
.shot-image img{max-width:100%;max-height:400px;object-fit:contain}
.shot-image .placeholder{color:var(--color-text-tertiary);font-size:12px;text-align:center;padding:24px}
.shot-prompt{display:flex;flex-direction:column;gap:8px}
.shot-prompt-label{color:var(--color-text-secondary);font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}
.shot-prompt-text{flex:1;padding:12px;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);background:var(--color-background-secondary);color:var(--color-text-secondary);font-size:12px;line-height:1.6;white-space:pre-wrap;word-break:break-word;font-family:"SF Mono",monospace}
.copy-btn{align-self:flex-end;padding:4px 10px;border:.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);background:var(--color-background-primary);color:var(--color-text-secondary);font-size:11px;cursor:pointer}
.copy-btn:hover{background:var(--color-background-secondary);color:var(--color-text-primary)}

/* 段落 */
p{margin:8px 0;color:var(--color-text-primary);opacity:0.88;font-size:12px}

/* 要点 */
.bullet{margin:4px 0;padding:6px 8px;font-size:12px;color:var(--color-text-secondary);line-height:1.6}

/* 2 列栅格 */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}

a{color:#3266ad;text-decoration:none}
a:hover{text-decoration:underline}
strong{color:var(--color-text-primary)}

/* 底部 */
.footer{margin-top:24px;color:var(--color-text-tertiary);font-size:11px;text-align:center;border-top:.5px solid var(--color-border-tertiary);padding-top:16px}

@media(max-width:768px){
  body{padding:1rem .5rem}
  .wrap{padding:1.2rem 1rem}
  .shot-card{grid-template-columns:1fr}
  .grid2{grid-template-columns:1fr}
}
"""

TAG_CLASS = {"🟢": "tt", "🟡": "ta", "🔴": "tc"}


# ── Markdown → HTML 转换 ────────────────────────────────────────────


def slugify(text: str, index: int) -> str:
    cleaned = re.sub(r"[^\w一-鿿-]+", "-", text).strip("-").lower()
    return cleaned or f"section-{index}"


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    for emoji, cls in TAG_CLASS.items():
        escaped = escaped.replace(emoji, f'<span class="tag {cls}">{emoji}</span>')
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
        body_html.append(
            "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
        )
    return (
        '<div class="table-card"><div class="table-scroll"><table>\n'
        + head + "\n" + "\n".join(body_html)
        + "\n</table></div></div>"
    )


def shot_card_to_html(shot_id: str, name: str, prompt: str, image_path: str = "") -> str:
    """渲染单张关键画面卡片：左侧图 + 右侧提示词 + 复制按钮。"""
    if image_path:
        image_html = (
            f'<img src="{html.escape(image_path)}" '
            f'alt="{html.escape(name)}" loading="lazy">'
        )
    else:
        image_html = (
            f'<div class="placeholder">[{html.escape(name)}]<br>图片待生成</div>'
        )
    return (
        f'<div class="shot-card" id="shot-{html.escape(shot_id)}">'
        f'<div class="shot-image">{image_html}</div>'
        f'<div class="shot-prompt">'
        f'<span class="shot-prompt-label">{html.escape(shot_id)} · {html.escape(name)}</span>'
        f'<div class="shot-prompt-text">{html.escape(prompt)}</div>'
        f'<button class="copy-btn" '
        f'onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent)">复制提示词</button>'
        f'</div>'
        f'</div>'
    )


def load_prompts(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    prompts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            prompts.append(json.loads(line))
    return prompts


def shot_cards_from_prompts(prompts: list[dict], image_prefix: str = "") -> str:
    if not prompts:
        return ""
    cards = []
    for item in prompts:
        shot_id = item.get("shot_id", "")
        name = item.get("name", shot_id)
        prompt = item.get("prompt_v1") or item.get("prompt") or ""
        image = item.get("generated_image") or ""
        if image and image_prefix:
            image = f"{image_prefix}/{image}" if not image.startswith(("http", "/", "data:")) else image
        cards.append(shot_card_to_html(shot_id, name, prompt, image))
    return "\n".join(cards)


def convert(markdown: str, prompts: list[dict] | None = None, image_prefix: str = "") -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    table_lines: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            out.append(table_to_html(table_lines))
            table_lines = []

    for line in lines:
        # {{SHOT_CARDS}} 占位
        if line.strip() == "{{SHOT_CARDS}}" and prompts:
            flush_table()
            out.append(shot_cards_from_prompts(prompts, image_prefix))
            continue
        if line.startswith("```"):
            if in_code:
                out.append(
                    "<pre><code>"
                    + html.escape("\n".join(code_lines))
                    + "</code></pre>"
                )
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
            table_lines.append(line)
            continue
        flush_table()
        if not line.strip():
            continue
        # 标题
        if line.startswith("# "):
            title = line[2:].strip()
            out.append(
                '<div class="title-block">'
                f'<div class="title-kicker">game-greenlight report</div>'
                f'<div class="title-main">{inline(title)}</div>'
                '</div>'
            )
        elif line.startswith("## "):
            title = line[3:].strip()
            out.append(
                f'<div class="section-title" id="{slugify(title, 0)}">'
                f'{inline(title)}</div>'
            )
        elif line.startswith("### "):
            out.append(
                f'<div class="card"><div class="card-title">'
                f'{inline(line[4:].strip())}</div></div>'
            )
        elif line.startswith("#### "):
            out.append(
                f'<div class="sec-label">{inline(line[5:].strip())}</div>'
            )
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:].strip())}</blockquote>")
        elif line.startswith("- "):
            out.append(f'<div class="bullet">• {inline(line[2:].strip())}</div>')
        elif re.match(r"^\d+\.\s+", line):
            out.append(f'<div class="bullet">{inline(line.strip())}</div>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    flush_table()

    body = "\n".join(out)
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<style>"
        + CSS_VARIABLES
        + CORE_CSS
        + "</style></head><body>\n"
        + '<div class="wrap">\n'
        + body
        + '\n<div class="footer">Generated by game-greenlight · modern-minimal-html fallback</div>'
        + '\n</div>\n</body></html>\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown 转 HTML（modern-minimal-html 兜底）")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument(
        "--prompts",
        default=None,
        help="images/prompts.jsonl 路径，用于注入关键画面卡片",
    )
    args = parser.parse_args()
    source = Path(args.input)
    target = Path(args.output)
    prompts = load_prompts(Path(args.prompts) if args.prompts else None)

    # 计算图片路径前缀：从 HTML 所在目录回到项目根目录
    cwd = Path.cwd()
    try:
        image_prefix = Path(os.path.relpath(cwd, target.parent.resolve()))
    except ValueError:
        image_prefix = Path("..")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        convert(source.read_text(encoding="utf-8"), prompts, str(image_prefix))
    )
    print(target)


if __name__ == "__main__":
    main()
