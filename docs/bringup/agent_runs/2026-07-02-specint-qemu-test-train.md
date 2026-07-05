# SPECint QEMU test/train bring-up, 2026-07-02

## 2026-07-05 continuation: `500.perlbench_r` fault-time call ring

Artifact root:

- `workloads/generated/specint-500-testpl-fault0-10-callring-qemu-20260705-r1`

Command shape:

```bash
python3 tools/spec2017/run_int_rate_qemu.py \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu /private/tmp/linx-qemu-clean-build/qemu-system-linx64 \
  --kernel kernel/linux/build-linx-fixed/vmlinux \
  --stage b --transport initramfs --input-set test \
  --bench 500.perlbench_r --run-index 2 --timeout 150 \
  --heartbeat-sec 15 --qemu-heartbeat-interval 1000000000 \
  --qemu-heartbeat-same-site-warn 4 --guest-heartbeat-sec 1 \
  --guest-child-maps-bytes 4096 --terminal-failure-grace-sec 3 \
  --append-extra norandmaps --linux-vm-trace \
  --qemu-fault-trace --qemu-fault-trace-regs \
  --qemu-fault-trace-addr-lo 0x0 --qemu-fault-trace-addr-hi 0x10 \
  --qemu-fault-trace-limit 16 \
  --qemu-call-trace-ring --qemu-call-trace-ring-size 128
```

Result:

- QEMU: `/private/tmp/linx-qemu-clean-build/qemu-system-linx64`,
  `QEMU emulator version 10.2.50 (v10.2.0-1029-g68bebbd9e7b)`.
- Runner summary:
  `workloads/generated/specint-500-testpl-fault0-10-callring-qemu-20260705-r1/stage_b_summary.json`.
- Classification: `user-trap`, not timeout or deadlock.
- Heartbeat: `heartbeat_running=true`, `heartbeat_site_progress=true`,
  last count `3000000003`, last BPC `0xffffffff803e91e8`.
- Terminal QEMU fault trace:
  `count=3347319869`, `tpc=0x1555672a00`, `report_bpc=0x15556729ea`,
  `traparg0=0xc`, `mem_va=0xc`, `cause=0x5`, `bi=1`, `precise=0`,
  `store_ok=0`, `store_cause=0x5`, `tq0..tq3=0`, `uq0..uq3=0`.
- Fault-time call ring:
  `LINX_CALL_TRACE_RING reason=fault fault_pc=0x1555672a00`
  with final entries `acre_enter` and `acre_staged` for the same user PC.
  The staged entry records `acr=2`, `cstate=0x12`, `a0=0x7`,
  `a1=0x3fefe55c50`, `a2=0x602`, `ra=0x15556727ce`.
- Linux VM trace:
  final `LINX_VM_FAULT stage=vma-gap addr=0xc tpc=0x1555672a00`
  and final `LINX_USER_TRAP ... addr=0xc ... traparg0=0xc`.
- Symbolization with the observed load bias maps `tpc=0x1555672a00` to
  linked `0x4011da00` in `S_SvPADSTALE_off`:
  `swi a0, [t#2, 12]`. The store address `0xc` means the base carried in the
  T queue for `t#2` was zero at the terminal execution. `orig_tpc=0x1555837f3c`
  maps to linked `0x402e2f3c`, the `sccp` ACRC/BSTOP return path.

Tool update:

- `tools/spec2017/run_int_rate_qemu.py` now extracts `LINX_FAULT_TRACE`
  records even when serial output glues a guest maps line and a QEMU trace
  record together. The captured log had this exact shape, so older parser code
  missed `fault_trace_seen` even though the raw QEMU log contained the fault.
- Validation: `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py
  tools/spec2017/test_run_int_rate_qemu.py` passed; `cd tools/spec2017 &&
  python3 -m unittest test_run_int_rate_qemu.py` passed 62 tests.

Interpretation:

The current row-2 failure remains in the QEMU/compiler/control-state
correctness lane. It is live until the terminal fault, then QEMU reports a
block-interior store fault where all captured T/U queue slots are zero at
fault time. The next loop should trace the producer of `t#2` across
`S_SvPADSTALE_off` and the `sccp` ACRC/BSTOP return path with a narrow PC/count
window, then compare against compiler lowering for the T-queue lifetime in
this function. Do not route this row to deadlock triage; BPC heartbeats and the
fault-time ring prove forward progress until the fatal user trap.

## 2026-07-05 continuation: `500.perlbench_r` Linux VM-fault trace

Artifact root:

- `workloads/generated/specint-500-testpl-linuxvmtrace-qemu-20260705-r1`

Command shape:

```bash
python3 tools/spec2017/run_int_rate_qemu.py \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu /private/tmp/linx-qemu-clean-build/qemu-system-linx64 \
  --kernel kernel/linux/build-linx-fixed/vmlinux \
  --stage b --transport initramfs --input-set test \
  --bench 500.perlbench_r --run-index 2 --timeout 150 \
  --heartbeat-sec 15 --qemu-heartbeat-interval 1000000000 \
  --qemu-heartbeat-same-site-warn 4 --guest-heartbeat-sec 1 \
  --guest-child-maps-bytes 4096 --terminal-failure-grace-sec 3 \
  --append-extra norandmaps --linux-vm-trace \
  --qemu-trap-delivery-trace \
  --qemu-trap-delivery-trace-count-lo 3161900000 \
  --qemu-trap-delivery-trace-count-hi 4100000000 \
  --qemu-trap-delivery-trace-limit 512
```

Result:

- QEMU: `/private/tmp/linx-qemu-clean-build/qemu-system-linx64`,
  `QEMU emulator version 10.2.50 (v10.2.0-1029-g68bebbd9e7b)`.
- Runner summary:
  `workloads/generated/specint-500-testpl-linuxvmtrace-qemu-20260705-r1/stage_b_summary.json`.
- Classification: `user-trap`, not timeout or deadlock.
- Heartbeat: `heartbeat_running=true`, `heartbeat_site_progress=true`,
  last count `3000000003`, last BPC `0xffffffff800fe9de`.
- QEMU trap delivery: `trap_delivery_trace_count=512`; the count-window tail
  still delivers nonzero `pending_arg0` values before the terminal signal.
- Linux VM fault trace: `linux_vm_fault_trace_count=1911`.
- Terminal Linux signal:
  `addr=0x10`, `tpc=0x15555e4608`, `bpc=0x15555e45fa`,
  `traparg0=0x10`, `trapno=0xc000000005000001`,
  `LINX_VM_FAULT stage=vma-gap`.
- Immediately preceding Linux VM fault at the same `tpc`/`bpc` was handled:
  `addr=0x3fefed04e0`, VMA `0x3fefed0000..0x3fefed2000`,
  `fault=0x0`.

Interpretation:

The current row-2 failure is a real null-ish user data dereference surfaced by
Linux, not an absence of QEMU progress and not the earlier mapped page-fault
delivery bug hypothesis. The next loop should symbolicate `0x15555e4608` in
`perlbench_r_base.mytest-m64`, trace the producer of the base pointer that
leads to `addr=0x10`, and use QEMU memory/PC-watch around that producer. Keep
the terminal classification in the correctness lane rather than raising broad
SPEC timeouts.

## Scope

This run used the all-SPECint fast gate with `test` and `train` input sets on the Linx QEMU Linux path.

- Root before this log commit: `06b5f45f175a60fbe1a183d392b76c36e765099d`
- LLVM: `57fa07afb3d1d6e7565e692c74ee7a910d8e10f7`
- QEMU: `5cfb672a711bb2172bfe7de6c6b7bd1bdb47e902`
- QEMU version: `QEMU emulator version 10.2.50 (v10.2.0-989-g5cfb672a711)`
- Kernel: `kernel/linux/build-linx-fixed/vmlinux`
- Sysroot: `out/libc/musl/install/phase-b`
- Artifact root: `workloads/generated/specint-test-train-all-after-blockify-20260702-r2`

Command shape:

```bash
SPECINT_TEST_ALL_TIMEOUT=240 SPECINT_TRAIN_ALL_TIMEOUT=360 \
SPEC_GUEST_HEARTBEAT_SEC=0 SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
SPEC_NO_PROGRESS_TIMEOUT=120 LINX_QEMU_HEARTBEAT_SAME_SITE_WARN=4 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile test-train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-test-train-all-after-blockify-20260702-r2 \
  --append-extra norandmaps --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 --guest-heartbeat-sec 0 \
  --no-progress-timeout 120 --stack-limit 2G --transports initramfs \
  --continue-on-fail --symbolize-heartbeat --dump-prefix-bytes 512
```

## Gate results

