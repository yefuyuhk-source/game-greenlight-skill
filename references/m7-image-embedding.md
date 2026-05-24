# M7 图片嵌入与更新流程

## 手动生成图片后的嵌入流程

当关键画面由用户手动生成（非 `gen_image.py` 自动出图）时，按以下流程嵌入报告：

### 1. 图片存放位置

将图片复制到 `report/` 目录（与 `report.html` 同级），命名规则：

```
report/s1.png  report/s2.png  ...  report/s7.png
```

### 2. HTML 图片引用

在 `report.html` 的 shot card 中，将占位图替换为：

```html
<img src="s1.png" alt="主界面 · 洞府全景" 
     style="width:100%;display:block;max-height:400px;object-fit:contain;background:var(--bg)">
```

**关键点**：
- 使用相对路径（图片与 HTML 同目录）
- `max-height:400px` 防止大图撑破页面
- `object-fit:contain` 保持比例不拉伸
- 背景色 `var(--bg)` 提供占位底色

### 3. 更新 prompts.jsonl

将每条记录的 `generated_image` 从 `null` 更新为相对路径：

```json
{
  "shot_id": "S1",
  "generated_image": "report/s1.png",
  "exception_reason": null,
  ...
}
```

### 4. 更新 project_state.json

```json
{
  "art": {
    "generated_images": [
      "report/s1.png", "report/s2.png", "report/s3.png",
      "report/s4.png", "report/s5.png", "report/s6.png", "report/s7.png"
    ],
    "engine_provider": "manual",
    "iterations": [
      {
        "time": "2026-05-21T14:24+08:00",
        "event": "images_generated",
        "note": "7关键画面全部手动生成，已嵌入HTML报告"
      }
    ]
  }
}
```

### 5. 更新报告文案

将第6节"视觉物料"的描述从"共7条提示词"更新为"共7张关键画面已全部生成"。

## 注意事项

- **不要 base64 内联**：图片总大小可能达 30-50MB，base64 会使 HTML 膨胀 1.3 倍，导致打开缓慢
- **相对路径原则**：HTML 双击打开时通过文件协议加载，相对路径最可靠
- **同步更新**：嵌入图片后，确保 `prompts.jsonl` 和 `project_state.json` 也同步更新，保持数据一致性
