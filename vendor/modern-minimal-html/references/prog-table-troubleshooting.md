# prog-table 对齐故障排查

## 症状速查

用户说法 → 最可能的根因：

| 用户说 | 大概率问题 | 排查优先级 |
|--------|-----------|-----------|
| 「表头正文对不上」「歪的」 | padding 不一致（表头 vs 数据） | ★★★ |
| 「列间距太挤」「第一列和第二列挨太近」 | prog-phase 缺少右 padding | ★★★ |
| 「候选名被挤断换行」 | 第一列 `grid-template-columns` 太窄 | ★★ |
| 「改了列宽没变化」 | 缓存/写错 CSS 选择器 | ★ |
| 「内容和标题对不齐」 | 某列加了 `text-align:center` 但表头是 left | ★★ |

## 三步排查法

### 第一步：查 padding（90% 的问题）

打开 `<style>` 找到 `.prog-phase`、`.prog-cell`、`.prog-header-cell`：

```
.prog-phase      padding: ?    ← 必须 = 10px
.prog-cell       padding: ?    ← 必须 = 10px  
.prog-header-cell padding: ?   ← 必须 = 10px（水平方向）
```

**三者水平 padding 必须相等**，否则文本起始位置偏移。

### 第二步：查列宽

```
.prog-c5 .prog-row{grid-template-columns:150px 80px 80px 60px 1fr}
```

- 短内容列（候选名、分数）给固定 px
- 长文列给 `1fr`
- **不要用 `auto`**——内容变化列宽会重排，挤到相邻列
- 必须加 `white-space:nowrap` 到可能换行的列

### 第三步：查对齐

- **不要**给中间列加 `text-align:center`——表头 left 数据 center 必错位
- 数字列如果一定要居中，表头和数据都要 center（不推荐）

## 常见错误模式

### 错误 1：prog-phase 无 padding

```css
.prog-phase{font-size:11px;font-weight:500;color:var(--color-text-secondary)}
/* ↑ 缺少 padding，表头数据错位 */
```

✅ 修复：
```css
.prog-phase{font-size:11px;font-weight:500;color:var(--color-text-secondary);padding:0 10px}
```

### 错误 2：prog-cell 和 prog-phase padding 不同

```css
.prog-phase{padding:0 10px}
.prog-cell{padding:0 6px}    /* ← 6px ≠ 10px，错位 */
```

✅ 修复：统一为相同值。

### 错误 3：用 auto 做第一列

```css
.prog-c5 .prog-row{grid-template-columns:auto 1fr 1fr 1fr 1fr}
/* auto 列宽随内容浮动，数据变化时可能挤到分数列 */
```

✅ 修复：改固定 px。

### 错误 4：分数列居中但表头没居中

```css
.prog-c5 .prog-cell:nth-child(2){text-align:center}
/* 表头仍是 left，表头字"原始分"在左，数据"8.85"在中间，对不上 */
```

✅ 修复：全部 left 对齐。

## 验证清单

交付前跑一遍：

- [ ] prog-phase padding-x == prog-cell padding-x?
- [ ] prog-header-cell padding-x == 数据行 padding-x?
- [ ] 第一列是固定 px 还是 auto？（推荐固定 px）
- [ ] 所有 `text-align` 在表头和数据行之间一致？
- [ ] `white-space:nowrap` 加在了可能换行的列？
- [ ] 在浏览器里 Cmd+Shift+R 强制刷新？

## 踩坑案例：评分对比表

```
迭代 1: 候选列 60px → 候选名被挤压换行
迭代 2: auto 64px 64px 52px 1fr + 居中 → 表头数据错位，列间距太挤
迭代 3: auto 1fr... + padding-right:12px → 用户说"完全没有变"
迭代 4: 统一 padding 为 0 10px → ✅
```

**教训**：对齐问题 90% 是 padding，先查 padding 再动列宽。
