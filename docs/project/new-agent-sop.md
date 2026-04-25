# LinxISA New Agent SOP

This is the shortest safe operating procedure for a new agent working inside
the `linx-isa` superproject.

Use this document when you need to start work quickly without reloading the full
superproject methodology.

## Mission

Your job is not to "make the repo look green." Your job is to:

1. stay inside the canonical workspace and allowed module scope;
2. find the smallest failing contract, gate, or test;
3. fix the owning leaf module first;
4. repin and rerun strict closure only after leaf proof is green;
5. leave machine-readable evidence behind.

## Before You Touch Anything

Run these commands from repo root:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

If layout validation fails, stop and fix topology first.

## Read These Files First

Read only what you need, in this order:

1. `AGENTS.md`
2. `docs/project/navigation.md`
3. `docs/bringup/agent_runs/manifest.yaml`
4. your owning checklist under `docs/bringup/agent_runs/checklists/`
5. the relevant gate script under `tools/bringup/` or `tools/regression/`

If the task is architectural, also read the relevant contract in `docs/` or
`isa/`.

## Scope Rules

Follow these rules strictly:

- Work only in declared modules.
- Do not create new top-level directories.
- Do not route work into forbidden legacy paths.
- Do not fix a leaf-module bug in the superproject unless the problem is
  genuinely superproject-owned.
- Do not treat generated markdown as source of truth.

## Canonical Source Of Truth

When different files disagree, trust them in this order:

1. failing test or gate command,
2. canonical contracts in `isa/` and `docs/architecture/`,
3. machine-readable reports such as `docs/bringup/gates/latest.json`,
4. generated markdown views such as `docs/bringup/GATE_STATUS.md`.

## Standard Agent Loop

Use this loop for nearly all bring-up work.

1. Reproduce the issue with the smallest gate that fails.
2. Identify the owning domain and module.
3. Fix the issue in the owning leaf module.
4. Rerun the leaf gate until it passes.
5. If the leaf repo changed, repin the submodule SHA in the superproject.
6. Run strict cross-repo closure.
7. Refresh machine-readable and generated evidence if the workflow requires it.

## Smallest Useful Commands

### Static policy check

Run this before trusting runtime closure:

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

### AVS contract check

Run this when the question is "is the bring-up contract itself still valid?":

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
```

### Strict cross-repo closure

Run this after leaf proof is green:

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

### Dual-lane convergence

Run this when integration parity matters:

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

## Domain Routing Cheat Sheet

If the first failing gate is here, start in this module:

| Failure Surface | Start Here |
| --- | --- |
| compile AVS, coverage, LLVM binutils | `compiler/llvm` |
| runtime AVS, strict system, opcode sync | `emulator/qemu` |
| Linux smoke/full boot, `vmlinux` build | `kernel/linux` |
| musl/glibc runtime or build closure | `lib/musl`, `lib/glibc` |
| cosim, stage/connectivity, perf floor | `rtl/LinxCore` |
| model diff, interface contract | `tools/pyCircuit` |
| contract docs, architecture lint, AVS contract | `isa`, `docs` |
| lane parity, gate consistency, evidence packaging | superproject |

## Failure Triage Order

Always triage in this order:

1. topology failure,
2. static policy failure,
3. leaf-module gate failure,
4. integration closure failure,
5. report freshness or evidence mismatch.

Do not debug lane parity before the leaf gate is green.

## Waiver Rules

Waivers are allowed only when they are:

- explicit,
- phase-bound,
- time-limited,
- recorded in `docs/bringup/agent_runs/waivers.yaml`.

If a failing required gate has no waiver entry, treat it as blocking.

## Evidence Rules

A serious run should leave behind:

- lane,
- run ID,
- exact command,
- SHA manifest,
- result in `docs/bringup/gates/latest.json`,
- logs or artifacts under `docs/bringup/gates/logs/<run-id>/<lane>/`.

If you cannot point to the evidence path, the run is not finished.

## Stop Conditions

Stop and escalate when:

- the task needs changes outside your declared module scope;
- the only available workaround violates the architecture contract;
- two canonical sources disagree and you cannot resolve which one is stale;
- the workspace contains user changes that directly conflict with the required
  fix.

## Closeout

Before you declare success:

1. confirm the smallest relevant leaf gate is green;
2. confirm strict cross-repo closure is green if integration changed;
3. confirm evidence paths are present;
4. decide explicitly: repin, no repin, or blocked with waiver;
5. update generated status pages only from canonical reports.

## One-Screen Summary

- Fix leaf modules first.
- Repin second.
- Run strict gates third.
- Trust JSON before markdown.
- No undocumented waivers.
- No path drift.
- No "green by narrative."
