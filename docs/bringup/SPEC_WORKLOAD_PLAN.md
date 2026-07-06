# SPEC Workload Plan

This page is the canonical planning surface for SPEC CPU2017 on LinxISA.

Legacy script flags such as `--stage a`, `--stage b`, `phase-b`, and `phase-c`
remain implementation details of existing helpers. They are not the canonical
planning taxonomy anymore.

The canonical taxonomy is capability-based:

- **Control Path**: wrapper, QEMU path, artifact handoff, reproducible launch.
- **Userspace Entry**: trivial firmwareless Linux + initramfs userspace startup.
- **Fast Gate**: cheap SPECint `test`/`train` suites for QEMU/Linux regressions.
- **Bringup Subset**: first useful SPEC subset for runtime debugging.
- **Hosted Runtime**: shared musl / dynamic-loader path for hosted benches.
- **Subset Closure**: bringup subset passes qemu + specdiff on required transports.
- **Scale-Out**: promotion set closure and LinxCore xcheck.

## Policy Sets

- `spec_policy.bringup_subset`
  Current set: all supported Linx SPECint C/C++ rate rows on `train` input:
  `500.perlbench_r`, `502.gcc_r`, `505.mcf_r`, `520.omnetpp_r`,
  `523.xalancbmk_r`, `525.x264_r`, `531.deepsjeng_r`, `541.leela_r`,
  `557.xz_r`, and `999.specrand_ir`.
- `spec_policy.fast_gate`
  Current suites:
  - `test-smoke`: `999.specrand_ir` on `test`
  - `train-smoke`: `999.specrand_ir` on `train`
  - `test-all`: all supported Linx SPECint C/C++ rate rows on `test`
  - `train-all`: all supported Linx SPECint C/C++ rate rows on `train`
  - `test-cpu-stress`: `531.deepsjeng_r` on `test`, isolated in nightly
    because it can run for minutes before guest progress
  - `test-vm-stress`: `505.mcf_r` on `test`, isolated because it is the
    known large-allocation/MMU stressor
  - `train-cpu-stress`: `531.deepsjeng_r` on `train`, isolated in nightly
    because profiling showed it can run for minutes before guest progress
- `spec_policy.promotion_required`
  Current set: full required SPECint promotion set excluding policy exclusions
- `spec_policy.excluded_benchmarks`
  Current policy exclusion: `548.exchange2_r`

## Milestones

### SPEC-M01 Control Path Ready

Goal:
- The canonical Stage-A/bringup matrix command runs from the superproject with
  an explicit or inherited QEMU path and produces per-transport run staging.

Done means:
- `tools/spec2017/run_stage_qemu_matrix.py` forwards `QEMU=...` or `--qemu ...`
  plus per-run timeout, kernel append, and heartbeat controls to
  `run_int_rate_qemu.py`.
- Per-transport run directories are created under the chosen out dir.

Primary evidence:
- matrix summary JSON/MD
- transport logs

### SPEC-M01F Fast Test/Train Gate

Goal:
- A fast, repeatable SPECint gate runs `test` and `train` inputs before any
  refrate-scale or broad promotion work.

Done means:
- `tools/bringup/run_specint_fast_gate.py --profile pr` runs the fast suites
  through the active QEMU binary and emits `specint_fast_gate_summary.json`.
- The PR gate keeps `505.mcf_r` and `531.deepsjeng_r` out of the fast smoke
  path so cheap `test`/`train` regressions are visible first.
- The test profile supports `--suite test-all` so all ten supported SPECint
  rows can be run with bounded test input.
- The train profile supports `--suite train-all` so all ten supported SPECint
  rows can be run with bounded train input before promotion-scale runs.
- The `test-train` profile runs `test-all` and `train-all` together when the
  goal is a complete bounded all-row gate rather than PR smoke.
- The all-row profiles keep `525.x264_r` in the suite, but route it through a
  generated `*-large-9p` shard by default because its full input payload is too
  large for the initramfs transport.
- Nightly uses `--profile nightly` to add CPU stress, VM stress, and promotion
  breadth.

Primary evidence:
- `workloads/generated/specint-fast-gate/specint_fast_gate_summary.json`
- per-suite `qemu_matrix_summary.json`

### SPEC-M02 Firmwareless Linux Userspace Entry

Goal:
- A trivial static initramfs userspace payload starts visibly under the same
  firmwareless Linux/QEMU path that SPEC uses.

Done means:
- Static hello control lane emits guest-visible start/pass markers.
- Failure, if any, is no longer a zero-output timeout.

