# CONFLICT — 冲突裁决（降级版）

单 Agent 生长，没有多管理员。这套只处理一种情况：**同一个问题上有两个判断打架。**

## 排序键（依次比较，前一档没分出胜负才看下一档）

1. **有出处** > 没出处。可指向文件/文档/源码/验证记录的一方胜。
2. **高置信** > 低置信。`confidence` 数值比较。
3. **近期验证** > 远期验证。`verified_at` 更晚的一方胜。

三档全平 → 不许自己仲裁，写进 `RUNTIME/gaps.md`，标 `needs_user`，问用户。

## 留痕

裁决写 `RUNTIME/arbitration/ARB-<id>.md`：

```markdown
# ARB-0003 · 先讲 A 还是先讲 B
- at: 2026-xx-xx
- 判断一：先讲 A（src: cycles/0003/fork.json C-02, confidence 0.7, verified 2026-..）
- 判断二：先讲 B（src: mechanisms/order-rule.md, confidence 0.8, verified 2026-..）
- 裁决档位：第 1 档打平（都有出处），第 2 档分出：B 胜（0.8 > 0.7）
- 结果：先讲 B
- 影响：promises P-0009 顺延
```

## 两个禁止

- 禁止"两个都讲"来回避裁决。回避会让课程变胖，不长。
- 禁止不带 `src` 进入裁决。没有出处的判断没有裁决资格，直接作废。
