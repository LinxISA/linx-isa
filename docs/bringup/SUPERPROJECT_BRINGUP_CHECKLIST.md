# LinxISA Superproject Bringup Blocker Checklist

Use this runbook for the current **red-gate recovery lane** in the `linx-isa`
superproject. It reflects the checked-in April 18, 2026 canonical gate report,
not the older March 15 baseline.

It is intentionally narrower than the full maturity plan:

- it focuses on the latest blocking bringup work in execution order;
- it assumes the per-domain owner checklists remain canonical for module detail;
- it names nightly/runtime follow-up lanes without trying to close them here.

Detailed owner checklists still live under
`docs/bringup/agent_runs/checklists/`.
Use this page to decide **what to do first**, then hand off to the owner
checklists for the module-specific closure criteria.

## Baseline

- Canonical baseline: [`docs/bringup/gates/latest.json`](gates/latest.json),
  generated `2026-04-18 02:11:34Z`, latest pin-lane run
  `2026-04-18-r9-pin-linuxlibc-refresh`.
- The April 18 report supersedes the stale March rows for Sail/model, PTO
  parity, AVS PR-tier closure, glibc/musl runtime, LinxCore/Testbench/Trace,
  pyCircuit, and TSVC compile-only PR coverage.
- Scope for this checklist:
  - `LINUX-004`
  - `INT-004`
  - `INT-016`
  - `INT-025`
  - `SPEC-003` / `SPEC-004` as nightly/runtime follow-up

## Current Blocker Map

| Area | Gate / ID | Current state | Triage note |
| --- | --- | --- | --- |
| Kernel | `Kernel::Linux busybox rootfs boot` / `LINUX-004` | Active blocker | Clean pinned QEMU/rootfs helpers run, but boot still trips kernel `E_BLOCK` after `/sbin/init`, currently at `__submit_bio` on `FRET.STK` with `ra=0`. |
| Kernel | `Kernel::Linux \`vmlinux\` build closure` / `LINUX-005` | Not blocked | The clean-build helper passes in the April 18 canonical run. |
| LLVM Linx target | `Compiler::AVS compile suites` + coverage | Not blocked | The active Bisheng compiler surface is `linx64`; the current in-repo compiler AVS lane and coverage are green for that registered target set. |
| Strict closure | `Regression::strict_cross_repo.sh` / `INT-004` | Active blocker | The row fails because the required BusyBox rootfs gate fails in the same run. Do not revive the stale March Sail decode diagnosis unless it reproduces. |
| Mixed tile + SIMT workloads | `Regression::PTO kernel parity` / `INT-020` | Not blocked | The April 18 canonical run records PTO parity as pass. |
| SIMT autovec | `Regression::TSVC strict coverage gate` / `INT-025` | PR not blocked | PR closure uses compile-only strict coverage at `148/151`; QEMU runtime remains a separate nightly/runtime follow-up. |
| QEMU baseline | `Emulator::QEMU all suites` + `QEMU strict system` | Not blocked | Baseline runtime/system gates are green; the remaining QEMU issue for this lane is TSVC runtime reproduction, not broad decode expansion. |
| Superproject breadth | `ISA::AVS tier closure` / `INT-016` | PR not blocked | PR-tier closure is green at `31/31`; nightly breadth remains `32/54`. |
| SPEC runtime | `Regression::SPEC stage A QEMU matrix` / `SPEC-003` | Nightly/runtime blocker | The PR run leaves this row opt-in; known follow-up remains 9p `E_BLOCK` in `___slab_alloc` and initramfs child-startup failure. |

## 1. Keep Gate Truth Current

- [x] Treat the stale March 15 Sail decode and PTO parity failures as replaced
      by the April 18 canonical report.
- [x] Re-render gate status markdown from the refreshed JSON report:

  ```bash
  python3 tools/bringup/gate_report.py render \
    --report docs/bringup/gates/latest.json \
    --out-md docs/bringup/GATE_STATUS.md
  ```

- [ ] If you need to publish a refreshed canonical report, run a new convergence
      pass instead of only editing markdown:

  ```bash
  LINX_GATE_TIER=pr \
  bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id>
  ```

- [ ] Do not keep “Sail decode generator broken” or `INT-020` as active blockers
      in prose unless they reproduce again under current workspace state.

Exit criteria:

- Sail/model status and PTO parity are green in the current canonical report.
- Gate status markdown is generated from `docs/bringup/gates/latest.json`.

## 2. Restore BusyBox Rootfs Runtime (`LINUX-004`)

- [x] Keep `LINUX-005` closed through the clean `vmlinux` helper:

  ```bash
  bash tools/bringup/run_linux_vmlinux_build_clean.sh \
    --linux-root "$PWD/kernel/linux" \
    --out-dir "$PWD/kernel/linux/build-linx-fixed" \
    --clang "$PWD/compiler/llvm/build-linxisa-clang/bin/clang" \
    --gmake /opt/homebrew/bin/gmake \
    --target vmlinux
  ```

