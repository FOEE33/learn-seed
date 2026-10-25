# mechanisms/ — 通用上下文（机制层）

只放**与主题无关**的机制条目。判定标准见 `RULES/context.md`：

> 把主题名词换成 XXX，句子还讲得通吗？讲不通就是路径，不许放这儿。

## 准入（两条都要）

1. 被 ≥2 个不同 cycle 实际用到并有效（正文写明是哪两轮）
2. `confidence >= 0.6`

## 命名

`<动词>-<对象>.md`，例：`order-by-dependency.md`、`degrade-when-unsourced.md`

## frontmatter 六项（缺一不收）

```yaml
kind: mechanism
claim: ...
applies_when: ...
failure_mode: ...     # 必填
source: ...
confidence: 0.0
verified_at: ...
```

## 当前状态

空。原初库不带任何一次生长的机制沉淀——机制是长出来的，不是预置的。
唯一预置的机制样本见 `_sample.md`（标注为 sample，不继承，仅供格式参考）。
