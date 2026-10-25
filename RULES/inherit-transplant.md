# INHERIT & TRANSPLANT — 继承与移植（项目级，不是库级）

两件事分开管，别混：

- **继承**：新副本从种子拿什么。方向：种子 → 副本。
- **移植**：副本长出来的经验能不能回流、往哪回流。方向：副本 → 种子（默认）。

## 一、继承分档（白名单制，机器可读）

权威在 `SEEDS/MANIFEST.json` 的 `inherit` 段，本文只是解释。

| 档 | 内容 | 继承方式 |
|---|---|---|
| `guide` 引导 | `RULES/**` | **全继承**，一字不改 |
| `mechanism` 机制上下文 | `SEEDS/mechanisms/**`（portability != local） | 继承，副本可继续加自己的 |
| `topic` 主题基线 | `SEEDS/baseline/**` | **仅同主题**继承；换主题只继承 `coverage-map.md` 的骨架 |
| — 路径层 | 任何 `deliver.md` / `cycles/**` | **不继承，永远** |
| — 运行时 | `RUNTIME/state.json`、`anchor.json`、`promises.json` | 不继承，副本新建 |

一句话：**引导全继承，上下文只继承验证过的机制层，不继承路径层。**

## 二、继承来的引导，副本有没有写权

未定 → `RUNTIME/open-questions.md#q1`。

当前实现按**只读**运行（`spawn.py` 拍副本后给 `RULES/` 打 `.readonly` 标记文件，`check.py --drift` 会发现改动）。理由：有写权就必须配回流闸门，闸门没定之前先不开写权。这是可逆选择，不是结论。

## 三、移植（回流）

默认**单向**：副本 → 原初库。原初库不主动向已存在的副本推机制更新（那等于从背后改写别人的路径）。

回流走闸门，不直接 push：

```
副本 SEEDS/mechanisms/xxx.md
  → RUNTIME/transplant/TP-<id>.md（写：来源副本、哪轮验的、改了什么）
  → RUNTIME/proposals/PROP-<id>.md（提案，人批）
  → 原初库 SEEDS/mechanisms/xxx.md + MANIFEST 登记
```

双向是否要开：`RUNTIME/open-questions.md#q3`，未定不做。

## 四、移植记录必填项

`RUNTIME/transplant/TP-<id>.md`：

- `from_copy`：副本 runtime_id
- `evidence_cycles`：哪几轮验证过（≥2）
- `portability`：universal / domain / local
- `changes_existing`：是否修改原初库已有条目（是则必须走提案）
- `rejected_reason`：若被拒，为什么

无 `evidence_cycles` 的回流请求直接拒，不看内容。
