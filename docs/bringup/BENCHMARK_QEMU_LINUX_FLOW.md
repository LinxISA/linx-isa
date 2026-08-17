# Benchmark QEMU/Linux Hard-Break Flow

This is the canonical execution order for moving from the current LinxISA
superproject state to full benchmark execution on QEMU with Linux. The
machine-readable source is `docs/bringup/benchmark_qemu_linux_flow.json`; the
runner is `tools/bringup/run_benchmark_linux_flow.py`.

## Current Analysis

Evidence:

- `docs/bringup/gates/qemu_isa_coverage_latest.md` is regenerated from the
  exact v0.58.1 QEMU leaf and records complete L1 decoder/source mapping at
  `731/731` mnemonics and `765/765` legal forms. The current-pin LLVM breadth
  report separately measures `147/731` unique mnemonics across 44 replay-verified
  C/C++ objects; it does not claim form acceptance or runtime semantics. L2
  runtime execution, L3 semantic oracles, and a current aggregate AVS translation
  report remain separate evidence levels; archived v0.57 reports do not close
  them.
- The v0.57 TSVC hard break is closed on clean QEMU
  `b270924c2240d7a1dc9bad4672345cc098510341`: 8/8 deterministic batches,
  `150/151` strict-vectorized kernels, and `151/151` QEMU completions. `s451`
  remains the intentional scalar transcendental-call case. The unbatched
  all-mode diagnostic is not the PR hard-break contract and may exceed its
  per-process timeout.
- The separately ordered BusyBox lane remains red on the same clean QEMU: two
  120-second attempts produced no UART output. This is tracked as the distinct
  Linux/MMU regression and does not invalidate the completed TSVC hard break.
- `workloads/generated/linux-busybox-latest-qemu-20260703-r1/report.json`
  records the current latest-QEMU Linux rootfs proof: QEMU
  `v10.2.0-1004-ga3061b963f3` boots the current `vmlinux` and virtio-blk
  BusyBox rootfs firmwareless, reaches `/sbin/init`, runs shell commands,
  observes `linx-timer` IRQ progress `40 -> 45`, and powers off through
  `LINX_REBOOT lisc_shutdown`. The initramfs full-boot command also passes on
  the same QEMU binary, including `/proc`/`/sys` probes, `getdents64`, and
  `sigill`/`sigsegv` tests. The older
  `workloads/generated/busybox-rootfs-boot-20260630-r1/` `addr=0x10000004`
  PID1 trap used a stale rootfs image whose BusyBox binary still performed
  direct UART MMIO from user mode.
- `docs/bringup/agent_runs/checklists/specint_qemu.md` records SPECint as a
  fast `test`/`train` gate first, with `505.mcf_r` isolated as VM stress rather
  than mixed into every cheap regression check.
- Both canonical SPEC lanes now hard-break between static build and runtime on
  `tools/spec2017/check_build_manifest.py attest` followed immediately by
  `verify`. The attestation binds the current superproject/LLVM/musl state,
  tool binaries, sysroot, immutable source tree, and the exact 10-benchmark / 12
  static-Linx-ELF set. It deliberately makes no claim about licensed SPEC input
  content, authorization, or test/train execution; those remain runtime-gate
  responsibilities.
- The nightly `full-benchmarks` stage requires an explicit
  `LINX_BENCHMARK_RUN_COMMAND` and passes it to the CoreMark/Dhrystone runner.
  A build-only result cannot satisfy this stage; each workload must return
  `RUN_PASS` with its workload-specific semantic markers. The launcher command
  remains explicit because the authoritative Linux image is still governed by
  the source-completeness gate rather than an unchecked local kernel.
- `docs/bringup/QEMU_SPECINT_PERFORMANCE_PLAN.md` records the current QEMU
  SPECint profile and the prioritized speedups for the Linx target.
- `workloads/generated/specint-train-all-current-clean-qemu-20260706-r2/` is
  the latest submitted-QEMU all-SPECint train ledger. It uses the rebuilt
  in-tree `emulator/qemu/build-linx/qemu-system-linx64` at QEMU head
  `4462415a388cad7c91909f628dd4f42290569428`, version
  `v10.2.0-1034-g4462415a388`, with `qemu_repo_dirty_tracked=false`. The
  runner records `clean_build_for_head=false` only because `build-linx` has no
  clean-build marker. The split train suite enables BPC heartbeat, extended
  MMU/TLB/frame/TB counters, `--qemu-mmu-cache`, `--qemu-frame-single-reg-fast`,
  and explicit `--template-chain`. `999.specrand_ir` is not in the failed list;
  every real tracked C/C++ row, including generated 9p `525.x264_r`, remains a
  heartbeat-backed `live-timeout` with site-changing BPC progress, no
  no-progress timeout, no panic, and no fresh user-trap classification. The
  next speed loop remains template/TB/soft-MMU dispatch first, `505.mcf_r`
  demand-walk pressure, Linux TLBI attribution for `531`/`557`, and a separate
  9p/kernel transport lane for `525`.