The run is red overall. The heartbeat/BPC switch separated live execution from hard failures: live-timeout rows continued to emit `LINX_HEARTBEAT ... bpc=... progress=site-change`, while `525.x264_r` stopped before init with no progress.

`test-all` summary:

| Bench | Runs | Pass | Failure | Evidence |
|---|---:|---:|---|---|
| `500.perlbench_r` | 2 | 1 | run 2 `spec-wrapper-fail` | child SIGSEGV after kernel Oops, `trapno=0xc000000002000001` |
| `502.gcc_r` | 1 | 1 | none | generated `.s` hash matched |
| `505.mcf_r` | 1 | 0 | `live-timeout` | BPC/site progress through 240 seconds |
| `520.omnetpp_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `523.xalancbmk_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `525.x264_r` | 1 | 0 | `kernel-panic` | `VFS: Unable to mount root fs`, initramfs is about 1.6 GB |
| `531.deepsjeng_r` | 1 | 0 | `live-timeout` | BPC/site progress through 240 seconds |
| `541.leela_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `557.xz_r` | 12 | 12 | none | all output hashes matched |
| `999.specrand_ir` | 1 | 1 | none | output hash matched |

`train-all` summary:

| Bench | Runs | Pass | Failure | Evidence |
|---|---:|---:|---|---|
| `500.perlbench_r` | 3 | 3 | none after runner fix | all three output hashes matched; historical JSON marked specdiff rc=2 |
| `502.gcc_r` | 1 | 0 | `spec-wrapper-fail` | child exit code 4; benchmark internal compiler-error message in stderr |
| `505.mcf_r` | 1 | 0 | `live-timeout` | BPC/site progress through 360 seconds |
| `520.omnetpp_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `523.xalancbmk_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `525.x264_r` | 1 | 0 | `kernel-panic` | `VFS: Unable to mount root fs`, initramfs is about 1.6 GB |
| `531.deepsjeng_r` | 1 | 0 | `live-timeout` | BPC/site progress through 360 seconds |
| `541.leela_r` | 1 | 0 | `spec-wrapper-fail` | child SIGKILL, `sig=9` |
| `557.xz_r` | 1 | 0 | `live-timeout` | BPC/site progress through 360 seconds; transient `LINX_HEARTBEAT_STALL` recovered to site changes |
| `999.specrand_ir` | 1 | 1 | none | output hash matched |

Machine-readable summaries:

- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/test-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/specint_fast_gate_summary.json`

The all-row wrapper has since been updated so this old `525.x264_r`
classification is no longer the default all-row gate behavior. `525.x264_r`
stays in `test-all` and `train-all`, but it runs through generated
`test-all-large-9p` / `train-all-large-9p` shards unless `--transports`
explicitly overrides the policy.

## Follow-up focused diagnostics

`520.omnetpp_r` was rerun with guest heartbeat `/proc` sampling enabled:

- Artifact: `workloads/generated/specint-520-guestdiag-20260702-r1/test/qemu_matrix_summary.json`
- Result: `live-timeout`, not a reproduced child SIGKILL.
- Liveness: QEMU heartbeat remained running with site progress through 240 seconds; last BPC was `0xffffffff800091dc`.
- Kernel symbols at recent heartbeat sites included `vsprintf.c`, `string.c`, `memory.c`, `page_alloc.c`, `printk_ringbuffer.c`, `mmap.c`, and final idle-loop sites.
- Guest memory snapshot at the child heartbeat showed `MemFree: 2040952 kB`, `MemAvailable: 2041044 kB`, and `oom_kill 0`.
- Interpretation: this reproduction is a throughput/live-progress failure, not guest OOM. The earlier SIGKILL rows still need per-row reproduction with guest heartbeat because the failure mode is not stable across focused reruns.

Wrapper compile/run smoke after the diagnostics change:

- Artifact: `workloads/generated/specint-999-guestdiag-compile-20260702-r1/test/qemu_matrix_summary.json`
- Result: `999.specrand_ir` test/initramfs passed in 19.328 seconds under strict hash validation.

Focused `525.x264_r` transport diagnostics:

- `workloads/generated/specint-525-9p-current-20260702-r1/test/qemu_matrix_summary.json`
  reran `525.x264_r` test input with 9p transport. It reached userspace and
  classified as `live-timeout` at 360 seconds, count `43000000004`, recent
  delta `7000000000`, eight recent unique BPC sites, no trap, no panic, and
  no 9p mount warning.
- `workloads/generated/specint-525-9p-train-20260702-r1/train/qemu_matrix_summary.json`
  reran `525.x264_r` train input with 9p transport, 4096 MiB, and the same
  `--stack-limit 2G` policy. It classified as `live-timeout` at 480 seconds,
  count `55000000000`, recent delta `6999999998`, eight recent unique BPC
  sites, no trap, no panic, and no 9p mount warning.
- Interpretation: x264 is a QEMU throughput/live-progress row under the proper
  payload transport. The prior `kernel-panic` rows are initramfs transport
  artifacts caused by the about-1.6 GiB generated cpio, not x264 correctness
  failures.

Additional focused diagnostics:

- `workloads/generated/specint-523-541-guestdiag-20260702-r1/test/qemu_matrix_summary.json`
  reran `523.xalancbmk_r` and `541.leela_r` with guest heartbeat sampling.
- `523.xalancbmk_r` first rerun: `user-trap`, not SIGKILL. Runtime BPC
  `0x15559efe1a` maps to ELF `0x404afe1a`, `.LBB24_28` in `locale.cpp`, at
  the libc++ `num_get` indirect-call path. Guest memory snapshot showed
  `MemAvailable: 1975216 kB` and `oom_kill 0`.
- `workloads/generated/specint-523-faultregs-20260702-r1/test/qemu_matrix_summary.json`
  reran `523.xalancbmk_r` with QEMU fault-register tracing enabled through the
  SPEC runner. The switch worked and emitted `LINX_FAULT_TRACE` plus
  `LINX_FAULT_REGS`, but this rerun did not reproduce the user trap; it became
  a `live-timeout` with BPC/site progress through 180 seconds.
- `workloads/generated/specint-541-oomclass-20260702-r1/test/qemu_matrix_summary.json`
  reran `541.leela_r` after the classifier update. It now reports
  `spec-child-sigkill-oom`; guest memory fell from about 2046404 kB available
  to 16348 kB available before `oom_kill` incremented to 1, then wait status
  reported `signaled=1 sig=9`.
- `workloads/generated/specint-541-mem4096-20260702-r1/test/qemu_matrix_summary.json`
  reran `541.leela_r` with 4096 MiB and `--stack-limit 2G`, removing the
  2 GiB OOM pressure. The old executable then failed with a user trap at
  `addr=0x3f7ffffff8`, `sp=0x3f80000000`, and `tpc=0x15556253d6`. Correcting
  the ET_DYN base maps this to ELF `0x400d03d6`, `__atomic_load_1`; disassembly
  showed that the compiler-rt specialized helper called itself recursively.
- `compiler/llvm/compiler-rt/lib/builtins/atomic.c` now has a Linx-only guard
  that keeps compiler-rt atomic builtins away from `__c11_atomic_*`, because
  the current Linx backend lowers those C11 atomics back to the same public
  `__atomic_*` symbols. This is a bring-up fallback until native atomic
  lowering exists.
- Rebuild evidence:
  - `MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh` passed and
    refreshed `out/libc/musl/logs/phase-b-summary.txt`.
  - `bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-b`
    passed and restored the spec-profile C++ runtime overlay into the phase-b
    sysroot.
  - `workloads/generated/specint-build-541-atomicfix-20260702-r1/build_manifest.json`
    records a successful static phase-b rebuild of `541.leela_r`.
  - `out/libc/musl/runtime/phase-b/obj/atomic.c.o` and the relinked Leela
    executable both show direct `lbui/lhui/lwi/ldi` bodies for
    `__atomic_load_{1,2,4,8}` rather than recursive calls.
- `workloads/generated/specint-541-atomicfix-20260702-r1/test/qemu_matrix_summary.json`
  reran the fixed `541.leela_r` binary with the same 4096 MiB /
  `--stack-limit 2G` policy. The row no longer traps, panics, or OOMs; it
  becomes `live-timeout` at 420 seconds with heartbeat site progress,
  count `45000000002`, recent count delta `6999999998`, seven recent unique
  BPC sites, `oom_kill 0`, and a small stack (`VmStk: 316 kB`).
