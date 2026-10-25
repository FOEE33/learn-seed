# PROPOSAL — 上书通道

Agent 发现规则该改、机制该回流、外部做法该借鉴 —— **不自己改库**，写成提案进队列，人批。

## 什么时候必须走提案（没有例外）

- 想动 `RULES/` 任何文件
- 想把机制条目回流到原初库
- 想引入外部仓库的做法
- 想把某条 `local` 机制升成 `universal`

## 什么时候不用

- 改 `RUNTIME/` 里的自己的东西（轨迹、状态、承诺、gap）
- 在副本自己的 `SEEDS/mechanisms/` 里新增条目（但回流要提案）

## 提案形状

`RUNTIME/proposals/PROP-<4位序号>-<slug>.md`：

```markdown
---
id: PROP-0007
status: pending          # pending | approved | rejected | withdrawn
kind: rule-change        # rule-change | mechanism-backflow | external-adopt
layer: RULES/fork.md     # 落在哪一层、哪个文件
conflicts_with: []       # 与现有设计冲突的条目（诚实填写，空就写 []）
requires: []             # 前置提案
created_at: 2026-xx-xx
---

## 提出什么
一句话。

## 为什么
问题是什么，现在的规则哪里不够用。要指向具体轮次或具体失败。

## 依据
文件/轮次/外部链接。空依据的提案不收。

## 落到哪层
为什么是这一层，不是别的层（尤其：为什么不是运行时层的临时做法）。

## 与现有设计冲突吗
逐条对照 CHARTER 五条。有冲突就写清冲突在哪、建议怎么解。

## 不采纳会怎样
写得出来才说明这事值得做。
```

## 闸门

- `status: pending` 的提案，Agent **不许**执行其中任何改动。
- 只有人把 `status` 改成 `approved` 后，才可动。
- 提案被 `rejected`：原因写进 `rejected_reason`，同一件事**不许**换个说法再提，除非有新依据。

## 自检

> 我是不是在心里已经把规则改了，只是在补记录？
> 如果是 → 撤回，改成待批提案，按未改的状态继续工作。