- `workloads/generated/specint-505-tlbf-hot-reuse-qemu-20260706-r1/` is the
  current focused `505.mcf_r` TLB-fill reuse packet on rebuilt dirty QEMU
  `v10.2.0-1034-g4462415a388-dirty`. It extends `LINX_TLB_FILL_HOT` evidence
  with `inserts`, `last_hits`, and `slot_hits`. The row remains
  heartbeat-live at `count=27000000003`, `bpc=0x157b815526`, with
  `tlbf_total=89914727` and `tlbf_user_load=81317911`. The hot sketch reports
  `inserts=89914720`, `evictions=89914704`, `last_hits=5`, `slot_hits=2`, and
  `top0_count=2`, proving the 16-slot sketch sees streaming page-walk churn
  rather than short-window hot-page reuse. Keep the next `505` loop on
  streaming page-walk/soft-MMU lookup cost instead of larger small-hot-page
  sketches.
- `workloads/generated/specint-train-all-shape-record-inline-clean-qemu-20260705-r1/`
  is the current clean latest-QEMU all-SPECint train ledger. It uses
  `/tmp/linx-qemu-clean-build/qemu-system-linx64` at QEMU head
  `418f56ba1f58c908dc75c095e07606b725dafba4`, version
  `v10.2.0-1025-g418f56ba1f5`, and records `clean_build_for_head=true`.
  The split train suite enables BPC heartbeat, `LINX_QEMU_TEMPLATE_CHAIN=1`,
  `--qemu-frame-single-reg-fast`, frame stats, TB stats, TLB aggregate stats,
  TLB-fill hot pages, and TLB-invalidation hot-source attribution.
  `999.specrand_ir` passes strict train hash; every other tracked C/C++ row,
  including generated 9p `525.x264_r`, is a heartbeat-backed `live-timeout`
  with site-changing BPC progress, no panic, no trap, and no no-progress
  timeout. Compared with the previous clean `7ae245b6...` all-row ledger, the
  bounded 120-second counts are neutral to mixed: `502`, `505`, `523`, and
  `525` improve by about 1B instructions, `500` and `557` regress by about 1B,
  and `520`, `531`, and `541` are effectively flat. The one-register frame
  fast path remains opt-in because normalized train-all throughput is mixed.
- `workloads/generated/specint-profile-suite-train-shape-record-inline-clean-qemu-20260705-r1/`
  is the matching latest-head all-row train profile suite. It profiles the nine
  non-sentinel SPECint workload rows with delayed post-marker host samples,
  records `ok=true`, keeps `525.x264_r` on 9p, and records QEMU head
  `418f56ba1f58c908dc75c095e07606b725dafba4` with
  `clean_build_for_head=true`. The analyzer report
  `workloads/generated/specint-qemu-progress-analysis-shape-record-inline-clean-20260705-r1/report.md`
  classifies the next work as six template/TB/soft-MMU rows, two TLBI
  attribution rows (`531`, `557`), one 9p transport row (`525`), and the
  passing `999.specrand_ir` correctness sentinel. The latest aggregate active
  QEMU frames remain `linx_template_fret_stk_impl`, `tb_lookup`,
  `linx_template_fentry_impl`, `helper_lookup_tb_ptr`, `mmu_lookup1`, and
  `probe_access_internal`; `helper_linx_tlb_iv` is concentrated in the
  `531`/`557` TLBI lane.
- QEMU head `418f56ba1f58c908dc75c095e07606b725dafba4` is the latest focused
  QEMU hygiene repin. It removes disabled frame-shape recorder calls from
  ordinary SPEC profiles and passes clean SPECint PR smoke in
  `workloads/generated/specint-pr-shape-record-inline-clean-qemu-20260705-r1/`.
  The latest all-row train ledger above shows the patch is profile-fidelity and
  hot-path hygiene, not a broad speedup, so the next throughput work is still
  TB dispatch, soft-MMU lookup, and row-specific TLBI attribution.
- `workloads/generated/specint-train-all-frame-single-fast-clean-qemu-20260705-r1/`
  is the previous clean all-SPECint train comparison baseline at QEMU head
  `7ae245b6a5e937fdfd1f377662efa00997f68025`, version
  `v10.2.0-1024-g7ae245b6a5e`.
- `workloads/generated/specint-train-all-clean-qemu-20260705-r1/` is the
  prior clean latest-QEMU all-SPECint train ledger. It uses
  `/tmp/linx-qemu-clean-build/qemu-system-linx64` at QEMU head
  `40f869298c75aa9378746d5bf93ad3ec64475f85`, version
  `v10.2.0-1022-g40f869298c7`, and records `clean_build_for_head=true`.
  The split train suite enables BPC heartbeat, frame stats, TB stats,
  TLB aggregate stats, TLB-fill hot pages, and TLB-invalidation hot-source
  attribution. `999.specrand_ir` passes strict train hash (`rand.11.out`,
  871 bytes, `0x973dcfc2`); every other tracked C/C++ row, including generated
  9p `525.x264_r`, is a heartbeat-backed `live-timeout` with site-changing BPC
  progress, no panic, no trap, and no no-progress timeout. The shared maximum
  TLBI burst remains `458884` at `get_p4d_virt_fixmap`, while steady rows point
  at Linux `memory.c` fault/update paths, QEMU soft-MMU/probe cost, TB lookup
  overhead, frame restore fallback traffic, and 9p/kernel transport cost.
