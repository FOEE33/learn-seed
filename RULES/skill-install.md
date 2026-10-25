# SKILL-INSTALL — skill 从 Release 装，库里不内联

规则层的可执行部分（怎么读状态、怎么写 checkpoint、怎么跑断言）不塞进 `RULES/`，而是打成 skill 包发 GitHub Release。原因：Release 能更新，`RULES/` 进副本后是只读的，内联就没法迭代。

## 装法

```bash
gh release download --repo FOEE33/learn-seed --pattern "course-grower-*.zip" --dir /tmp/cg
unzip /tmp/cg/course-grower-*.zip -d <skill 目录>
```

或不用 gh：Release 页面下载 zip → 解压到 Agent 的 skill 目录。

## 版本对表（重要）

`RULES/MANIFEST.lock` 里记着本库期望的 skill 版本：

```json
{ "skill": "course-grower", "version": "0.1.0", "min_check_schema": 1 }
```

- skill 版本 < 期望 → 缺功能，先提示用户升级
- skill 版本 > 期望 → 说明库该更新了，读新 skill 的 CHANGELOG，走提案

## 装不上怎么办（降级路径）

skill 只是加速器，不是前置条件。没装也能干，但要**手工执行等价动作**：

1. 阶段推进：手工验 `lifecycle.md` 的断言表，逐条勾，勾完才改 `state.json`（原子写）
2. 链校验：手工算 `sha256` 串起来，或跳过校验但在 `deliver.md` 标 `chain_unverified`
3. 承诺账本：手工维护 `promises.json`，别用脑记

**降级不等于免检。** 手工验比脚本验更容易糊弄自己，所以降级时要更严格写依据。