- `workloads/generated/specint-541-atomicfix-long-20260702-r1/test/qemu_matrix_summary.json`
  reran the same fixed binary with a 1200 second cap. It now fails earlier with
  a fresh user trap at `addr=0x0`, `tpc=0x155561559c`, `bpc=0x1555615598`,
  `orig_tpc=0x15556171e6`, and `ra=0x15556152ca`. Using the ET_DYN base
  `0x1551555000`, the trap maps to ELF `0x400c059c` in musl mallocng
  `get_meta`, specifically the `a_crash()` path for
  `assert(area->check == ctx.secret)`. Guest memory was not pressured
  (`oom_kill 0`), so this supersedes the 420 second live-timeout classification
  for `541`: atomic recursion is closed, and the next blocker is allocator
  metadata corruption, codegen, or mmap/free-path correctness.
- `workloads/generated/specint-541-mallocng-faultregs-20260702-r1/test/qemu_matrix_summary.json`
  reran the mallocng binary with QEMU fault-register filters around
  `0x1555615580..0x15556155b0`; the trap did not reproduce and the row stayed
  live through the 300 second cap.
- `workloads/generated/specint-541-mallocng-pcwatch-ring-20260702-r1/test/qemu_matrix_summary.json`
  tried to capture a late PC-watch ring, but an earlier null-address mallocng
  assert fired first at `tpc=0x1555616858`, count `1082228490`. That runtime PC
  maps to ELF `0x400c1858`, the `a_crash()` path for mallocng `queue()` and
  `assert(!m->next)` in the `alloc_slot()` path.
- `workloads/generated/specint-541-mallocng-queue-meta-20260702-r1/test/qemu_matrix_summary.json`
  narrowed the PC-watch count window around that `queue()` assert, but the
  failure did not reproduce in the 120 second cap. Treat the mallocng asserts
  as nondeterministic metadata corruption until a focused memory trace proves
  whether the owner is libc, codegen, or QEMU/Linux VM behavior.
- `MALLOC_IMPL=oldmalloc MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh`
  rebuilt phase-b musl with oldmalloc, `bash tools/build_linx_llvm_cpp_runtimes.sh
  --profile spec --mode phase-b` refreshed the C++ overlay, and
  `workloads/generated/specint-build-541-oldmalloc-20260702-r1/build_manifest.json`
  records a successful static relink of `541.leela_r`.
- `workloads/generated/specint-541-oldmalloc-20260702-r1/test/qemu_matrix_summary.json`
  reran oldmalloc-linked `541` with 4096 MiB and `--stack-limit 2G`. It stayed
  live through 420 seconds with BPC/site progress, count `45000000008`, recent
  count delta `6999999990`, eight recent unique BPC sites, no trap, no panic,
  and `oom_kill 0`.
- `workloads/generated/specint-541-oldmalloc-long-20260702-r1/test/qemu_matrix_summary.json`
  reran the oldmalloc-linked `541` with a 1200 second cap. It remained a
  heartbeat-backed `live-timeout`: elapsed `1200.376` seconds, count
  `133000000000`, last BPC `0x1555592176`, recent count delta `7000000000`,
  eight recent unique BPC sites, no trap, no panic, and `oom_kill 0`. This does
  not make `541` correct or fast enough, but it cleanly splits the current
  mallocng metadata asserts from the closed compiler-rt atomic recursion.

## Post-perlbench all-train split rerun

Artifact root:

- `workloads/generated/specint-train-split-post-perlbench-20260702-r1`

Version context:

- QEMU: `5cfb672a711b`, `QEMU emulator version 10.2.50 (v10.2.0-989-g5cfb672a711)`
- LLVM: `e4771587a947`
- Kernel: `kernel/linux/build-linx-fixed/vmlinux`
- Sysroot: `out/libc/musl/install/phase-b`

Command shape:

```bash
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-split-post-perlbench-20260702-r1 \
  --append-extra norandmaps --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 0 --stack-limit 2G \
  --guest-heartbeat-sec 0 --symbolize-heartbeat \
  --continue-on-fail
```

The generated train profile split `525.x264_r` into the large-payload 9p shard
and kept the other nine rows on initramfs. This run was started before the
final classifier/fail-fast patches in this loop, so the raw logs and focused
`502.gcc_r` repro below supersede any stale generic class in the original
matrix JSON.

Current all-train result ledger:

| Bench | Transport | Result | Liveness evidence |
|---|---|---|---|
| `500.perlbench_r` | initramfs | `live-timeout` | first train row now starts at `diffmail`; BPC changed through count `46000000002`, last BPC `0x15556d96a4` |
| `502.gcc_r` | initramfs | `spec-benchmark-internal-error` | focused current-code repro reports the SPEC GCC internal error at `tree-into-ssa.c:942`, child exit code 4 |
| `505.mcf_r` | initramfs | `live-timeout` | BPC changed through count `48000000005`, last BPC `0x155555c4a4` |
| `520.omnetpp_r` | initramfs | `live-timeout` | BPC changed through count `44000000019`, last BPC `0xffffffff800f683a` |
| `523.xalancbmk_r` | initramfs | `live-timeout` | BPC changed through count `44000000000`, last BPC `0xffffffff8006aca2` |
| `525.x264_r` | 9p | `live-timeout` | all four generated train rows timed out with site progress; final row reached count `22000000014`, last BPC `0xffffffff80112032` |
| `531.deepsjeng_r` | initramfs | `live-timeout` | BPC changed through count `46000000023`, last BPC `0x155555b6fa` |
| `541.leela_r` | initramfs | `live-timeout` | BPC changed through count `15000000005`, last BPC `0x155558ee8e` |
| `557.xz_r` | initramfs | `live-timeout` | BPC changed through count `36000000014`, last BPC `0x155558cc70` |
| `999.specrand_ir` | initramfs | pass | strict hash pass, `LINX_SPEC_PASS 999.specrand_ir` |

Machine-readable summaries:

- `workloads/generated/specint-train-split-post-perlbench-20260702-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-split-post-perlbench-20260702-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-split-post-perlbench-20260702-r1/train-all-large-9p/9p/stage_b_summary.json`

Focused `502.gcc_r` classifier proof:

- `workloads/generated/specint-502-internal-error-class-20260702-r3/qemu_matrix_summary.json`
- Result: `spec-benchmark-internal-error`
- Evidence: `200.c:63888:3: benchmark internal error: in ?, at tree-into-ssa.c:942; LINX_SPEC_FAIL child-exit; ... code=4`

## Current all-train rerun with QEMU helper-elision profile

Artifact root:

- `workloads/generated/specint-train-all-current-20260702-r1`

Version context:

- QEMU before the local helper-elision patch: `5cfb672a711b`
- Kernel: `kernel/linux/build-linx-fixed/vmlinux`
- Sysroot: `out/libc/musl/install/phase-b`

Command shape:

```bash
python3 tools/bringup/run_specint_fast_gate.py --profile train \
  --out-dir workloads/generated/specint-train-all-current-20260702-r1 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --qemu-heartbeat-interval 1000000000 \
  --qemu-heartbeat-same-site-warn 4 \
  --no-progress-timeout 180 \
  --stack-limit 2G \
  --continue-on-fail
```

The run covers every supported SPECint train row. It is red overall, but the
heartbeat records keep the failure classes separated:

| Bench | Transport | Result | Evidence |
|---|---|---|---|
| `500.perlbench_r` | initramfs | `live-timeout` | count `43000000006`, last BPC `0x15556d950a`, site progress |
| `502.gcc_r` | initramfs | `live-timeout` | count `22000000001`, last BPC `0xffffffff803f0644`, site progress |
| `505.mcf_r` | initramfs | `live-timeout` | count `46000000012`, last BPC `0x155555c4be`, recent site progress despite final same-site bucket |
| `520.omnetpp_r` | initramfs | `user-trap` | null-address trap at TPC `0x155577ec76`, BPC `0x155577ec6a` |
| `523.xalancbmk_r` | initramfs | `user-trap` | null-address trap at TPC `0x15559efe26`, BPC `0x15559efe1a` |
| `525.x264_r` | 9p | `live-timeout` | count `23000000000`, last BPC `0xffffffff801121ba`, site progress |
| `531.deepsjeng_r` | initramfs | `live-timeout` | count `47000000000`, last BPC `0x155555b7ac`, site progress |
| `541.leela_r` | initramfs | `live-timeout` | count `19000000005`, last BPC `0x1555585efe`, site progress |
| `557.xz_r` | initramfs | `live-timeout` | count `37000000010`, last BPC `0x155558d6ae`, site progress |
| `999.specrand_ir` | initramfs | pass | train output hash matched |

Machine-readable summaries:

- `workloads/generated/specint-train-all-current-20260702-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-current-20260702-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-current-20260702-r1/train-all-large-9p/qemu_matrix_summary.json`

Host sampling during this run showed two avoidable per-block helpers in the
scalar SPEC hot path:

- `workloads/generated/specint-train-all-current-20260702-r1/profile/qemu-500-perlbench.sample.txt`
- `workloads/generated/specint-train-all-current-20260702-r1/profile/qemu-502-gcc.sample.txt`