- `workloads/generated/specint-pr-provenance-clean-qemu-20260703-r1/` is the
  current clean-build provenance smoke for the SPECint PR gate. The default
  QEMU selector resolves `/tmp/linx-qemu-clean-build/qemu-system-linx64`,
  reports `v10.2.0-1006-gf690aa1f7da`, records QEMU repo head
  `f690aa1f7daf4fdc3f70802c074b65b633418aa3`, and has
  `clean_build_for_head=true` in both fast-gate and matrix summaries. Both
  `999.specrand_ir` test and train strict hashes pass.
- `workloads/generated/specint-train-all-provenance-clean-qemu-20260703-r1/`
  is the current all-SPECint train ledger on a clean latest-QEMU build selected
  by the default QEMU resolver (`v10.2.0-1006-gf690aa1f7da`, clean marker
  `f690aa1f7daf4fdc3f70802c074b65b633418aa3:worktree`). It runs the split
  train suite with `LINX_QEMU_TLB_FILL_STATS=1`, a 300s row cap, 1B-instruction
  QEMU heartbeat, and `2G` stack limit. `999.specrand_ir` passes strict train
  hash (`rand.11.out`, 871 bytes, `0x973dcfc2`); every other tracked C/C++
  row, including generated 9p `525.x264_r`, is heartbeat-backed
  `live-timeout` with BPC site progress and `tlbf=` evidence. There are no
  fresh user traps, kernel panics, wrapper child exits, no-progress timeouts,
  benchmark internal errors, or oversized-initramfs VFS panics in this suite
  shape. `548.exchange2_r` remains outside the tracked Linx suite because the
  current SPEC build flow intentionally skips Fortran.
- `workloads/generated/specint-505-tlbfill-split-qemu-20260703-r1/` is the
  current focused user/kernel split for the slowest train row. `505.mcf_r`
  remains a live-timeout at `32000000009` instructions, with
  `tlbf_total=102633834`, `tlbf_user=100756933`, `tlbf_kernel=1876901`, and
  `tlbf_user_load=92222996`; the simple 1024-entry QEMU soft-TLB default
  experiment under
  `workloads/generated/specint-505-tlb-default-1024-qemu-20260703-r1/` was
  slower and should not be promoted as the next speed fix.
- `workloads/generated/specint-profile-505-latest-qemu-20260703-r1/` is the
  current post-`LINX_SPEC_START` host profile for the slowest train row. The
  corrected sample targets the real QEMU child and shows hot stacks in
  `helper_linx_template_fentry`, `helper_linx_template_fret_stk`,
  `mmu_lookup1`, `mmu_lookup`, `probe_access_internal`, `probe_access`,
  `linx_frame_restore_commit`, and generic `cpu_ldq_mmu`/`cpu_stq_mmu`.
  Treat the profiler row's `timeout-no-heartbeat` as expected because heartbeat
  output was disabled for sampling; the guest log proves the run reached
  benchmark execution.
- Use `tools/spec2017/profile_qemu_after_spec_start.py` for future SPEC/QEMU
  host samples. The wrapper waits for `LINX_SPEC_START` in the generated
  `qemu.log` and matches the descendant executable basename
  `qemu-system-linx64`, avoiding false samples of Python parent commands that
  merely contain a `--qemu` argument.
- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/` is
  the last initramfs-only all-SPECint bounded diagnostic ledger after the QEMU
  Linx `virt` memory-node MMIO-hole fix and blockify rebuild. The run requested
  all ten SPECint rows on both `test` and `train` inputs with initramfs, QEMU BPC
  heartbeat every 1B guest instructions, and a `2G` stack limit on rebuilt QEMU
  `v10.2.0-989-g5cfb672a711`. It is red, but the failure mix is now narrower:
  `502.gcc_r`, `557.xz_r`, and `999.specrand_ir` pass on `test`;
  `999.specrand_ir` passes on `train`; remaining red rows are live-progress
  timeouts, focused user traps, guest OOM at 2 GiB, wrapper/benchmark exits, or
  the persistent `525.x264_r` oversized-initramfs VFS-root panic.
- `run_specint_fast_gate.py` now keeps the bounded all-row surface while
  splitting large payload rows onto the right transport: `525.x264_r` runs as
  `test-all-large-9p` / `train-all-large-9p` by default. Do not pass
  `--transports initramfs` for routine all-row gates unless intentionally
  reproducing the oversized-cpio VFS-root panic. Focused 9p evidence under
  `workloads/generated/specint-525-9p-current-20260702-r1/` and
  `workloads/generated/specint-525-9p-train-20260702-r1/` classifies x264 as
  live-progress timeout, not a boot transport failure.
- `workloads/generated/specint-523-guesthb-light-qemu-20260702-r1/` proves the
  SPEC guest heartbeat can run without the heavy `/proc` dumps: `523.xalancbmk_r`
  now classifies as `live-timeout` with `heartbeat_running=true`,
  `heartbeat_site_progress=true`, and BPC `0x1555764ecc` instead of the earlier
  guest-diagnostic-induced user trap.
- `workloads/generated/specint-train-all-current-qemu-20260702-r1/` is the
  prior split initramfs/9p train ledger on QEMU `v10.2.0-991-g5754b39fb76`.
  It is superseded for current latest-QEMU classification by the 2026-07-03
  TLB-fill run above, but remains useful historical evidence for the
  `502.gcc_r` benchmark internal-error closure.
- The canonical SPEC build stages now default `LINX_SPEC_BENCH_OPTIMIZE` to
  `502.gcc_r=-O0 -fno-vectorize -fno-slp-vectorize -fwrapv`. Focused evidence
  under `workloads/generated/specint-build-502-benchopt-wrapv-20260702-r1/`
  and `workloads/generated/specint-502-benchopt-wrapv-train-hb-20260702-r1/`
  shows that profile removes the `tree-into-ssa.c:942` child-exit row and moves
  `502.gcc_r` to heartbeat-backed live progress without traps or panics.
  The flow-shaped recheck is
  `workloads/generated/specint-build-502-flow-wrapv-20260702-r1/` plus
  `workloads/generated/specint-502-flow-wrapv-train-row1-qemu-20260702-r1/`:
  the manifest records the 502-specific flags, source immutability passes, and
  train row 1 reaches `live-timeout` at count `24000000002`, BPC
  `0x1555766900`, with no internal-error, trap, or panic marker.
- `emulator/qemu` commit `57715bca69f` fixes explicit scalar queue
  destinations (`RegDst=24` for `t#1`) and restores QEMU AVS D0D4. The refreshed
  all-row `test-train` SPEC ledger is
  `workloads/generated/specint-test-train-all-explicit-queue-dest-20260702-r1/`
  on QEMU `v10.2.0-994-g57715bca69f`: `test` passes `502.gcc_r`,
  `523.xalancbmk_r`, and `999.specrand_ir`; `train` passes
  `999.specrand_ir`; every remaining red row, including split 9p `525.x264_r`,
  is a heartbeat-backed `live-timeout` with BPC site progress and no fresh
  trap, panic, hash-mismatch, internal-error, or wrapper child-exit class.
- Fresh Linux evidence on the same QEMU includes passing initramfs smoke,
  initramfs full boot, 15/15 defconfig audit, and a rebuilt BusyBox rootfs boot
  in `workloads/generated/busybox-rootfs-qemu-explicit-queue-dest-20260702-r1/`
  with timer IRQ progress `32 -> 37`. A `SKIP_BUILD=1` BusyBox rootfs run still
  reproduces the stale PID1 `addr=0x10000004` trap, so stale rootfs results are
  non-authoritative for current closure.
- Focused `500.perlbench_r` test row 2 triage now has a lower-perturbation
  syscall/fault trace packet in
  `workloads/generated/specint-500-test-row2-syscalltrace-qemu-20260704-r1/`.
  The SPEC runners expose QEMU syscall tracing with
  `--qemu-syscall-trace*` switches and record the selected
  `LINX_SYSCALL_TRACE*` knobs in JSON/Markdown summaries. The current terminal
  trap is not a deadlock: with `norandmaps` bias `0x1515555000`, terminal
  `tpc=0x1555828b40` maps to musl `__malloc_alloc_meta` linked
  `0x402d3b40`, where a zero allocator-list link causes a store through
  `addr=0x8` after returning from the `sccp` syscall wrapper. Keep this in the
  correctness lane and trace allocator metadata writes plus caller/control-flow
  provenance before changing broad SPEC timeouts.
- `workloads/generated/specint-500-testpl-linuxvmtrace-qemu-20260705-r1/`
  is the current Linux VM-fault plus QEMU trap-delivery packet for focused
  `500.perlbench_r` test row 2 on clean QEMU
  `v10.2.0-1029-g68bebbd9e7b`. The new SPEC runner switches
  `--linux-vm-trace` and `--linux-vm-trace-addr` append Linux
  `linx_vm_trace=1` / `linx_vm_trace_addr=<addr>` cmdline arguments and parse
  `LINX_VM_FAULT` records into JSON summaries. This run records
  `linux_vm_fault_trace_count=1911` and `trap_delivery_trace_count=512`.
  The terminal signal is not a QEMU deadlock: QEMU BPC heartbeat progressed to
  count `3000000003`, and Linux reports a real user page fault at
  `addr=0x10`, `tpc=0x15555e4608`, `bpc=0x15555e45fa`,
  `stage=vma-gap`, `trapno=0xc000000005000001`. Immediately before the
  terminal null-ish dereference, the same `tpc`/`bpc` pair handled a mapped
  store fault at `addr=0x3fefed04e0` in VMA
  `0x3fefed0000..0x3fefed2000`. Keep the next loop in user-state corruption
  triage: trace writes to the data structure read at `tpc=0x15555e4608` and
  symbolicate that PC in `perlbench_r_base.mytest-m64`; do not treat the
  earlier mapped page faults as emulator delivery failures without new
  contrary evidence.
