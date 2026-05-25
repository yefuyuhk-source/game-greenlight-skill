#!/usr/bin/env python3
"""图像 provider 统一入口。

支持从品类 YAML 读取 model_route 参数。

支持的 provider:
- toapis:   调用 ToAPIs Gemini 2.5 Flash Image API（异步任务，自动轮询，默认）
- toapis31: 调用 ToAPIs Gemini 3.1 Flash Image API（异步任务，自动轮询）
- banana:   调用 Banana.dev serverless GPU API（Stable Diffusion）
- 未配置时降级为仅生成提示词

可通过 --toapis-model 或 TOAPIS_MODEL 环境变量指定模型名。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TOAPIS_API_URL = "https://toapis.com/v1/images/generations"
BANANA_API_URL = "https://api.banana.dev/score/v4/"

# 尺寸比例 → ToAPIs size 参数映射
ASPECT_MAP = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:3": "4:3",
    "3:4": "3:4",
}


# ── 品类配置加载 ──────────────────────────────────────────────────────


def find_skill_root() -> Path:
    """向上寻找包含 references/ 目录的 skill 根目录。"""
    start = Path(__file__).resolve().parent.parent  # scripts/..
    for candidate in [start, start.parent]:
        ref_dir = candidate / "references"
        if ref_dir.is_dir():
            return candidate
    ref_dir = start / "references"
    if ref_dir.is_dir():
        return start
    raise SystemExit("无法定位 references/ 目录")


def load_category_config(category_name: str) -> dict[str, Any]:
    """从 category_prompts.yaml 加载指定品类的 model_route 等配置。"""
    cat_path = find_skill_root() / "references" / "category_prompts.yaml"
    if not cat_path.exists():
        return {}
    with open(cat_path, "r", encoding="utf-8") as f:
        cat = yaml.safe_load(f) or {}
    # 精确匹配
    config = cat.get(category_name)
    if not config:
        # 模糊匹配
        normalized = category_name.replace("/", "").replace(" ", "")
        for key, val in cat.items():
            if key.replace("/", "").replace(" ", "") == normalized:
                config = val
                break
    return config or {}


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


# ── ToAPIs provider ──────────────────────────────────────────────────


def toapis_submit(api_key: str, prompt: str, size: str = "1:1",
                  model: str = "gemini-2.5-flash-image-preview") -> dict | None:
    """提交图像生成任务，返回任务响应 JSON。"""
    payload = {
        "model": model,
        "prompt": prompt[:1000],  # API 限制 1000 字符
        "size": size,
        "n": 1,
    }
    req = urllib.request.Request(
        TOAPIS_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "game-greenlight/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[toapis] 提交失败: {exc}", file=sys.stderr)
        return None


def toapis_poll(api_key: str, task_id: str) -> dict | None:
    """轮询任务状态，返回最新响应 JSON。"""
    url = f"{TOAPIS_API_URL}/{task_id}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "game-greenlight/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[toapis] 轮询失败: {exc}", file=sys.stderr)
        return None


def toapis_download(url: str) -> bytes | None:
    """下载生成的图片。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "game-greenlight/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except Exception as exc:
        print(f"[toapis] 下载失败: {exc}", file=sys.stderr)
        return None


def resolve_size(render_mode: str) -> str:
    """根据 render_mode 返回 ToAPIs size 参数。"""
    if render_mode == "concept_allowed":
        return "16:9"
    elif render_mode == "production_sheet":
        return "1:1"
    else:  # mobile_screenshot
        return "9:16"


