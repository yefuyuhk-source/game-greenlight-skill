#!/usr/bin/env python3
"""图像 provider 统一入口。

支持的 provider:
- banana: 调用 Banana.dev serverless GPU API（Stable Diffusion）
- 未配置时降级为仅生成提示词
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BANANA_API_URL = "https://api.banana.dev/score/v4/"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_prompts(path: Path) -> list[dict]:
    prompts = []
    if not path.exists():
        raise SystemExit(f"prompts 文件不存在: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            prompts.append(json.loads(line))
    return prompts


def save_prompts(path: Path, prompts: list[dict]) -> None:
    lines = [json.dumps(p, ensure_ascii=False) for p in prompts]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def banana_generate(api_key: str, model_key: str, prompt: str,
                    negative: str = "", width: int = 768, height: int = 768,
                    steps: int = 25, cfg_scale: float = 7.5) -> bytes | None:
    """调用 Banana.dev API 生成单张图像，返回 PNG 字节。"""
    payload = {
        "apiKey": api_key,
        "modelKey": model_key,
        "modelInputs": {
            "prompt": prompt,
            "negative_prompt": negative or "low quality, blurry, watermark, text",
            "num_inference_steps": steps,
            "guidance_scale": cfg_scale,
            "width": width,
            "height": height,
        },
    }
    req = urllib.request.Request(
        BANANA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[banana] API 调用失败: {exc}", file=sys.stderr)
        return None

    outputs = data.get("modelOutputs")
    if not outputs:
        print(f"[banana] 响应无 modelOutputs: {json.dumps(data, ensure_ascii=False)[:200]}", file=sys.stderr)
        return None

    image_b64 = outputs[0].get("image_base64")
    if not image_b64:
        print(f"[banana] modelOutputs 无 image_base64", file=sys.stderr)
        return None

    try:
        return base64.b64decode(image_b64)
    except Exception as exc:
        print(f"[banana] base64 解码失败: {exc}", file=sys.stderr)
        return None


def run_banana(prompts_path: Path, output_dir: Path) -> tuple[list[dict], int]:
    """运行 Banana provider，返回 (更新后的 prompts, 成功张数)。"""
    api_key = os.environ.get("BANANA_API_KEY")
    model_key = os.environ.get("BANANA_MODEL_KEY")
    if not api_key or not model_key:
        raise SystemExit("缺少 BANANA_API_KEY 或 BANANA_MODEL_KEY 环境变量")

    prompts = load_prompts(prompts_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    success = 0

    for index, item in enumerate(prompts):
        shot_id = item.get("shot_id", f"shot-{index}")
        name = item.get("name", shot_id)
        prompt = item.get("prompt_v1") or item.get("prompt") or ""
        negative = item.get("negative") or ""
        render_mode = item.get("render_mode", "mobile_screenshot")

        # 根据 render_mode 调整尺寸
        if render_mode == "production_sheet":
            width, height = 1024, 1024
        elif render_mode == "concept_allowed":
            width, height = 1216, 832
        else:
            width, height = 768, 1344  # 9:16 mobile

        print(f"[banana] 生成 {shot_id} «{name}» ({width}x{height}) ...")
        image_bytes = banana_generate(
            api_key, model_key, prompt, negative,
            width=width, height=height,
        )
        if image_bytes is None:
            print(f"[banana] {shot_id} 生成失败，跳过", file=sys.stderr)
            continue

        filename = f"{shot_id}.png"
        filepath = output_dir / filename
        filepath.write_bytes(image_bytes)
        item["generated_image"] = str(filepath.relative_to(output_dir.parent))
        success += 1
        print(f"[banana] {shot_id} 完成 -> {filepath}")

    save_prompts(prompts_path, prompts)
    return prompts, success


def main() -> None:
    parser = argparse.ArgumentParser(description="图像 provider 入口")
    parser.add_argument("--prompts", required=True, help="images/prompts.jsonl")
    parser.add_argument("--provider", default=os.environ.get("IMAGE_PROVIDER"))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    prompts_path = Path(args.prompts)
    output_dir = Path(args.output_dir) if args.output_dir else prompts_path.parent

    if args.dry_run:
        prompts = load_prompts(prompts_path)
        print(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "provider": args.provider or "none",
                    "prompt_count": len(prompts),
                    "output_dir": str(output_dir),
                    "time": now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not args.provider:
        prompts = load_prompts(prompts_path)
        print(
            json.dumps(
                {
                    "ok": False,
                    "degraded": True,
                    "reason": "未配置图像 provider，已保留提示词交付物",
                    "provider": None,
                    "prompt_count": len(prompts),
                    "output_dir": str(output_dir),
                    "time": now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.provider == "banana":
        updated, success = run_banana(prompts_path, output_dir)
        print(
            json.dumps(
                {
                    "ok": True,
                    "provider": "banana",
                    "total": len(updated),
                    "success": success,
                    "output_dir": str(output_dir),
                    "time": now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    raise SystemExit(
        f"provider '{args.provider}' 尚未安装 adapter。"
        f"支持的 provider: banana"
    )


if __name__ == "__main__":
    main()