- QEMU memory tracing is now usable without an address filter. Use
  `--qemu-mem-trace --qemu-mem-trace-pc-lo <pc> --qemu-mem-trace-pc-hi <pc>`
  for narrow producer windows, add `--qemu-mem-trace-pre` for faulting loads,
  and add `--qemu-mem-trace-regs` when T/U queue heads matter. Focused row-2
  packets in
  `workloads/generated/specint-500-test-row2-enframe-pcwatch-qemu-20260704-r1/`
  and
  `workloads/generated/specint-500-test-row2-rcrt1-memtrace-qemu-20260704-r1/`
  show normal PC-relative producers and startup relocation stores with nonzero
  operands, while the latter remains heartbeat-live through the timeout. Treat
  those packets as producer evidence; the uninstrumented/null-trap packets
  remain the terminal correctness evidence.

Inference:

- Full benchmarks should not be the next default action from a dirty or
  partially repaired workspace. The efficient path is to stop at the first red
  prerequisite: ISA/catalog, compiler, QEMU, TSVC direct runtime, Linux
  userspace entry, libc hosted runtime, then full benchmark expansion.
- The current strict PR benchmark lane reaches the TSVC/QEMU stage, and the
  Linux BusyBox rootfs lane now has a fresh latest-QEMU local pass. The next
  broad closure step is to refresh the canonical convergence/strict report and
  continue into libc hosted runtime plus SPEC correctness/performance rather
  than reopening the stale BusyBox-rootfs image failure.
- Markdown status pages are useful summaries, but several are stale relative to
  the current June 14 coverage snapshot and aggregate `latest.json` is older
  than some sidecar reports. Agents should use the JSON flow, command output,
  and fresh runner reports as the active source of truth for a new run.

## Stage Ladder

| Stage | Owner | Stop Rule | Purpose |
| --- | --- | --- | --- |
| `source-contract` | integration | hard break | Validate layout, canonical v0.58 catalog, and agent ownership map before build work. |
| `compiler-contract` | llvm | hard break | Prove active `clang` can build and cover the Linx64 AVS compile corpus. |
| `qemu-contract` | qemu | hard break | Prove strict QEMU AVS runtime and keep decode coverage visible. |
| `tsvc-qemu-hardbreak` | integration | hard break | Run compile-only TSVC floor, then batched QEMU TSVC before Linux rootfs or SPEC. |
| `linux-userspace-entry` | linux | hard break | Rebuild `vmlinux`, prove trivial initramfs userspace, then BusyBox rootfs. |
| `libc-hosted-runtime` | libc | hard break | Prove musl build/runtime and glibc runtime before hosted benchmarks. |
| `specint-fast-gate` | integration | hard break | Run fast SPECint `test`/`train` suites before broad promotion work. |
| `full-benchmarks` | integration | hard break | Run CoreMark/Dhrystone and nightly SPECint test/train promotion only after upstream stages pass. |

## Commands

The `qemu-contract` stage seeds or refreshes the clean QEMU binary for runtime
stages. The flow runner and `run_gates.py` automatically prefer this binary
when its marker matches the current QEMU submodule SHA; otherwise they fall
back to the in-tree build path or any explicit `QEMU=...` override. When the
user has not set `QEMU`, the runner refreshes the resolved QEMU path before
each command so commands after `qemu-clean-build` use the newly built binary.
SPECint runners now also include `qemu_provenance` in JSON summaries and
`qemu_version`, `qemu_repo_head`, and `qemu_clean_build_for_head` in Markdown
summaries; treat `qemu_clean_build_for_head=false` as stale-build evidence
until the run intentionally names a non-clean experimental QEMU binary.

```bash
bash tools/bringup/run_qemu_build_clean.sh \
  --qemu-root "$PWD/emulator/qemu" \
  --out-dir /tmp/linx-qemu-clean-build \
  --target qemu-system-linx64
```

List the selected PR stages:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py --profile pr --list
```

Dry-run the PR hard-break path:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py \
  --profile pr \
  --dry-run \
  --report-out workloads/generated/flow-pr-dry-run/report.json
```

Run the PR path and stop at the first real failure:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py \
  --profile pr \
  --report-out workloads/generated/flow-pr/report.json
```

Run the Linux/full-OS expansion only after the PR path passes:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py \
  --profile linux \
  --start-at linux-userspace-entry \
  --report-out workloads/generated/flow-linux/report.json
```

Run only the fast SPECint gate after Linux/libc prerequisites are green:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py \
  --profile linux \
  --start-at specint-fast-gate \
  --stop-after specint-fast-gate \
  --report-out workloads/generated/flow-specint-fast/report.json