Primary evidence:
- corrected control-lane summary
- corrected `qemu_hello_static.log`

### SPEC-M03 Bringup Subset Output Generation

Goal:
- The benches in `spec_policy.bringup_subset` create their expected output
  files before specdiff runs.

Done means:
- `rand.24239.out`, `inp.out`, `mcf.out`, and `test.out` exist in the Linx run
  directories for the bringup subset.

Primary evidence:
- per-transport Stage-A summaries
- output files present in run dirs

### SPEC-M04 Hosted Runtime Restoration

Goal:
- The shared musl / dynamic-loader route is restored and reproducible.

Done means:
- `MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  is green again.
- Dynamic hello or equivalent hosted control lane reaches guest-visible output.
- Shared-runtime SPEC benches no longer fail at setup because of missing
  `libc.so` / loader artifacts.

Primary evidence:
- `phase-c` build summary
- hosted control-lane summary

### SPEC-M05 Bringup Subset Closure

Goal:
- The bringup subset passes qemu + specdiff on required fast-gate transports.

Done means:
- `spec_policy.fast_gate` is green on the promoted initramfs transport.
- optional transport expansion can add `9p,initramfs` via the fast gate
  `--transports` override without redefining the baseline.
- aggregate fast-gate summary reports `ok=true`.

Primary evidence:
- fast-gate summary JSON/MD
- per-suite matrix summary JSON/MD
- per-transport summaries
- specdiff logs

### SPEC-M06 Promotion Set Closure And XCheck

Goal:
- The promotion set runs successfully on the runtime lane and is ready for
  LinxCore trace/xcheck expansion.

Done means:
- `spec_policy.promotion_required` is green on the promoted transport policy.
- phase-b static image prep is reproducible for the promotion set.
- LinxCore xcheck suite generation and report lane are green enough for
  promotion.

Primary evidence:
- promotion-set matrix summary
- phase-b image manifest
- xcheck suite/report artifacts

### SPEC-P01 Policy Exclusion

Goal:
- Keep `548.exchange2_r` explicitly excluded until the project deliberately
  expands scope to Fortran/runtime support.

Done means:
- exclusion remains documented in the manifest and checklists.
- promotion-set helpers do not silently reintroduce it.

## Current Live Interpretation

As of 2026-07-06:

- `SPEC-M01` is resolved.
- `SPEC-M01F` is the canonical fast gate shape for current QEMU/Linux SPECint
  work: run minimal `test-smoke` and `train-smoke` for cheap regression
  signal, then use `--profile test --suite test-all`,
  `--profile train --suite train-all`, or `--profile test-train` for bounded
  all-row ledgers before any refrate-scale or broad promotion run.
- Latest same-head all-row speed baseline is
  `workloads/generated/specint-train-all-speedpreset-latest-b8faff-qemu-20260706-r1/`
  on QEMU `b8faff79be9a157fa5100f86957532652f79d679`, using the current
  explicit speed stack (`--template-chain`, `--qemu-frame-single-reg-fast`,
  `--qemu-mmu-cache`) plus QEMU BPC heartbeat. It passes the strict
  `999.specrand_ir` train sentinel and keeps every real SPECint train row
  heartbeat-live with site progress rather than deadlock. Counts in the
  bounded 45-second ledger remain far from completion: `500=10B`, `502=9B`,
  `505=9B`, `520=5B`, `523=8B`, `525=9B` on the generated 9p shard,
  `531=13B`, `541=6B`, and `557=12B`.
- The latest rejected broad QEMU speed candidate is
  `workloads/generated/specint-train-all-restorehost-pagefast-b8faff-qemu-20260706-r1/`,
  compared by
  `workloads/generated/specint-qemu-run-compare-pagefast-restorehost-vs-speedpreset-b8faff-20260706-r1/report.md`.
  It preserves the `999.specrand_ir` sentinel but regresses six real rows
  (`500`, `502`, `505`, `520`, `531`, `557`), leaves `523`, `525`, and `541`
  flat, and improves none. Do not put `--qemu-frame-restore-host-load` plus
  `--qemu-frame-page-fast` into broad train-all gates unless a new same-head
  control reverses this result.
- Latest feature-compatible all-row profile evidence is
  `workloads/generated/specint-profile-suite-train-speedpreset-current-clean-qemu-20260706-r1/`
  with joined analysis
  `workloads/generated/specint-progress-analysis-speedpreset-current-clean-20260706-r2/report.md`.
  It classifies eight initramfs rows as the same
  `template-tb-mmu-throughput` lane with aggregate component counts
  `soft-mmu=4871`, `tb-dispatch=4531`, and `frame-template=3890`; `525.x264_r`
  remains a separate `transport-9p-throughput` lane. The leading shared QEMU
  frames are `linx_template_fret_stk_impl`,
  `linx_template_fentry_impl`, `tb_lookup`, `helper_lookup_tb_ptr`,
  `mmu_lookup1`, and `probe_access_internal`.
- Focused `541.leela_r` TB-hot follow-up is
  `workloads/generated/specint-541-tb-hot-speedpreset-b8faff-qemu-20260706-r1/`.
  With the same explicit speed stack plus `--qemu-tb-stats`,
  `--qemu-tb-hot`, and `--symbolize-heartbeat`, the row remains a
  heartbeat-backed live-timeout at 10B bounded instructions in 75 seconds. TB
  counters show code-cache pressure is not the first target (`tbs_flush=0`,
  `tbs_code_used=37818696` of
  `1073725352`, `tbs_miss=39207` against `895315888` lookups). Post-start
  hot PCs are benchmark loops, not kernel boot loops:
  `0x1555595d54 -> 0x40040d54 = .LBB154_22 Matcher.cpp:0` and
  `0x1555596180 -> 0x40041180 = .LBB173_3 Matcher.cpp:0`. Route 541-style TB
  evidence to dispatch/lookup overhead, template helper exits, and soft-MMU
  probe/load cost; do not spend the next loop enlarging the TB cache.
- Focused `531.deepsjeng_r` follow-up is
  `workloads/generated/specint-531-test-filesys-trace-20260701-r1/`: cwd,
  executable preflight, and `execve()` are correct, but the child writes the
  short `Allocated Workload not found` output without issuing a traced file
  syscall for `test.txt`. Static C musl `file_stdio` and `printf_string_arg`
  controls pass while static `cpp17_smoke` traps in
  `workloads/generated/musl-control-stdio-cpp-20260701-r1/`, so this row is
  currently a C++ runtime/codegen correctness blocker rather than a SPEC input
  packaging blocker.
- Focused `500.perlbench_r` addr-zero follow-up is
  `workloads/generated/specint-500-mmio-hole-fix-normal-store-20260701-r1/`:
  the earlier final `FRET.STK [ra ~ s5], sp!, 80` null-RA cause is closed. The
  root cause was the Linx `virt` DT memory node exposing the virtio-mmio page as
  allocatable RAM under large `-m` runs; QEMU now excludes UART/exit,
  test-finisher, and virtio-mmio pages from `/memory@0/reg`. The formerly bad
  FENTRY save at `ra@0x3fdd764798` now reads back `0x15558292f0` through MMU,
  host pointer, and debug readback while the frame store still uses the normal
  QEMU store helper. The same focused run remains red with a later addr-zero
  user trap at `tpc=0x1555622dba`, so the next owner is that later user fault,
  not stack-growth faulting, syscall return, or SPEC input packaging.
- Focused historical `541.leela_r` correctness follow-up is
  `workloads/generated/specint-541-atomicfix-20260702-r1/`: the earlier 4 GiB
  / `--stack-limit 2G` trap mapped to recursive compiler-rt
  `__atomic_load_1` lowering. After rebuilding musl phase-b builtins, the
  spec-profile C++ runtime overlay, and the `541` executable, the row no longer
  traps or OOMs; on the current QEMU speed stack it is a throughput row rather
  than a first-fault correctness row. Keep mallocng as the default phase-b
  allocator and use oldmalloc only as the focused bisection lane if fresh
  allocator-metadata traps recur.
- `SPEC-M02` is resolved for the SPEC initramfs userspace path: the wrapper
  reaches SPEC startup, and current `999.specrand_ir` train-smoke/all-row
  evidence passes strict hash on this QEMU/kernel stack. Keep `999` as the
  cheap correctness sentinel before and after QEMU speed experiments.
- `SPEC-M03` and `SPEC-M05` are active, not blocked by entry: current
  initramfs evidence reaches SPEC startup for every non-panic row. The current
  blockers are focused user traps, wrapper/benchmark child exits, confirmed
  2 GiB guest OOM rows, live-progress timeouts, and the persistent
  `525.x264_r` initramfs VFS-root panic. The current all-ten ledger is
  `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/`,
  with focused follow-up artifacts under `workloads/generated/specint-*-20260702-r1/`.
- `SPEC-M04` remains separately open for the shared-runtime path.
- `SPEC-M06` is not actionable until `SPEC-M05` train correctness and
  throughput lanes are green on the promoted static transport policy.
