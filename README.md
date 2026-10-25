# course-seed — 生长式课程的种子库

这不是一个知识库，是一个**种子库**。

它本身不含课程路径。它被一比一复制出去，每个副本在自己的运行时层上长自己的路径。
原初库只保留三样东西：怎么抉择（规则）、起点在哪（种子）、以及留给副本长的地方（空模板）。

## 三条不混的层

| 层 | 目录 | 性质 | 副本可写 |
|---|---|---|---|
| 规则层 | `RULES/` | 纲领。Agent 怎么抉择、搜索范围、不确定怎么降级、阶段怎么推进 | 只读（改要过提案闸门） |
| 种子层 | `SEEDS/` | 验证过的知识基线、初始覆盖度地图、初始状态 | 只读（继承白名单见 `SEEDS/MANIFEST.json`） |
| 运行时层 | `RUNTIME/` | 生长轨迹、阶段状态、提案队列、裁决记录、移植记录 | 可写（这是副本自己的） |

`SKILL/` 是 skill 的**源**，用于打包发 Release。它不属于种子，复制副本时排除。

## 生长循环

一轮只做两件事：

1. **兑现**：把上一轮承诺的教学内容高质量教下来 → `RUNTIME/trajectory/cycles/<n>/deliver.md`
2. **分叉**：推导下一轮学什么，候选列全，每个带依据与优先级 → `RUNTIME/trajectory/cycles/<n>/fork.json`

节奏分阶段，不是一套流程跑到底：

- `BIRTH`：只问一件事——你要学什么。不产出路径。
- `GROWTH`：循环跑起来（第一遍 → 第二遍）。记录重、判断轻。
- `REGULATED`：第三遍起，流程规范化。分叉必须走完整评分表，提案闸门生效。

阶段由 Agent 自判推进，但纲领不动、只动状态。状态在 `RUNTIME/state.json`，单一枚举 + 可机检条件，原子写入。

## 用一个副本

```bash
python scripts/spawn.py ../my-course            # 按 MANIFEST 白名单拍出干净副本
python scripts/check.py ../my-course --stage    # 校验种子完整性与阶段断言
```

拍完之后对这个副本说的话只有一句：

> 我要学 ……。

（`START-HERE.md` 里有可直接粘给 Agent 的启动语。）

## 装 skill

Agent 的抉择指南打成 Release 资产，库里只引导去装，不内联：

见 `RULES/skill-install.md`。

## 底线

写在 `RULES/CHARTER.md`，五条硬约束，每条带自检问句。

## 还没定的

`RUNTIME/open-questions.md`。未定项在库里是**空的**，不预填立场，等生长把它逼出答案。
