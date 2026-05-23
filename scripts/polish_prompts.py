#!/usr/bin/env python3
"""M5 提示词 LLM 二次润色器（参考保留，不再自动调用）。

⚠️ 此脚本已不再由 build_prompts.py 自动调用。
润色逻辑已交由 AI 助手在会话中直接完成（利用当前大模型）。

保留原因：可作为独立工具在非会话场景下使用。
直接调用时需要 OPENAI_API_KEY（或 TOAPIS_API_KEY）环境变量。

用法:
  python scripts/polish_prompts.py --prompts <project>/images/prompts.jsonl
  python scripts/polish_prompts.py --prompts <project>/images/prompts.jsonl --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any


# ── API 配置 ──────────────────────────────────────────────────────────

# 按优先级尝试：OPENAI_BASE_URL → 默认
# 按优先级尝试 API key: OPENAI_API_KEY → TOAPIS_API_KEY
DEFAULT_MODEL = "deepseek-v4-flash"


def get_api_config() -> dict[str, str]:
    """返回 {base_url, api_key, model}。"""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("TOAPIS_API_KEY") or ""
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("POLISH_MODEL", DEFAULT_MODEL)
    return {"base_url": base_url, "api_key": api_key, "model": model}


# ── LLM 调用 ──────────────────────────────────────────────────────────

def call_llm(system_prompt: str, user_prompt: str, config: dict[str, str]) -> str | None:
    """调用 OpenAI-compatible chat completions API。"""
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        f"{config['base_url'].rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "game-greenlight-polish/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[polish] API 调用失败: {exc}", file=sys.stderr)
        return None

    choices = result.get("choices", [])
    if not choices:
        print(f"[polish] API 响应无 choices: {json.dumps(result, ensure_ascii=False)[:200]}", file=sys.stderr)
        return None

    content = choices[0].get("message", {}).get("content", "")
    return content.strip() if content else None


# ── 润色逻辑 ──────────────────────────────────────────────────────────

POLISH_SYSTEM_PROMPT = """You are a specialist in refining game image generation prompts.
You take structured, comma-separated prompt fragments and rewrite them into a single,
cohesive, fluent English prompt for AI image generation.

Rules:
1. Keep ALL key visual elements, UI descriptions, and gameplay information from the original.
2. Remove redundancy — merge similar or overlapping descriptions into clear prose.
3. Maintain the same camera angle, composition, UI layout, and genre identity.
4. Preserve all technical constraints (aspect ratio, no UI for concept shots, etc.).
5. Output ONLY the final prompt text — no explanation, no commentary, no markdown.
6. The output length should be approximately the same as the input (don't add new elements).
7. Keep the "must include" items as explicit mentions in the final prompt."""


def build_polish_prompt(entry: dict[str, Any]) -> str:
    """构建用户侧提示词，提供上下文供 LLM 润色。"""
    parts = [
        f"Shot: {entry.get('shot_id', '')} - {entry.get('name', '')}",
        f"Render mode: {entry.get('render_mode', '')}",
        f"Purpose: {entry.get('purpose', '')}",
        "",
        "Structured prompt fragments to refine:",
        entry.get("prompt_v1", ""),
    ]
    return "\n".join(parts)


def polish_one(entry: dict[str, Any], config: dict[str, str]) -> str | None:
    """对单条 entry 进行 LLM 润色，返回润色后的 prompt。"""
    user_prompt = build_polish_prompt(entry)
    return call_llm(POLISH_SYSTEM_PROMPT, user_prompt, config)


# ── 主流程 ────────────────────────────────────────────────────────────

def load_prompts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"prompts 文件不存在: {path}")
    prompts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            prompts.append(json.loads(line))
    return prompts


def save_prompts(path: Path, prompts: list[dict[str, Any]]) -> None:
    lines = [json.dumps(p, ensure_ascii=False) for p in prompts]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="M5 提示词 LLM 二次润色器")
    parser.add_argument("--prompts", required=True, help="prompts.jsonl 路径")
    parser.add_argument("--dry-run", action="store_true", help="仅预览需润色的槽位（由 AI 助手在会话中手动完成润色，或直接调用本脚本）")
    args = parser.parse_args()

    prompts_path = Path(args.prompts)
    prompts = load_prompts(prompts_path)

    # 找出需润色的槽位
    to_polish = [p for p in prompts if p.get("llm_polish")]
    if not to_polish:
        print("[polish] 没有需要润色的槽位（所有 llm_polish=false）")
        return

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "total_to_polish": len(to_polish),
            "slots": [f"{p['shot_id']} {p['name']}" for p in to_polish],
        }, ensure_ascii=False, indent=2))
        return

    # 检查 API 配置
    config = get_api_config()
    if not config["api_key"]:
        print("[polish] 错误: 未配置 API key。请设置 OPENAI_API_KEY 或 TOAPIS_API_KEY", file=sys.stderr)
        print("[polish] 可跳过此步，直接使用 prompt_v1")
        sys.exit(1)

    success = 0
    for entry in to_polish:
        shot_id = entry.get("shot_id", "?")
        name = entry.get("name", "")
        print(f"[polish] 润色 {shot_id} «{name}» ...", end=" ", flush=True)

        refined = polish_one(entry, config)
        if refined:
            entry["prompt_v2"] = refined
            success += 1
            print("OK")
        else:
            entry["prompt_v2"] = entry.get("prompt_v1", "")
            print("失败，保持 prompt_v1")

    save_prompts(prompts_path, prompts)
    print(f"[polish] 完成: {success}/{len(to_polish)} 条润色成功 -> {prompts_path}")


if __name__ == "__main__":
    main()