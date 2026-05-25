# 结构化英文提示词写作法（4-Layer Method）

> 适用场景：M5 精细润色时，或用户要求**手工写高表现力概念图提示词**时。
> 不替代 `build_prompts.py` 的拼接逻辑——而是在 `prompt_v2` 润色时或手动输出时使用此结构。
>
> 出处：Superpowers Brainstorming 产出的 6 类概念图提示词（S1-S6，Dark Clinic 方向D）

## 核心公式

```
[Layer 1: Header]    一句定调句——锁定风格/画幅/质量
[Layer 2: Scene Blocks]   PATTERN: ALL-CAPS 标签 + 冒号 → 展开该区域
    [Layer 3: Detail Fill]   每元素三层填充：是什么 → 形态特征 → 情绪感受
[Layer 4: MOOD]      收尾情绪锚——用引号一句话定调整个画面的情感
```

---

## Layer 1：Header — 风格锁死句

一句话告诉 AI 这图长什么样，后面所有内容都在这句话的框架内展开。

**模板**：`A [图像类型] for [游戏名/项目], [美术风格], [画幅], [质量标签]`

**必须填充的 5 个槽位**：

| 槽位 | 说明 | 示例 |
|------|------|------|
| 图像类型 | 是什么图 | stunning key art poster / wide establishing shot / mobile game screen mockup / combat screen / boss battle screen / character progression screen |
| 服务对象 | 游戏名+风格 | a dark whimsical mobile game "Dark Clinic" |
| 美术基底 | 艺术风格+材质细节+配色 | Don't Starve art style with scratchy ink lines and cross-hatching, muted earthy palette with a single warm amber lantern glow |
| 画幅 | 比例 | Vertical 9:16 poster composition |
| 质量标签 | 预期质量 | highly polished illustration quality / concept mockup |

**技巧**：这一行承担了"风格锁定"的功能。AI 出图模型的第一印象决定了后续解读——在 Header 里锁死风格倾向、笔触质感、主色调，后面的场景细节就全在这个基调内展开。

---

## Layer 2：Scene Blocks — 区域拆分

把画面按**物理区域**拆成独立块，每块用 `大写标签 + 冒号` 开头。

### 通用模式

```
[区域名/功能名] — [一句话定调]:
    {该区域内的详细描述}
```

### 纯场景图的块拆分示例

```
COMPOSITION — dramatic diagonal split:
    TOP HALF (Night/Danger): ...
    BOTTOM HALF (Day/Safety): ...
    SPLIT LINE: ...
    TITLE AREA: ...
```

```
THE VALLEY: ...
THE CLINIC (center, largest element): ...
SURROUNDINGS: ...
TRANSITION DETAILS: ...
```

### 带 UI 的块拆分示例

```
SCENE (occupies the full background): ...
UI OVERLAY:
    TOP BAR: ...
    LEFT SIDE — Vertical icon column: ...
    RIGHT SIDE — Vertical action buttons: ...
    BOTTOM BAR — Horizontal navigation: ...
    CENTER FLOATING ELEMENT: ...
```

### 块拆分的要点

| 原则 | 说明 |
|------|------|
| **一块一域** | 每个块只讲一个区域，不混合 |
| **空行分隔** | 块与块之间用空行隔开，AI 读作独立思维段落 |
| **全大写标签** | 块标签写 ALL CAPS，目测比正文显眼 |
| **冒号后展开** | 标签后加冒号，直接展开内容 |
| **嵌套用 `-`** | 块内的次级元素用 `-` 列表展开 |
| **重要角色大写** | `CENTER HERO:`, `LEFT:`, `RIGHT:` — 关键角色也全大写 |

---

## Layer 3：Detail Fill — 三层填充法

每个元素写三层——**不写空泛词，写肉眼可见的细节**。

### 三层公式

```
[是什么] + [长什么样/形态特征] + [给观者什么感受]
```

### 示例对比

❌ 空泛：A doctor stands in front of the clinic.

✅ 三层填充：
> A chibi physician with oversized round glasses, holding a glowing mortar and pestle, looking up defiantly at the darkness above. His expression is determined but slightly nervous — brave because he has to be, not because he wants to be.

