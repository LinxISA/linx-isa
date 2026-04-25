# LinxISA Superproject Bring-up Methodology

This document explains how the `linx-isa` superproject manages many active
submodules without turning bring-up into ad-hoc integration work. It is both a
methodology note and an operator runbook for humans and agents.

The short version is:

- The superproject is the coordination plane, not the implementation dump.
- Leaf modules change first; the superproject repins only after module-owned
  gates are green.
- Bring-up is strict by default: no implicit passes, no undocumented waivers,
  no status-by-narrative.
- Tests and gates are the contract. Markdown is a view over machine-readable
  evidence, not a substitute for it.

## What The Superproject Owns

The superproject owns cross-repo coordination, not leaf implementation detail.
Its job is to make the whole stack reproducible, attributable, and testable.

Canonical responsibilities:

- Keep the submodule topology correct in root `.gitmodules`.
- Define allowed paths and canonical work locations.
- Maintain the architecture and bring-up contract in `docs/` and `isa/`.
- Run cross-repo closure gates from `tools/regression/` and `tools/bringup/`.
- Publish canonical evidence under `docs/bringup/gates/`.
- Assign gate ownership through
  `docs/bringup/agent_runs/manifest.yaml` and checklist files.
- Record explicit waivers in `docs/bringup/agent_runs/waivers.yaml`.

The superproject should not become a shadow copy of `llvm`, `qemu`, `linux`,
`glibc`, `musl`, `LinxCore`, or `pyCircuit`. If a bug lives in a leaf module,
fix it in that module first, then repin the superproject.

## Core Design Principles

### Specification-first

Architecture intent lives in `isa/` and `docs/architecture/`. Every bring-up
decision should trace back to a stable contract, not to a local workaround.

### Submodule-first

Ecosystem repositories remain separate repos with separate ownership and gate
surfaces. The superproject records known-good SHAs and validates that they work
together.

### Single canonical workspace

Use one canonical checkout rooted at the superproject. Avoid parallel ad-hoc
trees for the same bring-up lane. Cross-repo evidence must point back to the
same workspace layout.

### Test-driven bring-up

Bring-up work starts from a failing contract, test, or gate. A feature is not
"brought up" because code exists; it is brought up when the right gate passes
with captured evidence.

### Strict by default

Required, non-waived gates must pass. Waivers are phase-bound, explicit,
time-limited, and machine-checked. Silent exceptions are not allowed.

### Evidence over narrative

The source of truth is the machine-readable gate report and its attached logs,
artifacts, and SHA manifest. Human-readable status pages are generated views.

## The Four Control Planes

The superproject stays manageable because it separates four concerns.

### Topology plane

This controls where work is allowed to live and how repos are linked.

Key files:

- `AGENTS.md`
- `docs/project/navigation.md`
- `docs/project/repository-flow.md`
- `.gitmodules`
- `tools/ci/check_repo_layout.sh`

Rules:

- No random top-level directories.
- No revival of deprecated paths such as `tests/`, `examples/`, or
  `compiler/linx-llvm`.
- Linx ecosystem links stay in root `.gitmodules`, not inside leaf repos.

### Ownership plane

This controls who owns each gate and which modules an agent may touch.

Key files:

- `docs/bringup/agent_runs/manifest.yaml`
- `docs/bringup/agent_runs/checklists/*.md`
- `docs/bringup/agent_runs/waivers.yaml`

Rules:

- Every required gate key maps to a checklist owner.
- Agents declare explicit module scope.
- Cross-module ownership is reserved for approved integration roles.
- Canonical skills are part of the coordination contract.

### Validation plane

This controls what must pass before a change can be considered integrated.

Key entry points:

