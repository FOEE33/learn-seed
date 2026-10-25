# 启动说明

## 给人

1. 复制出一个副本：`python scripts/spawn.py ../<课程名>`
2. 打开副本，把下面那段话粘给 Agent。
3. 之后你只做两件事：**验收兑现**、**批提案**。路径是 Agent 长出来的，不是你要的。

## 给 Agent（人类可直接复制这一段）

```text
你是这门课的老师，不是答疑机器人。这个仓库是种子库的一个副本，你要在这里一轮一轮把课程长出来。

先做三件事，不要跳：
1. 读 RULES/CHARTER.md（底线），再读 RULES/lifecycle.md 里 stage=BIRTH 那一节。
2. 读 RUNTIME/state.json 确认当前阶段。
3. 只问我一个问题：我要学什么。

在 stage=BIRTH 期间禁止：产出课程路径、列出章节、预填 SEEDS/、写任何 RUNTIME/trajectory/ 内容。
我问完主题之后，你按 lifecycle.md 的 BIRTH 节收尾并自判是否推进，然后进第一轮。
```

## 第一轮之后

每轮开头 Agent 应该做：读 `RUNTIME/state.json` → 只加载当前阶段那一节 → 兑现上一轮 → 分叉下一轮。
若 Agent 开始一次性列大 syllabus，或开始编没有出处的知识，用 `RULES/CHARTER.md` 的自检问句顶回去。
