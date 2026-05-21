# M5 关键画面提示词模板

默认只生成提示词，不调用图像 API。每条提示词写入 `images/prompts.jsonl`。

## 核心原则：默认生成手游实际截图

M5 的目标不是只做“好看的概念图”，而是帮助团队判断项目是否可行。因此，除明确例外外，每个提示词都必须产出接近“手游实际画面截图”的结果：

- 画面像真实游戏内截图，而不是电影海报、纯概念设定、插画封面。
- 必须能看出 UI 层级、主要操作区域、玩法信息、角色/敌人/资源/按钮位置。
- 构图要服务于玩法可读性，不追求过度电影感。
- 可出现占位 UI 文本，但要避免大量不可读小字。
- 默认比例优先 `16:9` 或 `9:16`，按目标平台选择。
- 提示词必须有足够细节，不能只写“Q版、国风、战斗界面”这类泛描述。

允许例外：

- 宣传主视觉 / key visual
- 大氛围场景图
- 纯场景探索图
- 角色三视图 / 道具设定图

这些例外需要在 `render_mode` 标为 `concept_allowed` 或 `production_sheet`。其他画面默认 `mobile_screenshot`。

## prompts.jsonl 字段

```json
{
  "shot_id": "S1",
  "name": "主界面",
  "render_mode": "mobile_screenshot",
  "exception_reason": null,
  "purpose": "传达世界观氛围 + 核心模式入口",
  "composition": "中央对称 / 16:9 / 视线引导至中心 logo",
  "detail_checklist": ["视角", "UI层级", "关键角色", "玩法状态", "反馈特效", "环境细节"],
  "visual_keywords": ["关键词"],
  "engine_suggestion": "configured-image-provider",
  "prompt_v1": "正向提示词",
  "negative": "负向提示词",
  "reference_assets": [],
  "generated_image": null,
  "iteration_tag": "v1"
}
```

`render_mode` 可选值：

- `mobile_screenshot`: 手游实际画面截图，默认。
- `concept_allowed`: 主视觉、宣传图、氛围场景等允许概念化表达。
- `production_sheet`: 角色三视图、道具设定、风格规范图。

## 手游截图模式硬规则

当 `render_mode = mobile_screenshot`：

- prompt 必须包含：`actual mobile game screenshot`, `in-game UI`, `readable gameplay layout`。
- prompt 必须说明视角：俯视、斜 45 度、横版侧视、主界面 UI、战斗 UI 等。
- prompt 必须包含 2-4 个 UI 元素：资源栏、关卡进度、技能按钮、暂停按钮、单位卡槽、建造按钮、地图格子、血条等。
- prompt 必须写清楚玩家能判断什么：布阵、战斗反馈、资源消耗、成长入口、事件选择等。
- negative prompt 必须加入：`poster, cinematic key visual, pure illustration, no UI, mockup-only, unreadable tiny text`。

## 细节密度硬规则

LLM 生成 `prompt_v1` 时必须尽量具体，默认长度建议：

- 中文提示词不少于 180 字；英文提示词不少于 90 words。
- 不允许只堆风格词，必须描述可被画面呈现的对象、位置、状态和关系。
- 每条 `mobile_screenshot` prompt 至少覆盖 8 类信息中的 6 类：
  1. 游戏类型与画面身份：主界面、战斗、养成、事件、地图等。
  2. 镜头与构图：俯视、45 度、横版侧视、UI 主次层级。
  3. 核心玩法状态：正在布阵、波次进行中、升级选择、事件抉择等。
  4. 关键角色/单位/敌人：数量、位置、朝向、状态。
  5. UI 与交互元素：资源栏、按钮、卡槽、进度条、血条、提示框。
  6. 反馈信息：伤害数字、冷却、选中高亮、建造范围、路径箭头。
  7. 环境与题材细节：场景材质、地标、道具、民俗/科幻/奇幻符号。
  8. 美术约束：色彩、光照、角色比例、不要低幼/不要血腥等边界。
