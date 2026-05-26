# Tavily 搜索配置

## 前提

Tavily API Key 是 M2 联网调研的**必需**条件。无 key 时 `search_web.py` 会降级返回空结果，导致 `evidence_strength = weak`。

## Key 来源

1. 注册：https://tavily.com
2. 免费额度：每月 1000 次搜索（个人开发者够用）

## 配置方式（按优先级）

**方式 A：环境变量（推荐）**
```bash
# 在 shell profile（.zshrc / .bashrc）中设置即可
# TAVILY_API_KEY 会被 search_web.py 自动读取
```
> ⚠️ 不要在终端命令中直接拼接 API Key 明文。脚本已从 `os.environ` 读取。

**方式 B：配置文件**
Tavily Python SDK 支持读取 `~/.tavily/config.json`，结构见 SDK 文档。

## 验证

```bash
python3 -c "from tavily import TavilyClient; import os; c=TavilyClient(os.environ['TAVILY_API_KEY']); r=c.search('test', max_results=1); print('OK' if r.get('results') else 'FAIL')"
```

## 已知问题

- `search_web.py` 仅从 `os.environ.get("TAVILY_API_KEY")` 读取，不自动检测 `~/.tavily/config.json`
- 如果 key 在 config 文件中，需要手动 source：`export TAVILY_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.tavily/config.json'))['api_key'])" 2>/dev/null)`