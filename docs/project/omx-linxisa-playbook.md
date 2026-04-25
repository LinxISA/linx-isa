# LinxISA OMX Playbook

This playbook turns the LinxISA superproject rules into a repeatable OMX
operator flow.

Use it when work spans any combination of:

- gate triage,
- owner and module routing,
- leaf fix then repin discipline,
- strict cross-repo closure,
- dual-lane convergence,
- skill sync and reusable run knowledge.

## Operating Assumptions

- The superproject is the coordination plane, not the place to hide leaf fixes.
- `docs/bringup/gates/latest.json` is the canonical gate truth.
- `docs/bringup/GATE_STATUS.md` is a generated view.
- Required non-waived gates block progress.
- Work starts from the smallest failing contract or gate.
- Repins happen only after leaf proof is green.
- `avs/qemu` suites must not share the same output directory in parallel.

## Session Bootstrap

Start from repo root:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
omx --high
```

Use `--madmax` only when you intentionally want the less constrained path.

## Routing Matrix

| Situation | OMX surface | Goal |
| --- | --- | --- |
| Failing gate, unclear owner, unclear stop condition | `$deep-interview` | Lock the smallest reproducer, owner module, lane impact, and evidence target |
| Scope is known but plan, gate order, or repin policy is still fuzzy | `$ralplan` | Approve task order, proof requirements, and closeout criteria |
| One owner, one module, reversible steps | direct execution | Keep latency low and stay inside the owning module |
| Several small read-only questions | native subagents or `omx explore` | Parallelize lookup without starting a tmux runtime |
| Long-running multi-owner closure with durable coordination | `omx team` | Run work in manifest-aligned lanes with tmux/worktree state |
| Approved single-owner completion loop | `$ralph` or `omx ralph` | Keep the task driving until evidence-backed completion |

## Scenario 1: Gate Triage

Use this when a gate is red and the owner is not obvious.

1. Preflight:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

2. Fast lookup:

```bash
omx explore --prompt "Map gate <gate-key> to its owner, checklist ids, module scope, and primary scripts in /Users/zhoubot/linx-isa."
```

3. Inside the OMX session:

```text
$deep-interview "Investigate failing gate <gate-key>. Identify owner module, smallest reproducer, lane impact, and required evidence outputs."
$ralplan "Approve module scope, gate order, repin policy, and closeout evidence for <gate-key>."
```

Expected outcome:

- one owner from `docs/bringup/agent_runs/manifest.yaml`,
- one smallest leaf or superproject gate,
- explicit lane policy (`pin`, `external`, or both),
- explicit evidence paths under `docs/bringup/gates/`.

## Scenario 2: Leaf Fix Then Repin

Use this when the problem belongs to `compiler/llvm`, `emulator/qemu`,
`kernel/linux`, `lib/*`, `rtl/LinxCore`, or `tools/pyCircuit`.

1. Confirm the leaf owner and leaf gate first.
2. Fix the issue in the owning leaf module.
3. Rerun the leaf proof until it is green.
4. Repin only the intended submodule SHA.
5. Run superproject closure after the repin.

Prompt shape:

```text
$ralplan "For <module> and <gate>, approve the exact leaf proof, repin boundary, cross-repo gates to rerun, and whether dual-lane validation is required."
```

Repin sanity checks:

```bash
git status
git diff --submodule
```

Always answer:

- What leaf proof made the SHA safe?
- What cross-repo gate could regress?
- Does closure require `pin` only or both lanes?
- Does any waiver need to change?

## Scenario 3: PR-Tier Strict Closure

Use this after a leaf fix or superproject-owned integration change.

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists

python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml

python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

Use `omx sparkshell` if you want shell-native bounded verification with OMX
surface consistency:

```bash
omx sparkshell bash tools/ci/check_repo_layout.sh
```

## Scenario 4: Dual-Lane Runtime Convergence

Use this only after the owning leaf proof and PR-tier closure are credible.

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

Use `omx team` when this requires durable multi-owner work with separate
checklists and evidence streams. Keep lanes aligned with manifest owners such as
`arch`, `llvm`, `qemu`, `linux`, `libc`, `linxcore`, `pycircuit`, and
`integration`.

## Scenario 5: Skill Sync and Reusable Knowledge

Start a new bring-up cycle by refreshing canonical skills:

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

Use the local wiki for run knowledge that should not stay trapped in terminal
history:

```bash
omx wiki wiki_ingest --input '{"source":"docs/bringup/gates/latest.json","title":"gate-truth-notes"}' --json
omx wiki wiki_query --input '{"query":"strict_cross_repo stale artifact failure"}' --json
```

Good wiki targets:

- recurring gate failures,
- lane-specific footguns,
- evidence path conventions,
- skill-evolve decisions worth reusing.

## Scenario 6: Long-Running OMX Sessions

Useful operator surfaces:

```bash
omx status
omx hud --watch
omx resume
```

Use `omx team` only when tmux/worktree durability is worth the overhead.
For small in-session fanout, prefer native subagents.

## Anti-Patterns

Do not:

- debug lane parity before the owning leaf gate is green,
- treat markdown status as the source of truth,
- repin unrelated modules together,
- parallelize `avs/qemu` runs against the same output directory,
- fix a leaf bug only in the superproject,
- leave a run without command, lane, run-id, SHA manifest, and artifact paths.

## Closeout Checklist

Before declaring success:

1. Confirm the smallest relevant leaf or superproject gate is green.
2. Confirm PR-tier strict closure if integration changed.
3. Confirm dual-lane closure if the task required it.
4. Confirm evidence exists under `docs/bringup/gates/`.
5. Decide explicitly: repin, no repin, or blocked with waiver.
6. Update generated markdown only from canonical reports.

## Primary References

- `AGENTS.md`
- `docs/project/navigation.md`
- `docs/project/omx-linxisa-prompt-templates.md`
- `docs/project/new-agent-sop.md`
- `docs/project/maintainer-repin-checklist.md`
- `docs/project/superproject-bringup-methodology.md`
- `docs/bringup/agent_runs/manifest.yaml`
- `docs/bringup/agent_runs/waivers.yaml`
- `docs/bringup/gates/latest.json`
