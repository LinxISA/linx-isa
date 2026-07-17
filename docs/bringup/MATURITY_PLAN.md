# LinxISA Maturity Plan (Tier-1 Track vs ARM/x86)

Last updated: 2026-07-15

## Baseline

- Latest maintenance run: `2026-07-17-v057-release`
- Latest maintenance evidence: TSVC batched auto passes 151/151; BusyBox rootfs
  fails with no UART output in two 120-second attempts.
- Canonical report: `docs/bringup/gates/latest.json`
- Latest diagnostic strict rerun: `2026-04-17-r7-pin-recovery` (non-canonical; BusyBox rootfs skipped to expose downstream blockers in `docs/bringup/gates/logs/2026-04-17-r7-pin-recovery/pin/reg_strict_cross_repo.log`)
- The v0.57 packet is deliberately non-green: it clears the TSVC hard break
  but records the separate Linux/MMU failure and all unrun nightly gates.
- Active governance phase remains `LINUX-RUNTIME`; `docs/bringup/agent_runs/waivers.yaml` contains no waivers.
- Latest non-canonical Linux smoke diagnostic: 2026-05-17 local bring-up iterations move well past DT, percpu, log-buffer, proc/ns/pidfs pseudo-fs setup, and the pre-`rest_init()` late-init lane. The live boundary is now the first task-creation handoff after `rest_init()`, specifically `user_mode_thread()` / `kernel_clone()` / `copy_process()` on the Linx tiny-RCU configuration.
- June 14, 2026 flow reset: benchmark work now uses
  `docs/bringup/BENCHMARK_QEMU_LINUX_FLOW.md` and
  `tools/bringup/run_benchmark_linux_flow.py` as the hard-break execution
  order. The PR benchmark lane stops at TSVC/QEMU before Linux rootfs or SPEC.
- July 3, 2026 latest-QEMU Linux rerun: QEMU
  `v10.2.0-1004-ga3061b963f3` from
  `/tmp/linx-qemu-current-build-20260703-r1/qemu-system-linx64` passes both
  initramfs full boot and BusyBox virtio-blk rootfs boot. The BusyBox report
  `workloads/generated/linux-busybox-latest-qemu-20260703-r1/report.json`
  records `ok=true`, shell command execution, `linx-timer` IRQ progress
  `40 -> 45`, and poweroff through `LINX_REBOOT lisc_shutdown`. The stale
  rootfs `addr=0x10000004` PID1 trap remains closed.

## Gap Snapshot

- AVS PR-tier closure is now complete (`31/31` required tests pass), while nightly breadth remains `32/54`.
- The current recovery work is split into two ordered hard-break lanes:
  - PR benchmark lane: source contract, compiler contract, QEMU contract, then
    TSVC compile/QEMU runtime.
  - Linux/full-OS lane: `vmlinux`, trivial userspace entry, BusyBox rootfs,
    libc hosted runtime, then SPEC/full benchmarks.
- The Linux/userspace runtime closure has fresh local latest-QEMU evidence:
  - initramfs full boot reaches the shell, probes `/proc` and `/sys`, passes
    `getdents64`, `sigill`, and `sigsegv`, then powers off,
  - BusyBox rootfs now reaches `/sbin/init`, executes shell commands, observes
    timer IRQ progress, and powers off under `qemu-system-linx64`,
  - `strict_cross_repo.sh` is still red in the latest checked-in canonical run
    because that report predates the July 3 latest-QEMU Linux/rootfs proof,
  - canonical runtime evidence is otherwise refreshed through
    `2026-04-18-r9-pin-linuxlibc-refresh`,
  - the next required closure step is a refreshed convergence/strict report and
    then libc hosted runtime plus SPEC correctness, not another stale-rootfs
    BusyBox investigation.
