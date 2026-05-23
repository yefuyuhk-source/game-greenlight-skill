# M5 关键画面提示词模板

默认只生成提示词，不调用图像 API。每条提示词写入 `images/prompts.jsonl`。

画面槽位由 M4 根据 `references/shot_taxonomy.md` 的槽位规则生成，M5 不自行决定画面数量和类型。

## 核心原则：默认生成手游实际截图

M5 的目标不是只做"好看的概念图"，而是帮助团队判断项目是否可行。因此，除明确例外外，每个提示词都必须产出接近"手游实际画面截图"的结果：

- 画面像真实游戏内截图，而不是电影海报、纯概念设定、插画封面。
- 必须能看出 UI 层级、主要操作区域、玩法信息、角色/敌人/资源/按钮位置。
- 构图要服务于玩法可读性，不追求过度电影感。
- 可出现占位 UI 文本，但要避免大量不可读小字。
- 默认比例优先 `16:9` 或 `9:16`，按目标平台选择。
- 提示词必须有足够细节，不能只写"Q版、国风、战斗界面"这类泛描述。

允许例外：

- 宣传主视觉 / key visual（S1）
- 标志性场景图 / 氛围场景（S2）

这些例外需要在 `render_mode` 标为 `concept_allowed`。其他画面默认 `mobile_screenshot`。

## prompts.jsonl 字段

```json
{
  "shot_id": "S1",
  "name": "主视觉 KV",
  "slot_type": "fixed",
  "render_mode": "concept_allowed",
  "exception_reason": "海报级宣传主视觉，非实机截图",
  "purpose": "传达世界观 + 核心卖点",
  "composition": "中央对称 / 16:9 / 视线引导至中心主体",
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

新增字段 `slot_type`：
- `fixed`：固定核心槽位（S1-S6，所有品类强制出图）
- `replacement`：品类替换槽位（S7-S9，按品类查表补充）
- `optional`：可选社交槽位（S10，按品类条件启用）

`render_mode` 可选值：

- `mobile_screenshot`：手游实际画面截图，默认。
- `concept_allowed`：主视觉、宣传图、氛围场景等允许概念化表达。

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

---

## 固定核心槽位提示词模板（S1-S6）

以下 6 张为所有品类强制出图，槽位定义见 `references/shot_taxonomy.md`。

### S1 主视觉 KV

用途：传达世界观+核心卖点，海报级别。

模式：`concept_allowed`

```text
key visual poster for a game concept, {题材}, {美术风格}, clear protagonist or iconic object, cinematic composition, strong atmosphere that conveys the world setting and core selling point, 16:9, high impact, no UI elements
```

### S2 标志性场景图

用途：游戏内代表性场景/世界观大图。

模式：`concept_allowed`

```text
iconic environment concept, {题材} world, {美术风格}, wide establishing shot of a representative in-game location, atmospheric lighting, environmental storytelling through props and architecture, 16:9, no UI, cinematic but grounded in the game's world
```

### S3 主界面

用途：展示玩家进游戏后看到的真实主界面、核心入口和风格卖点。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, {题材} game main menu, {美术风格}, in-game UI, readable gameplay layout, camera facing the main hub background, clear start button in the lower center, mode entrance buttons on the right, resource bar and player avatar on the top, event banner with a small illustrated thumbnail, mission notification badge, settings icon, background shows {核心场景} with small animated details that reveal the world setting, polished mobile UI, consistent icon style, 16:9 or 9:16, no cinematic poster
```

### S4 战斗 / 核心玩法画面

用途：展示核心循环最高频的真实游戏画面。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, {玩法} core gameplay screen, {题材}, {美术风格}, in-game UI, readable gameplay layout, visible lanes or grid with interactive elements, player units placed at different strategic positions, enemies or objectives moving along a readable path, health bars above key targets, skill buttons at bottom right with cooldown rings, resource cost near action buttons, wave progress and timer at top, pause button, selected unit range indicator, damage numbers and status effects, tactical decision moment, clear feedback effects, 16:9 or 9:16
```

### S5 Boss战 / 高潮场景

用途：展示玩法上限和爽感天花板，传播截图级。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, boss battle or climactic gameplay moment, {题材}, {美术风格}, in-game UI, readable gameplay layout, oversized boss or high-stakes encounter with a large segmented health bar, player units in formation around key choke points, skill cooldown buttons glowing at bottom right, danger warning banner, wave timer, boss phase icon, damage numbers, debuff icons, clear attack telegraph on the ground, defensive effects from player units, high tension but still playable, 16:9 or 9:16
```

### S6 角色养成 / 成长系统

