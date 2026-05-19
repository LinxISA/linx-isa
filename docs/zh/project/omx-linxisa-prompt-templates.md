# 灵犀指令集 OMX 提示模板

这些模板是适合 灵犀指令集 的最短的可重复使用的提示
超级项目工作流程。

调整 `<...>` 占位符，但保持结构。目标是保护：

- 所有者和模块清晰，
- 叶前列宾纪律，
- 车道政策清晰，
- 有证据支持的收尾。

## 1. 门分类

当门是红色且主人不明显时使用。

```text
$deep-interview "Investigate failing gate <gate-key> in /Users/zhoubot/linx-isa. Identify the owning module, checklist ids, smallest reproducer, lane impact, blocking waivers if any, and required evidence outputs under docs/bringup/gates/."
```

## 2. 范围锁定和计划批准

在分类之后、实施之前使用。

```text
$ralplan "For <gate-key> / <task>, approve module scope, leaf proof, repin boundary, strict closure order, lane policy, and exact closeout evidence. Reject any plan that fixes a leaf-owned bug only in the superproject."
```

## 3. 叶子修复执行

当拥有的模块已知并且一位所有者应该开车去证明时使用。

```text
$ralph "Work only in <module>. Reproduce <gate-key>, fix the owning issue, rerun the smallest leaf proof until green, and stop before repin if the leaf proof is still not credible."
```

## 4.列宾评论

在移动子模块 SHA 之前使用。

```text
$ralplan "For repinning <module>, verify the new SHA has leaf proof, list the cross-repo gates that could regress, decide whether validation is pin-only or dual-lane, and define the evidence pack required before merge."
```

## 5. PR 级严格关闭

在叶修复或超级项目拥有的集成更改后使用。

```text
$ralph "Run the ZXTERMEN40QXZ PR-tier closure sequence for <task>: static policy guard, AVS contract, AVS tier closure, and strict_cross_repo. Record exact commands, lane, pass/fail, and artifact paths. Treat latest.json as the source of truth."
```

## 6. 双车道融合

仅在叶子证明和 PR 层关闭可信后使用。

```text
$ralplan "For <task>, define the dual-lane runtime convergence plan. Specify run-id format, pin and external lane prerequisites, expected artifacts, and what counts as a true parity failure versus stale evidence."
```

## 7. 团队跑

当多个清单所有者需要持久协调时使用。

```text
$team 4:executor "Execute <task> in manifest-aligned lanes. Keep owner scope explicit, fix leaf modules before repin, do not trust markdown over latest.json, and leave per-lane evidence under docs/bringup/gates/logs/<run-id>/<lane>/."
```

将工作人员数量调整为活动车道的实际数量。

## 8. 文件和合同刷新

当更改归 `isa` 或 `docs` 所有时使用。

```text
$ralph "Work only in isa/docs for <task>. Refresh the contract or manual artifacts that follow from the change, rerun the smallest contract checks, and record any downstream gates that must be revisited before closure."
```

## 9. 技能进化回顾

当您想要决定是否应该重用知识时，请使用接近收尾
晋升为技能。

```text
$ralplan "For the completed run <run-id>, decide skill-evolve:update or skill-evolve:no-update for each affected module. Only approve updates for reusable contracts, reproducibility commands, or recurring triage patterns."
```

## 10. 维基捕获

当结果应该在最终历史记录中存在时使用。

```text
$ralph "Summarize the reusable findings from <task> into concise wiki-ready notes: failure signature, owning gate/module, minimal reproducer, proof command, lane constraints, and artifact paths. Exclude stale or machine-specific absolute paths."
```

## 场景包

### 未知主人的红门

```text
$deep-interview "Investigate failing gate <gate-key> in /Users/zhoubot/linx-isa. Identify the owning module, checklist ids, smallest reproducer, lane impact, blocking waivers if any, and required evidence outputs under docs/bringup/gates/."
$ralplan "For <gate-key>, approve module scope, leaf proof, repin boundary, strict closure order, lane policy, and exact closeout evidence."
```

### 安全重新固定

```text
$ralplan "For repinning <module>, verify the new SHA has leaf proof, list the cross-repo gates that could regress, decide whether validation is pin-only or dual-lane, and define the evidence pack required before merge."
$ralph "Run the PR-tier closure sequence for the <module> repin and leave exact evidence paths."
```

### 每晚关闭

```text
$ralplan "Define the nightly closure plan for <task>: required gates, pin/external expectations, run-id naming, stale-evidence rejection, and failure classification."
$team 5:executor "Execute nightly closure for <task> in manifest-aligned lanes with durable evidence and no undocumented waivers."
```