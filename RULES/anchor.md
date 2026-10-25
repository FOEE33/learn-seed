# ANCHOR — 长程任务锚定

解决的问题：课程要长很多轮、可能跨很多次会话。**锚点漂移**是最贵的失败——长着长着教的东西已经不是用户想学的，或者上一轮承诺的东西没人记得。

借鉴自 ZeoStudio-TenGate 的长程任务锚定（固定 task_id + revision 单调 + checkpoint + 事件链可校验）。这里降级为**纯文件、可自校验、零依赖**的版本，不带 lease / 身份密封 / 多角色那套。

---

## 一、锚（Anchor）：一个副本只有一个，且稳定

`RUNTIME/anchor.json`，在 BIRTH 阶段写一次：

```json
{
  "anchor_id": "uuid",
  "topic_raw": "用户原话，一字不改",
  "goal": "把原话翻译成一句可验收的目标，不超过 40 字",
  "scope_in": ["明确算这节课范围的"],
  "scope_out": ["明确不算的，写下来防漂移"],
  "created_at": "ISO8601",
  "parent_seed": { "repo": "FOEE33/course-seed", "commit": "<sha>", "manifest_version": 1 }
}
```

规则：

1. `topic_raw` 只准粘贴，不准改写。改写会让锚点变成我的理解，而不是用户的要求。
2. `scope_out` 不是可选项。没有边界的锚定不叫锚定。
3. 锚一旦写入，**任何轮次都不许改**。分叉只能改"下一步学什么"，不能改"这门课是什么"。

## 二、重新锚定（Reanchor）：唯一合法的改动路径

当且仅当以下之一成立，可以改锚：

- 用户显式改变目标（"不学 X 了，改成 Y"）
- `scope_out` 里的东西被证明是必需前置（写清是哪条、为什么）

做法：不是覆盖 `anchor.json`，而是**追加**到 `RUNTIME/anchor-history.jsonl`，写 `{at, reason, user_quote, before, after}`，然后旧锚归档、新锚写回。锚 ID 变化必须记录，checkpoint 链上标明 `anchored: false` 的那一段是断的。

自检：没有 `anchor-history.jsonl` 记录的锚变动 = 漂移，本轮作废。

## 三、承诺账本（Promises）：兑现是锚定的肉

`RUNTIME/promises.json`，跨轮唯一真源：

```json
{
  "revision": 7,
  "open": [
    { "id": "P-0007", "cycle_made": 2, "statement": "讲清 X 为什么必须晚于 Y 学", "due_cycle": 3 }
  ],
  "delivered": [
    { "id": "P-0006", "cycle_made": 1, "cycle_delivered": 2, "evidence": "cycles/0002/deliver.md#sec-2", "verified_by_user": false }
  ]
}
```

规则：

1. 每轮分叉产出的**第一名候选，必须变成一条 open 承诺**，带 `due_cycle`。不许只写在 fork.json 里就算数。
2. 每轮兑现，必须关闭**上一轮欠的**承诺，并在 `evidence` 里指向 `deliver.md` 的具体锚点。指向整篇 = 没指向。
3. `open` 里过期未交付的承诺（`due_cycle < cycle`）**优先于新分叉**。欠账没清不许开新课。
4. 承诺只增不改。要改一条承诺的措辞 = 关掉它，开一条新的。

自检：`python scripts/check.py --promises` 报 0 条逾期，才算兑现完成。

## 四、检查点链（Checkpoint chain）：让长程可校验

每轮关闭时写 `RUNTIME/trajectory/cycles/<n>/checkpoint.json`：

```json
{
  "cycle": 3,
  "stage": "GROWTH",
  "revision": 3,
  "anchor_id": "...",
  "anchor_intact": true,
  "promises_digest": "sha256:...",
  "fork_digest": "sha256:...",
  "prev_hash": "sha256:上一轮 checkpoint 的 self_hash",
  "self_hash": "sha256:上一行规范序列化后的哈希",
  "closed_at": "ISO8601"
}
```

规则：

1. `prev_hash` 必须指向上一个 cycle 的 `self_hash`。跳过一轮 = 链断 = 作废。
2. `anchor_id` 与本轮 `anchor_intact` 必须与 `anchor.json` 一致。不一致说明漂了。
3. **内容指纹**：`deliver_digest` / `fork_digest` 必须是本轮产出文件的真实字节 sha256，不许填占位。只钉哈希不钉内容，等于没钉——改了正文而 hash 不变的话，长程追溯就是假的。
4. 验链：`python scripts/check.py --chain`。断了就说明有人在事后改历史，不接受解释。

## 五、每轮开头必读（三步，不可跳）

```
1. RUNTIME/anchor.json          → 我要教的是什么，边界在哪
2. RUNTIME/promises.json        → 我欠用户什么
3. 最近一个 checkpoint.json     → 我上一轮停在哪，链是否完好
```

读完才开始兑现。**先兑现，再分叉**。顺序反了就会变成永远在推新课、永远不交付。

## 六、何时可以不管锚定

不可以。锚定是长程任务的底座，不是阶段性的技巧。只有一种情况例外：用户明确说"这轮只是闲聊"——那就不写 checkpoint，也不动 promises。
