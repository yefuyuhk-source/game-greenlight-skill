# ToAPIs Gemini 图像生成 API 参考

## 支持模型

| Provider alias | 模型名 | 说明 |
|----------------|--------|------|
| `toapis` | `gemini-3.1-flash-image-preview` | Gemini 3.1 Flash（默认） |
| `toapis31` | `gemini-3.1-flash-image-preview` | 显式别名 |
| `--toapis-model gemini-2.5-flash-image-preview` | `gemini-2.5-flash-image-preview` | 回退到 2.5 Flash |

可通过 `--toapis-model` 或 `TOAPIS_MODEL` 环境变量指定任意模型名（优先级：CLI 参数 > 环境变量 > provider 默认）。

## 端点

| 操作 | 方法 | URL |
|------|------|-----|
| 提交生成任务 | POST | `https://toapis.com/v1/images/generations` |
| 查询任务状态 | GET | `https://toapis.com/v1/images/generations/{task_id}` |

## 认证

```
Authorization: Bearer <TOAPIS_API_KEY>
```

API Key 从 https://toapis.com 控制台获取。

## 提交请求体

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "prompt": "图像描述（最长 1000 字符）",
  "size": "9:16",
  "n": 1
}
```

### 尺寸选项

| 值 | 用途 | 像素参考 |
|----|------|---------|
| 1:1 | 正方形 / 角色三视图 | 1024x1024 |
| 16:9 | 横向宽屏 / 概念图 | 1792x1024 |
| 9:16 | 竖向长图 / 手游截图 | 1024x1792 |
| 4:3 | 横向标准 | 1365x1024 |
| 3:4 | 竖向标准 | 1024x1365 |
| 3:2 | 宽幅 | — |
| 2:3 | 窄幅 | — |

## 提交响应（异步任务）

```json
{
  "id": "tsk_img_xxx",
  "object": "generation.task",
  "model": "gemini-2.5-flash-image-preview",
  "status": "pending",
  "progress": 0,
  "created_at": 1700000000,
  "metadata": {}
}
```

## 完成响应

```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "type": "image",
    "data": [
      {"url": "https://files.toapis.com/generated/xxx.png"}
    ]
  }
}
```

图片 URL 路径：`result.data[0].url`（gen_image.py 做了多路径兼容：`images[0].url` / `data[0].url` / `image_url` / `url`）

## gen_image.py 用法

```bash
export TOAPIS_API_KEY=sk-xxx

# Gemini 2.5 Flash（默认）
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis --output-dir images/

# Gemini 3.1 Flash
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis31 --output-dir images/

# 干跑测试
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis --dry-run

# 指定模型（覆盖 provider 默认）
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis --toapis-model gemini-3.1-flash-image-preview
```

## 尺寸映射规则

gen_image.py 根据 prompt 的 `render_mode` 自动选择尺寸：

| render_mode | size | 说明 |
|-------------|------|------|
| `mobile_screenshot` | 9:16 | 手游截图默认竖屏 |
| `concept_allowed` | 16:9 | 概念图/主视觉横屏 |
| `production_sheet` | 1:1 | 角色三视图正方形 |

## 陷阱

### 1. 必须带 User-Agent 头

Python `urllib.request` 默认不发送 `User-Agent`，ToAPIs 会返回 **403 Forbidden**。
curl 默认带 UA 所以没问题，但 Python 代码必须显式添加：

```python
headers={"User-Agent": "game-greenlight/1.0"}
```

轮询接口的 GET 请求也需要带 `Authorization` 和 `User-Agent` 头。

### 2. 异步轮询 + 响应格式不确定

提交后返回 task_id，需要轮询等待。gen_image.py 内置了 5 分钟超时 + 每 5 秒轮询。
响应格式可能因模型版本不同有细微差异（completed 状态下 `images[0].url` vs `result.data[0].url`），
gen_image.py 做了多路径兼容（`images[0].url` / `data[0].url` / `image_url` / `url`），
如果实际格式不同需要调整 `toapis_poll()` 中的解析逻辑。

### 3. prompt 长度限制

API 限制 prompt 最长 1000 字符，gen_image.py 会自动截断。

### 4. 图生图（未实现）

API 支持 `image_urls` 参数用于图生图，但需要先通过文件上传接口获取 URL。gen_image.py 未实现此功能，需要时手动扩展。

## 安全：shot_id 消毒

`prompts.jsonl` 中的 `shot_id` 用于构造输出文件名。未消毒的 `shot_id`（如包含 `../`）可导致路径穿越，将文件写到输出目录之外。

`gen_image.py` 已内置消毒：`re.sub(r"[/\\\\]+", "_", str(shot_id)).strip(".")`

## HTML 报告中图片路径陷阱

`gen_image.py` 将图片路径以项目相对路径存入 `prompts.jsonl`（如 `images/S1.png`），但 HTML 报告输出在 `report/report.html`。

浏览器解析 `<img src="images/S1.png">` 时会请求 `report/images/S1.png`，而非正确的 `images/S1.png`。

**修复**：HTML 生成时需根据输出位置自动加 `../` 前缀，使 src 变为 `../images/S1.png`。`md_to_html.py` 和 `build_html_brief.py` 均已内置此逻辑。
