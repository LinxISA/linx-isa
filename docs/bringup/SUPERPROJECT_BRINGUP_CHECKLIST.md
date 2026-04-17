# LinxISA Superproject Bringup Blocker Checklist

Use this runbook for the current **red-gate recovery lane** in the `linx-isa`
superproject.

It is intentionally narrower than the full maturity plan:

- it focuses on the latest blocking bringup work in execution order;
- it assumes the per-domain owner checklists remain canonical for module detail;
- it does not try to solve unrelated red gates in libc runtime, LinxCore,
  Testbench, Trace, or pyCircuit.

Detailed owner checklists still live under
`docs/bringup/agent_runs/checklists/`.
Use this page to decide **what to do first**, then hand off to the owner
checklists for the module-specific closure criteria.

## Baseline

- Canonical baseline: [`docs/bringup/gates/latest.json`](gates/latest.json)
  from pin-lane run `2026-03-15-r2-pin` (`2026-03-15 02:38:42Z`).
- Fresher spot checks from **2026-04-11** override two stale March rows:
  - `python3 tools/bringup/check_sail_model.py --require-parser` is green.
  - `python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120`
    is green, and `workloads/generated/pto_kernel_parity_latest.json` reports
    `all_match=true` for 27 kernels.
- Scope for this checklist:
  - `LINUX-005`
  - `INT-016`
  - `INT-020`
  - `INT-025`
  - `INT-004`

## Current Blocker Map

| Area | Gate / ID | Current state | Triage note |
| --- | --- | --- | --- |
| Kernel | `Kernel::Linux \`vmlinux\` build closure` / `LINUX-005` | Active blocker | `kernel/linux` is git-clean, but source-tree generated state such as `kernel/linux/include/generated` still trips the Kbuild `mrproper` guard. |
| LLVM Linx target | `Compiler::AVS compile suites` + coverage | Not blocked | `linx32`, `linx64`, and coverage are already green in the March 15 canonical run. |
| Strict closure | `Regression::strict_cross_repo.sh` / `INT-004` | Active blocker, stale first-failure diagnosis | The March 15 Sail decode failure is stale; rerun strict closure and capture the next real first failure. |
| Mixed tile + SIMT workloads | `Regression::PTO kernel parity` / `INT-020` | Stale blocker | March 15 is red, but the 2026-04-11 spot check is green for all 27 kernels, including `flash_attention_cube`, `gqa`, `sparse_attention_local`, and `rmsnorm`. |
| SIMT autovec | `Regression::TSVC QEMU gate` / `INT-025` | Active blocker | `tsvc.auto.elf` currently times out after 240 seconds under QEMU. This is the main LLVM/SIMT blocker in the current lane. |
| QEMU baseline | `Emulator::QEMU all suites` + `QEMU strict system` | Not blocked | Baseline runtime/system gates are green; the remaining QEMU issue for this lane is TSVC reproduction, not broad decode expansion. |
| Superproject breadth | `ISA::AVS tier closure` / `INT-016` | Active blocker | PR-tier closure is still only `20/54` active entries implemented/pass. This remains the top-level breadth blocker after subsystem fixes are rerun. |

## 1. Refresh Stale Red-Gate Truth

- [ ] Re-run the stale spot checks first:

  ```bash
  python3 tools/bringup/check_sail_model.py --require-parser
  python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120
  ```

- [ ] Treat the March 15, 2026 Sail decode and PTO parity red rows as **stale**
      unless they reproduce under current workspace state.
- [ ] If you need to publish a refreshed canonical report, run a new convergence
      pass instead of only editing markdown:

  ```bash
  LINX_GATE_TIER=pr \
  bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id>
  ```

- [ ] Re-render gate status markdown from the refreshed JSON report:

  ```bash
  python3 tools/bringup/gate_report.py render \
    --report docs/bringup/gates/latest.json \
    --out-md docs/bringup/GATE_STATUS.md
  ```

- [ ] Do not keep “Sail decode generator broken” or `INT-020` as active blockers
      in prose once the rerun evidence is refreshed.

Exit criteria:

- Sail/model status is green under the current workspace.
- PTO kernel parity is either reproduced as failing now, or explicitly treated
  as a stale March row pending canonical report refresh.

## 2. Restore Kernel Build Closure (`LINUX-005`)

- [ ] Apply the kernel hygiene rule before any new `vmlinux` build attempt:
  - either run `make ARCH=linx mrproper` in `kernel/linux` before the pinned
    out-of-tree build,
  - or build from a fresh clean source export;
  - do not mix source-tree generated state with `O=...` builds.
- [ ] Re-run the pinned `vmlinux` gate command:

  ```bash
  env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH \
    /opt/homebrew/bin/gmake -C kernel/linux \
    ARCH=linx \
    LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ \
    'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' \
    HOSTCC=/usr/bin/clang \
    HOSTCXX=/usr/bin/clang++ \
    O=$PWD/kernel/linux/build-linx-fixed \
    vmlinux -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc)"
  ```