用途：长线留存的可视化锚点，展示角色成长和长期目标。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, character progression or upgrade screen, {题材}, {美术风格}, in-game UI, readable gameplay layout, character or unit roster with stats and levels, upgrade tree or skill paths with visible nodes, resource cost near upgrade button, equipment slots or inventory preview, progression bar showing next milestone, selection highlight on active character, consistent icon style, clear feedback on upgrade preview, 16:9 or 9:16
```

---

## 品类替换槽位提示词模板（S7-S9）

以下为按品类查表补充的画面模板。LLM 根据 `references/shot_taxonomy.md` 品类映射表，选择匹配的 2-3 张。

### 二次元角色驱动
- **多角色合影 KV**：`concept_allowed`，群像宣传图，突出角色关系和阵营
- **角色三视图**：`mobile_screenshot`（角色图鉴界面），正面/侧面/背面 + 属性面板
- **抽卡界面**：`mobile_screenshot`，gacha reveal screen，展示特效和角色展示动画定格

### SLG / 策略战争
- **世界大地图**：`mobile_screenshot`，hex or tile-based world map，行军线、领地标记、资源点
- **联盟/外交界面**：`mobile_screenshot`，alliance diplomacy screen，成员列表、科技树、战争状态
- **城建俯瞰图**：`mobile_screenshot`，isometric base layout，建筑等级、资源产出标识

### MMORPG
- **主城/枢纽**：`mobile_screenshot`，crowded city hub，NPC、玩家、传送点、任务板
- **世界观全景**：`concept_allowed`，world panorama establishing shot
- **组队副本**：`mobile_screenshot`，party dungeon entrance or party UI，职业分工可视化

### 自走棋 / 战棋
- **棋盘对局俯视**：`mobile_screenshot`，top-down board view，棋子站位、阵营特效
- **英雄/装备池**：`mobile_screenshot`，hero pool or equipment screen，星级、费用、羁绊图标
- **回合结算**：`mobile_screenshot`，round result screen，伤害统计、排名变化

### 卡牌（构筑型）
- **卡组构筑**：`mobile_screenshot`，deck building interface，卡牌列表、费用曲线、确认按钮
- **对局打牌**：`mobile_screenshot`，card game in play，手牌、费用、对手血量、回合指示
- **卡牌图鉴**：`mobile_screenshot`，card collection gallery，稀有度、收集进度

### Roguelike / Roguelite
- **地图节点选择**：`mobile_screenshot`，node-based map，分支路线、事件/战斗/商店标记
- **Build 界面**：`mobile_screenshot`，ability or relic selection screen，当前 build 组合预览
- **单局成型截图**：`mobile_screenshot`，late-run screenshot showing a powerful build in action

### 开放世界 / 沙盒
- **标志性场景全景**：`concept_allowed`，wide landscape shot
- **探索远景**：`mobile_screenshot`，character in open field，远景 POI 标记、罗盘 UI
- **世界地图**：`mobile_screenshot`，world map with POI icons，已探索/未探索区域

### 模拟经营
- **经营全景俯视**：`mobile_screenshot`，isometric town/business overview，建筑、人流、产出
- **装饰/家园**：`mobile_screenshot`，decoration or housing screen，家具/外观选择、预览
- **订单/任务**：`mobile_screenshot`，order board or task list，客户需求、奖励预览

### 恋爱 / AVG / 视觉小说
- **立绘对话**：`mobile_screenshot`，visual novel dialogue screen，角色立绘、对话框、选项按钮
- **好感度系统**：`mobile_screenshot`，affection/relationship screen，角色好感进度、解锁状态
- **关键剧情 CG**：`concept_allowed`，key story CG illustration

### 休闲 / 三消 / 益智
- **关卡内核心玩法**：`mobile_screenshot`，in-level gameplay，棋盘/操作区域、目标进度、步数
- **地图进度**：`mobile_screenshot`，level map，关卡节点、星级、解锁状态
- **装扮/家园**：`mobile_screenshot`，decoration screen（仅在装扮/家园向时加入）

### 射击 / 动作 / FPS
- **武器特写**：`mobile_screenshot`，weapon inspect or armory screen，属性、稀有度
- **技能释放瞬间**：`mobile_screenshot`，mid-combat ability cast，特效、范围指示器
- **地图标志点**：`mobile_screenshot`，tactical map or spawn selection，据点、队友位置

### 生存 / 建造
- **基地俯瞰**：`mobile_screenshot`，base overview，建筑布局、防御工事、资源储量
- **夜晚危机**：`mobile_screenshot`，night defense or survival moment，光源、敌人、生命值
- **合成/制作界面**：`mobile_screenshot`，crafting menu，配方树、材料需求、制作按钮

### 音游 / 节奏
- **演奏界面**：`mobile_screenshot`，rhythm gameplay，音符轨道、combo 计数、分数
- **歌曲选择**：`mobile_screenshot`，song select screen，难度、封面、排行榜
- **舞台演出**：`concept_allowed`，stage performance visual featuring characters

---

## 可选槽位：系统与社交界面（S10）

启用条件：品类标签命中 `MMORPG` / `社交模拟` / `恋爱` / `休闲（家园/装扮向）`。

模式：`mobile_screenshot`

```text
actual mobile game screenshot, social or guild system screen, {题材}, {美术风格}, in-game UI, readable gameplay layout, friend list or guild member roster, chat panel or interaction buttons, social activity entries like coop mission or gift exchange, player profile card with avatar and stats, notification badges for social events, polished mobile UI, 16:9 or 9:16
```

---

## negative prompt

默认负向提示：

```text
low quality, blurry, unreadable text, broken anatomy, inconsistent UI, watermark, logo, extra fingers, noisy composition
```

如用于 UI 类画面，增加：

```text
tiny unreadable UI text, cluttered interface, inconsistent icon style, poster, cinematic key visual, pure illustration, no UI, mockup-only
```
