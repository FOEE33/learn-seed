# transplant/ — 移植记录（运行时层）

副本经验回流原初库的中间站。`TP-<id>.md`：

```markdown
---
id: TP-0000
from_copy: <runtime_id>
evidence_cycles: [2, 5]
portability: universal | domain | local
changes_existing: false
status: pending
---

## 回流的条目
`SEEDS/mechanisms/xxx.md`（新增 / 修改）

## 改了什么
## 为什么原初库需要它
## 被拒原因（若 rejected）
```

必填 `evidence_cycles`（≥2 轮）。空着直接拒，不看内容。

方向默认**单向**（副本 → 原初库）。双向未定，见 `../open-questions.md#q3`。原初库此目录为空。