```

The flow build command records the effective per-benchmark flags in the emitted
manifest. Override the default signed-wrap profile only for deliberate
regression reproduction, for example by setting
`LINX_SPEC_BENCH_OPTIMIZE='502.gcc_r=-O0 -fno-vectorize -fno-slp-vectorize'`
before the flow command.

Run the bounded all-row test+train SPECint gate directly when the goal is to
exercise every supported SPECint row without refrate input cost:

```bash
SPECINT_TEST_ALL_TIMEOUT=120 \
SPECINT_TRAIN_ALL_TIMEOUT=180 \
SPEC_GUEST_HEARTBEAT_SEC=0 \
SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
SPEC_NO_PROGRESS_TIMEOUT=120 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile test-train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-test-train-all-<date> \
  --append-extra norandmaps \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --guest-heartbeat-sec 0 \
  --no-progress-timeout 120 \
  --stack-limit 2G \
  --continue-on-fail
```

Run the current all-SPECint train diagnostic loop directly when the goal is to
classify every train workload rather than stop at PR smoke:

```bash
SPECINT_TRAIN_ALL_TIMEOUT=300 \
SPEC_GUEST_HEARTBEAT_SEC=0 \
SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
SPEC_NO_PROGRESS_TIMEOUT=180 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-all-<date> \
  --append-extra norandmaps \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --guest-heartbeat-sec 0 \
  --no-progress-timeout 180 \
  --stack-limit 2G \
  --continue-on-fail