The new local QEMU patch replaces the translated block prologue calls to
`helper_linx_tile_set_attr(0)` and `helper_linx_tile_reset_block()` with direct
TCG stores. Focused validation after rebuilding
`emulator/qemu/build-linx/qemu-system-linx64`:

- `python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 15 --qemu emulator/qemu/build-linx/qemu-system-linx64` passed.
- `workloads/generated/specint-999-patched-qemu-20260702-r1/qemu_matrix_summary.json` passed `999.specrand_ir` train hashcheck.
- `workloads/generated/specint-500-patched-profile-20260702-r1/profile/qemu-500-patched-qemu.sample.txt` no longer samples `helper_linx_tile_set_attr` or `helper_linx_tile_reset_block`; remaining sampled QEMU owners include `helper_linx_template_step`, `helper_linx_check_bstart_target`, `linx_is_bstart_at_addr`, `probe_access_internal`, and `mmu_lookup1`.

This repro also closed a runner-reporting bug: QEMU output carries carriage
returns in the SPEC stderr marker block, so the classifier now normalizes QEMU
log bytes before matching `LINX_SPEC_STDERR_BEGIN/END`. Without that
normalization, the raw log contained the internal-error text while JSON stayed
at generic `spec-wrapper-fail`.

Focused `502.gcc_r` conservative-codegen probe:

- `workloads/generated/specint-502-current-argv-20260702-r1/stage_b_summary.json`
  reran train row 1 on the current runner and default 502 binary. It reproduced
  `spec-benchmark-internal-error` at `tree-into-ssa.c:942`, with child exit
  code 4 and exact argv now recorded in both JSON and QEMU log:
  `./cpugcc_r_base.mytest-m64 200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s`.
- `workloads/generated/specint-build-502-conservative-20260702-r1/build_manifest.json`
  rebuilt only `502.gcc_r` as a static phase-b binary with
  `-O0 -fno-vectorize -fno-slp-vectorize -fno-inline -fno-optimize-sibling-calls
  -fno-strict-aliasing -fwrapv -fno-jump-tables`; the source immutability check
  passed.
- `workloads/generated/specint-502-conservative-20260702-r1/stage_b_summary.json`
  reran the same row with a 240 second cap. The internal error did not
  reproduce; the row became `live-timeout`, with heartbeat site progress to
  count `32000000006`, last BPC `0x15559e77aa`, no trap, no panic, and no fail
  marker.
- `workloads/generated/specint-502-conservative-long-20260702-r1/stage_b_summary.json`
  extended the same conservative binary to 600 seconds. It remained
  `live-timeout`, with heartbeat site progress to count `91000000002`, last BPC
  `0x1555fbd61c`, recent count delta `6999999998`, seven recent unique BPC
  sites, no trap, no panic, and no fail marker.

Interpretation: the default 502 binary still has a real codegen-sensitive
misbehavior, but the conservative build turns the immediate benchmark internal
error into a throughput row rather than proving correctness. Keep this as a
compiler/codegen localization probe; do not promote the flag bundle as a
correctness fix until the generated `.s` output reaches strict hash/specdiff
validation. After the probe, `502.gcc_r` was rebuilt back to the default
`-O0 -fno-vectorize -fno-slp-vectorize` flag set; restore evidence is
`workloads/generated/specint-build-502-default-restore-20260702-r1/build_manifest.json`.

Focused `502.gcc_r` flag-bisect follow-up:

- `workloads/generated/specint-build-502-no-jumptables-20260702-r1/build_manifest.json`
  rebuilt 502 with default flags plus `-fno-jump-tables`. The row still
  reproduced `spec-benchmark-internal-error` at `tree-into-ssa.c:942` in
  `workloads/generated/specint-502-no-jumptables-20260702-r1/stage_b_summary.json`
  after `113.397` seconds, count `18000000001`, last BPC `0x1555e5429c`.
- `workloads/generated/specint-build-502-no-inline-20260702-r1/build_manifest.json`
  rebuilt 502 with default flags plus `-fno-inline`. The row still reproduced
  the same internal error in
  `workloads/generated/specint-502-no-inline-20260702-r1/stage_b_summary.json`
  after `145.321` seconds, count `18000000000`.
- `workloads/generated/specint-build-502-semantic-flags-20260702-r1/build_manifest.json`
  rebuilt 502 with default flags plus `-fno-optimize-sibling-calls
  -fno-strict-aliasing -fwrapv`. The row did not reproduce the internal error
  under the 240 second cap and instead classified as `live-timeout` in
  `workloads/generated/specint-502-semantic-flags-20260702-r1/stage_b_summary.json`,
  count `28000000002`, last BPC `0x15559475a8`, no trap, no panic, and no fail
  marker.
- `workloads/generated/specint-build-502-wrapv-20260702-r1/build_manifest.json`
  rebuilt 502 with default flags plus only `-fwrapv`. This single flag also
  suppressed the immediate internal error through the 240 second cap:
  `workloads/generated/specint-502-wrapv-20260702-r1/stage_b_summary.json`
  classified as `live-timeout`, count `32000000001`, last BPC `0x15556b207c`,
  no trap, no panic, and no fail marker.

Interpretation: `-fwrapv` is the narrowest tested build flag that changes the
default 502 failure class. This points at signed-overflow-sensitive behavior in
the Linx-built `cpugcc_r` binary or in Linx LLVM's lowering of code that relies
on wrapped signed arithmetic. It is still only a localization probe because the
row has not produced strict-hash-validated assembly output. After the probe,
502 was restored again to default flags; restore evidence is
`workloads/generated/specint-build-502-default-restore-after-wrapv-20260702-r1/build_manifest.json`.

Focused `502.gcc_r` mixed-object `-fwrapv` localization:

- `tools/spec2017/probe_502_mixed_flags.py` stages probe binaries that rebuild
  only selected 502 objects with extra flags, relink one `cpugcc_r` variant,
  leave that variant staged for the existing QEMU runner, and restore the build
  directory objects. The `restore` subcommand puts the default staged executable
  back after a QEMU run.
- `workloads/generated/specint-502-mixed-tree-into-ssa-wrapv-20260702-r1/`
  rebuilt only `tree-into-ssa.o` with `-fwrapv`. The row still reproduced the
  benchmark internal error at `tree-into-ssa.c:942`, but later than default:
  `stage_b_summary.json` records `spec-benchmark-internal-error`, count
  `22000000001`, last BPC `0xffffffff80049b3e`.
- `workloads/generated/specint-502-mixed-tree-all-wrapv-20260702-r1/` rebuilt
  all 78 `tree-*.o` objects with `-fwrapv`. The row became `live-timeout` under
  the 240 second cap, count `30000000004`, last BPC `0x1555941302`, with no
  trap, panic, or fail marker.
- `workloads/generated/specint-502-mixed-tree-changed7-wrapv-20260702-r1/`
  rebuilt only the seven `tree-*.o` objects whose object bytes changed under
  `-fwrapv`: `tree-data-ref.o`, `tree-dump.o`, `tree-inline.o`,
  `tree-into-ssa.o`, `tree-pretty-print.o`, `tree-ssa-pre.o`, and
  `tree-ssa-reassoc.o`. Its variant executable hash exactly matches the
  78-object `tree-*.o` variant, so unchanged `tree-*.o` objects are not needed
  to reproduce the suppression.
- `workloads/generated/specint-502-mixed-tree-changed6-no-into-ssa-wrapv-20260702-r1/`
  rebuilt those seven objects except `tree-into-ssa.o`. This did not preserve
  the live-timeout behavior: it classified as `user-trap` at `addr=0x8`, user
  `tpc=0x1555f17fea`, user `bpc=0x1555f17fe2`, count `24000000000`.
- `workloads/generated/specint-502-mixed-tree-into-plus-a3-wrapv-20260702-r1/`
  rebuilt `tree-into-ssa.o`, `tree-data-ref.o`, `tree-dump.o`, and
  `tree-inline.o` with `-fwrapv`. This four-object probe reached `live-timeout`
  under the 240 second cap, count `29000000003`, last BPC `0x1555ec8734`, with
  no trap, panic, or fail marker.
- `workloads/generated/specint-502-mixed-tree-minus-inline-wrapv-20260702-r1/`
  rebuilt `tree-into-ssa.o`, `tree-data-ref.o`, and `tree-dump.o` with
  `-fwrapv`. This also reached `live-timeout`, count `32000000001`, last BPC
  `0x1555cbeebc`, with no trap, panic, or fail marker.