def run_toapis(prompts_path: Path, output_dir: Path, model: str = "") -> tuple[list[dict], int]:
    """运行 ToAPIs provider，返回 (更新后的 prompts, 成功张数)。"""
    api_key = os.environ.get("TOAPIS_API_KEY")
    if not api_key:
        raise SystemExit("缺少 TOAPIS_API_KEY 环境变量")

    # 模型名优先级：参数 > 环境变量 > 默认
    model = model or os.environ.get("TOAPIS_MODEL") or "gemini-2.5-flash-image-preview"

    prompts = load_prompts(prompts_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    success = 0

    for index, item in enumerate(prompts):
        shot_id = item.get("shot_id", f"shot-{index}")
        # 消毒：防止路径穿越
        safe_id = re.sub(r"[/\\]+", "_", str(shot_id)).strip(".")
        name = item.get("name", shot_id)
        prompt = item.get("prompt_v2") or item.get("prompt_v1") or item.get("prompt") or ""
        render_mode = item.get("render_mode", "mobile_screenshot")
        size = resolve_size(render_mode)

        if not prompt.strip():
            print(f"[toapis] {shot_id} «{name}» 提示词为空，跳过", file=sys.stderr)
            continue

        print(f"[toapis] 提交 {shot_id} «{name}» (model={model}, size={size}) ...")
        task = toapis_submit(api_key, prompt, size=size, model=model)
        if task is None:
            print(f"[toapis] {shot_id} 提交失败，跳过", file=sys.stderr)
            continue

        task_id = task.get("id")
        if not task_id:
            print(f"[toapis] 响应无 task id: {json.dumps(task, ensure_ascii=False)[:200]}", file=sys.stderr)
            continue

        # 轮询直到完成
        max_wait = 300  # 最多等 5 分钟
        poll_interval = 5
        elapsed = 0
        image_url = None

        status_data = None
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval

            status_data = toapis_poll(api_key, task_id)
            if status_data is None:
                continue

            status = status_data.get("status", "")
            progress = status_data.get("progress", 0)
            print(f"[toapis] {shot_id} 状态: {status} ({progress}%)")

            if status == "completed":
                # 从响应中提取图片 URL：result.data[0].url
                result = status_data.get("result") or {}
                images = result.get("data") or status_data.get("images") or status_data.get("data") or []
                if isinstance(images, list) and images:
                    first = images[0]
                    if isinstance(first, dict):
                        image_url = first.get("url") or first.get("image_url")
                    elif isinstance(first, str):
                        image_url = first
                break
            elif status == "failed":
                error = status_data.get("error", status_data.get("message", "unknown"))
                print(f"[toapis] {shot_id} 任务失败: {error}", file=sys.stderr)
                break

        if not image_url:
            # 兜底：检查响应的其它常见字段
            image_url = (
                status_data.get("image_url")
                or status_data.get("url")
            ) if status_data else None

        if not image_url:
            print(f"[toapis] {shot_id} 未获取到图片 URL", file=sys.stderr)
            continue

        print(f"[toapis] {shot_id} 下载图片 ...")
        image_bytes = toapis_download(image_url)
        if image_bytes is None:
            continue

        # 保存
        ext = ".png"
        if image_url.endswith(".jpg") or image_url.endswith(".jpeg"):
            ext = ".jpg"
        elif image_url.endswith(".webp"):
            ext = ".webp"

        filename = f"{safe_id}{ext}"
        filepath = output_dir / filename
        filepath.write_bytes(image_bytes)
        item["generated_image"] = str(filepath.relative_to(output_dir.parent))
        success += 1
        print(f"[toapis] {shot_id} 完成 -> {filepath}")

    save_prompts(prompts_path, prompts)
    return prompts, success


# ── Banana provider ──────────────────────────────────────────────────


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
    if not outputs or not isinstance(outputs, list) or not outputs:
        print(f"[banana] 响应无 modelOutputs: {json.dumps(data, ensure_ascii=False)[:200]}", file=sys.stderr)
        return None

    first_output = outputs[0]
    if not isinstance(first_output, dict):
        print(f"[banana] modelOutputs[0] 不是 dict: {type(first_output)}", file=sys.stderr)
        return None

    image_b64 = first_output.get("image_base64")
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
        # 消毒：防止路径穿越
        safe_id = re.sub(r"[/\\]+", "_", str(shot_id)).strip(".")
        name = item.get("name", shot_id)
        prompt = item.get("prompt_v2") or item.get("prompt_v1") or item.get("prompt") or ""
        negative = item.get("negative") or ""
        render_mode = item.get("render_mode", "mobile_screenshot")

        if render_mode == "production_sheet":
            width, height = 1024, 1024
        elif render_mode == "concept_allowed":
            width, height = 1216, 832
        else:
            width, height = 768, 1344

        print(f"[banana] 生成 {shot_id} «{name}» ({width}x{height}) ...")
        image_bytes = banana_generate(
            api_key, model_key, prompt, negative,
            width=width, height=height,
        )
        if image_bytes is None:
            print(f"[banana] {shot_id} 生成失败，跳过", file=sys.stderr)
            continue

        filename = f"{safe_id}.png"
        filepath = output_dir / filename
        filepath.write_bytes(image_bytes)
        item["generated_image"] = str(filepath.relative_to(output_dir.parent))
        success += 1
        print(f"[banana] {shot_id} 完成 -> {filepath}")

    save_prompts(prompts_path, prompts)
    return prompts, success


# ── 主入口 ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="图像 provider 入口")
    parser.add_argument("--prompts", required=True, help="images/prompts.jsonl")
    parser.add_argument("--provider", default=os.environ.get("IMAGE_PROVIDER"))
    parser.add_argument("--toapis-model", default=None,
                        help="ToAPIs 模型名，缺省根据 provider 自动选择")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--category", default=None,
                        help="品类名，从 category_prompts.yaml 读取 model_route 参数")
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
                    "category": args.category,
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

    # 解析 toapis 模型
    toapis_model = args.toapis_model

    if args.provider == "toapis":
        updated, success = run_toapis(prompts_path, output_dir, model=toapis_model)
        print(
            json.dumps(
                {
                    "ok": True,
                    "provider": "toapis",
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

    if args.provider == "toapis31":
        # 缺省使用 gemini-3.1-flash-image-preview，--toapis-model 可覆盖
        updated, success = run_toapis(prompts_path, output_dir,
                                       model=toapis_model or "gemini-3.1-flash-image-preview")
        print(
            json.dumps(
                {
                    "ok": True,
                    "provider": "toapis31",
                    "model": toapis_model or "gemini-3.1-flash-image-preview",
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
        f"支持的 provider: toapis, toapis31, banana"
    )


if __name__ == "__main__":
    main()
