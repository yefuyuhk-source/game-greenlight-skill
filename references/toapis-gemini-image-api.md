# ToAPIs Gemini 2.5 Flash 图像生成 API 参考

## 端点

| 操作 | 方法 | URL |
|------|------|-----|
| 提交生成任务 | POST | `https://toapis.com/v1/images/generations` |
| 查询任务状态 | GET | `https://toapis.com/v1/images/generations/{task_id}` |

认证：`Authorization: Bearer TOAPIS_API_KEY`

## 提交请求体

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "prompt": "图像描述（最长 1000 字符）",
  "size": "9:16",
  "n": 1
}
```

## 尺寸选项

| 值 | 用途 | 像素参考 |
|----|------|---------|
| 1:1 | 正方形 / 角色三视图 | 1024x1024 |
| 16:9 | 横向宽屏 / 概念图 | 1792x1024 |
| 9:16 | 竖向长图 / 手游截图 | 1024x1792 |
| 4:3 | 横向标准 | 1365x1024 |
| 3:4 | 竖向标准 | 1024x1365 |

## 创建响应

```json
{
  "id": "task_img_abc123",
  "object": "generation.task",
  "model": "gemini-2.5-flash-image-preview",
  "status": "queued",
  "progress": 0,
  "created_at": 1703884800,
  "metadata": {}
}
```

## 完成响应（推断格式）

```json
{
  "status": "completed",
  "progress": 100,
  "images": [{"url": "https://cdn.toapis.com/..."}]
}
```

## gen_image.py 用法

```bash
export TOAPIS_API_KEY=sk-xxx

# 干跑测试
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis --dry-run

# 实际出图
python scripts/gen_image.py --prompts images/prompts.jsonl --provider toapis --output-dir images/
```

## 尺寸映射规则

gen_image.py 根据 prompt 的 `render_mode` 自动选择尺寸：

| render_mode | size | 说明 |
|-------------|------|------|
| `mobile_screenshot` | 9:16 | 手游截图默认竖屏 |
| `concept_allowed` | 16:9 | 概念图/主视觉横屏 |
| `production_sheet` | 1:1 | 角色三视图正方形 |

## Pitfalls

1. **异步轮询**：提交后返回 task_id，需要轮询等待。gen_image.py 内置了 5 分钟超时 + 每 5 秒轮询。
2. **prompt 截断**：API 限制 prompt 最长 1000 字符，gen_image.py 会自动截断。
3. **响应格式不确定**：ToAPIs 文档未完整展示 completed 状态的响应格式。gen_image.py 做了多路径兼容（`images[0].url` / `data[0].url` / `image_url` / `url`），如果实际格式不同需要调整 `toapis_poll()` 中的解析逻辑。
4. **图生图**：API 支持 `image_urls` 参数，但需要先通过文件上传接口获取 URL。gen_image.py 未实现此功能。
