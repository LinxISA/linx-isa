# LinxISA Maturity Plan (Tier-1 Track vs ARM/x86)

Last updated: 2026-05-15

## Baseline

- Latest canonical run: `2026-04-18-r9-pin-linuxlibc-refresh`
- Latest canonical report generation: `2026-04-18 02:11:34Z`
- Canonical report: `docs/bringup/gates/latest.json`
- Latest diagnostic strict rerun: `2026-04-17-r7-pin-recovery` (non-canonical; BusyBox rootfs skipped to expose downstream blockers in `docs/bringup/gates/logs/2026-04-17-r7-pin-recovery/pin/reg_strict_cross_repo.log`)
- The checked-in canonical report now includes the April 18 pin-lane recovery evidence. It clears the stale March false blockers for AVS PR-tier closure, model-diff, LinxCore/Testbench/Trace/pyCircuit leaf PR gates, glibc runtime, musl runtime, PTO parity, and TSVC compile-only PR coverage.
- Active governance phase remains `G0`; `docs/bringup/agent_runs/waivers.yaml` contains no waivers.

## Gap Snapshot

- AVS PR-tier closure is now complete (`31/31` required tests pass), while nightly breadth remains `32/54`.
- The current recovery work is now narrowed to Linux/userspace runtime closure:
  - Linux BusyBox rootfs still fails after `/sbin/init` even with a clean pinned QEMU build and clean rootfs build helper,
  - `strict_cross_repo.sh` remains red only because the required BusyBox rootfs row is red in the latest canonical run,
  - canonical runtime evidence is otherwise refreshed through `2026-04-18-r9-pin-linuxlibc-refresh`,
  - the latest diagnostic rerun with BusyBox skipped reaches TSVC and then times out after 240 seconds on `tsvc.auto.elf`, so TSVC QEMU runtime is the next blocker after BusyBox rather than an already-cleared lane.
- Hosted workload hardening is now split cleanly by tier:
  - PR lane: benchmark/polybench/portfolio/ctuning artifact publication, PTO parity, and TSVC compile-only strict coverage are green.
  - runtime-heavy follow-up: SPEC Stage A remains opt-in/not-run in the canonical report, and TSVC QEMU runtime still fails in the latest diagnostic rerun.
- Remaining superproject work: BusyBox rootfs Linux runtime, SPEC Stage A over 9p/initramfs, TSVC runtime, AVS nightly breadth, QEMU decode coverage, ABI/unwind/TLS hardening, privileged/MMU/debug scope, and SIMT/compiler maturity.

## Closure Lanes

### Scalar

Status: Active first-closure lane

- Priority:
  - generic C without explicit SIMT autovec or tile intrinsic source
  - scalar ABI/runtime/toolchain closure
  - direct returning call headers written as fused `BSTART ... , ra=...`
- Required cross-stack evidence:
  - compiler AVS compile suite + 100% active mnemonic coverage
  - scalar runtime startup asm on fused direct call headers
  - QEMU scalar call/ret contract runtime gate
- Explicit non-goals for this lane:
  - proving fused handwritten `ICALL ra=` source syntax before the current
    parser/MC gap is closed
  - proving grouped SIMT or tile lowering maturity

### SIMT

Status: Partial / staged after scalar

- Priority:
  - keep the documented SIMT subset explicit and verified
  - expand grouped-lane/runtime closure only inside the frozen subset boundary
- Canonical plans:
  - `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
  - `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

### Tile

Status: Partial / staged after scalar

- Priority:
  - keep tile/TEPL encoding and asm/manual sync green
  - expand decode/runtime semantics without conflating that work with scalar
    closure

## Immediate Recovery Lane (March-April 2026)

Status: Active

1. Keep the April 18, 2026 checked-in canonical report as the current PR-lane baseline.
2. Close the remaining kernel/userspace runtime blocker:
   - fix the BusyBox rootfs runtime regression (current signal: kernel `E_BLOCK` after `/sbin/init`; the same failure reproduces against a clean pinned QEMU build and currently lands in `__submit_bio` on `FRET.STK` with `ra=0`, while a clean-worktree `switch_to` EBARG rollback only stabilizes verbose boot),
   - refresh the canonical convergence report after BusyBox rootfs passes so `Regression::strict_cross_repo.sh` can turn green without a waiver.