- Separate non-canonical kernel smoke bring-up work is no longer blocked in DT parsing or pseudo-filesystem bootstrap:
  - read-only DT import, memory discovery, percpu setup, and late pseudo-fs smoke bypasses now complete,
  - the current local smoke trace reaches `...abcdefghijklZ` and then stalls before userspace launch,
  - rebuilt-image disassembly shows the active next lane is task creation from `rest_init()` into `user_mode_thread()` / `kernel_clone()`, not the earlier RCU tiny-helper callsite and not DT/procfs/nsfs/pidfs bring-up.
- Hosted workload hardening is now split cleanly by tier:
  - PR lane: benchmark/polybench/portfolio/ctuning artifact publication and PTO parity are green.
  - runtime-heavy follow-up: the active in-repo SPEC lane is CPU2017 SPECint
    train input, not a checked-in SPEC CPU2006 corpus. The latest clean all-ten
    train loop under
    `workloads/generated/specint-train-all-frame-single-fast-clean-qemu-20260705-r1/` runs all
    supported SPECint C/C++ rows on clean QEMU head
    `7ae245b6a5e937fdfd1f377662efa00997f68025`, passes `999.specrand_ir`,
    routes `525.x264_r` through the generated 9p shard, and proves timeout rows
    are live-progress rather than global QEMU deadlock by QEMU heartbeat/BPC,
    frame counters including one-register frame-fast usage, TB counters, TLB
    aggregate counters, TLB-fill hot pages, and TLBI hot-source evidence. The
    frame-fast switch remains opt-in because normalized train-all throughput is
    mixed; the next speed lanes are remaining
    fixmap/fault-path TLBI bursts, QEMU `probe_access_internal` / soft-MMU
    lookup, template/TB lookup dispatch, frame restore fallback traffic, and
    9p/kernel transport overhead.
- Remaining superproject work: refreshed strict/convergence publication, libc
  hosted runtime, SPEC correctness/performance, TSVC runtime, AVS nightly
  breadth, QEMU decode coverage, ABI/unwind/TLS hardening,
  privileged/MMU/debug scope, and SIMT/compiler maturity.

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
2. Publish the refreshed kernel/userspace runtime proof:
   - BusyBox rootfs runtime now passes locally with a clean rebuilt rootfs and
     firmwareless QEMU boot,
   - refresh the canonical convergence report after BusyBox rootfs passes so
     `Regression::strict_cross_repo.sh` can turn green without a waiver.
   - keep the local initramfs smoke diagnostic distinct from canonical BusyBox closure: the present smoke-only blocker is the first task-creation handoff after `rest_init()`, with the tiny-RCU state flip already inlined on Linx and the next live investigation target narrowed to `kernel_clone()` / `copy_process()`.
3. Re-run the runtime-heavy workload lanes that still block nightly closure:
   - keep the CPU2017 SPECint `train-all` QEMU matrix as the active static
     workload loop; the current all-ten ledger is
     `workloads/generated/specint-train-all-clean-qemu-20260705-r1/`,
   - keep the new Linx Linux `mprotect()` no-merge smoke in the regression
     loop so the former `502.gcc_r` no-VMA trap stays closed,
   - move `525.x264_r` train execution to 9p or a future block-backed transport
     instead of relying on a giant initramfs CPIO,
   - use the current clean-QEMU heartbeat/TB/TLB-fill ledger to guide speed
     work: remaining fixmap/fault-path TLBI sources, QEMU probe/soft-MMU
     lookup, template/TB lookup dispatch, frame restore fallback traffic, and
     9p transport, with strict `999.specrand_ir` as the cheap correctness
     sentinel.
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
  `docs/architecture/v0.57-simt-compiler-contract-plan.md`
- Compiler maturation plan:
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

These pages refine the `VEC`/SIMT lane of the broader maturity effort. They do
not replace the main maturity plan; they provide the missing depth for the
current LLVM/QEMU/AVS SIMT subset.

## Required Policy Defaults

- No new waivers by default for required strict gates.
- Dual-lane promotion remains required (`pin` + `external`).
- Existing strict green gates remain mandatory while maturity gates are added incrementally.