- `workloads/generated/specint-502-mixed-tree-into-dataref-wrapv-20260702-r1/`
  rebuilt only `tree-into-ssa.o` and `tree-data-ref.o` with `-fwrapv`. This
  two-object pair reached `live-timeout`, count `30000000001`, last BPC
  `0x1555fb1c0c`, with no trap, panic, or fail marker.
- `workloads/generated/specint-502-mixed-tree-dataref-only-wrapv-20260702-r1/`
  rebuilt only `tree-data-ref.o` with `-fwrapv`. The row still reproduced the
  same benchmark internal error at `tree-into-ssa.c:942`, count `23000000004`,
  last BPC `0xffffffff80049b02`. Combined with the earlier `tree-into-ssa.o`
  only failure, this makes `tree-into-ssa.o + tree-data-ref.o` the current
  minimal sufficient pair under this probe set.
- `workloads/generated/specint-502-mixed-tree-into-dataref-wrapv-20260702-r2/`
  reran the pair staging after the helper was extended to preserve mixed
  objects under `variant/mixed-objects/`; its variant hash
  `71a98b2f0fb16339656b1919e020bbe499a42545a18440bd872ebfbc99de9638`
  matches the QEMU-tested pair. Disassembly and symbol-size deltas are under
  `asm-diff/`. `tree-into-ssa.o` changes only `compute_global_livein` size
  (`444 -> 450` bytes); `tree-data-ref.o` changes only inline `omega.h`
  helpers `omega_copy_eqn` (`106 -> 112`) and `omega_init_eqn_zero`
  (`72 -> 80`).
- The helper's `summarize` subcommand now regenerates that object evidence from
  the preserved staged objects. The pair summary reports six disassembly hunks
  in `tree-into-ssa.o` and thirty-seven in `tree-data-ref.o`; generated IR
  diffs for the same sources show `-fwrapv` removes `nsw` from signed integer
  adds, including the `compute_global_livein` `last_basic_block + 1` allocation
  size and the inline omega `(s + 1) * sizeof(int)` `memcpy`/`memset` lengths.
- `tools/spec2017/build_int_rate_linx.sh` now supports an opt-in
  `--bench-optimize 502.gcc_r='<flags>'` profile and records the effective
  per-benchmark flags in the build manifest. Using this path,
  `workloads/generated/specint-build-502-benchopt-wrapv-20260702-r1/build_manifest.json`
  built only `502.gcc_r` with `-O0 -fno-vectorize -fno-slp-vectorize -fwrapv`.
  The fwrapv-built test row 1 passed strict output/specdiff under
  `workloads/generated/specint-502-benchopt-wrapv-test-hb-20260702-r1/stage_b_summary.json`
  with `LINX_SPEC_PASS`, no trap, and no panic. The fwrapv-built train row 1
  still timed out under the 180 second cap, but it is now explicitly
  heartbeat-backed live progress:
  `workloads/generated/specint-502-benchopt-wrapv-train-hb-20260702-r1/stage_b_summary.json`
  reports `live-timeout`, last count `25000000005`, BPC `0x1555941412`,
  recent count delta `6999999998`, eight recent unique sites, and no
  trap/panic/fail/internal-error marker.

Interpretation: the whole-benchmark `-fwrapv` effect is now localized to a
minimal 502 object pair. `tree-into-ssa.o` alone and `tree-data-ref.o` alone
both still fail with the same internal error; together they convert the row to
heartbeat-backed `live-timeout` under the same cap. The next compiler loop
should inspect the changed `compute_global_livein` and inline omega helper
codegen, especially whether Linx lowering is respecting the signed-overflow
contract difference between plain signed adds and `nsw`, before changing QEMU,
Linux, or libc. After every probe above, the default 502 executable was restored to digest
`6c5535276d410b82bf0f0bb12213302e742411d2dd679737ef482a974c69386b`.
The latest restore evidence is
`workloads/generated/specint-build-502-default-restore-after-benchopt-20260702-r1/build_manifest.json`.

The same profile was then applied to the full train diagnostic matrix:
`workloads/generated/specint-build-all-502-benchopt-wrapv-20260702-r1/build_manifest.json`
records all ten supported SPECint C/C++ benchmarks built, with only
`502.gcc_r` using `-fwrapv`. The split all-train run under
`workloads/generated/specint-train-all-502-benchopt-wrapv-20260702-r1/specint_fast_gate_summary.json`
is still strict-red, but it covers every train benchmark row with BPC
heartbeat evidence. `500.perlbench_r`, `502.gcc_r`, `505.mcf_r`,
`520.omnetpp_r`, `523.xalancbmk_r`, `531.deepsjeng_r`, and `541.leela_r`
classify as heartbeat-backed `live-timeout`; the large 9p shard
`525.x264_r` also classifies as `live-timeout` with BPC `0xffffffff801119ac`.
`999.specrand_ir` is not in the failure map for this run. The signed-wrap
profile moves `502.gcc_r` from the default all-train `spec-wrapper-fail` class
to `live-timeout`, with count `24000000010` and BPC `0x1555990338`. The one
remaining non-timeout train row is `557.xz_r`: at 2 GiB guest memory it exits
with SPEC stderr `spec_mem_init: Error mallocing 267386880 bytes...`, while
focused 2 GiB and 3 GiB reruns do not reproduce the child exit. The focused
2 GiB rerun
`workloads/generated/specint-557-mem2g-class-20260702-r1/stage_b_summary.json`
reaches `live-timeout`, count `35000000000`, BPC `0x155558d71c`; the focused
3 GiB rerun
`workloads/generated/specint-557-mem3g-train-20260702-r1/stage_b_summary.json`
reaches `live-timeout`, count `36000000000`, BPC `0x155558d700`, no
trap/panic, and no fail marker. The all-train 557 memory exit is therefore
run-shape sensitive rather than a simple guest-memory threshold. The default
502 executable was restored again
in `workloads/generated/specint-build-502-default-restore-after-all-benchopt-20260702-r1/build_manifest.json`.

`525.x264_r` note: this long train run used the pre-fail-fast generated 9p
command and therefore ran all four generated x264 train invocations after the
first timeout. The fast gate now auto-enables `--fail-9p-timeout` for generated
`*-large-9p` shards unless the caller explicitly overrides `--transports`, so
future all-train gates stop this shard on the first heartbeat-backed timeout.

## Post-Linux-smoke all-train rerun

Artifact root:

- `workloads/generated/specint-train-all-post-linux-smoke-20260702-r1`

Version context:

- Root at run: `1512b3be04d1bee003452125f68857acebb165f1`
- LLVM: `e4771587a947`
- QEMU: `5cfb672a711b`, `QEMU emulator version 10.2.50 (v10.2.0-989-g5cfb672a711)`
- Kernel: `e804a94929b9`, `kernel/linux/build-linx-fixed/vmlinux`
- Musl: `4ab3c65fc332`
- Sysroot: `out/libc/musl/install/phase-b`

Linux gate sanity before SPEC:

```bash
OUT_DIR=/tmp/linx-initramfs-Oz-current-88527 \
  bash kernel/linux/tools/linxisa/initramfs/build.sh

TIMEOUT=120 \
QEMU=/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64 \
QEMU_EXTRA_ARGS='-bios none' \
python3 kernel/linux/tools/linxisa/initramfs/smoke.py

TIMEOUT=180 \
QEMU=/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64 \
QEMU_EXTRA_ARGS='-bios none' \
python3 kernel/linux/tools/linxisa/initramfs/full_boot.py
```

Both standard wrappers passed after rebuilding the initramfs from the current
compiler. The prior `SKIP_BUILD=1` smoke failure was a stale BusyBox artifact:
fresh `write_uhex` disassembly has `cmp.ltui a0, 10, ->a0` followed by
`csel a0, a1, a2, ->a0`, matching the intended digit/letter source order.
The smoke log reached the `/proc` and `/sys` directory checks, `fd` checks,
`sigill: ok`, `sigsegv: ok`, and `poweroff`. Full boot also listed `/proc`
and `/sys`, probed `/proc/cpuinfo`, `/proc/meminfo`, and
`/proc/interrupts`, then powered off cleanly. Treat future `SKIP_BUILD=1`
Linux smoke failures as non-authoritative until the initramfs payload is
rebuilt or its codegen provenance is checked.

All-train command:

```bash
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --out-dir workloads/generated/specint-train-all-post-linux-smoke-20260702-r1 \
  --qemu /Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64 \
  --qemu-heartbeat-interval 1000000000 \
  --qemu-heartbeat-same-site-warn 4 \
  --no-progress-timeout 180 \
  --stack-limit 2G \
  --continue-on-fail
```

Machine-readable summaries:

- `workloads/generated/specint-train-all-post-linux-smoke-20260702-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-post-linux-smoke-20260702-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-post-linux-smoke-20260702-r1/train-all-large-9p/qemu_matrix_summary.json`

