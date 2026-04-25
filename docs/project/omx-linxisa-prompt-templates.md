# LinxISA OMX Prompt Templates

These templates are the shortest reusable prompts that fit the LinxISA
superproject workflow.

Adjust `<...>` placeholders, but keep the structure. The goal is to preserve:

- owner and module clarity,
- leaf-before-repin discipline,
- lane policy clarity,
- evidence-backed closeout.

## 1. Gate Triage

Use when a gate is red and the owner is not obvious.

```text
$deep-interview "Investigate failing gate <gate-key> in /Users/zhoubot/linx-isa. Identify the owning module, checklist ids, smallest reproducer, lane impact, blocking waivers if any, and required evidence outputs under docs/bringup/gates/."
```

## 2. Scope Lock and Plan Approval

Use after triage, before implementation.

```text
$ralplan "For <gate-key> / <task>, approve module scope, leaf proof, repin boundary, strict closure order, lane policy, and exact closeout evidence. Reject any plan that fixes a leaf-owned bug only in the superproject."
```

## 3. Leaf Fix Execution

Use when the owning module is known and one owner should drive to proof.

```text
$ralph "Work only in <module>. Reproduce <gate-key>, fix the owning issue, rerun the smallest leaf proof until green, and stop before repin if the leaf proof is still not credible."
```

## 4. Repin Review

Use before moving a submodule SHA.

```text
$ralplan "For repinning <module>, verify the new SHA has leaf proof, list the cross-repo gates that could regress, decide whether validation is pin-only or dual-lane, and define the evidence pack required before merge."
```

## 5. PR-Tier Strict Closure

Use after a leaf fix or superproject-owned integration change.

```text
$ralph "Run the LinxISA PR-tier closure sequence for <task>: static policy guard, AVS contract, AVS tier closure, and strict_cross_repo. Record exact commands, lane, pass/fail, and artifact paths. Treat latest.json as the source of truth."
```

## 6. Dual-Lane Convergence

Use only after leaf proof and PR-tier closure are credible.

```text
$ralplan "For <task>, define the dual-lane runtime convergence plan. Specify run-id format, pin and external lane prerequisites, expected artifacts, and what counts as a true parity failure versus stale evidence."
```

## 7. Team Run

Use when several manifest owners need durable coordination.

```text
$team 4:executor "Execute <task> in manifest-aligned lanes. Keep owner scope explicit, fix leaf modules before repin, do not trust markdown over latest.json, and leave per-lane evidence under docs/bringup/gates/logs/<run-id>/<lane>/."
```

Adjust worker count to the real number of active lanes.

## 8. Docs and Contract Refresh

Use when the change is owned by `isa` or `docs`.

```text
$ralph "Work only in isa/docs for <task>. Refresh the contract or manual artifacts that follow from the change, rerun the smallest contract checks, and record any downstream gates that must be revisited before closure."
```

## 9. Skill Evolution Review

Use near closeout when you want to decide whether reusable knowledge should
be promoted into skills.

```text
$ralplan "For the completed run <run-id>, decide skill-evolve:update or skill-evolve:no-update for each affected module. Only approve updates for reusable contracts, reproducibility commands, or recurring triage patterns."
```

## 10. Wiki Capture

Use when the result should survive terminal history.

```text
$ralph "Summarize the reusable findings from <task> into concise wiki-ready notes: failure signature, owning gate/module, minimal reproducer, proof command, lane constraints, and artifact paths. Exclude stale or machine-specific absolute paths."
```

## Scenario Bundles

### Red gate in unknown owner

```text
$deep-interview "Investigate failing gate <gate-key> in /Users/zhoubot/linx-isa. Identify the owning module, checklist ids, smallest reproducer, lane impact, blocking waivers if any, and required evidence outputs under docs/bringup/gates/."
$ralplan "For <gate-key>, approve module scope, leaf proof, repin boundary, strict closure order, lane policy, and exact closeout evidence."
```

### Safe repin

```text
$ralplan "For repinning <module>, verify the new SHA has leaf proof, list the cross-repo gates that could regress, decide whether validation is pin-only or dual-lane, and define the evidence pack required before merge."
$ralph "Run the PR-tier closure sequence for the <module> repin and leave exact evidence paths."
```

### Nightly closure

```text
$ralplan "Define the nightly closure plan for <task>: required gates, pin/external expectations, run-id naming, stale-evidence rejection, and failure classification."
$team 5:executor "Execute nightly closure for <task> in manifest-aligned lanes with durable evidence and no undocumented waivers."
```
