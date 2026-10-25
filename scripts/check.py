#!/usr/bin/env python3
"""course-seed 断言校验器。

把 RULES/lifecycle.md 里写的推进条件变成真的能跑的东西。
纯标准库，无依赖。退出码：0 全过 / 1 有失败。

用法:
    python scripts/check.py --all
    python scripts/check.py --stage
    python scripts/check.py --chain
    python scripts/check.py --promises
    python scripts/check.py --fork
    python scripts/check.py --seed
    python scripts/check.py --drift
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STAGES = ("BIRTH", "GROWTH", "REGULATED")
RESULTS = []


# ---------- 基础 ----------

def find_root(start=None):
    p = Path(start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "SEEDS" / "MANIFEST.json").is_file():
            return cand
    return None


def load_json(path, fallback=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha(obj):
    b = obj if isinstance(obj, bytes) else canon(obj)
    return "sha256:" + hashlib.sha256(b).hexdigest()


def hashable_checkpoint(cp):
    """计算 self_hash 时剔除 self_hash 与所有以 _ 开头的注释键。"""
    return {k: v for k, v in cp.items() if k != "self_hash" and not k.startswith("_")}


def record(ok, name, msg=""):
    RESULTS.append({"ok": bool(ok), "name": name, "msg": msg})
    return ok


def cycle_dirs(root):
    base = root / "RUNTIME" / "trajectory" / "cycles"
    if not base.is_dir():
        return []
    out = []
    for d in base.iterdir():
        if d.is_dir() and re.fullmatch(r"\d{4}", d.name):
            out.append(d)
    return sorted(out, key=lambda d: d.name)


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


# ---------- 断言组 ----------

def is_copy(root):
    """副本 = state.json 存在且已有 runtime_id。洁净度检查只对原初库有意义。"""
    st = load_json(root / "RUNTIME" / "state.json") or {}
    return bool(st.get("runtime_id"))


def check_seed(root):
    mf = load_json(root / "SEEDS" / "MANIFEST.json")
    if not mf:
        return record(False, "SEED/manifest", "SEEDS/MANIFEST.json 读不出来")

    miss = [f for f in mf.get("checks", {}).get("required_files", []) if not (root / f).is_file()]
    record(not miss, "SEED/required-files", "缺: " + ", ".join(miss) if miss else "齐")

    if is_copy(root):
        record(True, "SEED/clean", "副本（有 runtime_id），洁净度不适用")
    else:
        dirty = [f for f in mf.get("checks", {}).get("forbidden_in_seed", []) if (root / f).exists()]
        record(not dirty, "SEED/clean",
               "原初库脏了，绝不该存在的生长产物: " + ", ".join(dirty) if dirty else "干净（无生长痕迹）")

    tpl = root / "RUNTIME" / "templates"
    record(tpl.is_dir() and any(tpl.glob("*")), "SEED/templates",
           "RUNTIME/templates 只有模板" if tpl.is_dir() else "RUNTIME/templates 缺失")


def check_promises(root):
    p = load_json(root / "RUNTIME" / "promises.json")
    st = load_json(root / "RUNTIME" / "state.json", {}) or {}
    if p is None:
        return record(True, "PROMISES", "未进入循环（无 promises.json），跳过")
    cycle = int(st.get("cycle", 0) or 0)
    overdue = [x for x in p.get("open", []) if int(x.get("due_cycle", 0) or 0) < cycle]
    details = "; ".join(f"{x.get('id')} 逾期(应于第{x.get('due_cycle')}轮)" for x in overdue)
    record(not overdue, "PROMISES/overdue",
           details if overdue else f"{len(p.get('open', []))} 条未交、0 条逾期")
    bad = [x.get("id") for x in p.get("delivered", []) if not (x.get("evidence") or "").strip()]
    record(not bad, "PROMISES/evidence", "已交付但无 evidence 锚点: " + ", ".join(map(str, bad)) if bad else "全部有锚点")


def check_fork(root):
    cycles = cycle_dirs(root) or [None]
    checked = 0
    for cd in cycles:
        if cd is None:
            break
        fj = load_json(cd / "fork.json")
        if fj is None:
            continue
        checked += 1
        cands = fj.get("candidates", [])
        bad = [c.get("id") for c in cands
               if not c.get("basis") or not isinstance(c.get("priority"), int)]
        record(not bad, f"FORK/{cd.name}/basis+priority",
               "缺依据或优先级: " + ", ".join(map(str, bad)) if bad else f"{len(cands)} 个候选都带依据与优先级")
        missing_who = [k for k in (fj.get("why_not_others") or {}) ]
        unex = [c.get("id") for c in cands if c.get("excluded") is None]
        covered = len(missing_who) + len(fj.get("excluded", []))
        record(covered >= max(0, len(unex) - 1), f"FORK/{cd.name}/excluded",
               f"已记录 {covered} 条排除/落选理由，候选 {len(unex)} 个")
    if checked == 0:
        record(True, "FORK", "还没跑过循环，跳过")
    return checked


def check_chain(root):
    cycles = cycle_dirs(root)
    if not cycles:
        return record(True, "CHAIN", "还没跑过循环，跳过")
    prev = "sha256:"
    anchor = load_json(root / "RUNTIME" / "anchor.json") or {}
    for cd in cycles:
        cp = load_json(cd / "checkpoint.json")
        if cp is None:
            record(False, f"CHAIN/{cd.name}", "缺 checkpoint.json —— 该轮未关闭")
            return
        expect = sha(hashable_checkpoint(cp))
        if cp.get("self_hash") != expect:
            record(False, f"CHAIN/{cd.name}", "self_hash 不符 —— 事后改过内容")
            return
        if cp.get("prev_hash") != prev:
            record(False, f"CHAIN/{cd.name}", f"prev_hash 断链（期望 {prev}）")
            return
        if anchor.get("anchor_id") and cp.get("anchor_id") != anchor.get("anchor_id"):
            record(False, f"CHAIN/{cd.name}", "anchor_id 与当前锚不一致 —— 锚漂了")
            return
        # 内容指纹：checkpoint 必须钉住本轮产出的实际字节
        bad = []
        for key, fname in (("deliver_digest", "deliver.md"), ("fork_digest", "fork.json")):
            fp = cd / fname
            if key not in cp or not fp.is_file():
                continue
            actual = sha(fp.read_bytes())
            if cp.get(key) != actual:
                bad.append(f"{fname} 摘要不符（checkpoint 记 {cp.get(key)}，实际 {actual}）")
        if bad:
            record(False, f"CHAIN/{cd.name}", "；".join(bad))
            return
        prev = cp["self_hash"]
        record(True, f"CHAIN/{cd.name}", "链完好（含内容指纹）")


def check_stage(root):
    st = load_json(root / "RUNTIME" / "state.json")
    if st is None:
        return record(True, "STAGE", "副本尚未初始化（无 state.json）")
    stage = st.get("stage")
    if stage not in STAGES:
        return record(False, "STAGE/enum", f"stage={stage!r} 不在枚举 {STAGES} 内")
    record(True, "STAGE/enum", f"stage = {stage}")

    anchor = load_json(root / "RUNTIME" / "anchor.json")
    cmap = root / "SEEDS" / "baseline" / "coverage-map.md"

    if stage == "BIRTH":
        if anchor is None:
            record(False, "BIRTH/A1-anchor", "缺 anchor.json")
            return
        ok = all(str(anchor.get(k) or "").strip() for k in ("topic_raw", "goal", "scope_out"))
        record(ok, "BIRTH/A1-anchor", "topic_raw / goal / scope_out 齐" if ok else "anchor 有字段为空")
        g = str(anchor.get("goal") or "")
        record(0 < len(g) <= 40, "BIRTH/A2-goal-length", f"goal {len(g)} 字（≤40）")
        record(not cycle_dirs(root), "BIRTH/A3-no-path",
               "BIRTH 期间没偷跑路径" if not cycle_dirs(root) else "BIRTH 阶段已产生 cycles/，越界")
        regions = 0
        if cmap.is_file():
            for line in cmap.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("|") and "BIRTH 阶段填写" not in line and "---" not in line:
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if len(cells) >= 2 and cells[0] and cells[0] not in ("区域", "id"):
                        regions += 1
        record(regions >= 3, "BIRTH/A4-coverage-map", f"区域 {regions} 个（≥3）")
        ready = all(r["ok"] for r in RESULTS if r["name"].startswith(("BIRTH/", "STAGE/")))
        record(ready, "BIRTH → GROWTH", "断言全真，可推进" if ready else "有条件不真，留在 BIRTH")
        return

    # GROWTH / REGULATED
    cycles = cycle_dirs(root)
    complete = [d for d in cycles if all((d / f).is_file() for f in
                                         ("deliver.md", "fork.json", "checkpoint.json"))]
    if stage == "GROWTH":
        record(len(complete) >= 3, "GROWTH/B1-cycles", f"完成 {len(complete)} 轮（≥3）")
        last2 = complete[-2:]
        record(len(last2) == 2 and all((load_json(d / "checkpoint.json") or {}).get("anchor_intact") for d in last2),
               "GROWTH/B2-anchor-intact", "最近两轮锚完好" if len(last2) == 2 else "不足两轮")
        mech_dir = root / "SEEDS" / "mechanisms"
        qualified = 0
        if mech_dir.is_dir():
            for f in mech_dir.glob("*.md"):
                if f.name.startswith("_") or f.name == "README.md":
                    continue
                text = f.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                if fm.get("kind") != "mechanism":
                    continue
                try:
                    conf = float(fm.get("confidence", "0"))
                except ValueError:
                    conf = 0.0
                rounds = len(set(re.findall(r"cycles/(\d{4})", text)))
                if conf >= 0.6 and rounds >= 2:
                    qualified += 1
        record(qualified >= 1, "GROWTH/B5-mechanism", f"合格机制条目 {qualified} 条（≥1）")
        ready = all(r["ok"] for r in RESULTS if r["name"].startswith(("GROWTH/", "PROMISES/", "CHAIN/", "FORK/")))
        record(ready, "GROWTH → REGULATED", "断言全真，可推进" if ready else "有条件不真，留在 GROWTH")
    else:
        pending = list((root / "RUNTIME" / "proposals").glob("PROP-*.md"))
        unbatched = [p.name for p in pending if "status: approved" not in p.read_text(encoding="utf-8")]
        record(True, "REGULATED/gate", f"待批提案 {len(unbatched)} 条（不影响运行，但改动必须先批）")
        record(True, "REGULATED/score", "分叉须走 fork.md 评分表并把 rubric 写进 fork.json")


def check_drift(root):
    snap = root / "RULES" / ".baseline.sha256"
    if not snap.is_file():
        return record(True, "DRIFT", "无基线快照（原初库本身），跳过")
    bad = []
    for line in snap.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        fp = root / rel
        if not fp.is_file():
            bad.append(rel + "（缺失）")
        elif "sha256:" + hashlib.sha256(fp.read_bytes()).hexdigest() != digest:
            bad.append(rel + "（被改）")
    record(not bad, "DRIFT/RULES", "RULES 未被动过" if not bad else "只读层被改: " + ", ".join(bad))


# ---------- 入口 ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    for flag in ("stage", "chain", "promises", "fork", "seed", "drift", "all"):
        ap.add_argument("--" + flag, action="store_true")
    a = ap.parse_args()

    root = find_root(a.root)
    if root is None:
        print(f"[FATAL] 在 {a.root} 及其父目录找不到 SEEDS/MANIFEST.json")
        return 1

    do_all = a.all or not any([a.stage, a.chain, a.promises, a.fork, a.seed, a.drift])
    print(f"root = {root}\n")

    if do_all or a.seed:
        check_seed(root)
    if do_all or a.promises:
        check_promises(root)
    if do_all or a.fork:
        check_fork(root)
    if do_all or a.chain:
        check_chain(root)
    if do_all or a.drift:
        check_drift(root)
    if do_all or a.stage:
        check_stage(root)

    fails = [r for r in RESULTS if not r["ok"]]
    for r in RESULTS:
        print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['name']:<28} {r['msg']}")
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} 通过")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