Result ledger:

| Bench | Transport | Result | Liveness / failure evidence |
|---|---|---|---|
| `500.perlbench_r` | initramfs | `live-timeout` | BPC site progress through count `39000000001`, last BPC `0x15556d9704` |
| `502.gcc_r` | initramfs | `live-timeout` | BPC site progress, timeout summary BPC `0xffffffff80049b2a`; keep the signed-wrap/codegen lane from the focused 502 probes |
| `505.mcf_r` | initramfs | `live-timeout` | BPC site progress, last BPC `0x155555cc06` |
| `520.omnetpp_r` | initramfs | `live-timeout` | BPC site progress, last BPC `0x15555f1144` |
| `523.xalancbmk_r` | initramfs | `user-trap` | child SIGSEGV at `addr=0`, `tpc=0x15559efe26`, `bpc=0x15559efe1a` |
| `525.x264_r` | 9p | `live-timeout` | large-payload shard fail-fast timeout, site-progress BPC `0xffffffff8011232a` |
| `531.deepsjeng_r` | initramfs | `live-timeout` | BPC site progress, last BPC `0x155555fac8` |
| `541.leela_r` | initramfs | `live-timeout` | BPC site progress, last BPC `0x1555570b34`; oldmalloc/mallocng split remains the focused allocator lane |
| `557.xz_r` | initramfs | `live-timeout` | BPC site progress, last BPC `0x155558cd50`; no repeat of the earlier all-train `spec_mem_init` exit |
| `999.specrand_ir` | initramfs | pass | no failure entry in the strict summary |

The refreshed all-train run supersedes the earlier `557.xz_r`
`spec_mem_init` all-row symptom for the current payload and wrapper state:
`557` now joins the live-timeout throughput group. The BPC heartbeat switch
also confirms that the live-timeout rows are running with site changes rather
than sitting in a same-site deadlock.

Focused `523.xalancbmk_r` trap classification:

- QEMU log:
  `workloads/generated/specint-train-all-post-linux-smoke-20260702-r1/train-all/initramfs/523_xalancbmk_r/run_001/qemu.log`
- Effective argv: `./cpuxalan_r_base.mytest-m64 -v allbooks.xml xalanc.xsl`
- Pre-exec probes show the target binary exists and has ELF magic.
- Runtime trap: `signo=0xb`, `code=0x1`, `addr=0x0`,
  `tpc=0x15559efe26`, `bpc=0x15559efe1a`, `ra=0x15559efcba`.
- With ET_DYN load bias `0x1515555000`, the trap maps to file addresses
  `0x4049ae1a`, `0x4049ae26`, and `0x4049acba`. `llvm-addr2line` maps these
  to musl `rcrt1.c:0`, labels `.LBB0_29` and `.Ltmp0`.
- Disassembly at the trap window:
  `ldi [a4, -16], ->t; add t#1, a0, ->u; ldi [a4, 0], ->t; add t#1, a0, ->t; sdi t#1, [u#1, 0]`.

Interpretation: `523.xalancbmk_r` is now a distinct startup-relocation
correctness lane for a large C++ static PIE. The faulting store uses a null
relocation destination inside musl `rcrt1.c` startup processing, so the next
owner is compiler/libc relocation table generation or runtime startup logic,
not QEMU throughput. Add fault-register and relocation-table probes around the
startup loop before changing generic QEMU execution.

Loop update:

1. Keep Linux smoke/full boot ahead of SPEC when QEMU or compiler artifacts
   have been rebuilt. If `SKIP_BUILD=1` is used, verify the initramfs binary
   disassembly before assigning ISA/QEMU semantics.
2. Split current SPEC work into two queues: `523.xalancbmk_r` startup
   relocation correctness, and all other failing rows as QEMU throughput/live
   progress unless a fresh trap/internal-error marker appears.
3. For throughput rows, profile after `LINX_SPEC_START` with heartbeat disabled
   or coarse enough to avoid dominating the sample. The prior profiles still
   point at `helper_linx_template_step`, `helper_linx_check_bstart_target`,
   `probe_access_flags` / `mmu_lookup`, and trace hook frames.
4. Proposed QEMU speed fixes remain: cache BSTART legality per TB or code
   page, add counters for template/BSTART/MMU-probe/trace-helper calls at exit,
   fast-path `helper_linx_template_step` when tracing/templates are inactive,
   and keep all verbose PC/fault/memory traces opt-in.
5. Keep `525.x264_r` in the generated large 9p shard. Its current 9p timeout
   is live progress, while oversized initramfs panics are transport artifacts.

## Tool fixes in this loop

- Fixed the GCC test input verifier to compare the generated `.s` output instead of a nonexistent `.out`.
- Added an opt-in printf self-test to the SPEC init wrapper for ABI debug.
- Fixed a false-red path where exact strict host hashes were overwritten by host `specdiff` rc=2. The train `500.perlbench_r` run artifact predates this fix, so its JSON still shows `specdiff-mismatch` even though every output hash matches.
- Added guest heartbeat process/memory sampling for initramfs child runs: `/proc/$pid/status`, `/proc/meminfo`, `/proc/vmstat`, and optional `/proc/pressure/memory`.
- Split child SIGKILL/SIGSEGV rows into explicit JSON failure classes (`spec-child-sigkill`, `spec-child-sigsegv`) instead of generic `spec-wrapper-fail`.
- Split SIGKILL plus observed guest `oom_kill` into `spec-child-sigkill-oom`.
- Added runner/matrix switches for QEMU's existing fault-register tracing:
  `--qemu-fault-trace-regs` and `--qemu-fault-trace-limit`.
- Added runner/matrix pass-through for focused QEMU fault-trace filters:
  `--qemu-fault-trace`, `--qemu-fault-trace-pc[-lo|-hi]`,
  `--qemu-fault-trace-addr[-lo|-hi]`, `--qemu-fault-trace-count[-lo|-hi]`,
  and `--qemu-fault-trace-trapnum`.
- Classified SPEC benchmark stderr internal-error blocks as
  `spec-benchmark-internal-error`, including CR-normalized QEMU log marker
  blocks such as the current `502.gcc_r` train failure.
- Added `tools/spec2017/probe_502_mixed_flags.py` to stage and restore
  selected-object 502 probe binaries without modifying SPEC sources. The helper
  now also preserves the mixed object files under each generated variant
  directory and can summarize staged baseline-vs-variant object disassembly plus
  symbol-size deltas with the `summarize` subcommand.
- Added per-benchmark `--bench-optimize bench=flags` support to
  `tools/spec2017/build_int_rate_linx.sh` and surfaced the effective flags in
  build manifests. This lets the gate run a named 502 signed-wrap profile
  without changing the global SPEC build policy or silently leaving the default
  executable in place.
- Streamed `run_stage_qemu_matrix.py` child-runner output directly into the
  stage log instead of buffering the entire child stdout and writing it at the
  end. The first all-train rerun hit host `ENOSPC` while writing
  `stage_b_initramfs.log`; the streamed log path completed the rerun and keeps
  parent memory/log pressure bounded.
- Classified SPEC stderr `spec_mem_init: Error mallocing...` child exits as
  `spec-mem-init-fail` instead of generic `spec-wrapper-fail`, preserving the
  malloc size plus wait status in failure evidence.
- Split large-payload SPEC rows in `run_specint_fast_gate.py`: by default the
  all-row suites keep `525.x264_r` but run it as `test-all-large-9p` /
  `train-all-large-9p`, while explicit `--transports` still forces a single
  transport for focused bisection.
- Added generated large-9p fail-fast policy so `525.x264_r` train/test shards
  do not spend a full gate running every generated row after the first 9p
  timeout.
- Added effective-argv evidence to SPEC init wrappers and per-run JSON:
  generated QEMU logs now emit `LINX_SPEC_ARGV_BEGIN/END` with indexed argv
  values, and each run records both `configured_argv` and `effective_argv`.
  This makes `LINX_SPEC_ARGV<n>_OVERRIDE` focused probes self-describing after
  the fact, including the `502.gcc_r` flag-override/debug lane.

## Profile observations

Profiles:

- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/profiles/qemu-train-active.sample.txt`
- `workloads/generated/specint-test-train-all-after-blockify-20260702-r2/profiles/qemu-train-520-active.sample.txt`
- `workloads/generated/specint-train-split-post-perlbench-20260702-r1/profiles/qemu-531-active.sample.txt`

Hot paths seen in both profiles:

- `helper_linx_template_step`
- `helper_linx_check_bstart_target`
- `probe_access_flags` and `mmu_lookup` under BSTART legality checks
- `linx_trace_wb` and `linx_call_trace_emit`, even in non-trace SPEC runs

The latest `531.deepsjeng_r` sample still shows the same throughput owners:
`helper_linx_template_step` around 313 samples, `probe_access_internal` around
291, `helper_linx_check_bstart_target` around 188, `mmu_lookup1` around 178,
`helper_linx_tile_set_attr` around 146, plus visible `linx_trace_wb`,
`helper_lookup_tb_ptr`, and `linx_call_trace_emit` frames. The next speed loop
should focus on reducing template-step and BSTART/probe/MMU helper cost before
raising SPEC train timeouts.

## Proposed next loops

1. QEMU speed: cache BSTART legality per TB or per guest code page and avoid repeated helper-side `probe_access_flags` for the same target. This is the hottest repeated path in both profiles.
2. QEMU speed: split `helper_linx_template_step` into fast paths for common non-template/non-trace execution and keep trace hooks fully disabled unless an explicit trace switch is set.
3. QEMU debug: add an exit counter summary with TB count, dynamic instruction count, BSTART checks, BSTART cache hits/misses, template helper calls, MMU probes, trace hook calls, heartbeat stall count, and last BPC.
4. SPEC gate: classify `live-timeout` as a performance failure distinct from correctness failures. Keep the correctness gate on hash-matching rows, and run timeout rows in a separate throughput budget.
5. `525.x264_r`: the fast gate now splits x264 to 9p by default. Treat both
   test and train focused 9p runs as `live-timeout` throughput rows; use
   initramfs only to reproduce the oversized-cpio panic.
6. `502.gcc_r`: treat train as a compiler/codegen bug first. The default
   binary exits with code 4 and reports a benchmark internal compiler error at
   `tree-into-ssa.c:942`. A conservative rebuild suppresses that internal error
   for at least 600 seconds but only reaches `live-timeout`; follow-up bisection
   narrowed the first suppressing flag to `-fwrapv`, then mixed-object probes
   narrowed the sufficient set to the pair `tree-into-ssa.o` and
   `tree-data-ref.o`. The next loop is to compare generated Linx assembly/IR
   for `compute_global_livein` and the inline omega helpers, then decide whether
   the wrong behavior is source UB exposure or Linx codegen/ABI lowering. This
   is not yet a correctness fix.
7. SIGKILL rows are now split by evidence. `541.leela_r` is real guest OOM at
   2 GiB, but at 4 GiB the old user trap was compiler-rt atomic recursion and
   is now fixed. The next `541` blocker is mallocng-specific so far: the fixed
   mallocng binary has hit both `get_meta` `assert(area->check == ctx.secret)`
   and `queue()` `assert(!m->next)`, while the oldmalloc relink stays live
   through 1200 seconds with no trap or OOM. Keep mallocng as the maintained
   default, but use `MALLOC_IMPL=oldmalloc` as a bisection lane before changing
   QEMU/compiler/libc for allocator metadata traps. Prior `520` did not
   reproduce SIGKILL and showed `oom_kill 0`; keep it in live-timeout/
   performance triage unless a fresh run proves otherwise. `523.xalancbmk_r` is
   unstable between user-trap and live-timeout; rerun with fault trace filters
   around the user BPC if the trap reproduces.
8. `557.xz_r`: the current rebuilt train binary is run-shape sensitive. The
   all-train profile saw a SPEC `spec_mem_init` allocation failure for
   267386880 bytes, but focused 2 GiB and 3 GiB reruns both become
   heartbeat-backed `live-timeout`. Keep the new `spec-mem-init-fail`
   classifier because the failure is actionable when it appears, but do not
   treat the all-train row as a deterministic memory-size threshold until a
   focused repro exists.
9. `500.perlbench_r` test run 2: investigate as a user-space corruption/debug lane separately from train. Linux VM trace shows the terminal row-2 failure is a real user trap, not deadlock: `S_unshare_hek_or_pvn` faults at `addr=0x10` after the same PC/BPC handles mapped HEK refcount stores, and a narrower rerun failed earlier in `Perl_do_exec3` through a zero jump-table pointer. Keep the next loop on low-overhead call/queue-state tracing around those two sites before changing Linux or Perl source.
10. All other train failures in the current split run are heartbeat-backed
   live-timeouts, not deadlocks. Keep correctness work on the explicit
   internal-error/trap rows and run live-timeout rows through the QEMU
   throughput profile loop.

## Verification

- `PYTHONPATH=tools/spec2017 python3 -m unittest -q tools.spec2017.test_run_int_rate_qemu tools.spec2017.test_run_stage_qemu_matrix`
- `git diff --check -- tools/spec2017/run_int_rate_qemu.py tools/spec2017/test_run_int_rate_qemu.py`
- `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py tools/spec2017/test_run_int_rate_qemu.py`
- `PYTHONPATH=tools/spec2017 python3 -m unittest tools.spec2017.test_run_int_rate_qemu`
- Focused current-code repro:
  `workloads/generated/specint-502-internal-error-class-20260702-r3/qemu_matrix_summary.json`
- `python3 -m py_compile run_int_rate_qemu.py test_run_int_rate_qemu.py` from `tools/spec2017`
- `python3 -m unittest test_run_int_rate_qemu.py` from `tools/spec2017`
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 520.omnetpp_r --input-set test --transports initramfs --guest-heartbeat-sec 10 --timeout 240` (expected red, classified `live-timeout`)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 999.specrand_ir --input-set test --transports initramfs --guest-heartbeat-sec 10 --timeout 180` (passed)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 523.xalancbmk_r --bench 541.leela_r --input-set test --transports initramfs --guest-heartbeat-sec 10 --timeout 240` (expected red, classified `523` as `user-trap`, `541` as SIGKILL before OOM classifier)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 523.xalancbmk_r --input-set test --transports initramfs --guest-heartbeat-sec 10 --qemu-fault-trace-regs --timeout 180` (expected red, verified QEMU fault-reg switch; rerun classified `live-timeout`)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --input-set test --transports initramfs --guest-heartbeat-sec 10 --timeout 240` (expected red, classified `spec-child-sigkill-oom`)
- `MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh` (passed after Linx compiler-rt atomic fallback)
- `bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-b` (passed, restored C++ overlay)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 541.leela_r --emit-manifest workloads/generated/specint-build-541-atomicfix-20260702-r1/build_manifest.json` (passed)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --timeout 420` (expected red, old `__atomic_load_1` user trap closed; classified `live-timeout` with heartbeat progress)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --timeout 1200` (expected red, old atomic recursion still closed; later mallocng `get_meta` assertion traps at `addr=0`)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --qemu-fault-trace-regs --qemu-fault-trace-addr 0 --qemu-fault-trace-pc-lo 0x1555615580 --qemu-fault-trace-pc-hi 0x15556155b0 --timeout 300` (expected red; mallocng trap did not reproduce, classified `live-timeout`)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --qemu-fault-trace-regs --qemu-fault-trace-addr 0 --timeout 900` (expected red; captured mallocng `queue()` assert at `0x1555616858`)
- `MALLOC_IMPL=oldmalloc MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh` (passed; allocator bisection sysroot)
- `bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-b` (passed after oldmalloc sysroot refresh)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 541.leela_r --emit-manifest workloads/generated/specint-build-541-oldmalloc-20260702-r1/build_manifest.json` (passed; oldmalloc-linked `541`)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --timeout 420` against the oldmalloc-linked binary (expected red; `live-timeout`, no trap/panic/OOM)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 541.leela_r --memory-mb 4096 --stack-limit 2G --timeout 1200` against the oldmalloc-linked binary (expected red; `live-timeout`, count `133000000000`, no trap/panic/OOM)
- `skill-evolve: update linx-compiler (record compiler-rt/C11 atomic recursion triage and fallback verification)`
- `skill-evolve: update linx-lib (record oldmalloc bisection for mallocng metadata traps)`
- `python3 -m unittest tools.bringup.test_run_specint_fast_gate` (passed)
- `python3 -m py_compile tools/bringup/run_specint_fast_gate.py tools/bringup/test_run_specint_fast_gate.py` (passed)
- `python3 tools/bringup/run_specint_fast_gate.py --profile test-train --dry-run ...` (passed; generated `test-all-large-9p` and `train-all-large-9p` x264 shards)
- `python3 tools/spec2017/run_stage_qemu_matrix.py ... --bench 525.x264_r --input-set train --transports 9p --memory-mb 4096 --stack-limit 2G --timeout 480 --fail-9p-timeout` (expected red; `live-timeout`, no trap/panic/mount failure)
- `LINX_SPEC_ARGV2_OVERRIDE=10 python3 tools/spec2017/run_int_rate_qemu.py ... --bench 999.specrand_ir --input-set test --transport initramfs --run-index 1 --no-strict-hash` (passed; `workloads/generated/specint-argv-log-smoke-20260702-r1/stage_b_summary.json` records configured argv count `24239`, effective argv count `10`, and the QEMU log emits matching `LINX_SPEC_ARGV` lines)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set train --transport initramfs --run-index 1` on the default binary (expected red; `workloads/generated/specint-502-current-argv-20260702-r1/stage_b_summary.json`, classified `spec-benchmark-internal-error` with argv evidence)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize -fno-inline -fno-optimize-sibling-calls -fno-strict-aliasing -fwrapv -fno-jump-tables' --emit-manifest workloads/generated/specint-build-502-conservative-20260702-r1/build_manifest.json` (passed)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set train --transport initramfs --run-index 1 --timeout 240` against the conservative binary (expected red; `live-timeout`, no internal error/trap/panic)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set train --transport initramfs --run-index 1 --timeout 600` against the conservative binary (expected red; `live-timeout`, count `91000000002`, no internal error/trap/panic)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize' --emit-manifest workloads/generated/specint-build-502-default-restore-20260702-r1/build_manifest.json` (passed; restored the default 502 binary after the conservative probe)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize -fno-jump-tables' --emit-manifest workloads/generated/specint-build-502-no-jumptables-20260702-r1/build_manifest.json` (passed; focused probe still reproduced `tree-into-ssa.c:942`)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize -fno-inline' --emit-manifest workloads/generated/specint-build-502-no-inline-20260702-r1/build_manifest.json` (passed; focused probe still reproduced `tree-into-ssa.c:942`)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize -fno-optimize-sibling-calls -fno-strict-aliasing -fwrapv' --emit-manifest workloads/generated/specint-build-502-semantic-flags-20260702-r1/build_manifest.json` (passed; QEMU row became `live-timeout`)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize -fwrapv' --emit-manifest workloads/generated/specint-build-502-wrapv-20260702-r1/build_manifest.json` (passed; `-fwrapv` alone made the row `live-timeout`, count `32000000001`)
- `bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --optimize '-O0 -fno-vectorize -fno-slp-vectorize' --emit-manifest workloads/generated/specint-build-502-default-restore-after-wrapv-20260702-r1/build_manifest.json` (passed; restored the default 502 binary after the flag bisection)
- `python3 -m py_compile tools/spec2017/probe_502_mixed_flags.py` (passed)
- `python3 tools/spec2017/probe_502_mixed_flags.py list` (passed; enumerated 502 source/object map)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-into-ssa-wrapv-20260702-r1 --objects tree-into-ssa.o --jobs 10 --force` plus `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set train --transport initramfs --run-index 1 --timeout 240` (expected red; same internal error later, count `22000000001`)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-all-wrapv-20260702-r1 --objects '<all tree-*.o>' --jobs 10 --force` plus the same QEMU row (expected red; `live-timeout`, count `30000000004`, no internal error/trap/panic)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-changed7-wrapv-20260702-r1 --objects 'tree-data-ref.o tree-dump.o tree-inline.o tree-into-ssa.o tree-pretty-print.o tree-ssa-pre.o tree-ssa-reassoc.o' --jobs 10 --force` (passed; variant hash matches the all-`tree-*.o` probe)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-changed6-no-into-ssa-wrapv-20260702-r1 --objects 'tree-data-ref.o tree-dump.o tree-inline.o tree-pretty-print.o tree-ssa-pre.o tree-ssa-reassoc.o' --jobs 10 --force` plus the same QEMU row (expected red; classified `user-trap` at `addr=0x8`)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-into-plus-a3-wrapv-20260702-r1 --objects 'tree-into-ssa.o tree-data-ref.o tree-dump.o tree-inline.o' --jobs 10 --force` plus the same QEMU row (expected red; `live-timeout`, count `29000000003`, no internal error/trap/panic)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-minus-inline-wrapv-20260702-r1 --objects 'tree-into-ssa.o tree-data-ref.o tree-dump.o' --jobs 10 --force` plus the same QEMU row (expected red; `live-timeout`, count `32000000001`, no internal error/trap/panic)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-into-dataref-wrapv-20260702-r1 --objects 'tree-into-ssa.o tree-data-ref.o' --jobs 10 --force` plus the same QEMU row (expected red; `live-timeout`, count `30000000001`, no internal error/trap/panic)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-dataref-only-wrapv-20260702-r1 --objects 'tree-data-ref.o' --jobs 10 --force` plus the same QEMU row (expected red; same internal error at `tree-into-ssa.c:942`, count `23000000004`)
- `python3 tools/spec2017/probe_502_mixed_flags.py stage --out-dir workloads/generated/specint-502-mixed-tree-into-dataref-wrapv-20260702-r2 --objects 'tree-into-ssa.o tree-data-ref.o' --jobs 10 --force` (passed; preserves mixed `.o` files and reproduces the QEMU-tested pair variant hash)
- `compiler/llvm/build-linxisa-clang/bin/llvm-objdump -dr --no-show-raw-insn ...` on the pair baseline/mixed objects (generated `workloads/generated/specint-502-mixed-tree-into-dataref-wrapv-20260702-r2/asm-diff/*.diff.txt`)
- `compiler/llvm/build-linxisa-clang/bin/llvm-nm -S --size-sort ...` on the pair baseline/mixed objects (generated `asm-diff/*.symbol-size-delta.tsv`)
- `python3 tools/spec2017/probe_502_mixed_flags.py restore --out-dir <each mixed-object probe dir>` (passed; final default staged/build executable digest `6c5535276d410b82bf0f0bb12213302e742411d2dd679737ef482a974c69386b`)
- `bash -n tools/spec2017/build_int_rate_linx.sh` (passed)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --bench-optimize '502.gcc_r=-O0 -fno-vectorize -fno-slp-vectorize -fwrapv' --emit-manifest workloads/generated/specint-build-502-benchopt-wrapv-20260702-r1/build_manifest.json` (passed; manifest records 502-specific flags)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set test --run-index 1 --qemu-heartbeat-interval 1000000000 --timeout 180` against the fwrapv-built binary (passed; `LINX_SPEC_PASS`, specdiff OK)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 502.gcc_r --input-set train --run-index 1 --qemu-heartbeat-interval 1000000000 --timeout 180` against the fwrapv-built binary (expected red; `live-timeout`, count `25000000005`, BPC `0x1555941412`, no internal error/trap/panic)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --emit-manifest workloads/generated/specint-build-502-default-restore-after-benchopt-20260702-r1/build_manifest.json` (passed; restored default staged/build executable digest `6c5535276d410b82bf0f0bb12213302e742411d2dd679737ef482a974c69386b`)
- `python3 -m py_compile tools/spec2017/run_stage_qemu_matrix.py tools/bringup/run_specint_fast_gate.py tools/spec2017/run_int_rate_qemu.py` (passed)
- `python3 -m unittest test_run_int_rate_qemu.py test_run_stage_qemu_matrix.py` from `tools/spec2017` (passed)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench-optimize '502.gcc_r=-O0 -fno-vectorize -fno-slp-vectorize -fwrapv' --emit-manifest workloads/generated/specint-build-all-502-benchopt-wrapv-20260702-r1/build_manifest.json` (passed; all ten benchmarks built, only 502 used non-global flags)
- `SPECINT_TRAIN_ALL_TIMEOUT=180 python3 tools/bringup/run_specint_fast_gate.py --profile train --suite train-all --qemu-heartbeat-interval 1000000000 --qemu-heartbeat-same-site-warn 4 --stack-limit 2G --continue-on-fail --out-dir workloads/generated/specint-train-all-502-benchopt-wrapv-20260702-r1` (expected red; all train rows covered, 502 becomes `live-timeout`, 557 is `spec-mem-init-fail` at 2 GiB, 525 9p is `live-timeout`)
- `LINX_SPEC_LINK_MODE=default bash tools/spec2017/build_int_rate_linx.sh --mode phase-b --force-static --bench 502.gcc_r --emit-manifest workloads/generated/specint-build-502-default-restore-after-all-benchopt-20260702-r1/build_manifest.json` (passed; restored default 502 after all-train profile)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 557.xz_r --input-set train --run-index 1 --memory-mb 3072 --qemu-heartbeat-interval 1000000000 --timeout 180` (expected red; focused 3 GiB `live-timeout`, count `36000000000`, BPC `0x155558d700`)
- `python3 tools/spec2017/run_int_rate_qemu.py ... --bench 557.xz_r --input-set train --run-index 1 --memory-mb 2048 --qemu-heartbeat-interval 1000000000 --timeout 180` (expected red; focused 2 GiB did not reproduce the all-train `spec_mem_init` exit, `live-timeout`, count `35000000000`, BPC `0x155558d71c`)
- `skill-evolve: update linx-superproject (record large SPEC payload transport split)`
