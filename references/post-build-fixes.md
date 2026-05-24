# build_prompts.py 后处理修正指南

## 背景

`build_prompts.py` 使用来自 `category_prompts.yaml` 的单一品类配置生成 M5 提示词。当项目品类是**杂交品类**（如「RPG+城池建设」「动作+Roguelike」），选一个品类名跑脚本后，产出需要三方面的手动修正。

## 修正内容

### 1. 负面词冲突（最常出问题）

所选品类的 `negative_extra` 可能与其他玩法组件冲突。典型例子：

| 所选品类 | 反义词 | 冲突的玩法 |
|---------|--------|-----------|
| 模拟经营 | combat-heavy, military | 三国/战争游戏的 S4 战斗、S5 Boss战 |
| 自走棋战棋 | real-time action, FPS perspective | 动作类游戏的 S4 战斗 |
| 休闲三消益智 | dark themes, horror, violence, complex strategy | 任何中度策略/战争游戏 |

**修正方式**：对 S4、S5（以及任何需要战斗/动作表现的槽位），从 `negative` 字段中移除冲突词：

```python
removals = ["combat-heavy", "military"]
for r in removals:
    neg = neg.replace(f"{r}, ", "")
```

同时检查 S1（KV）和 S2（场景图）的负面词——如果它们也不该排除战斗元素，一样处理。

### 2. 美术风格替换

所选品类的 `art_style` 描述该品类的默认画风，与杂交品类的实际画风几乎一定不同。需要替换 `prompt_v1` 中的三段内容：

| 替换目标 | 原内容（举例） | 替换内容（举例） |
|---------|--------------|----------------|
| art_style | `isometric or top-down simulation art, cozy detailed visuals, warm illustration style, Stardew Valley inspired` | `pixel art, retro 16-bit pixel graphics, retro game aesthetic, vibrant pixel textures` |
| ui_aesthetic | `simulation game UI with resource bars at top (gold/supplies/happiness), build menu at bottom` | `pixel game UI with retro-style borders, pixel font text, nostalgic interface elements` |
| color_palette | `warm inviting palette, pastel accents, rich natural tones` | `vibrant retro color palette, high saturation pixel colors, warm nostalgic tones, Three Kingdoms red and gold accents` |

**修正方式**：对 prompts.jsonl 中所有 9 条图做 `str.replace()`。

### 3. S7-S9 槽位名和描述替换

品类层 `replacement_shots` 的槽位名是品类默认的。按 `hybrid-category-mapping.md` 映射后，逐一覆盖：

- `name` — 从品类默认改到杂交映射名称
- `purpose` — 匹配实际用途
- `composition` — 匹配实际构图
- `visual_keywords` — 匹配实际关键词

示例（模拟经营→三国RPG+城建）：

```python
fixes = {
    'S7': { 'name': '城池建设俯瞰', 'purpose': '展示城池建设和布局规划界面' },
    'S8': { 'name': '武将招募系统', 'purpose': '展示抽卡/招募武将功能' },
    'S9': { 'name': '城内交互场景', 'purpose': '展示城池内资源经营和居民互动' },
}
```

## 修正顺序

1. 先改 S7-S9 槽位名 → 确保名称正确
2. 再改 art_style/ui_aesthetic/color_palette → 确保风格正确
3. 最后改负面词冲突 → 确保战斗场景不受限制

## 验证清单

修正后检查 9 条 prompts.jsonl：

- [ ] S4/S5 的 negative 不再包含 combat-heavy、military（或其他品类冲突词）
- [ ] 所有 prompt_v1 中的 art_style 已替换为实际画风
- [ ] S1-S6 的名称匹配 slot_prompts.yaml 规范
- [ ] S7-S9 的名称匹配 hybrid-category-mapping.md 映射

## 当品类命中 13 品类之一时（非杂交）

如果项目完全匹配某个固定品类（如纯「模拟经营」），不需要上述修正。后处理只针对杂交品类。