- [ ] Reproduce the current BusyBox rootfs failure with the clean helper path:

  ```bash
  QEMU="$(bash tools/bringup/run_qemu_build_clean.sh \
    --qemu-root "$PWD/emulator/qemu" \
    --out-dir /tmp/linx-qemu-clean-build \
    --target qemu-system-linx64)" \
  ROOTFS_IMG="$(bash tools/bringup/run_linux_busybox_rootfs_build_clean.sh \
    --linux-root "$PWD/kernel/linux" \
    --out-dir /tmp/linx-linux-rootfs-clean-out \
    --llvm-build "$PWD/compiler/llvm/build-linxisa-clang")" \
  SKIP_BUILD=1 QEMU="$QEMU" \
    python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py
  ```

- [ ] Keep initramfs smoke/full boot green while iterating:

  ```bash
  python3 kernel/linux/tools/linxisa/initramfs/smoke.py
  python3 kernel/linux/tools/linxisa/initramfs/full_boot.py
  ```

Exit criteria:

- `LINUX-004` reaches BusyBox userspace and powers off cleanly.
- `LINUX-005`, smoke, and full boot remain green.

## 3. Re-run Strict Closure To First Real Failure (`INT-004`)

- [ ] After Step 2 is complete, rerun strict closure.
- [ ] Prefer the canonical convergence wrapper when refreshing checked-in gate
      truth:

  ```bash
  LINX_GATE_TIER=pr \
  bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id>
  ```

- [ ] When iterating on `strict_cross_repo.sh` in isolation, reuse the exact
      `Regression::strict_cross_repo.sh` command recorded in
      [`docs/bringup/gates/latest.json`](gates/latest.json) for the active run
      shape, so the environment matches the failing row.
- [x] Replace the stale March Sail first-failure diagnosis with the current
      BusyBox-rootfs-driven strict closure failure.
- [ ] Do not preserve “Sail decode generator broken” as the active `INT-004`
      narrative unless it reproduces again under the current workspace.

Exit criteria:

- `INT-004` points at the current first real failure, not the stale March Sail
  failure.
- The rerun has a new run ID, updated log paths, and a refreshed multi-agent
  summary.

## 4. Keep TSVC PR Coverage Separate From Runtime Follow-Up (`INT-025`)

- [x] Keep the PR lane on compile-only strict coverage until the auto-runtime
      hangs are closed. Dedicated runtime triage should still classify the
      first hanging kernel against
      [`docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`](SIMT_COMPILER_SUPPORTED_SUBSET.md)
      as exactly one of:
  - within the documented supported subset;
  - intentional scalar fallback;
  - blocked on missing grouped EXEC-mask save/restore support.
- [ ] Keep the current architecture boundary explicit during runtime triage:
  - grouped single-block if-converted and active-replay shapes are valid work;
  - raw grouped multi-block divergence is still intentionally unclosed because
    the canonical surface lacks a first-class `p` save/restore carrier.
- [ ] Only promote support inside the documented subset. If a timed-out shape
      falls outside that subset, treat the issue as workload-policy or coverage
      scope, not as proof that grouped divergent closure is already required.

Exit criteria:

- The PR lane uses compile-only strict coverage at the documented `148/151`
  floor instead of a stale `151/151` QEMU gate.
- Dedicated runtime follow-up still has a recorded first hanging kernel and a
  documented classification.

## 5. Re-run Closure Audits

- [ ] Treat the commands below as **repo-root commands**. If you need to `cd`
      into a subdirectory, capture the root first:

  ```bash
  ROOT=$PWD
  ```

- [ ] Re-run the current workload PR checks after relevant changes:

  ```bash
  python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120
  python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --vector-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --no-run-qemu --out-dir workloads/generated
  ```

- [ ] Re-run the integration breadth checks:

  ```bash
  python3 tools/bringup/check_avs_profile_closure.py \
    --matrix avs/linx_avs_v1_test_matrix.yaml \
    --status avs/linx_avs_v1_test_matrix_status.json \
    --tier pr
  ```

- [ ] Re-run strict closure after the BusyBox fix:
  - canonical report refresh: `tools/bringup/run_runtime_convergence.sh`
  - focused iteration: exact `strict_cross_repo.sh` command from the current
    gate report row
- [ ] Update integration checklist statuses only from fresh rerun evidence.

Exit criteria:

- stale blockers have been replaced by current evidence;
- `LINUX-005` is resolved and `LINUX-004` carries the current failing logs;
- `INT-025` remains a PR compile-coverage gate with runtime tracked separately;
- `INT-016` and `INT-004` reflect current rerun evidence, not March carryover.

## Assumptions And Defaults

- This page is limited to the current superproject blocker slice for kernel,
  LLVM/SIMT autovec, mixed tile/SIMT workloads, QEMU baseline, and strict
  closure.
- The April 18, 2026 canonical report is the checked-in baseline until a newer
  canonical run replaces it.
- Owner-specific PR gates in glibc runtime, LinxCore, Testbench, Trace, and
  pyCircuit are green in the current baseline; their nightly breadth remains
  separate follow-up work.