| 层 | 内容 | 示例 |
|----|------|------|
| ① 是什么 | 身份、外观 | chibi physician with oversized round glasses |
| ② 形态/动作 | 在干什么 | holding a glowing mortar and pestle, looking up defiantly |
| ③ 感受/情绪 | 给人什么感觉 | brave because he has to be, not because he wants to be |

### 环境的三层填充

| 层 | 内容 | 示例 |
|----|------|------|
| ① 是什么 | 场景元素 | A thin layer of supernatural mist hugs the ground |
| ② 如何呈现 | 形态/范围 | low enough to see the scene, thick enough to feel otherworldly |
| ③ 比喻/感受 | 像什么/什么氛围 | will-o'-wisps drift lazily through the air like fireflies but with a blue-white glow |

**要点**：第③层是让 prompt 有画面感的关键——用比喻（like fireflies）、对比（warm vs cool）、感受词（defiantly, protective, unsettling）让描述活起来。

---

## Layer 4：MOOD — 情绪锚

每个 prompt 结束前，用一句带引号的话定义画面情感基调。

### 两种风格

| 类型 | 写法 | 效果 |
|------|------|------|
| **引号名言式**（S1/S2 等概念图） | `MOOD: "这句话定义了画面的情感"` | 控制整体打光方向、饱和度、对比度、角色表情 |
| **设计意图式**（S3-S6 带 UI） | 融入描述末尾：`This screen should trigger the collector's instinct.` | 给 AI 一个"画面应该达到什么效果"的方向 |

### 示例

```
MOOD: "We are small and scared but we're holding the line."
  → 控制：上半部尽最大努力压迫，下半部尽最大努力温暖

MOOD: "This is home."
  → 控制：画面要让人想在游戏里生活

MOOD: This is the "everything on the line" moment.
  → 控制：画面要满、紧张、有庆祝感
```

---

## 完整示例：S1 主视觉 KV

```
[Header]
A stunning hand-drawn key art poster for a dark whimsical mobile game "Dark Clinic",
Don't Starve art style with scratchy ink lines and cross-hatching, muted earthy palette
with a single warm amber lantern glow. Vertical 9:16 poster composition, highly polished
illustration quality.

[Block 1: COMPOSITION]
COMPOSITION — dramatic diagonal split:

TOP HALF (Night/Danger):
The upper portion of the frame is consumed by an inky dark sky with swirling mist.
Silhouettes of eerie monsters with big googly eyes but sharp teeth press in from all
sides — twisted tree branches that look like claws, floating shadow spirits with
scribbly forms, and a gigantic ghostly face forming in the clouds above.

[Block 2: BOTTOM HALF + characters]
BOTTOM HALF (Day/Safety):
A crooked but charming Chinese clinic nestles at the bottom of the frame... Four cute
chibi characters stand in front of the clinic:

- CENTER HERO: A chibi physician with oversized round glasses, holding a glowing mortar
  and pestle, looking up defiantly. His expression is determined but slightly nervous
  — brave because he has to be, not because he wants to be.
- LEFT: A chibi female ghost patient... [etc]

[Block 3: transition detail]
SPLIT LINE:
The dividing line between top and bottom halves is marked by floating yellow talisman
papers that catch the lantern light on one side and fade into shadow on the other.

[Block 4: functional area]
TITLE AREA:
Negative space at the very bottom for game title text overlay.

[MOOD]
MOOD: "We are small and scared but we're holding the line."
The overwhelming scale of the darkness vs the tiny warm clinic creates emotional stakes
— you want to protect this place.
```

---

## 常见错误

| 错误 | 表现 | 修正 |
|------|------|------|
| 跨区混合 | S1 的描述在上半部区域里写了下半部角色的特征 | 每个块只讲自己区域内的内容 |
| 缺乏头层锁风格 | 直接开始写场景，没有定调句 | 先写 Header，再写场景 |
| 只有"是什么"没有"什么感觉" | 堆了一堆元素但没有氛围 | 每个元素补第③层感受 |
| MOOD 太长 | 写了一段议论文 | MOOD 一句话（或一句带一句展开），精炼 |
| 场景描述和 UI 描述混在一起 | 在写 UI 布局时又回去描述场景细节 | SCENE 块单独写场景，UI_OVERLAY 块独立写 UI |