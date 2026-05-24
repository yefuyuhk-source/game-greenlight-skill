# ToAPIs Gemini 图像生成 API 参考

## 端点

| 操作 | 方法 | URL |
|------|------|-----|
| 提交任务 | POST | `https://toapis.com/v1/images/generations` |
| 轮询状态 | GET | `https://toapis.com/v1/images/generations/{task_id}` |

## 认证

```
Authorization: Bearer <TOAPIS_API_KEY>
```

API Key 从 https://toapis.com 控制台获取。

## 提交请求

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "prompt": "...",
  "size": "1:1",
  "n": 1
}
```

模型别名：`nano-banana`

尺寸支持：`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`

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

图片 URL 路径：`result.data[0].url`

## 陷阱

### 1. 必须带 User-Agent 头

Python `urllib.request` 默认不发送 `User-Agent`，ToAPIs 会返回 **403 Forbidden**。

curl 默认带 UA 所以没问题，但 Python 代码必须显式添加：

```python
headers={"User-Agent": "game-greenlight/1.0"}
```

### 2. 图片 URL 在嵌套路径

响应格式是 `result.data[0].url`，不是顶层 `images` 或 `data`。

轮询接口的 GET 请求也需要带 `Authorization` 和 `User-Agent` 头。

### 3. 轮询策略

- Gemini 2.5 Flash 通常 3-10 秒完成
- 建议每 5 秒轮询一次
- 超时设 300 秒（5 分钟）兜底

## game-greenlight 的尺寸映射

| render_mode | ToAPIs size |
|-------------|-------------|
| `mobile_screenshot` | `9:16` |
| `concept_allowed` | `16:9` |
| `production_sheet` | `1:1` |

## HTML 报告中图片路径陷阱

`gen_image.py` 将图片路径以项目相对路径存入 `prompts.jsonl`（如 `images/S1.png`），但 HTML 报告输出在 `report/report.html`。

浏览器解析 `<img src="images/S1.png">` 时会请求 `report/images/S1.png`，而非正确的 `images/S1.png`。

**修复**：HTML 生成时需根据输出位置自动加 `../` 前缀，使 src 变为 `../images/S1.png`。`md_to_html.py` 和 `build_html_brief.py` 均已内置此逻辑。

## 安全：shot_id 消毒

`prompts.jsonl` 中的 `shot_id` 用于构造输出文件名。未消毒的 `shot_id`（如包含 `../`）可导致路径穿越，将文件写到输出目录之外。

`gen_image.py` 已内置消毒：`re.sub(r"[/\\]+", "_", str(shot_id)).strip(".")`
