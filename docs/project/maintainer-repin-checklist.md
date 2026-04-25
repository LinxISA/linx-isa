# LinxISA Maintainer Repin Checklist

This checklist is for maintainers who are updating one or more submodule SHAs in
the `linx-isa` superproject.

Use it to keep repins disciplined, attributable, and reproducible.

## Repin Preconditions

Do not start a repin until these are true:

- the leaf-module change already exists in the owning repository;
- the leaf owner has run the module-owned gates for that change;
- the reason for the repin is explicit;
- the expected gate impact is known.

Bad repin pattern:

- "these modules changed upstream, so I bumped them all together."

Good repin pattern:

- "QEMU strict-system fix landed upstream; repin `emulator/qemu`; rerun QEMU and
  integration closure."

## Scope Declaration

Before editing SHAs, write down:

- which module or modules are being repinned;
- why each module is changing;
- which gates are expected to move;
- whether the change is leaf-only or cross-module.

If you cannot answer those four questions, the repin batch is too vague.

## Workspace Preparation

From repo root:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

Refresh canonical skills at the start of a new bring-up cycle:

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

## Static Policy Guard

Run this before runtime closure:

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

If this fails, do not trust later runtime results until policy is fixed.

## Repin Mechanics

Update only the intended modules:

```bash
git submodule update --remote \
  compiler/llvm \
  emulator/qemu \
  kernel/linux \
  rtl/LinxCore \
  tools/pyCircuit \
  lib/glibc \
  lib/musl \
  workloads/pto_kernels
```

In practice, narrow that command to the specific modules you are repinning.

After updating SHAs:

```bash
git status
git diff --submodule
```

Check that:

- only intended submodules moved;
- `.gitmodules` changed only if URL policy really changed;
- no unrelated workspace churn is mixed into the repin.

## Required Questions Per Module

For every repinned module, answer:

1. What leaf gate proved the new SHA was healthy?
2. What cross-repo gate could regress because of this SHA move?
3. Does this repin require `pin` only, or both `pin` and `external` lane
   validation?
4. Does any waiver need to be added, removed, or allowed to expire?

## Minimal Gate Matrix After Repin

### Always

Run:

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

### When strict integration parity matters

Run both lanes:

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

### When closing a strict release-quality run

Run the consistency gate:

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

## Domain-Specific Expectations

Use this table to avoid under-testing a repin.

| Module | Minimum Proof You Should Expect |
| --- | --- |
| `compiler/llvm` | compile AVS, coverage, auxiliary LLVM tools if Linux/libc closure matters |
| `emulator/qemu` | strict system, runtime AVS, opcode sync, pinned binary build |
| `kernel/linux` | `vmlinux` build, initramfs smoke/full boot |
| `lib/glibc` | G1a/G1b stage gates that apply to the current profile |
| `lib/musl` | build closure and runtime smoke as applicable |
| `rtl/LinxCore` | lint/cosim/perf gates appropriate to the phase |
| `tools/pyCircuit` | interface contract and model-diff surfaces |
| `isa`, `docs` | contract checks and any generated artifact refresh they imply |

## Evidence Packaging Checklist

Before merging a repin, make sure you can point to:

- run ID,
- lane,
- exact command,
- log path,
- SHA manifest entry in `docs/bringup/gates/latest.json`,
- generated status refresh if applicable,
- multi-agent summary JSON for strict runtime closure.

If any of those are missing, the repin is not ready to merge.

## Waiver Discipline During Repin

Do not smuggle a red gate through a repin by editing prose or by relying on an
implicit understanding.

If a waiver is necessary:

- record it in `docs/bringup/agent_runs/waivers.yaml`;
- bind it to the active phase;
- set an owner and `expires_utc`;
- make sure runtime validators can see it.

If a waiver is no longer needed, remove it in the same maintenance window.

## Merge Decision

A repin is ready only when:

- intended modules are the only SHA moves in the batch;
- required non-waived gates pass;
- evidence is fresh and machine-readable;
- `pin` and `external` lane policy is satisfied for the target closure level;
- generated markdown agrees with canonical JSON;
- the commit message explains the module scope and reason.

## Commit Shape

Prefer repin commits that are narrow and explainable.

Good examples:

- `chore(submodule): repin emulator/qemu for strict-system timer fix`
- `chore(submodules): repin compiler/llvm and kernel/linux for pinned build closure`

Avoid opaque messages such as:

- `update deps`
- `sync repos`
- `latest upstream`

## Anti-Patterns

Do not:

- repin multiple unrelated modules just because they are available;
- merge a repin with stale `latest.json` evidence;
- edit `GATE_STATUS.md` by hand;
- assume `pin` lane success is enough when strict closure requires both lanes;
- accept blocked-mode shortcuts in release-strict closure.

## Final Merge Checklist

1. Intended submodule SHAs only.
2. Leaf proof identified for each moved module.
3. PR-tier or nightly-tier strict closure run.
4. Dual-lane validation if required.
5. Consistency check passed for strict release closure.
6. Waivers reviewed.
7. Evidence paths recorded.
8. Commit message names the repinned modules and reason.
