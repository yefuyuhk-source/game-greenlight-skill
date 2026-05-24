# 本地自定义文件清单

> ⚠️ **重要更新**：自 v0.6.0 起，以下所有文件已合并到 GitHub 主仓库。已安装版本与 GitHub 版本完全一致，无需手动维护差异。

## 历史背景

2026-05-24 之前，已安装版本包含 12 个本地增强文件（不在 GitHub 上游）。经评估全部有价值，已准备合并到 GitHub。合并完成后：

- **GitHub 版本 = 已安装版本** — 完全一致
- **本地项目（Desktop 等）** — 应删除，需要时从 GitHub 重新 clone

## 合并后文件列表（全部已在 GitHub 上）

| 文件 | 类型 | 说明 |
|------|------|------|
| `references/chinese-folklore-minigame-landscape.md` | 调研 | 中式民俗小游戏市场格局调研笔记 |
| `references/design_styles.md` | 参考 | 兜底 HTML 8 种设计风格 CSS 变量库 |
| `references/hybrid-category-mapping.md` | 参考 | 杂交品类映射表（品类不匹配时的手动修正指南） |
| `references/local-customizations.md` | 文档 | 本文件 — 本地文件清单与维护指南 |
| `references/m7-image-embedding.md` | 参考 | M7 报告图片嵌入规范 |
| `references/polish-guidelines.md` | 参考 | 提示词润色质量准则 |
| `references/post-build-fixes.md` | 参考 | 杂交品类后处理指南（负面词冲突、美术风格替换、槽位名修正） |
| `references/prompt-assembly-architecture.md` | 参考 | 三层提示词组装架构说明 |
| `references/tavily-setup.md` | 配置 | Tavily API 配置指南 |
| `references/toapis-gemini-image-api.md` | 参考 | ToAPIs Gemini 图像 API 文档 |
| `references/toapis-image-api.md` | 踩坑笔记 | ToAPIs 图像 API 踩坑笔记（Python urllib 必须带 UA 头否则 403） |
| `references/toapis-provider.md` | 配置 | ToAPIs 提供商配置说明 |

## 版本一致性检查

合并后，已安装版本与 GitHub 版本应完全一致。检查方法：

```bash
# 检查已安装版本 references 目录
ls ~/.hermes/skills/game-greenlight/references/ | wc -l
# 预期：22 个文件（13 基础 + 12 增强 - 1 重复计算）

# 检查 GitHub references 目录
curl -s https://api.github.com/repos/yefuyuhk-source/game-greenlight-skill/contents/references | jq -r '.[].name' | wc -l

# 如果数量一致，说明版本同步
```

## 维护策略（合并后）

| 仓库 | 建议 |
|------|------|
| **GitHub** (`yefuyuhk-source/game-greenlight-skill`) | ✅ **唯一维护源头**，所有更新推这里 |
| **已安装版本** (`~/.hermes/skills/game-greenlight`) | ✅ 与 GitHub 完全一致，无需特殊处理 |
| **本地项目** (Desktop 等) | ❌ 删除，需要时 `git clone https://github.com/yefuyuhk-source/game-greenlight-skill.git` |

## 同步上游更新

当 GitHub 有更新时：

```bash
# 方法 1：直接覆盖已安装版本（推荐）
cd ~/.hermes/skills/game-greenlight
git pull origin main

# 方法 2：如果已安装版本不是 git repo，从 GitHub 重新 clone
rm -rf ~/.hermes/skills/game-greenlight
git clone https://github.com/yefuyuhk-source/game-greenlight-skill.git ~/.hermes/skills/game-greenlight
```

## 添加新本地文件

如果未来发现需要新增本地增强文件：

1. 先评估是否应合并到 GitHub（大多数情况应该）
2. 如果是，按 GitHub 推送流程提交
3. 如果确实只需本地（如含敏感信息），添加到本文件清单并标注 `LOCAL-ONLY`
