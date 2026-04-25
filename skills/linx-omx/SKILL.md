---
name: linx-omx
description: Use when operating inside /Users/zhoubot/linx-isa with OMX and you need LinxISA-specific task routing, gate triage, leaf-before-repin discipline, strict closure, dual-lane convergence, or evidence-backed bring-up workflows.
---

# Linx OMX

Use this skill when the task is about using OMX well inside the LinxISA
superproject.

This skill does not replace the domain skills such as `linx-superproject`,
`linx-compiler`, `linx-qemu`, `linx-linux`, `linx-core`, `linx-pycircuit`, or
`linx-lib`. It routes OMX behavior so those domain skills are used in the right
order and with the right proof requirements.

## Core Rules

- Treat the superproject as the coordination plane, not the place to hide leaf
  fixes.
- Start from the smallest failing contract, gate, or test.
- Trust `docs/bringup/gates/latest.json` over markdown summaries.
- Run topology and static policy checks before trusting runtime closure.
- Fix leaf modules first; repin second; run strict closure third.
- Keep evidence path clean: command, lane, run-id, SHA manifest, pass/fail, and
  artifact path.
- Do not run `avs/qemu` suites in parallel against the same output directory.

## Default Startup

From `/Users/zhoubot/linx-isa`:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
omx --high
```

Use `--madmax` only when you intentionally want the less constrained path.

## OMX Routing

### Use `$deep-interview` when:

- the failing gate owner is unclear,
- module boundaries are unclear,
- lane policy is unclear,
- stop conditions are unclear.

Prompt shape:

```text
$deep-interview "Investigate failing gate <gate-key>. Identify owner module, smallest reproducer, lane impact, and required evidence outputs."
```

### Use `$ralplan` when:

- scope is known but gate order is still fuzzy,
- you need to lock repin policy,
- you need to define exact closeout proof,
- multiple plausible owners exist and the integration boundary must be fixed.

Prompt shape:

```text
$ralplan "Approve module scope, leaf proof, repin boundary, closure gates, lane policy, and evidence outputs for <task>."
```

### Execute directly when:

- one owner and one module are already obvious,
- the task is small and reversible,
- tmux/worktree durability is not needed.

### Use native subagents when:

- you have several small read-only questions,
- the next step benefits from parallel lookup,
- the work does not need durable tmux or worktree state.

### Use `omx team` when:

- the task is long-running and cross-owner,
- tmux/worktree durability matters,
- you need manifest-aligned lanes such as `arch`, `llvm`, `qemu`, `linux`,
  `libc`, `linxcore`, `pycircuit`, or `integration`.

Do not use `omx team` for trivial fanout.

### Use `$ralph` or `omx ralph` when:

- the plan is already approved,
- one owner should keep pushing until verification is complete,
- the task benefits from a persistent completion loop.

## Mandatory Checks

### Topology preflight

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

### Static policy guard

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

### PR-tier closure

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml

python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

### Dual-lane runtime convergence

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

## Domain Handoff

Route the work into the owning domain skill after OMX routing is settled:

- `linx-superproject` for cross-repo closure, topology, repin, and evidence
  packaging.
- `linx-compiler` for compile AVS and LLVM closure.
- `linx-qemu` for runtime AVS, strict system, opcode sync, and emulator issues.
- `linx-linux` for Linux boot and initramfs closure.
- `linx-core` for RTL, block structure, testbench, and trace-adjacent RTL work.
- `linx-pycircuit` for model-diff and interface-contract work.
- `linx-lib` for glibc/musl closure.
- `linx-isa` for architecture contracts and docs gates.

## Evidence Contract

For every serious run, leave behind:

- exact command,
- lane,
- run-id,
- SHA manifest,
- pass/fail result,
- artifact or log path under `docs/bringup/gates/`.

If you cannot point to the evidence path, the run is not complete.

## Anti-Patterns

Do not:

- trust `GATE_STATUS.md` over `latest.json`,
- repin before the owning leaf proof is green,
- debug dual-lane parity before leaf correctness,
- route work to forbidden legacy paths,
- run shared-output runtime suites in parallel,
- use `omx team` where native subagents or direct execution are enough.

## References

Read these as needed:

- `/Users/zhoubot/linx-isa/docs/project/omx-linxisa-playbook.md`
- `/Users/zhoubot/linx-isa/docs/project/omx-linxisa-prompt-templates.md`
- `/Users/zhoubot/linx-isa/docs/project/superproject-bringup-methodology.md`
- `/Users/zhoubot/linx-isa/docs/project/new-agent-sop.md`
- `/Users/zhoubot/linx-isa/docs/project/maintainer-repin-checklist.md`
- `/Users/zhoubot/linx-isa/docs/bringup/agent_runs/manifest.yaml`
