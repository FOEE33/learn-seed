---
name: course-grower
description: 生长式课程的可执行流程。当你在一个 learn-seed 副本里做"一轮一轮把课程长出来"的工作时使用：读锚、兑现上轮承诺、分叉下轮候选、写 checkpoint、验阶段断言。不是知识问答技能，是长程迭代的节奏控制。
version: 0.1.0
requires: python>=3.9（仅 check.py / spawn.py 需要，纯标准库）
---

# course-grower

一轮只做两件事：**兑现**上一轮的承诺，**分叉**下一轮学什么。
纲领在库里的 `RULES/`，本 skill 只负责把动作做对。

## 每轮开头的三步（不可跳、不可并）

```bash
cd <副本根>
cat RUNTIME/anchor.json          # 教什么、边界在哪
cat RUNTIME/promises.json        # 欠用户什么（只看 open）
python scripts/check.py --chain   # 上一轮链是否完好
```

链断或锚不一致 → **停**。别接着生长，先查历史被谁动了。

## 第一段 · 兑现

1. 取 `promises.json` 里 `due_cycle <= 当前 cycle` 的全部承诺。
2. 写 `RUNTIME/trajectory/cycles/<0001>/deliver.md`，模板 `RUNTIME/templates/deliver.example.md`。
3. 每条知识标档：`[D0]` 有出处 / `[unverified]` 待验 / 不产出（D2 → 写 gaps）。
4. 关承诺：把 id 从 `open` 移到 `delivered`，`evidence` 指到 `deliver.md#sec-n`。
5. 有逾期承诺 → 本段没完 → **不许进下一段**。

## 第二段 · 分叉

```bash
python - <<'PY'   # 没必要，用它只为提醒顺序
print("扫 gap → blocked → prereq → user，再筛，不是先想答案")
PY
```

1. 扫四个来源（缺一个就是没列全）。
2. 每个候选写 `basis`（指向文件#锚点）+ `priority`（由 rubric 算）。
3. 写 `cycles/<n>/fork.json`，`why_not_others` 必填。
4. 第一名候选 → 写进 `promises.json` 的 `open`，带 `due_cycle`。

## 收尾 · 写 checkpoint

```python
# 关键：fork_digest / deliver_digest 必须是文件真实字节的 sha256
import hashlib, json
from pathlib import Path
d = Path("RUNTIME/trajectory/cycles/0001")
digest = lambda p: "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
cp = {
    "cycle": 1, "stage": "GROWTH", "revision": 1,
    "anchor_id": json.loads(Path("RUNTIME/anchor.json").read_text(encoding="utf-8"))["anchor_id"],
    "anchor_intact": True,
    "promises_digest": digest(Path("RUNTIME/promises.json")),
    "fork_digest": digest(d / "fork.json"),
    "deliver_digest": digest(d / "deliver.md"),
    "prev_hash": "<上一轮 self_hash，首轮 sha256:>",
    "closed_at": "2026-02-01T00:00:00Z",
}
cp["self_hash"] = "sha256:" + hashlib.sha256(canon({k: v for k, v in cp.items() if k != "self_hash"})).hexdigest()
(d / "checkpoint.json").write_text(json.dumps(cp, ensure_ascii=False, indent=2), encoding="utf-8")
```

## 状态推进（只在断言全真时）

```bash
python scripts/check.py --stage    # 看断言表结果，别自己拿主意
```

- `BIRTH → GROWTH`：A1-A4 全真
- `GROWTH → REGULATED`：B1-B5 全真（含链、含机制条目）
- 改 `state.json`：写 `.tmp` → `os.replace`，`cycle` 单调不减；`stage_history` 追加一条 `{from,to,at,reason}`

断言不真 → **留在当前阶段**。没有"差不多"。

## 常见跑偏（照这几条自查）

| 症状 | 对应底线 |
|---|---|
| 直接列一整份 syllabus | 这轮该兑现的没兑现 |
| 候选只有第一名，没有落选理由 | 没列全（CHARTER 4） |
| 交付内容没有标档 | 在编（CHARTER 2） |
| 改了上一轮的 deliver 让它"更对" | 改历史 = 断链（CHARTER 3） |
| 想动 `RULES/` | 走 `RUNTIME/proposals/`，人批才动 |

## 缺脚本时

没装 python / 没脚本 → 手工执行等价动作，但在 `deliver.md` 顶部标 `chain_unverified: true`，**不许假装验过**（见 `RULES/skill-install.md`）。
