#!/usr/bin/env python3
"""按 SEEDS/MANIFEST.json 的白名单拍出一个干净的副本。

    python scripts/spawn.py ../my-course               # 新主题：只继承 RULES + 机制层 + 地图骨架
    python scripts/spawn.py ../my-course --same-topic  # 同主题：连 baseline 一起继承

拍出来的副本：RUNTIME 只有模板，anchor/promises/cycles 全空，RULES 打只读标记。
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def frontmatter_portability(text):
    if not text.startswith("---"):
        return "universal"
    end = text.find("\n---", 3)
    body = text[3:end] if end > 0 else text
    m = re.search(r"^portability:\s*(\S+)", body, re.M)
    return m.group(1).strip() if m else "universal"


def copy_tree(src, dst, exclude=()):
    n = 0
    if not src.is_dir():
        return n
    for f in src.rglob("*"):
        if f.is_dir():
            continue
        rel = f.relative_to(src)
        if any(str(rel).startswith(e) for e in exclude):
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--same-topic", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    seed = Path(__file__).resolve().parent.parent
    manifest = load(seed / "SEEDS" / "MANIFEST.json")
    dest = Path(a.dest).resolve()

    if dest.exists() and any(dest.iterdir()) and not a.force:
        print(f"[ABORT] {dest} 非空。要覆盖加 --force（会清空）")
        return 1
    if dest.exists() and a.force:
        for c in dest.iterdir():
            shutil.rmtree(c) if c.is_dir() else c.unlink()
    dest.mkdir(parents=True, exist_ok=True)

    stats = {}

    # 1. 规则层：全继承
    stats["RULES"] = copy_tree(seed / "RULES", dest / "RULES")

    # 2. 种子层：机制层按 portability 过滤；baseline 按主题
    mech_src = seed / "SEEDS" / "mechanisms"
    (dest / "SEEDS" / "mechanisms").mkdir(parents=True, exist_ok=True)
    keep = manifest["inherit"]["mechanism"]
    excluded = set(keep.get("exclude_portability", []))
    mc = 0
    for f in mech_src.glob("*"):
        if f.is_dir():
            continue
        if f.name.startswith("_") or f.name == "README.md":
            shutil.copy2(f, dest / "SEEDS" / "mechanisms" / f.name)
            continue
        if frontmatter_portability(f.read_text(encoding="utf-8")) in excluded:
            continue
        shutil.copy2(f, dest / "SEEDS" / "mechanisms" / f.name)
        mc += 1
    stats["mechanisms"] = mc

    base_src = seed / "SEEDS" / "baseline"
    if a.same_topic:
        stats["baseline"] = copy_tree(base_src, dest / "SEEDS" / "baseline")
        stats["baseline-mode"] = "same-topic（全继承）"
    else:
        (dest / "SEEDS" / "baseline").mkdir(parents=True, exist_ok=True)
        for rel in manifest["inherit"]["topic_baseline"]["skeleton_only_if_new_topic"]:
            src = seed / rel
            if src.is_file():
                shutil.copy2(src, dest / rel)
        stats["baseline-mode"] = "new-topic（只继承地图骨架）"

    for f in ("MANIFEST.json", "state.seed.json"):
        shutil.copy2(seed / "SEEDS" / f, dest / "SEEDS" / f)

    # 3. 运行时层：只给模板和空目录
    stats["RUNTIME-templates"] = copy_tree(seed / "RUNTIME" / "templates", dest / "RUNTIME" / "templates")
    for d, name in ((dest / "RUNTIME" / "trajectory" / "cycles", None),
                    (dest / "RUNTIME" / "proposals", None),
                    (dest / "RUNTIME" / "arbitration", None),
                    (dest / "RUNTIME" / "transplant", None)):
        d.mkdir(parents=True, exist_ok=True)
    for sub, readme in (("trajectory", "trajectory/README.md"),
                        ("proposals", "proposals/README.md"),
                        ("arbitration", "arbitration/README.md"),
                        ("transplant", "transplant/README.md")):
        src = seed / "RUNTIME" / readme
        if src.is_file():
            shutil.copy2(src, dest / "RUNTIME" / sub / "README.md")
    for f in ("open-questions.md",):
        if (seed / "RUNTIME" / f).is_file():
            shutil.copy2(seed / "RUNTIME" / f, dest / "RUNTIME" / f)

    # 4. 状态初始化（原子写）
    state = load(seed / "SEEDS" / "state.seed.json")
    state.pop("_note", None)
    state["runtime_id"] = str(uuid.uuid4())
    state["stage_entered_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["seed"]["manifest_version"] = manifest.get("manifest_version", 1)
    write_atomic(dest / "RUNTIME" / "state.json", state)

    # 5. 只读标记 + RULES 基线快照（供 check.py --drift 用）
    (dest / "RULES" / ".readonly").write_text(
        "继承自 course-seed，按只读使用。改动走 RUNTIME/proposals/，见 RULES/proposal.md\n",
        encoding="utf-8")
    lines = []
    for f in sorted((dest / "RULES").rglob("*")):
        if f.is_file() and f.name != ".baseline.sha256":
            digest = "sha256:" + hashlib.sha256(f.read_bytes()).hexdigest()
            lines.append(f"{digest}  RULES/{f.relative_to(dest / 'RULES').as_posix()}")
    (dest / "RULES" / ".baseline.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 6. 根文件
    for f in ("README.md", "START-HERE.md", ".gitignore", "LICENSE"):
        if (seed / f).is_file():
            shutil.copy2(seed / f, dest / f)
    copy_tree(seed / "scripts", dest / "scripts")

    print(f"[OK] 副本已拍出: {dest}")
    for k, v in stats.items():
        print(f"  {k:<20} {v}")
    print(f"  runtime_id           {state['runtime_id']}")
    print(f"  stage                {state['stage']}")
    print("\n下一步：把 START-HERE.md 里那段话粘给 Agent。")
    return 0


def write_atomic(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with open(tmp, "rb") as fh:
        try:
            import os
            os.fsync(fh.fileno())
        except Exception:
            pass
    tmp.replace(path)


if __name__ == "__main__":
    sys.exit(main())
