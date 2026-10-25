# FORK — 分叉

每轮只回答一个问题：**下一步学什么**。答案是候选列表，不是一个答案。

"列全"不是堆量。列全的定义：**每个候选都带依据和优先级，且排除了什么也写下来了。**排不出理由的不算列全（CHARTER 第 4 条）。

---

## 一、候选来源（先扫这四类，再筛，不许凭印象出候选）

| 来源 | 说明 | 标记 |
|---|---|---|
| `gap` | 覆盖度地图上的空白区域 | 必扫 |
| `blocked` | 上一轮兑现时卡住的、没讲透的 | 必扫，优先级最高 |
| `prereq` | 第一名候选的依赖前置（不补就学不下去） | 必扫 |
| `user` | 用户明确提过的兴趣或要求 | 有则必进候选 |

扫完才筛。**不许跳过扫描直接给结论**——跳过扫描是最常见的"看起来列全了"。

## 二、候选的形状

```json
{
  "id": "C-03",
  "claim": "学 X（一句话，可验收）",
  "source": "gap | blocked | prereq | user",
  "basis": [
    "coverage-map.md#区域B 空洞",
    "cycles/0002/deliver.md#sec-3 提到但没展开"
  ],
  "priority": 78,
  "cost": 2,
  "risk": "low | medium | high",
  "rubric": { "gap_value": 8, "prereq_blocking": 9, "user_alignment": 6, "cost_fit": 7 },
  "excluded": null
}
```

硬要求：

- `basis` 空数组 = 候选无效，直接删掉，不许进列表充数
- `basis` 必须指向**可查的东西**（文件#锚点、覆盖度区域、上一轮 deliver 小节），不许写"一般来说""经验上"
- `priority` 是 0-100 整数，必须由 `rubric` 算出来，不许拍脑袋给
- `excluded` 非 null 的候选保留在文件里，但不算进候选列表——**排除要留痕**

## 三、评分表（GROWTH 粗排可用印象，REGULATED 必须算分）

四个维度，各 0-10，加权：

```
priority = round(
    0.35 * gap_value          # 补的是不是真空洞（覆盖度地图上真没有的）
  + 0.25 * prereq_blocking    # 不学它，后面多少东西学不动
  + 0.25 * user_alignment     # 跟 anchor.goal / 用户原话的贴合度
  + 0.15 * cost_fit           # 10 - cost*2，越便宜越高
)
```

约束：

- 同分时，`blocked` 来源的候选胜出
- 任何候选若与 `anchor.scope_out` 冲突，直接 `excluded`，不参与排序
- `risk: high` 的候选若排第一，必须写明"要什么前置条件才敢教"

## 四、fork.json 的文件形状

`RUNTIME/trajectory/cycles/<n>/fork.json`：

```json
{
  "cycle": 3,
  "stage": "GROWTH",
  "scanned": ["gap", "blocked", "prereq", "user"],
  "candidates": [ ... ],
  "excluded": [
    { "id": "C-05", "claim": "...", "reason": "与 scope_out 冲突", "basis": "..." }
  ],
  "chosen": "C-03",
  "why_chosen": "priority 最高（78），且其依赖链最短",
  "why_not_others": {
    "C-01": "priority 61：区域覆盖度尚可，不紧迫",
    "C-02": "priority 55：cost=5，本轮预算不够"
  },
  "next_promise": "P-0009"
}
```

`why_not_others` 是必填项。**只写为什么选它、不写为什么不选别人 = 没列全。**

## 五、收尾动作（顺序固定）

1. 第一名候选 → 写进 `promises.json` 的 `open`，带 `due_cycle = cycle + 1`
2. `fork.json` 里记下 `next_promise` 的 id
3. 若被排除的候选里有"以后可能要学"的，回填 `coverage-map.md` 对应区域，别让它凭空消失

## 六、自检两问

1. 如果有人问我"为什么不是 C-01 而是 C-03"，我能用文件里的依据回答吗？
2. 如果三个月后回看这轮，我能看出当时**被排除的东西**长什么样吗？

两问只要有一答不上来，本轮 fork 无效，重做（CHARTER 第 3、4 条）。
