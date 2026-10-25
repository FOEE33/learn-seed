# proposals/ — 提案队列（运行时层）

`PROP-<4位序号>-<slug>.md`，模板见 `../templates/proposal.example.md`。

闸门（硬）：

- `status: pending` → Agent 不许执行其中任何改动
- `status: approved` → 可执行，执行后在同文件写 `applied_at`
- `status: rejected` → 写 `rejected_reason`，不许换个说法重提

原初库此目录为空。
