# LIFECYCLE — 阶段推进

纲领不动，动的是状态。

读法：Agent 每轮**只加载当前阶段那一节**。三节互不重叠，不要一起读。

状态真源：`RUNTIME/state.json`（不是本文件，不是任何 md）。
本文件规定的是：**什么时候允许改状态，以及改状态前必须验什么**。

---

## 阶段枚举（单一枚举，不许扩展成组合态）

```
BIRTH      只问要学什么。不产出路径。
GROWTH     循环跑起来（第一遍 → 第二遍）。重记录，轻判断。
REGULATED  第三遍起。流程规范化，闸门生效。
```

无第四态。`state.json` 里只有 `stage` 一个字段决定行为，其余字段都是它的证据。

## 状态文件

```json
{
  "schema": 1,
  "stage": "BIRTH",
  "stage_entered_at": null,
  "cycle": 0,
  "last_delivered_cycle": 0,
  "stage_history": []
}
```

写入规范（原子写，硬要求）：

1. 写临时文件 `state.json.tmp` → `fsync` → `os.replace` 到 `state.json`。
2. 写前校验：四个阶段字段类型正确、`stage` 在枚举内、`cycle` 单调不减。
3. 失败不覆盖原文件。宁可本轮不推进，不许写出半个状态。

不存进去的东西（可从别处推导，存了就是冗余真源）：
课程内容、候选清单、承诺、历史路径、任何 deliver 正文。

---

## § stage = BIRTH

你在做的事情只有一件：**拿到锚**。

允许做：
- 问"你要学什么"，最多追问 2 次边界（学到什么程度 / 明确不学什么）
- 把回答原样记进 `anchor.json` 的 `topic_raw`

禁止做：
- 列 syllabus、列章节、给学习顺序
- 预填 `SEEDS/baseline/`
- 在 `RUNTIME/trajectory/cycles/` 下写任何东西
- 承诺任何具体教学内容（"我会先讲 X"）——此时你还不知道学序

收尾（拿到主题后执行，顺序不可换）：
1. 写 `RUNTIME/anchor.json`（`topic_raw` / `goal` / `scope_out` 必填）
2. 写 `RUNTIME/promises.json`（`revision: 0`，`open: []`，`delivered: []`）
3. 建立初始覆盖度地图 `SEEDS/baseline/coverage-map.md`：只写"这个主题下有哪些**区域**"，不写顺序、不写深浅
4. 验推进条件 → 允许则改 `stage=GROWTH`

### BIRTH → GROWTH 的断言（全部为真才可推进）

| # | 断言 | 机检方式 |
|---|---|---|
| A1 | `anchor.json` 存在，且 `topic_raw`/`goal`/`scope_out` 均非空 | `--stage` |
| A2 | `goal` 长度 ≤ 40 字 | `--stage` |
| A3 | `RUNTIME/trajectory/cycles/` 为空（BIRTH 内没偷跑路径） | `--stage` |
| A4 | `coverage-map.md` 存在且至少 3 个区域 | `--stage` |

任何一条不真 → 留在 BIRTH，不要"差不多就推进"。

---

## § stage = GROWTH

你在做的事情：把循环跑通，**同时把流程打磨到能自动化**。

每轮固定两段，顺序不可换：

**第一段 · 兑现**（这轮的主要工作量）
- 关掉 `promises.json` 里 `due_cycle <= cycle` 的承诺，`evidence` 指向 `deliver.md` 的具体小节锚点
- 写 `cycles/<n>/deliver.md`：正文 + 每条知识标注降级档（见 `degrade.md`）
- 逾期承诺未清零 → 本段没完成 → **不许进第二段**

**第二段 · 分叉**
- 按 `fork.md` 列全候选，每个带 `basis` 与 `priority`
- 第一名候选写成新的 open 承诺（带 `due_cycle`）
- 写 `cycles/<n>/fork.json`，含 `excluded` 段（排除了什么、为什么）

GROWTH 的特征是**记录比判断重**：允许候选排得粗糙，但依据和排除必须写下来。这一段的粗糙是有价值的——它给 REGULATED 阶段提供了"哪些判断规则真的有用"的证据。

阶段自检（每轮结束问一次）：
- 我已经跑了 ≥3 轮了吗？
- 最近两轮的分叉，我是不是每次都在做同样的判断，几乎不用想？
- 如果是 → 那些判断可以固化成评分表 → 考虑推进

### GROWTH → REGULATED 的断言（全部为真才可推进）

| # | 断言 | 机检方式 |
|---|---|---|
| B1 | 已完成 cycle ≥ 3，且每轮都有 `deliver.md` + `fork.json` + `checkpoint.json` | `--stage` |
| B2 | 最近 2 轮 `checkpoint.anchor_intact == true` 且链连续 | `--chain` |
| B3 | 最近 2 轮 `fork.json` 每个候选都有 `basis`（非空数组）与 `priority`（0-100 整数） | `--fork` |
| B4 | `promises.json` 逾期数 = 0 | `--promises` |
| B5 | 至少 1 条 `mechanism` 条目满足准入（被 2 轮验证、confidence ≥ 0.6） | `--stage` |

B5 是这条路的关隘：跑三轮还没沉淀出一条机制，说明是在堆内容，不是在长课程。

---

## § stage = REGULATED

你在做的事情：同样的循环，但判断不再靠临场发挥。

与 GROWTH 的差别（只有这四条，别自己加）：

1. **分叉必须走完整评分表**（`fork.md` 的 rubric），不许口头排序。分数写进 `fork.json`。
2. **机制条目的准入需要显式证据**：两个 cycle 编号写进正文，`verified_at` 每用一次更新。
3. **提案闸门生效**：任何想改 `RULES/` 的念头，写 `RUNTIME/proposals/PROP-*.md`，人批了才动。没有 `status: approved` 的提案引用，Agent 不许改纲领。
4. **冲突必须裁决留痕**：两个判断矛盾时按 `conflict.md` 排序，写 `RUNTIME/arbitration/ARB-*.md`。没有裁决记录的矛盾视为未处理。

REGULATED 不是终点，也不许再往上加阶段。流程够了就停在这儿，把力气花在兑现上。

## 不许做的事（全阶段）

- 不许把阶段推进当成"升级奖励"。断言不真就老老实实留在当前阶段。
- 不许跳过断言直接改 `stage`。改 `stage` 的同一个动作里必须能指向断言结果。
- 不许回头看 `stage_history` 决定怎么做。历史只用于抽检，不用于决策。