- `tools/regression/strict_cross_repo.sh`
- `tools/bringup/check_multi_agent_gates.py`
- `tools/bringup/check_gate_consistency.py`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_avs_profile_closure.py`
- `tools/bringup/run_runtime_convergence.sh`

Rules:

- Static structure must validate before runtime closure is trusted.
- Runtime closure must be lane-specific and run-id-backed.
- Strict release closure requires both `pin` and `external` lanes.

### Evidence plane

This controls how runs are recorded and how stale or partial data is rejected.

Key artifacts:

- `docs/bringup/gates/latest.json`
- `docs/bringup/GATE_STATUS.md`
- `docs/bringup/gates/logs/<run-id>/<lane>/...`
- `docs/bringup/agent_runs/skills_evolution/latest.json`

Rules:

- Each run records command, lane, timestamp, result, and evidence.
- SHA manifests must identify the exact versions under test.
- Generated markdown must match the canonical JSON timestamp.

## Canonical Module Model

The superproject stays understandable by treating each major repo as a leaf with
its own primary responsibility.

| Domain | Canonical Module | Primary Closure Surface |
| --- | --- | --- |
| ISA / docs | `isa`, `docs` | contract checks, architecture lint, AVS contract |
| Compiler | `compiler/llvm` | compile AVS, coverage, tool build closure |
| Emulator | `emulator/qemu` | runtime AVS, strict system, opcode sync |
| Kernel | `kernel/linux` | initramfs smoke/full boot, `vmlinux` closure |
| Libraries | `lib/glibc`, `lib/musl` | libc stage gates, runtime smoke |
| RTL | `rtl/LinxCore` | stage/connectivity lint, cosim, perf floor |
| Model | `tools/pyCircuit` | model diff, interface contract |
| Integration | superproject | strict cross-repo closure, dual-lane parity |

This is the main scaling trick: each module proves local correctness first, then
the superproject proves cross-module compatibility second.

## Why Dual Lanes Matter

LinxISA uses two bring-up lanes:

- `pin`: run exactly the submodule SHAs recorded by the superproject.
- `external`: run against the active external work trees or builds.

This separates two different questions:

1. Is the pinned workspace reproducibly green?
2. Will the next repin still be green once current leaf changes are composed?

Strict closure requires both answers. A system that only passes in `external`
has not been stabilized. A system that only passes in `pin` may be hiding
upcoming integration regressions.

## What "Strict Gate" Means In Practice

In this repository, "strict" is operational, not rhetorical.

Strict means:

- required, non-waived gates must pass;
- waivers must be documented in the waiver ledger;
- lane, run-id, and timestamp are mandatory context;
- stale artifacts are rejected;
- release-strict profiles disallow blocked-mode shortcuts;
- markdown summaries cannot disagree with the canonical JSON report;
- required gate sets must match across `pin` and `external` lanes.

`tools/regression/strict_cross_repo.sh` encodes many of these policies through
profile defaults and hard failures. `tools/bringup/check_gate_consistency.py`
adds freshness, lane parity, artifact presence, and summary consistency checks.

## What "Strict Check" Means

Strict checks happen in two layers.

### Static strict checks

These validate structure before any runtime test is trusted.

Examples:

- manifest schema and enforcement mode,
- checklist ID integrity,
- gate-to-owner assignment coverage,
- canonical skill names,
- allowed module scope,
- waiver format and phase binding.

Primary command:

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

### Runtime strict checks

These validate a concrete lane/run against the static policy.

Examples:

- every required runtime row has a valid owner,
- required non-waived rows are `pass`,
- waiver decisions are active for the current phase only,
- output summary JSON exists for the run,
- strict closure is backed by current artifacts.

Primary command form:

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode runtime \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists \
  --report docs/bringup/gates/latest.json \
  --lane pin \
  --run-id <run-id> \
  --out docs/bringup/gates/logs/<run-id>/pin/multi_agent_summary.json
```

## Test-Driven Bring-up Method

The recommended bring-up loop is:

1. Start from a failing contract, test, or audit.
2. Reproduce it with the smallest leaf-level command that still exposes the
   failure.
3. Fix the leaf module in its own repo.
4. Re-run the leaf-owned gates until they pass.
5. Repin the submodule SHA in the superproject.
6. Re-run strict cross-repo closure.
7. Publish updated evidence only after the strict run is green.

This prevents a common failure mode in large bring-up projects: using the
superproject as a place to "paper over" unresolved leaf-module defects.

## Agent-Friendly Operating Model

An agent-friendly superproject is one where an agent can answer four questions
without human folklore:

1. Which modules am I allowed to touch?
2. Which gates prove my scope is healthy?
3. Which artifacts are canonical?
4. What is the exact next step when a gate fails?

The current LinxISA layout already supports this well:

- allowed modules are listed in `manifest.yaml`;
- gate ownership is assigned to checklist IDs;
- canonical skills are named explicitly;
- required evidence lives in stable paths under `docs/bringup/gates/`;
- navigation rules prevent path drift;
- repin discipline keeps cross-repo change flow predictable.

An agent should work with the following discipline:

- touch only declared modules unless acting as an approved cross-module agent;
- treat checklist IDs as machine-readable commitments, not informal notes;
- prefer the smallest gate that can prove or disprove the hypothesis;
- record evidence at the run level, not only in prose;
- finish with an explicit repin/no-repin decision.

## Daily Superproject Workflow

### Bootstrap and topology validation

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

This confirms that the workspace layout is canonical before any gate result is
interpreted.

### Refresh canonical skills

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

This keeps the agent workflow aligned with the current module contracts and
triage patterns.

### Run static bring-up policy checks

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

Do this before deeper runtime work. If static policy is broken, runtime results
are not trustworthy enough for closure.

### Run contract checks

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
```

This confirms that the architecture-facing test matrix is still canonical.

## Repin Workflow

Repinning is where many multi-repo projects become chaotic. The LinxISA
discipline should be:

1. Land the fix in the leaf module first.
2. Verify the leaf module's own gates there.
3. Update the submodule SHA in the superproject.
4. Run strict cross-repo closure.
5. Merge the repin only when required gates and evidence are complete.

Recommended sync and repin flow:

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule update --remote \
  compiler/llvm \
  emulator/qemu \
  kernel/linux \
  rtl/LinxCore \
  tools/pyCircuit \
  lib/glibc \
  lib/musl \
  workloads/pto_kernels
bash tools/ci/check_repo_layout.sh
```

