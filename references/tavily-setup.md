# Tavily 搜索配置

## 前提

Tavily API Key 是 M2 联网调研的**必需**条件。无 key 时 `search_web.py` 会降级返回空结果，导致 `evidence_strength = weak`。

## Key 来源

1. 注册：https://tavily.com
2. 免费额度：每月 1000 次搜索（个人开发者够用）

## 配置方式（按优先级）

`search_web.py` 的 `_load_api_key()` 按以下优先级读取：

**优先级 1：`TAVILY_API_KEY` 环境变量**
```bash
# 由 ~/.zshrc 的 hermes() wrapper 从 Keychain 自动加载
# 或手动设置：export TAVILY_API_KEY=...
```

**优先级 2：macOS Keychain（execute_code 沙箱自动回退）**
```bash
# execute_code 沙箱不继承父 shell 环境变量
# search_web.py 内置 Keychain 回退，自动读取：
security find-generic-password -a $USER -s "hermes:TAVILY_API_KEY" -w
```
> 此回退对 `execute_code` 内调用 search_web.py 自动生效，无需手动配置。

**优先级 3：降级**
```
未找到 API Key → 返回 degraded=True，无结果
```

## 验证

```bash
python3 scripts/search_web.py "test"
# 输出应包含 "degraded": false 和实际结果
```

## 已知问题

- `execute_code` 沙箱不继承 shell 环境变量（已通过 Keychain 回退解决）
- 非 macOS 环境需设置 `TAVILY_API_KEY` 环境变量