- 对每张图补充 `detail_checklist`，用于自检这条 prompt 覆盖了哪些细节。
- 如果某张图是例外模式，必须写 `exception_reason`，说明为什么不是实机截图。

## 固定 6 张

### S1 主界面

用途：展示玩家进游戏后看到的真实主界面、核心入口和风格卖点。

模式：`mobile_screenshot`

模板：

```text
actual mobile game screenshot, {题材} game main menu, {美术风格}, in-game UI, readable gameplay layout, camera facing the main hub background, clear start button in the lower center, mode entrance buttons on the right, resource bar and player avatar on the top, event banner with a small illustrated thumbnail, mission notification badge, settings icon, background shows {核心场景} with small animated details that reveal the world setting, polished mobile UI, consistent icon style, 16:9 or 9:16, no cinematic poster
```

### S2 主城 / 枢纽

用途：展示玩家长期停留空间、成长系统入口和可点击功能区。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, {题材} hub screen, {美术风格}, in-game UI, readable gameplay layout, isometric or 2.5D view, multiple tappable functional zones with subtle labels, upgrade entrance, shop entrance, mission board, event NPC, resource bar on top, player avatar panel, notification badges, selected building highlight, small path arrows showing navigation, environmental props that reinforce {题材}, 16:9 or 9:16
```

### S3 战斗-普通

用途：说明核心玩法循环的常规战斗体验。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, {玩法} normal battle screen, {题材}, {美术风格}, in-game combat UI, readable gameplay layout, visible lanes or grid with buildable tiles, player units placed at different strategic positions, enemies moving along a readable path, health bars above key enemies, skill buttons at bottom right with cooldown rings, resource cost near build button, wave progress and timer at top, pause button, selected tower range indicator, damage numbers and status effects, tactical decision moment, clear feedback effects, 16:9 or 9:16
```

### S4 战斗-Boss

用途：展示高光、压迫感、传播截图。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, boss battle screen, {题材}, {美术风格}, in-game UI, readable gameplay layout, oversized boss entering from the main path with a large segmented health bar, player units in formation around key choke points, skill cooldown buttons glowing at bottom right, danger warning banner, wave timer, boss phase icon, damage numbers, debuff icons, clear attack telegraph on the ground, defensive effects from player units, high tension but still playable, 16:9 or 9:16
```

### S5 角色三视图

用途：定义角色造型规则和美术统一性。

模式：`production_sheet`

```text
character turnaround sheet, front side back view, {题材}, {美术风格}, consistent proportions, clean silhouette, production concept sheet, neutral background
```

### S6 宣传主视觉

用途：用于内部汇报封面和方向辨识。

模式：`concept_allowed`

```text
key visual poster for a game concept, {题材}, {玩法}, {美术风格}, clear protagonist or iconic object, strong tagline space, cinematic composition, high impact, 16:9
```

## 动态补充画面

- SLG / 4X：世界地图、城池争夺。默认 `mobile_screenshot`，必须包含地图 UI、行军线、资源栏。
- 卡牌：抽卡界面、卡牌构筑界面。默认 `mobile_screenshot`，必须包含卡组、费用、确认按钮。
- 养成：科技树、角色养成页。默认 `mobile_screenshot`，必须包含节点、资源消耗、升级按钮。
- 多角色：角色合影、阵营展示。若是图鉴/编队界面用 `mobile_screenshot`；若是宣传合影用 `concept_allowed`。
- 经营：生产链、店铺/基地俯视图。默认 `mobile_screenshot`，必须包含可点击建筑、产出状态、资源栏。

## negative prompt

默认负向提示：

```text
low quality, blurry, unreadable text, broken anatomy, inconsistent UI, watermark, logo, extra fingers, noisy composition
```

如用于 UI 类画面，增加：

```text
tiny unreadable UI text, cluttered interface, inconsistent icon style, poster, cinematic key visual, pure illustration, no UI, mockup-only
```
