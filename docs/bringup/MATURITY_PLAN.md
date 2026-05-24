# LinxISA Maturity Plan (Tier-1 Track vs ARM/x86)

Last updated: 2026-05-17

## Baseline

- Latest canonical run: `2026-04-18-r9-pin-linuxlibc-refresh`
- Latest canonical report generation: `2026-04-18 02:11:34Z`
- Canonical report: `docs/bringup/gates/latest.json`
- Latest diagnostic strict rerun: `2026-04-17-r7-pin-recovery` (non-canonical; BusyBox rootfs skipped to expose downstream blockers in `docs/bringup/gates/logs/2026-04-17-r7-pin-recovery/pin/reg_strict_cross_repo.log`)
- The checked-in canonical report now includes the April 18 pin-lane recovery evidence. It clears the stale March false blockers for AVS PR-tier closure, model-diff, LinxCore/Testbench/Trace/pyCircuit leaf PR gates, glibc runtime, musl runtime, PTO parity, and TSVC compile-only PR coverage.
- Active governance phase remains `LINUX-RUNTIME`; `docs/bringup/agent_runs/waivers.yaml` contains no waivers.
- Latest non-canonical Linux smoke diagnostic: 2026-05-17 local bring-up iterations move well past DT, percpu, log-buffer, proc/ns/pidfs pseudo-fs setup, and the pre-`rest_init()` late-init lane. The live boundary is now the first task-creation handoff after `rest_init()`, specifically `user_mode_thread()` / `kernel_clone()` / `copy_process()` on the Linx tiny-RCU configuration.

## Gap Snapshot

- AVS PR-tier closure is now complete (`31/31` required tests pass), while nightly breadth remains `32/54`.
- The current recovery work is now narrowed to Linux/userspace runtime closure:
  - Linux BusyBox rootfs still fails after `/sbin/init` even with a clean pinned QEMU build and clean rootfs build helper,
  - `strict_cross_repo.sh` remains red only because the required BusyBox rootfs row is red in the latest canonical run,
  - canonical runtime evidence is otherwise refreshed through `2026-04-18-r9-pin-linuxlibc-refresh`,
  - TSVC runtime is no longer part of the active bring-up gate path; current focus remains Linux boot closure first.
- Separate non-canonical kernel smoke bring-up work is no longer blocked in DT parsing or pseudo-filesystem bootstrap:
  - read-only DT import, memory discovery, percpu setup, and late pseudo-fs smoke bypasses now complete,
  - the current local smoke trace reaches `...abcdefghijklZ` and then stalls before userspace launch,
  - rebuilt-image disassembly shows the active next lane is task creation from `rest_init()` into `user_mode_thread()` / `kernel_clone()`, not the earlier RCU tiny-helper callsite and not DT/procfs/nsfs/pidfs bring-up.
- Hosted workload hardening is now split cleanly by tier:
  - PR lane: benchmark/polybench/portfolio/ctuning artifact publication and PTO parity are green.
  - runtime-heavy follow-up: the active in-repo SPEC lane is CPU2017 Stage A, not a checked-in SPEC CPU2006 corpus. A new 2026-05-17 non-canonical rerun shows static-only `999.specrand_ir` now reaches the same late kernel task-creation stall as initramfs smoke, while dynamic `531.deepsjeng_r` remains blocked earlier because `phase-c` shared musl packaging is still missing `libc.so` (`m3_notext_probe_signature=ld.lld: error: relocation R_LinxV5_64_BNEXT cannot be used against symbol 'malloc'; recompile with -fPIC`). TSVC QEMU runtime still fails in the latest diagnostic rerun.
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
   - keep the local initramfs smoke diagnostic distinct from canonical BusyBox closure: the present smoke-only blocker is the first task-creation handoff after `rest_init()`, with the tiny-RCU state flip already inlined on Linx and the next live investigation target narrowed to `kernel_clone()` / `copy_process()`.
3. Re-run the runtime-heavy workload lanes that still block nightly closure:
   - re-run the CPU2017 Stage A QEMU matrix once the shared-musl hosted lane is restored for dynamic benches and the kernel task-creation stall is cleared for static benches,
   - reclassify the next Linux/userspace runtime fault after each fix.
4. Resume nightly AVS breadth work on decode/block edge cases, atomics, FP, vector runtime, and Linux workload launch semantics.

## Canonical Milestones

The old numbered `M1..M6` plan is retired as the canonical planning taxonomy.
Use these two documents instead:

- repo-wide plan: `docs/bringup/SUPERPROJECT_MILESTONES.md`
- SPEC-specific workload plan: `docs/bringup/SPEC_WORKLOAD_PLAN.md`

Current milestone interpretation:

- `CORE-M01` through `CORE-M04`: mostly far enough along that they are no
  longer the first active blockers
- `LINUX-M01`: current first unresolved superproject runtime milestone
- `LINUX-M02`: blocked by `LINUX-M01`
- `LIBC-M01`: repaired locally on `phase-b`, but still requires tracked
  artifact refresh as evidence
- `LIBC-M02`: still open for the shared hosted-runtime path
- `SPEC-M01`: resolved
- `SPEC-M02`: current first unresolved SPEC milestone
- `SPEC-M03` / `SPEC-M05`: blocked downstream of `SPEC-M02`
- `SPEC-M04`: separately open for hosted shared-runtime restoration
- `TSVC-M02`: tracked as optional follow-up only after Linux boot closure; it is not part of the active gate path
- `AVS-M02`, `PRIV-M01`, and `REL-M02`: downstream promotion work

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