```

Leave `--transports` unset in these wrapper commands so the gate can split
`525.x264_r` to 9p while keeping the remaining all-row benches on initramfs.
Use an explicit `--transports` override only for focused transport bisection.

Use `run_int_rate_qemu.py --run-index <n>` for focused SPEC command-row
debugging after an all-row report identifies one failing invocation. The
selector is 1-based, can be repeated, records `source_run_index` in the QEMU
run summary, and filters compare checks to the selected row's declared outputs
so a single-row probe does not fail against unexecuted sibling outputs.

Use `LINX_TP_TRACE=1 LINX_TP_TRACE_LIMIT=<n>` only for focused TP/TLS
diagnosis. Use `LINX_TP_TRACE_SSR=1` or `LINX_TP_TRACE_READS=1` only after a
focused run identifies a TP handoff window; those switches are too noisy for
routine train-all profiling.

Use `LINX_QEMU_HEARTBEAT_REGS=1` only for focused register snapshots. The
normal train-all loop should rely on `LINX_HEARTBEAT` plus the runner summary
fields `heartbeat_running`, `heartbeat_site_progress`, `heartbeat_last_bpc`,
and `heartbeat_last_progress` to decide whether a timeout is deadlock or live
slow execution.

Use `LINX_QEMU_HEARTBEAT_CODE_BYTES=<n>` only for focused PC/BPC byte
snapshots after the summary identifies a narrow failure window. If a temporary
workload or library instrumentation changes a deterministic failure into a live
timeout, keep the original uninstrumented run as the canonical blocker and
record the instrumented run as perturbation evidence.

Use `LINX_TLB_FILL_TRACE=1` or `LINX_QEMU_TLB_FILL_TRACE=1` only for focused
page-walk windows. Narrow with `LINX_TLB_FILL_TRACE_VA=<addr>` or
`LINX_TLB_FILL_TRACE_VA_LO/HI`, plus `LINX_TLB_FILL_TRACE_COUNT_LO/HI`, before
running a SPEC row. Each record prints the requested VA, access kind, QEMU prot,
fault cause, PC/BPC/TPC, and the legacy leaf descriptor decision. This is the
preferred discriminator when a syscall such as `mprotect()` appears to succeed
but the next access still faults.

Use `LINX_QEMU_TLB_FILL_STATS=1` for routine long-row ledgers before enabling
per-fill traces. Heartbeats expose aggregate `tlbf_` counters, including
user/kernel/other split fields on current QEMU, and the SPEC summaries print
compact `/u<user>/k<kernel>/o<other>` suffixes when those fields are present.

Use `LINX_QEMU_FRAME_STATS=1` or SPEC runner `--qemu-frame-stats` when a
live-timeout row needs aggregate FENTRY/FRET frame-template attribution without
full frame slot traces. Current QEMU appends `fr_` counters to
`LINX_HEARTBEAT`, and SPEC summaries record them as `heartbeat_frame_stats`.
Use this before reopening frame-store or return-target experiments: the
2026-07-03 focused `505.mcf_r` probe has `fr_save_fallback=0` and a 99.986%
return fast-hit rate, so the active frame-related speed question is restore
load/probe lookup cost, not fallback stores or return-cache misses.

Use `LINX_QEMU_TB_STATS=1` or SPEC runner `--qemu-tb-stats` when a live-timeout
row needs aggregate TCG TB execution/cache pressure without full TCG tracing.
Current QEMU appends `tbs_` counters to `LINX_HEARTBEAT`, and SPEC summaries
record them as `heartbeat_tb_stats`. Use this before changing TCG cache size or
dispatch behavior: the 2026-07-03 focused `505.mcf_r` probe has
`tbs_flush=0`, stable miss/generation counts, and about 36 MiB of roughly 1 GiB
code-buffer use, so the active speed question is per-TB dispatch/JIT transition
and soft-MMU lookup cost, not TB code-cache churn.

Use `LINX_FENTRY_TRACE=1` or `LINX_QEMU_FENTRY_TRACE=1` only for focused frame
save windows. Narrow with `LINX_FENTRY_TRACE_PC`, `LINX_FENTRY_TRACE_RA`,
`LINX_FENTRY_TRACE_SP`, `LINX_FENTRY_TRACE_NEW_SP`, or the `COUNT_LO/HI`
filters, and cap output with `LINX_FENTRY_TRACE_LIMIT`. Each slot record prints
the save address, value, MMU readback, direct host pointer/readback when the
translation is RAM-backed, and debug readback. This is the preferred next step
when `FRET.STK` restores a stale or zero register and the producer frame save
must be proven.

Use `LINX_SYSCALL_TRACE_DUMP_ARG=<0..5>` with
`LINX_SYSCALL_TRACE_NR=<nr>` or a comma-separated list such as
`LINX_SYSCALL_TRACE_NR=48,56,79,221` for focused syscall copyout checks. Pair it
with `LINX_SYSCALL_TRACE_DUMP_BYTES=<n>` to cap the returned buffer dump; leave
the variable unset for normal train-all runs. This is the preferred next step
when the symptom is `errno`/fd/path corruption but `LINX_SYSCALL_RETURN` does
not show the reported errno.

Use `LINX_MEM_TRACE_CONTEXT=1` when a memory trace must prove whether two
stores come from the same guest address space. Pair it with
`LINX_MEM_TRACE_ACR=2` for focused userspace heap/list traces; leave both unset
for normal train-all runs because context printing belongs in narrow triage
windows.
Use `LINX_MEM_TRACE_PRE=1` only when faulting loads need their computed address
before `tcg_gen_qemu_ld_i64` can raise the MMU exception. Store trace lines are
already emitted before the QEMU store. Use `LINX_MEM_TRACE_REGS=1` only when
the T/U queue heads decide the root cause; it appends `tq0..tq3` and `uq0..uq3`
to every memory trace line in the filtered window.
For late SPEC faults, also set `LINX_MEM_TRACE_COUNT_LO=<insns>` and
`LINX_MEM_TRACE_COUNT_HI=<insns>` with the address/PC/ACR filters. Without a
count window, repeated stack-slot reuse can spend `LINX_MEM_TRACE_LIMIT` long
before the final producer.

Use `LINX_DEBUG_PC_WATCH=<pc>[,<pc>...] LINX_DEBUG_PC_WATCH_REGS=1` after a
fault, heartbeat, or symbolization pass identifies a narrow PC window. This
adds `LINX_PC_WATCH_REGS` full-register records without making the normal
train-all loop noisy. Reserve `LINX_DEBUG_PC_WATCH_EXIT=1` for short smoke
checks, not correctness runs.
For long SPEC loops, bound focused watchpoints with
`LINX_DEBUG_PC_WATCH_COUNT_LO=<insns>`, `LINX_DEBUG_PC_WATCH_COUNT_HI=<insns>`,
and `LINX_DEBUG_PC_WATCH_HIT_LIMIT=<n>` so a hot symbol does not flood the QEMU
log. The count window is an arming gate before PC matching, so late user faults
can be watched without paying a full reset-to-userspace PC-scan cost. A printed
watch record includes both the count-window hit count and the filtered
`printed=` count. The translator emits the host debug hook only for exact
`LINX_DEBUG_PC_WATCH` PCs; broad per-instruction hooks are reserved for co-sim
and work-grab debug modes. When a single PC window needs several frame or object slots,
use `LINX_DEBUG_PC_WATCH_DUMP_OFFSETS=<off>[,<off>...]` with
`LINX_DEBUG_PC_WATCH_DUMP_REGS=<reg>[,<reg>...]` so one run captures all needed
memory words.
Use `LINX_DEBUG_PC_WATCH_DUMP_WIDTH=1|2|4|8` only for focused structure-field
probes. The default remains 8-byte word dumps; narrower dumps are useful for
32-bit Perl SV flags, C++ object fields, and stack slots where 64-bit grouping
would hide the field boundary.
Use `LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS=<off>[,<off>...]` with
`LINX_DEBUG_PC_WATCH_DUMP_REGS=<reg>[,<reg>...]` when stack or object slots
hold guest pointers that need one-hop dereference in the same long run. This
keeps pointer provenance and pointee fields in one bounded PC-watch window; it
is too noisy for routine train-all loops.

When a fault-trace run is expected to dump a late PC-watch ring, pair
`LINX_FAULT_TRACE_PC_LO/HI` with `LINX_FAULT_TRACE_COUNT_LO/HI`. Early boot
faults and unrelated user faults otherwise consume `LINX_FAULT_TRACE_LIMIT`
before QEMU reaches the final SPEC window. For null-branch or null-data traps,
`LINX_FAULT_TRACE_ADDR=0` now arms an explicit zero-address fault filter.

When a suspected replay or trap-return bug needs ACRE evidence, prefer
`LINX_ACRE_TRACE=1` over the older unfiltered `LINX_DEBUG_ACRE_STDERR=1`.
Filter by `LINX_ACRE_TRACE_PC=<resume-pc>` or
`LINX_ACRE_TRACE_BPC=<resume-bpc>`, and add `LINX_ACRE_TRACE_COUNT_LO/HI` once
fault trace has identified the failing instruction-count window. The trace
prints paired `phase=entry` and `phase=staged` records so the run can compare
saved block/queue state before restore with the state actually staged for
userspace.

For SPEC initramfs waits, `--guest-heartbeat-sec <n>` is intended to stay
lightweight: child liveness, output growth, and maps snapshots. Use
`--guest-proc-diagnostics` or `LINX_SPEC_GUEST_PROC_DIAGNOSTICS=1` only for
focused runs that need `/proc` status, meminfo, vmstat, or pressure dumps; those
extra guest syscalls can perturb startup fault paths.

When a null-branch fault comes from `FRET.STK` restoring `ra=0`, use
`LINX_FRET_STK_TRACE=1` with `LINX_FRET_STK_TRACE_PC=<fret-pc>`,
`LINX_FRET_STK_TRACE_RA=0`, and optional `LINX_FRET_STK_TRACE_COUNT_LO/HI`.
Add `LINX_FRET_STK_TRACE_DUMP_WORDS=<n>` only for focused frame snapshots. The
trace prints the computed restore addresses and values before QEMU commits the
register file, so it distinguishes a bad return slot from syscall-return or
branch-target handling.

For user traps at `addr = sp - 8` or at the current stack bottom, run a bounded
stack-limit classifier before treating the failure as a C++ runtime, atomic, or
QEMU memory bug. Use `--stack-limit <bytes|512M|1G|2G|unlimited>` on
`run_int_rate_qemu.py`, `run_stage_qemu_matrix.py`, or
`run_specint_fast_gate.py`, and keep an explicit `--timeout`; if the failure
changes from `user-trap` to heartbeat-visible live progress, record it as stack
policy first. The `541.leela_r` follow-up refined this rule: small stack limits
trap at `sp - 8`, but the 4 GiB / `--stack-limit 2G` user trap was compiler-rt
`__atomic_load_1` self-recursion, not stack-growth or QEMU MMU behavior. After
relinking against Linx compiler-rt builtins that avoid `__c11_atomic_*`
recursion, `workloads/generated/specint-541-atomicfix-20260702-r1/` changes the
row to heartbeat-backed `live-timeout` through 420 seconds, count
`45000000002`, no `LINX_USER_TRAP`, no panic, and `oom_kill 0`. A longer
`workloads/generated/specint-541-atomicfix-long-20260702-r1/` run later trips a
fresh null-address mallocng `a_crash` in `get_meta`, mapping to
`assert(area->check == ctx.secret)`. A second mallocng-focused run also exposed
the `queue()` `assert(!m->next)` path at runtime PC `0x1555616858`. Before
changing QEMU, compiler, or libc for these allocator metadata traps, run the
oldmalloc bisection lane: rebuild with `MALLOC_IMPL=oldmalloc`, refresh the
spec C++ runtime overlay, relink the target row, and compare the same QEMU
matrix shape. For `541.leela_r`,
`workloads/generated/specint-541-oldmalloc-long-20260702-r1/` stayed live
through 1200 seconds, count `133000000000`, no trap, no panic, and `oom_kill 0`;
route this as mallocng metadata/codegen/VM-path correctness, not the closed
atomic-recursion bug. Oldmalloc remains a bisection aid, not the default
phase-b allocator baseline.

Run the promotion path only when the Linux path is green:

```bash
python3 tools/bringup/run_benchmark_linux_flow.py \
  --profile nightly \
  --report-out workloads/generated/flow-nightly/report.json
