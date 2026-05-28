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

**方式 B：从 config.json 临时导出（常用 workaround）**
如果 key 存在 `~/.tavily/config.json` 但未设置环境变量，每次搜索前执行：
```bash
export TAVILY_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.tavily/config.json'))['api_key'])")
```
> 此命令需在每次搜索前 `&&` 串联，因为子 shell 不继承 export。可简写为一行：
> ```bash
> export TAVILY_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.tavily/config.json'))['api_key'])") && python3 scripts/search_web.py "query" --json
> ```

## 验证

```bash
python3 -c "from tavily import TavilyClient; import os; c=TavilyClient(os.environ['TAVILY_API_KEY']); r=c.search('test', max_results=1); print('OK' if r.get('results') else 'FAIL')"
```

## 已知问题

- `search_web.py` 仅从 `os.environ.get("TAVILY_API_KEY")` 读取，不自动检测 `~/.tavily/config.json`
- 如果 key 在 config 文件中，需要手动 source：`export TAVILY_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.tavily/config.json'))['api_key'])" 2>/dev/null)`