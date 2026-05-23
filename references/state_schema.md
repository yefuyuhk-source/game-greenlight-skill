# project_state.json 状态契约

`project_state.json` 是项目恢复、回退、审计的唯一状态源。所有脚本和 Skill 步骤在开始前读取它，在结束后写回它。Markdown 文件负责给人读，状态文件负责给流程恢复。

## 顶层字段

```json
{
  "project_id": "20260519_scifi_autobattler_001",
  "created_at": "2026-05-19T16:05:20+08:00",
  "updated_at": "2026-05-19T16:42:11+08:00",
  "workspace": "/Users/xx/game-greenlight-workspace",
  "current_step": "M1",
  "status": "in_progress",
  "skill_version": "0.3.1",
  "inputs": {},
  "research": {},
  "direction_judgment": {},
  "candidates": [],
  "selected_candidate_id": null,
  "concept": {},
  "art": {},
  "video": {},
  "report": {},
  "claim_labels": {
    "green": [],
    "yellow": [],
    "red": []
  },
  "errors": [],
  "history": []
}
```

## 枚举

- `current_step`: `M1` 到 `M8`
- `status`: `in_progress`、`paused`、`done`、`error`
- `direction_judgment.light`: `green`、`yellow`、`red`
- `direction_judgment.evidence_strength`: `strong`、`medium`、`weak`
- `claim_labels` / 维度标签: `green`、`yellow`、`red`

## inputs

```json
{
  "theme": "赛博朋克",
  "gameplay": ["自走棋"],
  "art_style": "2.5D 像素霓虹",
  "background": "补充背景",
  "platforms": ["Steam", "iOS"],
  "audience": "目标玩家描述",
  "research_keywords": {
    "primary_keywords": ["赛博朋克 自走棋", "cyberpunk autobattler"],
    "competitor_keywords": ["Teamfight Tactics"],
    "player_need_keywords": ["短局策略", "阵容构筑"],
    "negative_keywords": ["NFT"]
  }
}
```

M1 至少要获得 `theme`、`gameplay`、`art_style`、`platforms`、`audience` 中任意 2 项；否则继续追问，不进入 M2。

## research

```json
{
  "sources_path": "research/sources.jsonl",
  "findings_path": "research/findings.md",
  "direction_path": "research/direction.md",
  "source_count": 13,
  "high_reliability_count": 2,
  "medium_reliability_count": 6,
  "low_reliability_count": 5
}
```

## direction_judgment

```json
{
  "light": "yellow",
  "summary": "方向存在玩家需求与差异化切口，但仍需验证目标玩家规模。",
  "evidence_strength": "medium",
  "axes": {
    "market_opportunity": {
      "label": "green",
      "summary": "市场机会摘要",
      "sources": ["S003"]
    },
    "player_need_signal": {
      "label": "yellow",
      "summary": "玩家需求信号摘要",
      "sources": ["S005"]
    },
    "competitor_gap": {
      "label": "green",
      "summary": "竞品差异空间摘要",
      "sources": ["S010"]
    }
  },
  "assumptions_to_validate": ["待验证假设"],
  "notes": ["注意事项"]
}
```

## candidates

```json
[
  {
    "id": "C1",
    "title": "一句话定位",
    "raw_score": 8.4,
    "weighted_score": 8.1,
    "score_label": "green",
    "status_note": null,
    "dimension_scores": {
      "market_fit": { "score": 8, "label": "green", "sources": ["S003"] },
      "player_attraction": { "score": 9, "label": "green", "sources": ["S005"] },
      "differentiation": { "score": 8, "label": "green", "sources": ["S010"] },
      "visual_impact": { "score": 8, "label": "yellow", "sources": [] },
      "viral_hook": { "score": 7, "label": "yellow", "sources": [] }
    },
    "key_sources": ["S003", "S005", "S010"]
  }
]
```

8 分以上候选必须至少 3 个维度为 `green`，否则折算分封顶 7.5，并写入 `status_note: "高潜但待验证"`。

## concept

```json
{
  "concept_path": "concept.md",
  "shotlist_path": "shotlist.md",
  "fields": {
    "name": "",
    "main_character": "",
    "characters": [],
    "key_scene": "",
    "theme_keywords": [],
    "enemies": [],
    "boss_description": "",
    "landmark_scene": "",
    "featured_character": "",
    "color_preference": ""
  },
  "direction_hypotheses": {
    "target_players": "具体玩家画像",
    "pain_or_thrill": "痛点或爽点",
    "competitor_gap": "竞品没满足的切口",
    "viral_hook": "30 秒内讲清楚的传播钩子"
  },
  "shotlist": [
    { "id": "S1", "name": "主界面", "fixed": true, "engine": null, "image": null }
  ]
}
```

## art / video / report

```json
{
  "art": {
    "prompts_path": "images/prompts.jsonl",
    "engine_provider": null,
    "generated_images": [],
    "iterations": []
  },
  "video": {
    "storyboard_path": "video/storyboard.md",
    "provider": null,
    "final_video_path": null
  },
  "report": {
    "md_path": "report/report.md",
    "html_path": "report/report.html",
    "design_style": "auto"
  }
}
```

`images/prompts.jsonl` 中每条提示词建议包含：

```json
{
  "shot_id": "S1",
  "name": "主界面",
  "render_mode": "mobile_screenshot",
  "exception_reason": null,
  "purpose": "展示真实主界面和核心入口",
  "composition": "16:9，主界面 UI，核心按钮清晰",
  "detail_checklist": ["视角", "UI层级", "关键角色", "玩法状态", "反馈特效", "环境细节"],
  "visual_keywords": ["中式民俗", "微恐", "可读 UI"],
  "engine_suggestion": "configured-image-provider",
  "prompt_v1": "actual mobile game screenshot, in-game UI, readable gameplay layout...",
  "negative": "poster, cinematic key visual, pure illustration, no UI, unreadable tiny text",
  "reference_assets": [],
  "generated_image": null,
  "iteration_tag": "v1"
}
```

除主视觉、宣传图、纯氛围场景、角色/道具设定图外，`render_mode` 默认必须是 `mobile_screenshot`。

## 错误与历史

```json
{
  "errors": [
    { "step": "M2", "time": "2026-05-19T16:20:00+08:00", "message": "Tavily API key missing", "retryable": true }
  ],
  "history": [
    { "time": "2026-05-19T16:20:00+08:00", "step": "M2", "event": "research_done", "note": "13 sources" }
  ]
}
```

每次写入状态前，`scripts/state.py` 必须先创建 `.bak` 备份。