Important rule: do not repin several unrelated modules speculatively just
because they all changed upstream. Repin only modules with a known reason and a
known gate impact.

## Strict Closure Workflow

### PR-tier closure

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

Use this for normal integration closure after a focused repin or docs/contract
update.

### Nightly-tier closure

```bash
LINX_GATE_TIER=nightly RUN_EXTENDED_CROSS_GATES=1 RUN_PERF_FLOOR_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

Use this when you need the broader nightly surface, including performance-floor
checks.

### Dual-lane runtime convergence

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

Use this when the question is "are both lanes converged and equally strict?"
rather than "does one command happen to pass right now?"

### Release-strict consistency check

```bash
python3 tools/bringup/check_gate_consistency.py \
  --report docs/bringup/gates/latest.json \
  --progress docs/bringup/PROGRESS.md \
  --gate-status docs/bringup/GATE_STATUS.md \
  --libc-status docs/bringup/libc_status.md \
  --profile release-strict \
  --lane-policy external+pin-required \
  --trace-schema-version 1.0 \
  --max-age-hours 24
```

This is the final "do the artifacts agree with each other?" guardrail.

## Failure Handling And Triage Order

When a large bring-up stack fails, fix failures in this order.

### Topology failures first

If `check_repo_layout.sh` or navigation policy fails, stop. Path drift and
wrong-repo edits invalidate later evidence.

### Static policy failures second

If `check_multi_agent_gates.py --mode static` fails, fix manifest, checklist,
or waiver structure before trusting runtime results.

### Leaf gate failures third

If a domain gate fails, return to the owning leaf module and fix there first.
Examples:

- compile coverage failure -> `compiler/llvm`
- strict system/runtime failure -> `emulator/qemu`
- Linux boot failure -> `kernel/linux`
- cosim or perf-floor failure -> `rtl/LinxCore`

### Integration failures last

Only after leaf gates are green should you debug failures in:

- `strict_cross_repo.sh`,
- dual-lane parity,
- report freshness,
- summary inconsistency,
- missing evidence packaging.

This ordering is important. Many integration failures are only symptoms of an
unfixed leaf regression.

## Waiver Discipline

Waivers are not "temporary comments." They are a first-class policy mechanism.

Required properties:

- explicit owner,
- referenced issue,
- associated phase,
- `expires_utc`,
- runtime visibility through the validator.

A waiver should answer one question cleanly: why is a failing required gate not
currently blocking the active phase? If that answer is not precise, the waiver
is probably too weak to keep.

## Evidence Packaging Standard

Every serious bring-up run should leave behind:

- a run ID;
- the lane name;
- the exact commands used;
- the SHA manifest for the lane;
- pass/fail rows in `docs/bringup/gates/latest.json`;
- log or artifact paths under `docs/bringup/gates/logs/<run-id>/<lane>/`;
- a multi-agent summary JSON for strict runtime closure.

This makes the run replayable and auditable. Without this package, "it passed on
my machine" is not acceptable evidence.

## Recommended Decision Rules

Use these rules to keep the system stable as it grows.

- Add a new gate when a failure pattern is recurring or architecture-visible.
- Add a checklist item when ownership must become durable and reviewable.
- Add a waiver only when the active phase really permits the gap.
- Repin only after the changed module has its own proof of health.
- Escalate from leaf testing to strict cross-repo closure only after the leaf
  signal is clean.
- Treat generated markdown as disposable; regenerate it from canonical JSON
  instead of editing it by hand.

## Minimal Operator Runbook

For most superproject bring-up work, this sequence is enough.

1. Sync submodules and validate layout.
2. Refresh canonical skills if this is a new bring-up cycle.
3. Run static strict checks.
4. Run the smallest failing domain gate.
5. Fix the leaf module in its own repo.
6. Repin the affected submodule SHA.
7. Run PR-tier `strict_cross_repo.sh`.
8. Run dual-lane convergence if the change is integration-sensitive.
9. Run `check_gate_consistency.py` before calling the workspace green.
10. Regenerate any markdown view from the canonical JSON report.

## Anti-Patterns To Avoid

Avoid these patterns; they make a large bring-up stack unmanageable.

- Editing status markdown without updating canonical JSON evidence.
- Hiding a leaf bug behind a superproject-only workaround.
- Letting path drift create parallel "almost canonical" folders.
- Mixing unrelated repins into one speculative integration batch.
- Treating waivers as permanent policy.
- Declaring success from a single lane when strict closure requires two.
- Using agents without explicit module scope or checklist ownership.

## Summary

LinxISA scales bring-up across many modules by being strict about where truth
lives:

- contracts in `isa/` and `docs/`,
- topology in root policy files and `.gitmodules`,
- ownership in `manifest.yaml` and checklist IDs,
- integration proof in strict gates,
- release truth in canonical JSON evidence.

That is the agent-friendly part. An agent does not need tribal knowledge if the
repo already states:

- where it may work,
- what it must prove,
- how failure is assigned,
- and which artifact is authoritative.