- [ ] After `vmlinux` succeeds, rerun the Linux runtime smoke/full-boot gates:

  ```bash
  python3 kernel/linux/tools/linxisa/initramfs/smoke.py
  python3 kernel/linux/tools/linxisa/initramfs/full_boot.py
  ```

- [ ] Record the refreshed build and boot logs under the active run directory in
      `docs/bringup/gates/logs/<run-id>/pin/`.

Exit criteria:

- `LINUX-005` is green with fresh evidence.
- Smoke and full boot remain green after the build-closure fix.

## 3. Re-run Strict Closure To First Real Failure (`INT-004`)

- [ ] After Step 1 and Step 2 are complete, rerun strict closure.
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
- [ ] Replace the stale March Sail first-failure diagnosis with the new first
      failing gate or command window from the rerun.
- [ ] Do not preserve “Sail decode generator broken” as the active `INT-004`
      narrative unless it reproduces again under the current workspace.

Exit criteria:

- `INT-004` points at the current first real failure, not the stale March Sail
  failure.
- The rerun has a new run ID, updated log paths, and a refreshed multi-agent
  summary.

## 4. Close The TSVC / Autovec Blocker (`INT-025`)

- [ ] Reproduce the timeout with the pinned toolchain/QEMU command:

  ```bash
  python3 workloads/tsvc/run_tsvc.py \
    --clang compiler/llvm/build-linxisa-clang/bin/clang \
    --lld compiler/llvm/build-linxisa-clang/bin/ld.lld \
    --vector-mode auto \
    --strict-fail-under 148 \
    --source-policy linx-v03-parity \
    --no-run-qemu \
    --out-dir workloads/generated
  ```

- [ ] Keep the PR lane on compile-only strict coverage until the auto-runtime
      hangs are closed. Dedicated runtime triage should still classify the
      first hanging kernel against
      [`docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`](SIMT_COMPILER_SUPPORTED_SUBSET.md)
      as exactly one of:
  - within the documented supported subset;
  - intentional scalar fallback;
  - blocked on missing grouped EXEC-mask save/restore support.
- [ ] Keep the current architecture boundary explicit during triage:
  - grouped single-block if-converted and active-replay shapes are valid work;
  - raw grouped multi-block divergence is still intentionally unclosed because
    the canonical surface lacks a first-class `p` save/restore carrier.
- [ ] Only promote support inside the documented subset. If the timed-out shape
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

- [ ] Re-run the LLVM compile baseline if the TSVC investigation touched codegen:

  ```bash
  ROOT=$PWD
  cd "$ROOT/avs/compiler/linx-llvm/tests"
  CLANG="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang" TARGET=linx64-linx-none-elf OUT_DIR="$PWD/out-linx64" ./run.sh
  CLANG="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang" TARGET=linx32-linx-none-elf OUT_DIR="$PWD/out-linx32" ./run.sh
  python3 analyze_coverage.py --out-dir "$PWD/out-linx64" --fail-under 100
  python3 analyze_coverage.py --out-dir "$PWD/out-linx32" --fail-under 100
  ```

- [ ] Re-run QEMU baseline audits:

  ```bash
  ROOT=$PWD
  cd "$ROOT/avs/qemu"
  LINX_DISABLE_TIMER_IRQ=0 CLANG="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang" LLD="$ROOT/compiler/llvm/build-linxisa-clang/bin/ld.lld" QEMU="$ROOT/emulator/qemu/build/qemu-system-linx64" ./run_tests.sh --all --timeout 10
  LINX_DISABLE_TIMER_IRQ=0 CLANG="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang" LLD="$ROOT/compiler/llvm/build-linxisa-clang/bin/ld.lld" QEMU="$ROOT/emulator/qemu/build/qemu-system-linx64" ./check_system_strict.sh
  ```

- [ ] Re-run the current workload blockers:

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

- [ ] Re-run strict closure after the targeted fixes:
  - canonical report refresh: `tools/bringup/run_runtime_convergence.sh`
  - focused iteration: exact `strict_cross_repo.sh` command from the current
    gate report row
- [ ] Update integration checklist statuses only from fresh rerun evidence.

Exit criteria:

- stale blockers have been replaced by current evidence;
- `LINUX-005` is resolved or reclassified with fresh logs;
- `INT-025` has a current owner and first-failure diagnosis;
- `INT-016` and `INT-004` reflect current rerun evidence, not March carryover.

## Assumptions And Defaults

- This page is limited to the current superproject blocker slice for kernel,
  LLVM/SIMT autovec, mixed tile/SIMT workloads, QEMU baseline, and strict
  closure.
- The March 15, 2026 canonical report remains the checked-in baseline until a
  new canonical run replaces it.
- The 2026-04-11 Sail and PTO parity spot checks are authoritative for stale
  blocker cleanup even before the next canonical report refresh.
- Owner-specific red gates in glibc runtime, LinxCore, Testbench, Trace, and
  pyCircuit remain separate follow-on lanes after this blocker slice is
  refreshed.
