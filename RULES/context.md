# CONTEXT — 通用上下文

解决的问题：多轮长出来的东西，下一轮要不要全塞进上下文？全塞会爆，只塞摘要会丢。答案是——**上下文不按"内容"存，按"可复用的机制条目"存**。

借鉴自 ZeoStudio-TenGate 的通用上下文思路：上下文要能与具体任务解绑，才能在别的副本里用。这里落成"机制条目 / 路径"两分。

---

## 一、两种上下文，不许混着写

| 类型 | 定义 | 放哪 | 可继承到副本 | 可回流 |
|---|---|---|---|---|
| `mechanism` | 与主题无关的"怎么做"。删掉课程名字仍然成立 | `SEEDS/mechanisms/<slug>.md` | ✅ 全继承 | ✅ |
| `path` | 这次生长出来的具体路径：章节、顺序、例子、结论 | `RUNTIME/trajectory/` 与本轮 deliver | ❌ 不继承 | ❌ |

判定方法（唯一标准，机械可用）：

> 把这条上下文里所有主题名词换成 XXX，句子还讲得通吗？
> 讲得通 → `mechanism`。讲不通 → `path`。

例：
- "抽象概念要等它依赖的最小可运行例子先讲" → mechanism
- "线性代数要放在梯度下降之前，因为第 3 轮发现学生卡在偏导" → path

## 二、机制条目的形状

`SEEDS/mechanisms/<slug>.md`，frontmatter 固定六项：

```yaml
---
kind: mechanism
claim: 一句话机制（动词开头，可执行）
applies_when: 什么情况下该用
failure_mode: 用错了会怎样（必填，缺这条不算条目）
source: 哪次生长 / 哪份资料逼出来的（指向 cycle 或链接）
confidence: 0.0-1.0
verified_at: ISO8601 最近一次被实际验证
---
正文：展开、反例、边界。
```

`failure_mode` 是必填项。写不出用错了会怎样的"机制"，大概率是口号，不是机制。

## 三、准入：不是提炼出来就能进机制层

要进 `SEEDS/mechanisms/`，必须满足两条：

1. **至少被 2 个不同的 cycle 实际用到并有效**（在正文里写明是哪两轮）
2. `confidence >= 0.6`

不满足的，写在当前 cycle 的 `deliver.md` 里当观察，不进机制层。**未验证的机制一旦进了种子层，就会被继承到所有未来副本**——这是污染，不是积累。

## 四、加载策略：窄取，不整读

每轮需要上下文时，按顺序取，取到够用就停：

1. `anchor.json`（永远是全读，它很短）
2. `promises.json` 的 `open` 段（只读未交付）
3. 最近一个 checkpoint（只读元信息，不读正文）
4. **按本轮分叉的第一名候选**，检索相关 `mechanisms/` 与上几轮 `deliver.md` 的锚点——**只取命中段**，不整篇加载

禁止：为了"有背景"而把历史 deliver 全读一遍。那是把长程优势换成上下文浪费。

## 五、跨副本可携带性标注

每个机制条目在 `SEEDS/MANIFEST.json` 里登记 `portability` 档：

- `universal`：任何课程都能用（怎么问、怎么降级、怎么判优先级）
- `domain`：同领域课程能用（某学科的学序约束）
- `local`：本副本专属，**不许**回流，也不许进种子

`local` 的条目允许暂存在 `mechanisms/`，但 MANIFEST 里必须标 `local`，spawn 时不继承。

## 六、与移植（transplant）的关系

机制条目的回流路径：副本 `SEEDS/mechanisms/` → 提案（`RUNTIME/proposals/`）→ 人批 → 原初库 `SEEDS/mechanisms/`。

**默认单向回流**（副本→原初库）。原初库不主动往已存在的副本推机制更新——否则副本的路径会被人从后面改写。双向是否要开，见 `RUNTIME/open-questions.md`，未定就不做。