```

## Agentic Rules

- Work one stage at a time. Do not debug a downstream stage until every
  upstream hard-break stage is green in the same lane.
- Keep each agent inside its stage ownership unless the runner output proves a
  cross-stage failure. For example, a TSVC compiler crash belongs to `llvm`
  before it becomes a QEMU runtime problem.
- Publish a runner report for every run and attach the first failing command,
  return code, and log/artifact paths to the agent closeout.
- Put new generated benchmark artifacts under `workloads/generated/<run-id>/`.
  Do not create new `workloads/generated-*` sibling directories.
- Treat `skill-evolve` as a closeout decision. Update skills only when the
  failing stage teaches a reusable command, invariant, or triage order.
- When `--report-out` is set, the flow runner writes per-command logs under
  `<report-dir>/logs/`. Use those logs, not terminal scrollback, as the
  handoff artifact for the first failed command.
- The tiny userspace proof can take slightly over 10 seconds on the current
  clean QEMU path, so the flow sets `TINY_USERSPACE_TIMEOUT=30` by default.

## Why This Is More Efficient

- It avoids expensive SPEC/rootfs/full benchmark runs when the cheaper QEMU or
  TSVC direct lane is already red, and it runs cheap SPECint `test`/`train`
  suites before any refrate-scale or broad promotion workload.
- It separates PR, Linux, and nightly profiles instead of using one monolithic
  strict run for every question.
- It makes the handoff boundary explicit for QEMU, compiler, libc, Linux, and
  ISA/docs agents, which reduces duplicate investigation across stale summaries.
