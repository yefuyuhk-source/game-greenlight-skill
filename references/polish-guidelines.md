# M5 提示词 LLM 二次润色指南

`build_prompts.py --polish` 输出全部提示词的润色清单后，由 AI 助手在会话中完成润色。
以下为润色质量准则。

## 润色范围（全部槽位）

所有槽位均需二次润色，但策略不同：

| 槽位 | 润色策略 | 核心关注点 |
|------|----------|-----------|
| S1 主视觉 KV | ⭐ 精细润色 | 艺术表现力、冲击力、品牌感 |
| S2 标志性场景图 | ⭐ 精细润色 | 氛围感、文学性描述、世界构建 |
| S3 主界面 | 结构化精简 | UI 描述清晰度、布局可读性 |
| S4 战斗/核心玩法 | 结构化精简 | 操作可读性、反馈信息完整性 |
| S5 Boss战/高潮场景 | ⭐ 精细润色 | 叙述张力、紧张感、动感 |
| S6 角色养成 | 结构化精简 | 系统信息清晰度、层级感 |
| S7-S9 品类替换 | 结构化精简 | 品类特异性、玩法表现力 |
| S10 社交界面 | 结构化精简 | 社交功能清晰度、信息密度 |

> ⭐ 精细润色 = 将碎片拼接改写为流畅自然叙述，加入语气/节奏/连贯性
> 结构化精简 = 去除冗余碎片、合并重叠描述、保持信息准确，不改变基本结构

## 润色质量准则

### 1. 保留全部关键信息
- 视觉元素、角色、场景、构图必须完整保留
- UI 布局和交互元素（有 UI 的场景）不可丢失
- 不得删除或模糊化 "must_include" 中的任何条目

### 2. 去冗余，合成自然叙述
- 合并重叠的描述，避免重复
- 将逗号分隔的碎片列表重写为连贯的自然语言
- 示例对比：
  - 拼接版：`hero composition with dynamic pose, eye-catching focal point, balanced negative space for title placement, fantasy art style, dramatic heroic lighting`
  - 润色版：`Hero composition with a dynamic pose and eye-catching focal point, balanced negative space reserved for title placement. Rendered in a vibrant fantasy art style with dramatic heroic lighting that emphasizes the central figure.`

### 3. 保持技术约束
- `render_mode` 决定 UI 有无：
  - `mobile_screenshot` → 必须保留 UI 元素和 gameplay 可读性
  - `concept_allowed` → 纯概念图，禁止 UI 元素
- `with_ui: false` 的槽位不得加入 HUD、按钮、血条等 UI 描述
- 输出长度应接近输入长度（不要大幅扩充或缩略）

### 4. 按用途调整语气
| 用途 | 语气 |
|------|------|
| KV / 主视觉 | 有冲击力、电影感、突出品牌 |
| 场景图 | 氛围感、叙述性、世界构建 |
| Boss战 | 紧张感、动感、操作可读性并重 |
| 角色展示 | 质感、细节、特征差异化 |

### 5. 格式约束
- 输出纯英文提示词文本，不附加解释、备注或 markdown
- 只输出 prompt 文本本身（与 prompt_v1 相同的语言）
- `must_include` 中的项目必须在最终提示词中以明确措辞体现
- 保持相机角度、构图、品类美术风格与原始拼接版一致

### 6. 写入方式
- 润色后的文本写入 prompts.jsonl 对应 entry 的 `prompt_v2` 字段
- 如果润色失败或不满意，保留 `prompt_v1` 并用 `prompt_v2` = `prompt_v1` 兜底
- 标记 `iteration_tag` 为 `v2`