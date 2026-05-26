# ToAPIs Gemini 图像生成 Provider 集成笔记

## API 端点

- 提交任务：`POST https://toapis.com/v1/images/generations`
- 轮询状态：`GET https://toapis.com/v1/images/generations/{task_id}`
- 模型名：`gemini-2.5-flash-image-preview`（别名 `nano-banana`）

## 认证

```
Authorization: Bearer <TOAPIS_API_KEY>
```

## 请求体

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "prompt": "提示词文本（最长 1000 字符）",
  "size": "9:16",
  "n": 1
}
```

支持的 size：`1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`

## 响应（任务创建）

```json
{
  "id": "tsk_img_xxx",
  "status": "pending",
  "progress": 0
}
```

## 响应（任务完成）

有两种可能格式：

格式 A（2026年实测常见）：
```json
{
  "status": "completed",
  "progress": 100,
  "images": [
    {"url": "https://files.toapis.com/generated/xxx.png"}
  ]
}
```

格式 B（文档旧版）：
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

## 坑

### 1. 必须带 User-Agent 头

Python `urllib.request` 默认不带 `User-Agent`，ToAPIs 直接返回 **403 Forbidden**。

**修复**：所有请求加 `User-Agent: game-greenlight/1.0`。

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "game-greenlight/1.0",
}
```

### 2. 响应格式变化：图片 URL 路径不固定

实际 API 返回有两种格式：

格式 A（2026年实测）：
```json
{
  "status": "completed",
  "images": [{"url": "https://files.toapis.com/generated/xxx.png"}]
}
```

格式 B（文档旧版）：
```json
{
  "status": "completed",
  "progress": 100,
  "result": {
    "type": "image",
    "data": [{"url": "https://files.toapis.com/generated/xxx.png"}]
  }
}
```

**修复**：提取时多路径兼容，依次检查 `images[0].url` → `result.data[0].url` → 顶层 `url/image_url`。gen_image.py 的 `extract_toapis_url()` 已内置此逻辑。

### 3. 出图速度快

实测 5 秒内从提交到完成，轮询间隔 5 秒足够。

## 尺寸映射（game-greenlight 内）

| render_mode | ToAPIs size |
|-------------|------------|
| `mobile_screenshot` | `9:16` |
| `concept_allowed` | `16:9` |
| `production_sheet` | `1:1` |

## 环境变量

API Key 通过 `TOAPIS_API_KEY` 环境变量注入，不要在命令行或代码中拼接明文。