3. Re-run the runtime-heavy workload lanes that still block nightly closure:
   - re-run SPEC Stage A QEMU matrix,
   - re-run the TSVC strict QEMU gate (the latest diagnostic rerun reaches this lane only when BusyBox is skipped and then times out after 240 seconds on `tsvc.auto.elf`),
   - reclassify the next Linux/userspace runtime fault after each fix.
4. Resume nightly AVS breadth work on decode/block edge cases, atomics, FP, vector runtime, and Linux workload launch semantics.

## Milestones

### M1 (1-2 weeks): Recovery of broken strict-gate prerequisites

Status: In progress

- Completed in this refresh:
  - checklist/manifest ownership now includes AVS normalize/audit plus the workload regression rows recorded in the March 15 canonical report.
  - the execution-order runbook now lives in `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`.
  - the April 18 canonical report captures PR-tier AVS closure, model-diff recovery, PTO parity, TSVC compile-only coverage, glibc/musl runtime recovery, and LinxCore/Testbench/Trace/pyCircuit leaf recovery.
- Remaining for M1:
  - `LINUX-004`,
  - `INT-004` through the BusyBox-dependent strict closure row,
  - nightly/runtime follow-up for SPEC Stage A, TSVC runtime, and AVS nightly breadth.

### M2 (3-6 weeks): AVS core coverage expansion

Status: Partially complete for PR tier; nightly breadth still open

- Keep the April 18, 2026 PR subset fixed at the evidenced `31` required IDs.
- Implement the remaining nightly AVS IDs next: `DEC/BLK edge cases`, `BR exact scaling`, `MEM endianness/misalignment`, `ATOM`, `FP`, `VEC`, runtime histogram semantics, and SPEC/workload launch semantics.
- Add a dedicated SIMT kernel compile matrix for grouped-lane launch, inner
  control flow, and `.local` scratch usage once the contract pages above are
  frozen.
- Promote AVS matrix status validation as strict maturity artifact:
  - checker: `tools/bringup/check_avs_matrix_status.py`
  - artifact: `docs/bringup/gates/avs_matrix_status_audit.json`

### M3 (4-8 weeks): Emulator/model completeness gates

Status: Started (coverage reporting landed; PR-lane compatibility wrapper restored)

- Keep canonical ISA-vs-QEMU coverage report machine-generated:
  - `tools/bringup/report_qemu_isa_coverage.py`
- Expand `run_model_diff_suite.py` required coverage from scalar/basic to vector/tile + restart/fault scenarios.
- Add SIMT body execution/runtime coverage for:
  - grouped launch mapping,
  - branch-heavy kernels,
  - partial-lane progress,
  - compiler-generated `.local` state.
- Keep unsupported instructions deterministic via explicit illegal traps until implemented.

### M4 (4-10 weeks): Hosted toolchain/runtime workload maturity

Status: Planned (PR compile/artifact lanes green; runtime execution lanes still open)

- Close `SPEC-001..SPEC-007` in `docs/bringup/agent_runs/checklists/specint_qemu.md`.
- Keep the canonical workload report current; PTO parity is reflected as green in `2026-04-18-r9-pin-linuxlibc-refresh`.
- Keep 9p/virtfs compatibility (`LINUX-003`) as hard prerequisite for SPEC lane.
- Evolve C++ runtime policy beyond current no-EH/no-RTTI baseline once dual-lane evidence is stable.
- Convert ABI/unwind/TLS checklist into executable runtime gates.

### M5 (6-12 weeks): Privileged/MMU/debug parity

Status: Planned

- Close privileged/MMU/debug gaps in `docs/bringup/ISA_GAP_ANALYSIS.md`.
- Add Linux selftests for restartable tile faults and bridged memory ordering.
- Define minimal debug architecture contract (single-step, breakpoints/watchpoints, privilege interactions).

### M6 (ongoing): Performance and release-grade parity

Status: Planned

- Keep benchmark methodology and artifact discipline under `workloads/generated/`.
- Track static/dynamic instruction trends and optimization roadmap closure.
- Expand CI-like orchestration for full-stack, cross-repo reproducibility.

## SIMT-Specific Planning Pages

- Architecture detail plan:
  `docs/architecture/v0.56-simt-compiler-contract-plan.md`
- Compiler maturation plan:
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

These pages refine the `VEC`/SIMT lane of the broader maturity effort. They do
not replace the main maturity plan; they provide the missing depth for the
current LLVM/QEMU/AVS SIMT subset.

## Required Policy Defaults

- No new waivers by default for required strict gates.
- Dual-lane promotion remains required (`pin` + `external`).
- Existing strict green gates remain mandatory while maturity gates are added incrementally.
