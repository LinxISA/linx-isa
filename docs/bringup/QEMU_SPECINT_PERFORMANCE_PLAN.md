# QEMU SPECint Performance Plan

This note records the fast SPECint gate shape and the first QEMU profile taken
from that gate. Treat generated profiler output as evidence and this document as
the current optimization plan.

## Fast Gate Shape

Use `tools/bringup/run_specint_fast_gate.py` instead of launching full refrate
or the broad promotion set directly.

- `smoke`: `test-smoke` only, for quick local sanity.
- `pr`: `test-smoke` and `train-smoke`, both using `999.specrand_ir`.
- `test`: `test-all`, all ten supported SPECint rows on `test` input.
- `train`: `train-all`, all ten supported SPECint rows on `train` input.
- `test-train`: `test-all` followed by `train-all`, for the bounded all-row
  gate before promotion-scale runs.
- `nightly`: PR suites plus `test-cpu-stress`, `test-vm-stress`,
  `train-cpu-stress`, `train-vm-stress`, and train promotion breadth.

The gate uses initramfs by default to avoid 9p overhead while debugging QEMU
and Linux correctness. Use `--transports 9p,initramfs` only when transport
coverage is the point of the run.

For bounded 9p transport coverage, use `run_stage_qemu_matrix.py
--fail-9p-timeout` with train input. That mode treats a per-run 9p timeout as a
fast-gate failure and stops the current benchmark instead of continuing every
train invocation for full host-visible specdiff. The 2026-06-30 all-row 9p run
under `workloads/generated/specint-train-all-9p-failtimeout-20260630-r1/`
covers all ten supported SPECint rows and classifies every row as
heartbeat-backed `live-timeout`; this proves the current 9p suite state is
running, not deadlocked, but it is not a full correctness substitute for the
initramfs strict-hash sentinel or a long 9p specdiff run.

The SPEC 9p runner now appends `linx_storage_init=1` automatically unless the
caller explicitly provides `linx_storage_init=...`. This keeps future 9p gates
from failing before benchmark execution with `9p-mount-failed raw_rc=-19` when a
manual append string omits the Linx storage-init switch. The focused proof is
`workloads/generated/specint-999-9p-storageinit-auto-20260630-r1/`: the command
line contains the automatic bootarg, reaches `LINX_SPEC_START`, emits no 9p
mount warning, and times out with BPC site progress in kernel allocator code
instead of failing `chdir-rundir`.

## Current Train Ledger

The current clean-head QEMU ledger is
`workloads/generated/specint-train-all-latest-qemu-20260704-r2/`. It uses the
clean build `/tmp/linx-qemu-clean-build/qemu-system-linx64` from QEMU head
`1db7e12b6809c8ca2e2bee397f6019a14966e2ad`, version
`QEMU emulator version 10.2.50 (v10.2.0-1017-g1db7e12b680)`. The fast-gate
summary records `qemu_repo_dirty_tracked=false`,
`clean_build_for_head=true`, and `clean_build_marker_matches_head=true`. The
SPEC build manifest for the same ledger is
`workloads/generated/specint-train-all-latest-qemu-20260704-r2/build-manifest.json`;
it rebuilds all selected INT C/C++ phase-B binaries and passes the source
immutability check.

Result shape:

- `999.specrand_ir` passes the strict train hash (`rand.11.out`, 871 bytes,
  `0x973dcfc2`).
- `500.perlbench_r`, `502.gcc_r`, `505.mcf_r`, `520.omnetpp_r`,
  `523.xalancbmk_r`, `525.x264_r`, `531.deepsjeng_r`, `541.leela_r`, and
  `557.xz_r` are heartbeat-backed `live-timeout` rows with BPC site progress,
  no panic, and no trap.
- `525.x264_r` is routed through the generated `train-all-large-9p` shard; the
  current failure is 9p/kernel-path throughput, not the old oversized-initramfs
  VFS panic.
- Final heartbeat counts are `500=58B`, `502=38B`, `505=55B`, `520=28B`,
  `523=34B`, `525=49B`, `531=60B`, `541=32B`, and `557=56B`, with recent
  progress deltas of about `7B` instructions for each red row.

Speed lanes from the current counters:

- Every long row records millions of `tlb.iv` operations. The shared maximum
  per-heartbeat hot burst is `max_delta=458884` at `0xffffffff80405980`
  (`get_p4d_virt_fixmap`), followed by steady invalidations from Linux MM paths
  such as `0xffffffff800db2b6` / BPC `0xffffffff800db2ac` and
  `0xffffffff800daf70` / BPC `0xffffffff800daf62`.
- Frame restore host loads are active and effective in this clean-head ledger:
  every long row has `fr_restore_fallback=0`. The remaining red rows are
  throughput-limited after the restore-load fast path, not blocked on fallback
  restore loads.
- Earlier TLB-fill and TB-stat ledgers still identify `probe_access_internal`,
  template dispatch, and TB lookup as QEMU-side costs. This current ledger says
  the next speed loop should first reduce or batch Linx Linux
  `local_flush_tlb_page()` volume, then rerun the same all-train gate before
  returning to QEMU cputlb changes.

### Post-Linux TLBI Range-Batching Follow-Up

`workloads/generated/specint-train-all-linux-tlbirange-qemu-20260704-r1/`
reruns the same all-train shape after Linux head
`a1bdaf6bce6949e5c0081bf96e76f6c845fafc11` adds range-aware local TLB
flush batching for the SPEC fault/update path. It uses the same clean QEMU
head `1db7e12b6809c8ca2e2bee397f6019a14966e2ad` and clean build marker as the
current train ledger, with `LINX_QEMU_TEMPLATE_CHAIN=1`, frame stats,
restore-host loads, TLBI aggregate counters, and TLBI hot-source attribution.

Result shape:

- `999.specrand_ir` still passes the strict train hash.
- The nine real train workloads remain heartbeat-backed `live-timeout` rows
  with BPC site progress, no panic, and no trap.
- The old large steady `mm/memory.c` hot loop at `0xffffffff800db2b6` moves to
  the new batched path site `0xffffffff800db20c`, but the all-row count change
  is mixed rather than a closure result.
- The early common `tlbi-hot max_delta=458884` burst at
  `0xffffffff80405980` (`get_p4d_virt_fixmap`) remains visible.

Comparison against `specint-train-all-latest-qemu-20260704-r2`:

| Benchmark | Result | Count after Linux batching | Prior count | Delta | BPC | TLBI iv | TLBI iall | Last TLBI PC | Hot source delta |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| `500.perlbench_r` | live-timeout | 59000000003 | 58000000010 | +999999993 | `0x15556d9536` | 3687828 | 565 | `0xffffffff800db20c` | `0xffffffff800db20c` / 77 |
| `502.gcc_r` | live-timeout | 41000000003 | 38000000005 | +2999999998 | `0x155599b182` | 3789138 | 10953 | `0xffffffff800daf1a` | `0xffffffff800db20c` / 2224 |
| `505.mcf_r` | live-timeout | 55000000003 | 55000000002 | +1 | `0x155555c4a4` | 3675648 | 10 | `0xffffffff800db20c` | `0xffffffff8000d8ea` / 0 |
| `520.omnetpp_r` | live-timeout | 28000000000 | 28000000004 | -4 | `0x15555fe9ca` | 3797422 | 7305 | `0xffffffff800db20c` | `0xffffffff800db20c` / 1406 |
| `523.xalancbmk_r` | live-timeout | 33000000002 | 34000000000 | -999999998 | `0x1555699c0e` | 3742538 | 193 | `0xffffffff800db20c` | `0xffffffff800db20c` / 2306 |
| `525.x264_r` | live-timeout | 45000000004 | 49000000001 | -3999999997 | `0xffffffff80108930` | 3670920 | 9 | `0xffffffff800daf1a` | `0xffffffff8000d8ea` / 0 |
| `531.deepsjeng_r` | live-timeout | 60000000005 | 60000000003 | +2 | `0x15555683b2` | 3849676 | 9 | `0xffffffff800db20c` | `0xffffffff8000d8ea` / 0 |
| `541.leela_r` | live-timeout | 31000000001 | 32000000001 | -1000000000 | `0x1555574e08` | 3675299 | 309 | `0xffffffff800daf1a` | `0xffffffff800db20c` / 335 |
| `557.xz_r` | live-timeout | 58000000003 | 56000000009 | +1999999994 | `0x1555576750` | 3861941 | 21 | `0xffffffff800db20c` | `0xffffffff800db20c` / 296 |

Loop update: Linux range batching is correct enough to keep, but it did not
close the SPEC train throughput blocker. The next speed loop should no longer
assume that `update_mmu_cache_range()` alone is the dominant fix. Profile and
attribute the remaining early `get_p4d_virt_fixmap` burst, the
`0xffffffff800daf1a`/`0xffffffff800db20c` `mm/memory.c` fault/update sites,
and the rows with zero current TLBI hot delta (`505`, `525`, `531`) against
QEMU `probe_access_internal`, soft-MMU lookup, template dispatch, and 9p
transport cost. Keep `999.specrand_ir` as the cheap correctness sentinel before
any wider run.

### Post-Batching `505.mcf_r` QEMU Profile

`workloads/generated/specint-profile-505-post-tlbirange-qemu-20260704-r1/`
samples the real QEMU child after `LINX_SPEC_START` with QEMU heartbeat output
disabled. The wrapper report records `ok=true`, real QEMU PID `40158`, sample
duration `30.435s`, and a bounded `timeout-no-heartbeat` matrix result because
the profiler run intentionally disables progress heartbeats.

The active QEMU frames are no longer dominated by `helper_linx_tlb_iv`:

| Frame | Samples |
| --- | ---: |
| `linx_template_fentry_impl` | 1087 |
| `linx_template_fret_stk_impl` | 755 |
| `tb_lookup` | 746 |
| `probe_access_internal` | 744 |
| `helper_lookup_tb_ptr` | 689 |
| `flatview_translate` | 535 |
| `linx_frame_restore_prepare` | 492 |
| `address_space_ldm_internal` | 472 |
| `address_space_translate_internal` | 462 |
| `linx_mmu_translate` | 367 |
| `linx_tlb_fill_stats_record` | 71 |
| `linx_tlb_fill_trace_emit` | 68 |
| `helper_linx_tlb_iv` | 17 |

QEMU cleanup: `emulator/qemu/target/linx/cpu.c` now checks whether
TLB-fill stats/hot-site recording or TLB-fill tracing are enabled before
calling their full helper bodies from `linx_cpu_tlb_fill()`. This removes the
disabled instrumentation helper calls that appeared in the profile while
leaving the enabled debug paths intact.

Validation:

| Check | Result |
| --- | --- |
| `ninja -C emulator/qemu/build-linx qemu-system-linx64` | pass |
| `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_TLB_FILL_STATS=1 ... 999.specrand_ir ...` | pass, `workloads/generated/specint-999-tlbfill-guard-qemu-20260704-r1/` |
| `LINX_QEMU_TLB_FILL_HOT=1 ... 999.specrand_ir ...` | pass, `workloads/generated/specint-999-tlbfill-hot-guard-qemu-20260704-r1/` |
| `LINX_QEMU_TLB_FILL_TRACE=1 ... 999.specrand_ir ... --timeout 120` | emits the bounded 64 `LINX_TLB_FILL_TRACE` lines and remains heartbeat-live, but times out before strict hash under trace overhead |

Focused `505.mcf_r` A/B: the guard is neutral at the 120-second count level.
Clean QEMU reaches `35000000005` instructions in
`workloads/generated/specint-505-tlbfill-guard-baseline-qemu-20260704-r1/`;
patched QEMU reaches `35000000002` in
`workloads/generated/specint-505-tlbfill-guard-patched-qemu-20260704-r1/`.
Keep the patch as a low-risk disabled-instrumentation cleanup, not as the SPEC
throughput closure. The next substantive speed lane remains template
entry/return, TB lookup, `probe_access_internal`, address-space translation,
and frame save/restore traffic.

## Initial Profile

Command shape:

```bash
SPECINT_TRAIN_CPU_STRESS_TIMEOUT=900 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile nightly \
  --suite train-cpu-stress \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --append-extra norandmaps \
  --guest-heartbeat-sec 0 \
  --heartbeat-sec 10 \
  --out-dir workloads/generated/specint-qemu-profile-20260627-train-cpu-stress/specint-train-cpu-stress
```

Sampling artifact:

- `workloads/generated/specint-qemu-profile-20260627-train-smoke/qemu-531.sample.txt`

The sampled process was `531.deepsjeng_r` on train input before the gate split
that workload out of `train-smoke`. A follow-up `531.deepsjeng_r` test-input
run also exceeded two minutes before guest-visible completion. The profile
shows the CPU thread spending most visible Linx-specific time under:

- `helper_linx_check_bstart_target`
- `linx_is_bstart_at_addr`
- `cpu_memory_rw_debug`
- `linx_mmu_translate`
- disabled debug/trace helpers, including `linx_dbg_check_mem`
- repeated `getenv`/`__findenv_locked` checks from hot helper paths

The main structural cost is indirect target validation reading guest text via
debug memory access, which then re-enters the Linx MMU walk. The main accidental
cost is disabled diagnostics still present in hot translated code.

## Implemented Low-Risk Fixes

- Cache the `LINX_CFI_TRACE` environment flag before the CFI helper hot path.
- Emit load/store debug watchpoint helpers only for TBs with
  `LINX_TB_FLAG_DBG_ACTIVE`.
- Remove temporary QEMU/kernel diagnostic logging before profiling.

Post-patch sample:

- `workloads/generated/specint-qemu-profile-20260627-train-cpu-stress-postpatch/qemu-531-postpatch.sample.txt`

Top-stack count changes from the initial sample to the post-patch sample:

| Frame | Before | After |
| --- | ---: | ---: |
| `__findenv_locked` | 1446 | 0 |
| `getenv` / `DYLD-STUB$$getenv` | 32 | 0 |
| `linx_dbg_check_mem` | 1157 | 0 |
| `helper_linx_dbg_check_load` | 180 | 0 |
| `helper_linx_dbg_check_store` | 66 | 0 |
| `helper_linx_check_bstart_target` | 249 | 130 |
| `linx_is_bstart_at_addr` | 369 | 182 |
| `cpu_memory_rw_debug` | 258 | 196 |
| `linx_mmu_translate` | 1347 | 933 |
| `address_space_translate_internal` | 2310 | 1567 |

The remaining QEMU-specific target is BSTART validation: indirect control-flow
checks still fetch guest text through `cpu_memory_rw_debug`, which repeatedly
enters address-space translation and Linx MMU walking.

## Implemented Target-Read Fix

QEMU commit `7e1981adf5f` replaces the Linx trap and block-recovery
instruction-byte probes with target-MMU-aware text reads. This removes
`cpu_memory_rw_debug` from that recovery path, preserves Linx legacy-MMU fault
details for diagnostics, and keeps user fault/IRQ resume state anchored to a
real BSTART header.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `qemu-system-linx64 --version` reports
  `v10.2.0-943-g7e1981adf5f`.
- `python3 avs/qemu/run_tests.py --all --timeout 20` passes.
- `./avs/qemu/check_system_strict.sh` passes.
- `boot_userspace_proof.py` reaches Linux userspace.
- `run_specint_fast_gate.py --profile smoke` passes on `999.specrand_ir`
  test input.

Post-fix 531 sample:

- `workloads/generated/specint-qemu-profile-20260627-test-cpu-stress-qemu7e/profile/qemu-531-test-qemu7e.sample.txt`

This sample was intentionally interrupted after profiling. It shows the
disabled diagnostic overhead is still gone, but `helper_linx_check_bstart_target`
continues to call `cpu_memory_rw_debug` from `helper.c`; the target-aware text
read fix did not yet move the hot CFI helper itself.

| Frame | Post-fix sample count |
| --- | ---: |
| `__findenv_locked` | 0 |
| `linx_dbg_check_mem` | 0 |
| `helper_linx_dbg_check_load` | 0 |
| `helper_linx_dbg_check_store` | 0 |
| `helper_linx_check_bstart_target` | 626 |
| `cpu_memory_rw_debug` | 1329 |
| `linx_mmu_translate` | 1157 |

## Implemented BSTART Cache-Hit Fix

QEMU commit `f80300d12c8` trusts positive BSTART cache hits on the hot CFI
path by default and moves that hit check before the call-fallthrough text
probe. `LINX_BSTART_CACHE_REVALIDATE=1` preserves the old revalidate-on-hit
behavior for self-modifying-code or mapping-churn debugging. Existing MMU
programming, TLB invalidation, CSTATE/ACR switches, and trap/ACRE transitions
reset the cache.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `qemu-system-linx64 --version` reports
  `v10.2.0-944-gf80300d12c8`.
- `python3 avs/qemu/run_tests.py --all --timeout 20` passes.
- `./avs/qemu/check_system_strict.sh` passes.
- `boot_userspace_proof.py` and `full_boot.py` reach Linux userspace.
- `run_specint_fast_gate.py --profile pr` passes on `999.specrand_ir`
  test and train input in `28.458s`.

Post-cache 531 sample:

- `workloads/generated/specint-qemu-profile-20260627-test-cpu-stress-bstart-cache/profile/qemu-531-test-bstart-cache.sample.txt`

The 531 stress run was intentionally interrupted after sampling. Compared with
the `7e1981adf5f` sample, visible helper/MMU/debug-memory frames dropped:

| Frame | Before cache hit trust | After cache hit trust |
| --- | ---: | ---: |
| `helper_linx_check_bstart_target` | 626 | 355 |
| `cpu_memory_rw_debug` | 1329 | 682 |
| `linx_mmu_translate` | 1157 | 524 |
| `address_space_translate_internal` | 552 | 296 |
| `linx_is_bstart_at_addr` | 733 | 340 |
| `__findenv_locked` | 0 | 0 |
| `linx_dbg_check_mem` | 0 | 0 |

## Implemented Helper Target-Read Fix

The next QEMU patch moves `helper_linx_check_bstart_target`,
`linx_is_bstart_at_addr`, and call-fallthrough validation away from
`cpu_memory_rw_debug`. The helper now uses a nonfaulting instruction-fetch
probe to copy RAM-backed guest text and preserves the previous demand-paging
behavior by deferring validation when executable text cannot be read.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `qemu-system-linx64 --version` reports
  `v10.2.0-945-g8f819f1df18`.
- `python3 avs/qemu/run_tests.py --all --timeout 20` passes.
- `./avs/qemu/check_system_strict.sh` passes.
- `boot_userspace_proof.py` and `full_boot.py` reach Linux userspace.
- `run_specint_fast_gate.py --profile pr` passes on `999.specrand_ir`
  test and train input.
- `SPECINT_TEST_CPU_STRESS_TIMEOUT=900 run_specint_fast_gate.py --profile
  nightly --suite test-cpu-stress` passes `531.deepsjeng_r` test input in
  `468.038s`; the benchmark exits 0, emits `LINX_SPEC_PASS`, and the
  `test.out` FNV-1a hash matches `0x391c9299`.

Post-target-read 531 sample:

- `workloads/generated/specint-nightly-test-cpu-stress-20260627-target-read/profile/qemu-531-test-target-read.sample.txt`

Compared with the immediately preceding current-QEMU 531 sample, the helper
path no longer samples `cpu_memory_rw_debug`, and the Linx MMU walk nearly
disappears from the sampled CFI validation stack:

| Frame | Before target-read helper | After target-read helper |
| --- | ---: | ---: |
| `helper_linx_check_bstart_target` | 363 | 244 |
| `cpu_memory_rw_debug` | 704 | 0 |
| `linx_mmu_translate` | 585 | 5 |
| `address_space_translate_internal` | 360 | 3 |
| `linx_is_bstart_at_addr` | 350 | 198 |
| `probe_access_flags` | 0 | 140 |

## 2026-06-29 BPC Heartbeat And Train-All Triage

Current Linx QEMU adds an opt-in Linx heartbeat in the QEMU log. Set either
`LINX_HEARTBEAT_INTERVAL` or `LINX_QEMU_HEARTBEAT_INTERVAL` to a nonzero
instruction-count interval. When enabled, QEMU emits `LINX_HEARTBEAT` records
with host time, instruction count, count delta, PC, BPC, body TPC, branch
state, `progress=first|site-change|same-site`, `same_site`, stack/return
registers, TP, ring-1 ETEMP/ETEMP0 breadcrumbs, and selected argument
registers. A high or growing `same_site` value means the same `(pc, bpc, tpc)`
location is recurring at heartbeat boundaries; changing BPC/PC with increasing
count means the guest is still executing and should be treated as slow, not
deadlocked.

For focused register snapshots at heartbeat sites, also set
`LINX_HEARTBEAT_REGS=1` or `LINX_QEMU_HEARTBEAT_REGS=1`. This emits a
`LINX_HEARTBEAT_REGS` companion line with the full Linx GPR file. The SPEC
runner lifts heartbeat evidence into `heartbeat_running`,
`heartbeat_site_progress`, `heartbeat_last_bpc`, `heartbeat_last_progress`,
`heartbeat_last_same_site`, and recent-count/site deltas in both per-benchmark
and matrix summaries.

For focused code identification without enabling full fault or PC-watch traces,
set `LINX_HEARTBEAT_CODE_BYTES=<n>` or `LINX_QEMU_HEARTBEAT_CODE_BYTES=<n>`.
QEMU emits `LINX_HEARTBEAT_CODE` records with up to 32 bytes at both the current
PC and BPC. Use this only for short or coarse-interval diagnostics; it reads
guest memory at every heartbeat boundary.

For TLB-invalidation profiling, set `LINX_TLB_TRACE=1` or
`LINX_QEMU_TLB_TRACE=1`. QEMU emits bounded `LINX_TLB_TRACE` records with the
translated invalidation PC, BPC/TPC, ACR, control state, stack/return/TLS
registers, and selected arguments. `LINX_TLB_TRACE_LIMIT` defaults to 64 records
to avoid runaway logs; set it to `0` only for tightly filtered runs. Narrow with
open-ended or closed `LINX_TLB_TRACE_PC_LO/HI` and
`LINX_TLB_TRACE_COUNT_LO/HI` ranges. `LINX_TLB_TRACE_CODE_BYTES=<n>` dumps up to
32 bytes at the invalidation PC and BPC.

For page-walk/protection profiling, set `LINX_TLB_FILL_TRACE=1` or
`LINX_QEMU_TLB_FILL_TRACE=1`. QEMU emits bounded `LINX_TLB_FILL_TRACE` records
for TLB fill attempts, including requested VA, access kind, QEMU prot, fault
cause, PC/BPC/TPC, TCR/TTBR state, and the legacy page-table leaf descriptor
decision. `LINX_TLB_FILL_TRACE_LIMIT` defaults to 64 records. Narrow with
`LINX_TLB_FILL_TRACE_VA=<addr>` or `LINX_TLB_FILL_TRACE_VA_LO/HI`, plus
`LINX_TLB_FILL_TRACE_PC_LO/HI` and `LINX_TLB_FILL_TRACE_COUNT_LO/HI`, before
using it on SPEC rows. Matching `LINX_QEMU_TLB_FILL_TRACE_*` aliases are
accepted.

For low-overhead aggregate page-walk attribution on long SPEC rows, use
`LINX_TLB_FILL_STATS=1` or `LINX_QEMU_TLB_FILL_STATS=1` before enabling full
fill traces. The switch adds `tlbf_total`, fetch/load/store/probe/ok/fault
counts, and `tlbf_last_*` fields to `LINX_HEARTBEAT`; the SPEC runner records
the final values under `heartbeat_tlb_fill` and prints compact `tlbf=` liveness
tags in matrix markdown.

For kernel-space heartbeat timeouts, add `--symbolize-heartbeat` to the SPEC
runner, or set `LINX_SPEC_SYMBOLIZE_HEARTBEAT=1`. The runner symbolizes recent
kernel PC/BPC/RA heartbeat sites with `llvm-addr2line` against the active
`vmlinux` and records `heartbeat_kernel_symbols`,
`heartbeat_kernel_symbol_evidence`, and `heartbeat_kernel_panic_loop`. Timeout
rows whose recent heartbeat sites resolve into `panic.c` are reclassified as
`kernel-panic-loop-timeout` instead of generic `live-timeout`.

The SPEC fast gate now has explicit `test`, `train`, and `test-train`
profiles, backed by all-row `test-all` and `train-all` suites covering all
current Linx SPECint rate benchmarks:

- `500.perlbench_r`
- `502.gcc_r`
- `505.mcf_r`
- `520.omnetpp_r`
- `523.xalancbmk_r`
- `525.x264_r`
- `531.deepsjeng_r`
- `541.leela_r`
- `557.xz_r`
- `999.specrand_ir`

The direct train-all loop should keep `LINX_QEMU_HEARTBEAT_INTERVAL` enabled
and `SPEC_GUEST_HEARTBEAT_SEC=0`. QEMU heartbeat BPC/PC churn is the active
deadlock discriminator; guest wrapper output can remain quiet for minutes in
initramfs mode while SPEC is still executing.

For deadlock triage, set `LINX_HEARTBEAT_SAME_SITE_WARN=<n>` or
`LINX_QEMU_HEARTBEAT_SAME_SITE_WARN=<n>` alongside the heartbeat interval.
QEMU emits a one-shot `LINX_HEARTBEAT_STALL` line after the same
`(pc, bpc, tpc)` recurs for `n` heartbeat buckets. The record includes count,
delta, PC, BPC, TPC, ACR, CSTATE, repeat count, threshold, and
`status=same-site-running`. Treat it as a focused "probably spinning here"
marker, not as proof of a hard deadlock: the runner still reports
`heartbeat_site_progress=true` if later heartbeat buckets move to other BPCs.

The latest all-train static diagnostic run is
`workloads/generated/specint-train-all-latest-qemu-20260630-r1/`, using rebuilt
QEMU `v10.2.0-969-gf03477a0f56`. Its build manifest is
`workloads/generated/specint-build-all-static-byval-fix-20260630/phaseb_build_manifest.json`.
It uses the mallocng-default phase-b musl sysroot, the refreshed spec C++
runtime overlay, the Linx LLVM f64 extload fix, the indirect-call target-register
constraint, the `502.gcc_r` variadic-function-table workaround, the QEMU scalar
queue fast path, the QEMU heartbeat guard, the LLVM Blockify ABI call-arg fix,
and the LLVM by-value aggregate call fix in `compiler/llvm` commit
`870fb448edd6f`. It proves the current failed rows are not global QEMU
deadlocks: every failed row has QEMU heartbeat progress, increasing count/BPC
evidence, and `999.specrand_ir` still passes strict hash. That run splits the
work into five lanes:

- Closed 500 correctness stop: `500.perlbench_r` run_001 passes
  `perfect.b.3.out` by hash `0xc69c7085`; run_002 no longer traps at the old
  bad target `0x003f7fee56880000` and is now heartbeat-backed live-slow. The
  root cause was compiler-side: Blockify erased the shifted byte-count producer
  for ABI register `a2` before `Perl_repeatcpy`, corrupting Perl op pointers.
- Closed 502 byval correctness stop: `502.gcc_r` trapped at `addr=0x8` with
  `tpc=0x1555f26c0e`, `bpc=0x1555f26c02`, and `orig_tpc=0x1556075fe2`.
  With slide `0x1515555000`, the trap PC maps to `gsi_prev` in
  `tree-ssa-dse.c`, specifically the second list-link load after loading
  `[a0]`; the origin PC maps to the musl `mmap.c` return block. Focused runs
  under `workloads/generated/specint-502-gsiprev-pcwatch-20260629-r1/` and
  `workloads/generated/specint-502-gsiprev-ring-final-filtered-20260629-r1/`
  prove the final iterator slot itself is null: the final `LINX_PC_WATCH_RING`
  entry at `pc=0x1555f26c0e` has `a0=0x3ffffff750`, `mem_value=0x0`, and
  `tq0=0x0` immediately before the `addr=0x8` fault. The source signature
  `dse_optimize_stmt(..., gimple_stmt_iterator gsi)` takes the iterator by
  value, but that callee calls `gsi_remove(&gsi, true)`; the caller disassembly
  passes `sp+80` to `dse_optimize_stmt` and then reuses the same slot for
  `gsi_prev`. This is now closed by the Linx LLVM by-value aggregate lowering
  fix: by-value structs are copied to callee-owned temporaries before calls.
  The focused rebuild and rerun under
  `workloads/generated/specint-502-byval-fix-build-20260629/` and
  `workloads/generated/specint-502-byval-fix-train-20260629-r1/` crosses the
  former 35B-instruction trap window and reaches `live-timeout` at count
  `61000000006` with BPC `0x155598d706`, `progress=site-change`, and no
  `LINX_USER_TRAP`.
- Live-slow train rows: `500.perlbench_r` run_002, `502.gcc_r`, `505.mcf_r`,
  `531.deepsjeng_r`, and `557.xz_r` time out under diagnostic budgets with
  heartbeat site progress.
- Wrapper child-exit rows: `520.omnetpp_r`, `523.xalancbmk_r`, and
  `541.leela_r` emit `LINX_SPEC_FAIL child-exit`. The runner now appends the
  wrapper `LINX_SPEC_DBG wait ... status/code/sig` line to `spec-wrapper-fail`
  evidence, so the next rerun should identify whether each child exited
  nonzero or died by signal before treating these as C++ runtime or QEMU
  throughput failures.
- Kernel panic-loop row: `525.x264_r` does not reach `LINX_SPEC_START`; recent
  symbolized heartbeat sites resolve to `panic.c` and `udelay`, so the runner
  classifies it as `kernel-panic-loop-timeout` rather than throughput-only.
- Closed historical lanes: the earlier 502 bad RTL pointer path is closed by
  keeping indirect call targets out of ABI argument registers and by compiling
  502 with SPEC's existing `SPEC_GCC_VARIADIC_FUNCTIONS_MISMATCH_WORKAROUND`.
  The later 502 allocator/VM `mremap` end-page trap is closed by the Linx Linux
  mremap workaround and `avs/qemu/out/mremap-end-smoke-r3/summary.json`.
  Historical stack/startup traps for `520`, `523`, and `541` are not reproduced
  under the current `--stack-limit 2G` static train loop.

For `502.gcc_r`, the focused runs under
`workloads/generated/specint-502-icall-target-fix-20260629-r1` and
`workloads/generated/specint-502-icall-target-varfn-fix-20260629-r1` split the
root cause. The first run proves the indirect call target was no longer
allocated in `a0`, but the generated GCC table still called fixed-argument
`gen_*` functions through a variadic function-pointer type, conflicting with
Linx's stack-passed real-vararg policy. The 502-only SPEC workaround changes
that table to unprototyped calls, so `gen_movsi` receives operands in `a0/a1`
and the earlier `ix86_rtx_costs`/code-pointer trap is closed. The next stop was
the allocator/VM boundary: runtime `tpc=0x1556074e1a` mapped, with the static PIE
slide, to musl `realloc.c` at static `0x40b1fe1a`, immediately after the
`mremap.c` return body around static `0x40b2040a`. The trap wrote
`sbi a3, [a1, -4]` with `a1=0x3f7e729000`, faulting at `addr=0x3f7e728ffc`.
The Linx Linux mremap workaround still closes that old end-page producer:
`avs/qemu/out/mremap-end-smoke-r3/summary.json` passes the isolated end-page
store, and `workloads/generated/specint-train-all-mremap-fix-20260629-r1/`
classified 502 as heartbeat-backed live timeout at that point.

2026-06-30 correction: the current `502.gcc_r` allocator/VM lane is open again,
but the new evidence points away from QEMU stale-TLB behavior. In
`workloads/generated/specint-502-mprotect-tlbfill-20260630-r2/`, the final
mallocng metadata-page sequence enters `mprotect(0x3f7fa8d000, 0x1000,
PROT_READ|PROT_WRITE)` and the next store faults at `0x3f7fa8d010`. The new
`LINX_TLB_FILL_TRACE` record for that store reports `ok=0`, `access=store`,
`legacy_why=type0`, and `legacy_desc=0x0`; the companion `LINX_FAULT_TRACE`
reports `mem_va=0x3f7fa8d010`, `store_ok=0`, and
`legacy_store=1:0:type0`. Therefore the current owner is Linx Linux
`mprotect()`/VMA/page-fault bring-up: QEMU sees no writable or present legacy
PTE for the faulting data VA after the syscall path has returned to userspace.
The next kernel trace should log `do_mprotect_pkey()` VMA coverage and
`do_page_fault()` `find_vma()`/`access_error()` results for this VA before
changing QEMU TLB policy.

2026-06-30 VM-trace update: QEMU commit `883737038a7` plus the latest local
debug patch adds address-filtered fault tracing (`LINX_QEMU_FAULT_TRACE_ADDR*`)
and `LINX_QEMU_FAULT_TRACE_REGS`. The rebuilt Linx kernel adds boot-arg gated
VM fault UART tracing through `linx_vm_trace=1` and
`linx_vm_trace_addr=<va>`. Focused evidence under
`workloads/generated/specint-502-vmtrace-uart-20260630-r1/` proves the early
faults on `0x3f7fa8d008` have `LINX_VM_FAULT stage=good-vma` followed by
`stage=handled fault=0`, while the terminal store to `0x3f7fa8d010` has
`LINX_TLB_FILL_TRACE legacy_why=type0 legacy_desc=0x0`,
`LINX_FAULT_TRACE mem_va=0x3f7fa8d010`, and
`LINX_VM_FAULT stage=no-vma`. The active 502 owner is therefore Linux
VMA/mprotect/mapping lifetime, not QEMU liveness. The next fix should trace or
repair the kernel `mprotect()` VMA split/merge path around
`0x3f7fa8d000..0x3f7fa8efff` and then rerun this focused gate before touching
QEMU TLB policy.

2026-06-30 no-merge update: the focused mprotect trace and Linux fix close the
current 502 correctness stop. The new Linx-only kernel trace switch
`linx_mprotect_trace=1` logs `LINX_MPROTECT` before/after VMA neighborhoods,
with optional `linx_mprotect_trace_addr=<va>` and
`linx_mprotect_trace_limit=<n>`. Before the fix,
`workloads/generated/specint-502-mprotect-trace-20260630-r1/` showed the second
metadata-page `mprotect()` returning success while `prev`, `cur`, `next`, and
`target` all disappeared for `0x3f7fa8d010`; the next store then faulted as
`LINX_VM_FAULT stage=no-vma`. `mm/vma.c` now keeps Linx
`vma_modify()` operations out of `vma_merge_existing_range()`, matching the
existing Linx no-merge policy for mmap/brk/mremap until the maple-tree merge
path is repaired. After the fix,
`avs/qemu/out/musl-mprotect-adjacent-nomerge-20260630-r1/summary.json` passes
and the post-mprotect trace keeps both VMAs present. Focused `502.gcc_r` in
`workloads/generated/specint-502-mprotect-nomerge-20260630-r1/` moves from
`user-trap` to heartbeat-backed `live-timeout`, and the refreshed train-all
ledger `workloads/generated/specint-train-all-nomerge-qemu-20260630-r1/` keeps
`999.specrand_ir` passing strict hash `0x973dcfc2` while classifying `500`,
`502`, `505`, `520`, `523`, `531`, `541`, and `557` as live-slow and
`525.x264_r` as the remaining initramfs VFS-root panic. The next QEMU work is
therefore throughput profiling, not further 502 TLB correctness triage.

2026-07-02 split-train update: the all-train fast gate now runs every SPECint
train row while keeping `525.x264_r` in a generated large-payload 9p shard.
The latest split run is
`workloads/generated/specint-train-split-post-perlbench-20260702-r1/` with QEMU
`v10.2.0-989-g5cfb672a711`, LLVM `e4771587a947`, phase-b musl, and a 2 GiB
SPEC stack cap. It confirms the current all-train state:

- `999.specrand_ir` passes strict hash.
- `502.gcc_r` is a real SPEC GCC internal-error row, not a generic wrapper
  failure. The current-code proof is
  `workloads/generated/specint-502-internal-error-class-20260702-r3/`, which
  classifies the row as `spec-benchmark-internal-error` with child exit
  code 4 and the `tree-into-ssa.c:942` benchmark message.
- `500.perlbench_r`, `505.mcf_r`, `520.omnetpp_r`, `523.xalancbmk_r`,
  `531.deepsjeng_r`, `541.leela_r`, and `557.xz_r` are heartbeat-backed
  `live-timeout` rows with changing BPCs.
- `525.x264_r` runs under 9p and all four generated train invocations were
  heartbeat-backed `live-timeout` rows in the pre-fail-fast run. The fast gate
  now auto-enables `--fail-9p-timeout` for generated `*-large-9p` shards unless
  explicit `--transports` is supplied, so future gates stop this shard after
  the first timeout.

The newest QEMU sample for the split run is
`workloads/generated/specint-train-split-post-perlbench-20260702-r1/profiles/qemu-531-active.sample.txt`.
The top sampled owners remain:

| Frame | Samples |
| --- | ---: |
| `helper_linx_template_step` | 313 |
| `probe_access_internal` | 291 |
| `helper_linx_check_bstart_target` | 188 |
| `mmu_lookup1` | 178 |
| `helper_linx_tile_set_attr` | 146 |
| `linx_trace_wb` | 89 |
| `helper_lookup_tb_ptr` | 81 |
| `linx_call_trace_emit` | 72 |

Immediate speed hypotheses:

1. Template-step fast path: audit why common SPEC execution still samples
   `helper_linx_template_step` heavily and split cold trace/template work out
   of the hot path.
2. BSTART/probe path: extend the BSTART legality cache or per-TB memoization so
   `helper_linx_check_bstart_target` does not repeatedly enter
   `probe_access_internal` and `mmu_lookup1` for stable code pages.
3. Trace hooks: make `linx_trace_wb` and `linx_call_trace_emit`
   translation-time gated for non-trace runs, or prove from counters that these
   samples are unavoidable architectural work.
4. Tile attribute/reset path: inspect `helper_linx_tile_set_attr` and tile
   reset traffic in SPEC loops; if attributes are unchanged, cache the no-op or
   move validation out of repeated helper calls.

2026-07-02 helper-elision update: host samples from
`workloads/generated/specint-train-all-current-20260702-r1/` showed
`helper_linx_tile_set_attr` and `helper_linx_tile_reset_block` in the scalar
SPEC hot path. These helpers were emitted at every translated Linx block start
even though scalar SPEC normally needs only the architectural zero/default tile
state. QEMU now emits equivalent direct TCG stores for that block-prologue reset
state instead of calling the two helpers.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 15 --qemu emulator/qemu/build-linx/qemu-system-linx64` passed.
- `workloads/generated/specint-999-patched-qemu-20260702-r1/qemu_matrix_summary.json` passed `999.specrand_ir` train hashcheck.
- `workloads/generated/specint-500-patched-profile-20260702-r1/profile/qemu-500-patched-qemu.sample.txt` has zero samples in `helper_linx_tile_set_attr` and `helper_linx_tile_reset_block`.

2026-07-02 current-QEMU all-train update:
`workloads/generated/specint-train-all-current-qemu-20260702-r1/` reran the
split train suite on QEMU `v10.2.0-991-g5754b39fb76`, phase-b musl, no guest
heartbeat, QEMU BPC heartbeat every 1B guest instructions, `norandmaps`, and a
2 GiB SPEC stack limit. The aggregate stayed red, but there were no
`LINX_USER_TRAP` or kernel panic rows. `999.specrand_ir` passed strict train
hash `0x973dcfc2`; `502.gcc_r` is the active correctness row with child exit
code 4 and `tree-into-ssa.c:942`; every other row is heartbeat-backed live
progress and should stay in the throughput lane.

| Benchmark | Transport | Result | Last BPC | Count | HB running/progress |
| --- | --- | --- | --- | ---: | --- |
| `500.perlbench_r` | `initramfs` | `live-timeout` | `0x1555660652` | 48000000021 | true/true |
| `502.gcc_r` | `initramfs` | `spec-benchmark-internal-error` | `0xffffffff803d359e` | 18000000000 | true/true |
| `505.mcf_r` | `initramfs` | `live-timeout` | `0x155555cd12` | 47000000001 | true/true |
| `520.omnetpp_r` | `initramfs` | `live-timeout` | `0x1555632e94` | 13000000003 | true/true |
| `523.xalancbmk_r` | `initramfs` | `live-timeout` | `0x155567f3be` | 19000000003 | true/true |
| `531.deepsjeng_r` | `initramfs` | `live-timeout` | `0x155556a7ca` | 45000000001 | true/true |
| `541.leela_r` | `initramfs` | `live-timeout` | `0x155559bc92` | 18000000001 | true/true |
| `557.xz_r` | `initramfs` | `live-timeout` | `0x155558d604` | 36000000008 | true/true |
| `999.specrand_ir` | `initramfs` | pass | - | - | - |
| `525.x264_r` | `9p` | `live-timeout` | `0xffffffff8010629c` | 22000000003 | true/true |

Signed-wrap build profile update: the benchmark flow now rebuilds SPEC with
`LINX_SPEC_BENCH_OPTIMIZE` defaulting to
`502.gcc_r=-O0 -fno-vectorize -fno-slp-vectorize -fwrapv`. The focused current
verification
`workloads/generated/specint-build-502-flow-wrapv-20260702-r1/build_manifest.json`
records the 502-specific flags and source immutability; the matching QEMU run
`workloads/generated/specint-502-flow-wrapv-train-row1-qemu-20260702-r1/stage_b_summary.json`
moves train row 1 from `spec-benchmark-internal-error` to `live-timeout` with
`heartbeat_running=true`, `heartbeat_site_progress=true`, count `24000000002`,
BPC `0x1555766900`, and no `tree-into-ssa`, trap, or panic marker. This keeps
the default 502 build as a deliberate regression-repro lane, not the canonical
SPEC fast-gate build.

2026-07-02 signed-wrap all-train refresh: the canonical all-row train build is
now `workloads/generated/specint-build-all-flow-wrapv-20260702-r1/`, whose
manifest records every supported SPECint binary built with the signed-wrap 502
profile. The matching QEMU gate is
`workloads/generated/specint-train-all-flow-wrapv-qemu-20260702-r1/`, using
QEMU `v10.2.0-991-g5754b39fb76`, phase-b musl, no guest heartbeat, QEMU BPC
heartbeat every 1B guest instructions, `norandmaps`, and a 2 GiB SPEC stack
limit. The aggregate remains red on runtime, but the prior 502 correctness stop
is closed in this flow: there are no `tree-into-ssa`, benchmark internal-error,
trap, or panic signatures in the logs.

| Benchmark | Transport | Result | Last BPC | HB progress |
| --- | --- | --- | --- | --- |
| `500.perlbench_r` | `initramfs` | `live-timeout` | `0x1555670cb8` | site-change |
| `502.gcc_r` | `initramfs` | `live-timeout` | `0x1555c751a6` | site-change |
| `505.mcf_r` | `initramfs` | `live-timeout` | `0x155555cbac` | site-change |
| `520.omnetpp_r` | `initramfs` | `live-timeout` | `0x15555f7258` | site-change |
| `523.xalancbmk_r` | `initramfs` | `live-timeout` | `0x15559493a8` | site-change |
| `531.deepsjeng_r` | `initramfs` | `live-timeout` | `0x155556da62` | site-change, earlier same-site warning |
| `541.leela_r` | `initramfs` | `live-timeout` | `0x15555709ee` | site-change |
| `557.xz_r` | `initramfs` | `live-timeout` | `0x155558d6da` | same-site at final heartbeat, recent-site progress |
| `999.specrand_ir` | `initramfs` | pass | - | strict hash `0x973dcfc2` |
| `525.x264_r` | `9p` | `live-timeout` | `0xffffffff80112170` | site-change |

2026-07-02 call-trace fast-disabled update: the focused current profile
`workloads/generated/specint-qemu-profile-500-train-current-20260702-r1/`
showed disabled call tracing still entering `linx_call_trace_init` from hot
frame-template helpers. QEMU now keeps the slow call-trace emitter behind an
inline fast-disabled check and removes two stale hardcoded PC-specific
FENTRY/FRET.STK diagnostic log branches. This does not change architectural
state; setting `LINX_CALL_TRACE=1` still takes the slow path.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `emulator/qemu/build-linx/qemu-system-linx64 --version` reports
  `v10.2.0-992-g8188cc41328`.
- `python3 avs/qemu/run_tests.py --all --timeout 20` passed.
- `bash avs/qemu/check_system_strict.sh` passed.
- `tools/bringup/run_specint_fast_gate.py --profile pr` passed both
  `999.specrand_ir` test and train sentinels in
  `workloads/generated/specint-pr-calltrace-fastpath-20260702-r1/`.
- `LINX_CALL_TRACE=1 LINX_CALL_TRACE_LIMIT=1 run_stage_qemu_matrix.py ...`
  passed `999.specrand_ir` and emitted a bounded `LINX_CALL_TRACE` record in
  `workloads/generated/specint-999-calltrace-fastpath-enabled-20260702-r1/`.

The before/after 30-second `500.perlbench_r` train samples remain
heartbeat-backed live-timeouts with site progress. Stack-count extraction from
the macOS `sample` reports shows the intended debug-path reduction:

| Frame | Before | After |
| --- | ---: | ---: |
| `linx_call_trace_init` | 279 | 0 |
| `linx_call_trace_emit*` | 450 | 356 |
| `helper_linx_template_step` | 6006 | 5942 |
| `helper_linx_check_bstart_target` | 2953 | 2932 |
| `linx_is_bstart_at_addr` | 1856 | 1865 |
| `probe_access_internal` | 1619 | 1725 |
| `mmu_lookup1` | 1270 | 1327 |

2026-07-02 wider BSTART cache update: the focused `531.deepsjeng_r` test-input
profile still showed repeated CFI target validation and text probes after the
call-trace fast-disabled patch. QEMU now widens the direct-mapped legal-target
cache from 64 to 1024 entries, hashes target addresses before indexing, checks
the cache before the call-continuation scan, and caches continuation positives.
It also adds opt-in cache counters via `LINX_BSTART_CACHE_STATS=1` and
`LINX_BSTART_CACHE_STATS_INTERVAL=<n>`; `LINX_BSTART_CACHE_REVALIDATE=1`
continues to force revalidation for self-modifying-code/debug runs.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `python3 avs/qemu/run_tests.py --all --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` passed.
- `bash avs/qemu/check_system_strict.sh` passed.
- `QEMU=emulator/qemu/build-linx/qemu-system-linx64 bash avs/qemu/run_tests.sh --all --timeout 10` passed.
- `python3 avs/qemu/run_callret_contract.py` passed.
- `tools/bringup/run_specint_fast_gate.py --profile pr` passed both
  `999.specrand_ir` test and train sentinels in
  `workloads/generated/specint-pr-bstart-cache-20260702-r1/`.
- `SPECINT_TEST_CPU_STRESS_TIMEOUT=900 tools/bringup/run_specint_fast_gate.py
  --profile nightly --suite test-cpu-stress` passed `531.deepsjeng_r` test
  input in `404.207s` under
  `workloads/generated/specint-test-cpu-stress-bstart-cache-20260702-r1/`.
  The row exited 0, emitted `LINX_SPEC_PASS`, and matched `test.out` hash
  `0x391c9299`.

Focused 180-second `531.deepsjeng_r` timing improved from
`46000000006` to `50000000021` guest instructions under the same timeout and
heartbeat settings:

| Run | Artifact | Count | Last BPC |
| --- | --- | ---: | --- |
| Baseline | `workloads/generated/specint-profile-531-test-20260702-r1/` | 46000000006 | `0x155556a8b4` |
| Wider cache | `workloads/generated/specint-profile-531-test-bstart-cache-nostats-20260702-r1/` | 50000000021 | `0x155556a7ca` |

The stats-enabled run under
`workloads/generated/specint-profile-531-test-bstart-cache-20260702-r1/`
reported `1022200000` checks, `929791076` cache hits, `92408922` BSTART
inserts, and zero bad targets at the final stats line, for about a 91% hit
rate. The macOS `sample` comparison also showed the intended reduction:

| Frame | Baseline samples | Wider-cache samples |
| --- | ---: | ---: |
| `helper_linx_check_bstart_target` | 657 | 429 |
| `linx_is_bstart_at_addr` | 519 | 202 |
| `probe_access_internal` | 433 | 222 |
| `probe_access_flags` | 361 | 118 |
| `helper_linx_template_fret_stk` | 513 | 472 |

2026-07-02 template trace fast-disabled update: the latest-QEMU focused
`531.deepsjeng_r` test-input profile, with QEMU rebuilt at
`v10.2.0-995-gcdb2a01e2bb` before the local patch, showed disabled trace
instrumentation still visible inside frame-template helpers. QEMU commit
`8f6de68e091` caches the
no-trace state in `CPULinxState` after the first commit/minst/cosim/log check,
keeps disabled FENTRY/FRET.STK debug trace checks out of repeated scan paths,
and forces the call-trace fast-disabled helper inline. Architectural frame
save/restore, BSTART validation, and enabled trace behavior are unchanged.

Validation after rebuilding `emulator/qemu/build-linx/qemu-system-linx64`:

- `emulator/qemu/build-linx/qemu-system-linx64 --version` reports
  `v10.2.0-996-g8f6de68e091`.
- `python3 avs/qemu/run_tests.py --all --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` passed.
- `bash avs/qemu/check_system_strict.sh` passed when rerun sequentially; an
  earlier parallel attempt overlapped `avs/qemu/out` and reproduced the known
  shared-output undefined-symbol hazard.
- `python3 avs/qemu/run_callret_contract.py` passed.
- `tools/bringup/run_specint_fast_gate.py --profile pr` passed both
  `999.specrand_ir` test and train sentinels in
  `workloads/generated/specint-pr-trace-fast-disabled-20260702-r1/`.
- `LINX_CALL_TRACE=1 LINX_CALL_TRACE_LIMIT=1 run_int_rate_qemu.py ... --bench
  999.specrand_ir` passed in
  `workloads/generated/specint-999-calltrace-enabled-trace-fast-disabled-20260702-r1/`
  and emitted a bounded `LINX_CALL_TRACE` record, proving the enabled trace
  path still reaches the slow emitter.
- `tools/bringup/run_specint_fast_gate.py --profile nightly --suite
  test-cpu-stress` passed `531.deepsjeng_r` test input in
  `workloads/generated/specint-test-cpu-stress-trace-fast-disabled-20260702-r1/`;
  strict hash validation matched `test.out` at `0x391c9299`, the Stage-A run
  took `373.577s`, and the last BPC heartbeat recorded count `108000000001`
  at `0xffffffff800f7f6c`.

Focused `531.deepsjeng_r` 180-second timing with 1B-instruction BPC heartbeat:

| Run | Artifact | Count | Last BPC |
| --- | --- | ---: | --- |
| Pre-BSTART-cache baseline | `workloads/generated/specint-profile-531-test-20260702-r1/` | 46000000006 | `0x155556a8b4` |
| Wider BSTART cache | `workloads/generated/specint-profile-531-test-bstart-cache-nostats-20260702-r1/` | 50000000021 | `0x155556a7ca` |
| Trace fast-disabled | `workloads/generated/specint-profile-531-test-trace-fast-disabled-20260702-r1/` | 52000000005 | `0x15555683a2` |

Focused strict `531.deepsjeng_r` test-input completion:

| Run | Artifact | Stage elapsed | Strict hash |
| --- | --- | ---: | --- |
| Wider BSTART cache | `workloads/generated/specint-test-cpu-stress-bstart-cache-20260702-r1/` | `404.207s` | `0x391c9299` |
| Trace fast-disabled | `workloads/generated/specint-test-cpu-stress-trace-fast-disabled-20260702-r1/` | `373.577s` | `0x391c9299` |

The sample comparison between
`workloads/generated/specint-profile-531-test-latest-qemu-20260702-r2/qemu-sample-delayed-15s.txt`
and
`workloads/generated/specint-profile-531-test-trace-fast-disabled-20260702-r1/qemu-sample-15s.txt`
shows the intended disabled-trace reduction:

| Frame | Before trace fast-disabled | After trace fast-disabled |
| --- | ---: | ---: |
| `linx_trace_wb` | 109 | 0 |
| `linx_call_trace_emit` | 82 | 0 |
| `helper_linx_template_fret_stk` | 328 | 296 |
| `helper_linx_template_fentry` | 302 | 270 |
| `linx_frame_restore_commit` | 91 | 70 |

Focused and all-row `557.xz_r` test-input closure on latest QEMU:

- Historical split artifact:
  `workloads/generated/specint-557-test-strict-latest-qemu-20260702-r1/`.
  It proved run 1 strict hash correctness, then exposed a tooling/logging
  failure where run 2 reached `LINX_SPEC_DBG wait ... status=0x0` and stayed
  heartbeat-live in Linux allocator/free-list paths before `parent-hash`.
- Runner fix: the generated SPEC init wrapper now emits the post-child wait
  status through one bounded `snprintf` line and one `write_log_all()` call
  instead of a sequence of tiny console/log writes. The Python regression is
  `test_generated_wait_status_log_uses_single_helper_write`.
- Focused closure: `workloads/generated/specint-557-test-run2-atomic-wait-20260702-r1/`
  passes row 2 with `LINX_SPEC_HASH cpu2006docs.tar-4-1.out 684
  0xc1cd766a` and `LINX_SPEC_PASS 557.xz_r`. Row 12 also passes in
  `workloads/generated/specint-557-test-run12-extended-20260702-r1/`.
- Full-row closure: `workloads/generated/specint-557-test-all-atomic-wait-20260702-r2/stage_b_summary.json`
  passes all 12 `557.xz_r` test rows under strict initramfs hash validation on
  QEMU `v10.2.0-996-g8f6de68e091`: 12/12 rows pass, 12/12 hash checks match,
  elapsed `953.286s`.

This moves current `557.xz_r` test input out of the correctness blocker list.
Keep the earlier partial run as the reason for the atomic wait-status log, and
use a larger per-row cap such as `1200s` for full `557.xz_r` test sweeps; the
600s all-row attempt reached 11/12 hashes and timed out live on row 12, while
focused row 12 and the full 1200s rerun both passed.

Focused `505.mcf_r` test/train split on latest QEMU:

- `workloads/generated/specint-505-test-strict-900-20260702-r1/stage_b_summary.json`
  passes strict initramfs hash validation in `294.032s`: `inp.out`
  `0xebc57874`/`2020` bytes and `mcf.out` `0x2cbcef6f`/`11` bytes both match.
- `workloads/generated/specint-505-train-strict-1200-20260702-r1/stage_b_summary.json`
  keeps running until the `1200.289s` cap. The row is `live-timeout`, not a
  correctness stop: QEMU heartbeat is running with site progress, last count
  `383000000001`, recent delta `7000000000`, eight recent sites, and last BPC
  `0x155555c6fa`.

This confirms that `505.mcf_r` test input is a usable fast correctness gate,
while train input remains a throughput/VM-stress workload. Keep train `505` out
of the cheap PR gate; run it in nightly/profiling loops with coarse or disabled
heartbeat after `LINX_SPEC_START`, and re-open correctness triage only if a
fresh run shows a trap, panic, child-exit marker, or hash mismatch.

Focused `500.perlbench_r` test-input split on latest QEMU:

- `workloads/generated/specint-500-test-kernel-oops-classified-20260702-r1/stage_b_summary.json`
  proves row 1 (`makerand.pl`) under strict initramfs hash validation on QEMU
  `v10.2.0-998-gea87f8ca513`: `makerand.out` matches hash `0xdff9dd08`
  and size `43841`.
- Row 2 (`test.pl`) is not a live-timeout or a QEMU deadlock. The run was
  classified directly as `kernel-oops` from `LINX_DIE msg=Oops
  tpc=0xffffffff8012b58e bpc=0xffffffff8012b572 ... a7=0x3b
  traparg0=0x8`; `test.out` is absent, so strict hash validation cannot match
  expected hash `0x0bcb1242` size `15506`. The fault symbolizes to Linux
  `create_pipe_files` / `pipe.c:0` with `a0=0`.

Keep `500.perlbench_r` row 2 out of the generic throughput queue until the
kernel Oops is explained. The next owner should inspect the Linx
`execve`/pipe-creation path and the QEMU/kernel state handoff that leaves
`create_pipe_files` dereferencing a null file pointer.

The remaining sampled QEMU owners after the wider BSTART cache and trace
fast-disabled patches are therefore still the expected next targets:

| Frame | Samples |
| --- | ---: |
| `helper_linx_template_step` | dominant |
| `helper_linx_check_bstart_target` | dominant under returns |
| `linx_is_bstart_at_addr` | repeated target text probes |
| `probe_access_internal` / `probe_access_flags` | target/text and frame probes |
| `mmu_lookup1` / `mmu_lookup` | frame memory and probe traffic |
| `pthread_jit_write_protect_np` | translation/JIT write-protect churn |

Next implementation loops:

1. Split frame-template helpers (`FENTRY`, `FEXIT`, `FRET.RA`, `FRET.STK`) from
   restartable memory templates and move cold trace/debug decisions off the
   no-trace path. Preserve the existing stack-growth/page-fault restart
   contract: FENTRY probes save slots before SP commit, and restore templates
   load all slots before SP/register commit.
2. Add a page-local or per-TB BSTART decode cache with explicit text/TB
   invalidation. The wider target cache improves repeated exact-target hits,
   but cold targets and cache churn still enter the BSTART byte classifier.
3. Profile translation churn separately from execution churn. The
   `pthread_jit_write_protect_np` samples may reflect TB generation during early
   SPEC execution rather than steady-state execution; take a delayed sample
   after boot and benchmark warm-up before changing TCG policy.
4. Revisit TLB-fill map-size handling. `linx_mmu_translate()` can return large
   block mappings, but `linx_cpu_tlb_fill()` still clamps oversized mappings to
   `TARGET_PAGE_SIZE`; this may amplify MMU/TLB churn on large SPEC working
   sets. Any change must first audit permission-changing paths such as
   `mprotect()`, page faults, and page invalidations.

Additional opt-in QEMU debug switches used during this pass:

- `LINX_TLB_TRACE=1` records Linx TLB invalidation helpers with translated PC,
  BPC/TPC, ACR/control state, stack/return/TLS registers, and optional code
  bytes. Use `LINX_TLB_TRACE_COUNT_LO=<post-start-count>` when a host sample must
  exclude boot-time fixmap churn. Matching `LINX_QEMU_TLB_TRACE_*` aliases are
  accepted.
- `LINX_TLB_FILL_TRACE=1` records TLB fill/page-walk attempts with requested VA,
  access kind, QEMU prot, cause, TCR/TTBR state, and legacy leaf descriptor
  details. Use `LINX_TLB_FILL_TRACE_VA=<addr>` or `_VA_LO/_VA_HI` with count
  filters for long SPEC rows. Matching `LINX_QEMU_TLB_FILL_TRACE_*` aliases are
  accepted.
- `LINX_FAULT_TRACE=1` records synchronous fault handoff state, including
  source/destination ACR, faulting VA, report BPC, TPC, selected registers,
  instruction bytes, and fetch/store page-walk probes. Use
  `LINX_FAULT_TRACE_ADDR=<va>` or `_ADDR_LO/_ADDR_HI` to filter data faults by
  `pending_trap_arg0`; `LINX_FAULT_TRACE_VA*` is accepted as an alias for data
  VA filters. Literal `0` is accepted, so `LINX_FAULT_TRACE_ADDR=0` is the
  focused null-fault filter. Matching `LINX_QEMU_FAULT_TRACE_*` aliases are accepted. Use
  `LINX_FAULT_TRACE_PC*`, `LINX_FAULT_TRACE_COUNT*`, and
  `LINX_FAULT_TRACE_TRAPNUM*` when a late SPEC run needs the quota to survive
  until the failing window.
- `LINX_CALL_TRACE_RING=1` records recent call/return/ACRE events in a bounded
  ring and dumps them after `LINX_FAULT_TRACE` reports a synchronous fault.
  Use `LINX_CALL_TRACE_RING_SIZE=<1..128>` to tune the retained window.
- `LINX_BSTART_CACHE_STATS=1` records aggregate CFI target-validation cache
  counters on stderr as `LINX_BSTART_CACHE_STATS` lines. Use
  `LINX_BSTART_CACHE_STATS_INTERVAL=<checks>` to lower or raise the emission
  cadence; the default interval is one million checks. Pair this with
  `LINX_BSTART_CACHE_REVALIDATE=1` only for self-modifying-code or stale-cache
  debugging, because revalidation intentionally takes the slower target-probe
  path.
- `LINX_FRET_STK_TRACE=1` records `FRET.STK` restore slots before the register
  file is committed. Narrow with `LINX_FRET_STK_TRACE_PC=<pc>`,
  `LINX_FRET_STK_TRACE_COUNT_LO/HI`, and `LINX_FRET_STK_TRACE_RA=<value>`;
  literal `0` is accepted for the RA filter. Add
  `LINX_FRET_STK_TRACE_DUMP_WORDS=<n>` or `_REGS=1` when the frame contents or
  live GPRs are needed. Matching `LINX_QEMU_FRET_STK_TRACE_*` aliases are
  accepted.
- `LINX_MEM_TRACE_ADDR=<addr>` instruments translated loads/stores and prints
  only accesses overlapping the requested address range. Narrow with
  `LINX_MEM_TRACE_SIZE`, `LINX_MEM_TRACE_ACCESS=loads|stores|all`,
  `LINX_MEM_TRACE_LIMIT`, `LINX_MEM_TRACE_PC_LO/HI`, and
  `LINX_MEM_TRACE_ACR=<0..15>`. Use `LINX_MEM_TRACE_COUNT_LO/HI` when a late
  SPEC window must retain the final producer instead of spending
  `LINX_MEM_TRACE_LIMIT` on earlier stack-slot reuse. Use
  `LINX_MEM_TRACE_CONTEXT=1` when the trace must show the current user/kernel
  address-space context; it appends `mmu_idx`, `ttbr0`, `ttbr1`, and `tcr` to
  each matching record. QEMU now emits the helper call only for translated
  accesses that overlap the watched range; set `LINX_MEM_TRACE_FAST=0` to restore
  the older helper-on-every-access path if the fast address guard itself is under
  suspicion.
- `LINX_SYSCALL_TRACE=1` logs Linx hosted syscall entry and ACRE return pairs
  with syscall number, BPC/TPC, arguments, return value, and cstate. Narrow
  with `LINX_SYSCALL_TRACE_NR` as one number or a comma-separated list,
  `LINX_SYSCALL_TRACE_LIMIT`, and `LINX_SYSCALL_TRACE_PC_LO/HI`.
- `LINX_SYSCALL_TRACE_STRINGS=1` augments syscall tracing with separate
  `LINX_SYSCALL_ARGSTR` records for pathname arguments. Bound reads with
  `LINX_SYSCALL_TRACE_STRING_MAX=<1..255>` so path/fd failures can be
  diagnosed without enabling full memory traces.
- `LINX_SYSCALL_TRACE_DUMP_ARG=<0..5>` dumps one syscall argument buffer on
  `LINX_SYSCALL_RETURN` as `LINX_SYSCALL_ARGDUMP`. Bound the read with
  `LINX_SYSCALL_TRACE_DUMP_BYTES=<1..256>`; the default is 64 bytes when an
  argument is selected. This is the low-noise copyout check for stat, ioctl,
  and similar output-buffer paths.
- `LINX_SYSCALL_TRACE_REGS=1` prints a `LINX_SYSCALL_REGS` record for each
  traced syscall entry and return with the full Linx GPR file. This is useful
  when return-value clobbering, TLS state, or caller-save handling is suspect.
- `LINX_ACRE_TRACE=1` logs filtered ACRE/trap-return handoff records before
  block-state restore (`phase=entry`) and after resume staging
  (`phase=staged`). Narrow with `LINX_ACRE_TRACE_PC`, `_PC_LO/_PC_HI`,
  `_BPC`, `_BPC_LO/_BPC_HI`, `_COUNT_LO/_COUNT_HI`, `_TARGET`, `_RRA`, and
  `_TRAPNUM`; set `LINX_ACRE_TRACE_LIMIT=0` only for deliberately unbounded
  short runs. Add `LINX_ACRE_TRACE_REGS=1` or
  `LINX_ACRE_TRACE_CODE_BYTES=<n>` for focused register/code snapshots.
  Matching `LINX_QEMU_ACRE_TRACE_*` aliases are accepted. Use this instead of
  the older all-or-nothing `LINX_DEBUG_ACRE_STDERR=1` on SPEC rows.
- `--guest-heartbeat-sec <n>` keeps guest-side child/output liveness logging
  lightweight by default. Use `--guest-proc-diagnostics` or
  `LINX_SPEC_GUEST_PROC_DIAGNOSTICS=1` only when `/proc/<pid>/status`,
  `/proc/meminfo`, `/proc/vmstat`, and `/proc/pressure/memory` dumps are
  needed, because those extra guest syscalls can perturb startup fault paths.
- `LINX_FAULT_TRACE_REGS=1` prints a `LINX_FAULT_REGS` record after
  `LINX_FAULT_TRACE` reports a synchronous trap, again with the full GPR file.
- `LINX_TRACE_REGS=1` enables both syscall and fault register records.
- `LINX_HEARTBEAT_REGS=1` or `LINX_QEMU_HEARTBEAT_REGS=1` prints
  `LINX_HEARTBEAT_REGS` companion records with all GPRs at heartbeat sites.
  Use this only for focused runs; the normal train-all loop keeps it disabled.
- `LINX_HEARTBEAT_CODE_BYTES=<n>` or `LINX_QEMU_HEARTBEAT_CODE_BYTES=<n>`
  prints `LINX_HEARTBEAT_CODE` companion records with code bytes at PC and BPC.
  This is useful when runtime mapping is ambiguous and guest `/proc/<pid>/maps`
  is unavailable.
- `LINX_FCMP_TRACE=1` or `LINX_FP_TRACE=1` records scalar FP compare helpers
  without enabling a full instruction trace. Narrow with
  `LINX_FCMP_TRACE_PC_LO/HI`, `LINX_FCMP_TRACE_COUNT_LO/HI`,
  `LINX_FCMP_TRACE_LIMIT`, and `LINX_FCMP_TRACE_OP=feq,flt,fge`; matching
  `LINX_FP_TRACE_*` aliases are accepted. Records include op, instruction
  count, PC, BPC, TPC, source type, raw operands, interpreted `f64`/`f32`
  values, result, and FCSR. Use this first for range/arithmetic failures where
  scalar compare operands or materialized FP constants are suspect.
- `LINX_DEBUG_PC_WATCH=<pc>[,<pc>...]` prints focused architectural state when
  translation reaches specific PCs. Add `LINX_DEBUG_PC_WATCH_REGS=1` to emit
  `LINX_PC_WATCH_REGS` full-GPR companion records; `LINX_TRACE_REGS=1` also
  enables the PC-watch register records. Use `LINX_DEBUG_PC_WATCH_EXIT=1` only
  for short smoke checks.
- `LINX_DEBUG_PC_WATCH_DUMP_CODE_BYTES=<n>` adds a `LINX_PC_WATCH_CODE`
  companion record with up to 32 bytes at the watched PC.
- `LINX_DEBUG_PC_WATCH_DUMP_REGS=<reg>[,<reg>...]` dumps guest words from
  several GPR/TP/TQ/UQ pointer sources in one PC-watch hit. It shares
  `LINX_DEBUG_PC_WATCH_DUMP_WORDS`, `LINX_DEBUG_PC_WATCH_DUMP_OFFSET`, and
  optional `LINX_DEBUG_PC_WATCH_DUMP_OFFSETS=<off>[,<off>...]` with the
  single-source `LINX_DEBUG_PC_WATCH_DUMP_REG` path. Use the offset list when
  allocator/list/frame corruption needs several slots from the same
  multi-billion-instruction run without rerunning the window.
- `LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS=<off>[,<off>...]` reads a 64-bit guest
  pointer from each selected source plus offset and dumps the pointee memory
  with the same word count and width controls. Use it for stack frames or SV/C++
  objects where the decisive state is one pointer hop away.
- `LINX_DEBUG_PC_WATCH_DUMP_WIDTH=1|2|4|8` changes the unit size for focused
  PC-watch memory dumps. The default is still 8-byte words with the old log
  shape; set width 4 for 32-bit flag fields, width 2 for packed halfwords, and
  width 1 for byte-level object or string fields.
- `LINX_DEBUG_PC_WATCH_COUNT_LO=<insns>` and
  `LINX_DEBUG_PC_WATCH_COUNT_HI=<insns>` arm PC matching only inside the chosen
  instruction-count window. Use this for late SPEC user faults after a
  fault-trace run has found the failing count; the PC-watch hit counter is then
  local to the armed window. The translator emits the host debug hook only for
  exact watched PCs, so PC-watch does not globally instrument reset-to-userspace
  execution.
- `LINX_DEBUG_PC_WATCH_PRINT=0` suppresses immediate `linx_pc_watch:` output
  after the selected PC/count/hit/GPR filters pass. Pair it with
  `LINX_DEBUG_PC_WATCH_RING=1` to record matching hits in a bounded ring and
  dump them only when `LINX_FAULT_TRACE` reports a synchronous fault. Tune the
  retained window with `LINX_DEBUG_PC_WATCH_RING_SIZE=<1..128>`. This is the
  preferred path when synchronous PC-watch printing perturbs a SPEC failure.
  Add `LINX_DEBUG_PC_WATCH_RING_MEM_REG=<gpr|tp|tqN|uqN|t#N|u#N>` and
  `LINX_DEBUG_PC_WATCH_RING_MEM_OFFSET=<bytes>` when each deferred ring entry
  must also snapshot a guest 64-bit word derived from a watched pointer.
- `LINX_TP_TRACE=1` records user-to-kernel TP handoff points for service
  requests, synchronous traps, IRQ entry, same-ACR trap/IRQ frame creation, and
  ACRE staging. Same-ACR frame records include the interrupted `x1` value saved
  into ETEMP. Use `LINX_TP_TRACE_LIMIT=<n>` on full SPEC runs.
- `LINX_TP_TRACE_SSR=1` adds TP/ETEMP/ETEMP0 SSR writes and swaps to
  `LINX_TP_TRACE`. `LINX_TP_TRACE_READS=1` adds reads. These are high-volume
  options for focused runs, not for train-all profiling.

## 2026-06-30 9p TLBI Trace

A focused 9p host sample for `999.specrand_ir` under
`workloads/generated/specint-profile-999-9p-current-20260630-r1/` showed visible
CPU-thread time in `helper_linx_tlb_iall`, `tlb_flush_by_mmuidx_async_work`, and
`tcg_flush_jmp_cache`. The new `LINX_TLB_TRACE` switch was added to determine
whether that cost is boot setup, 9p mount setup, or benchmark steady state.

Evidence:

- `workloads/generated/specint-tlbtrace-999-9p-20260630-r1/999_specrand_ir/run_001/qemu.log`
  records the first 80 invalidations. Apart from two reset-time low-address
  entries, all entries are before `LINX_SPEC_START` and symbolize through
  `kernel/linux/build-linx-fixed/System.map` to `get_pmd_virt_fixmap`,
  `get_pud_virt_fixmap`, and `get_p4d_virt_fixmap`.
- `workloads/generated/specint-tlbtrace-999-9p-postboot-20260630-r2/` reruns the
  same row with `LINX_TLB_TRACE_COUNT_LO=1000000000`. It emits zero
  `LINX_TLB_TRACE` records after the first heartbeat bucket while QEMU heartbeat
  reaches `count=5000000018`, `progress=site-change`, and
  `heartbeat_site_progress=true`.

Conclusion: the TLBI hot frames in whole-process samples are real, but for this
9p SPEC sentinel they are boot/fixmap biased, not the current post-start SPEC
bottleneck. Future host profiles must either start sampling after
`LINX_SPEC_START` or use QEMU count filters before optimizing the sampled top
frame.

Speedup candidates:

- QEMU: `tlb.iv` and the Linux packed-VA form of `tlb.iav` now use
  `tlb_flush_page()` plus page-scoped BSTART-cache invalidation instead of
  routing through full `tlb_flush()`. Preserve full flush for `tlb.iall` and
  keep `tlb.ia` conservative until QEMU models ASID-tagged TLB entries
  independently from TTBR/MMU-index state.
- QEMU: a future BSTART validation cache should move from direct-mapped target
  tags to page/generation-aware invalidation if self-modifying text or
  page-remap churn becomes visible in post-start profiles; current page-scoped
  TLBI only clears entries on the invalidated VA page.
- Linux: reduce redundant fixmap clear/set invalidations in
  `arch/linx/mm/init.c` during early page-table construction. This is a
  boot-time speed lane and should be validated with a boot/userspace proof before
  applying it to SPEC throughput claims.
- SPEC steady state: focus next on allocator/free-list heartbeat BPCs such as
  `kfree`/`__update_cpu_freelist_fast`, template/BSTART helper samples, tile
  block reset/set helpers, and 9p I/O transport overhead. Use initramfs
  `999.specrand_ir` as the cheap correctness sentinel; use 9p
  `999.specrand_ir` as the transport/profiling sentinel until a block-backed
  SPEC transport exists.

2026-06-30 page-scoped TLBI update: QEMU commit candidate
`target/linx/{helper.c,helper.h,translate.c}` splits the TLB maintenance
helpers. `tlb.iall` still performs a full local flush and full BSTART-cache
reset. `tlb.ia` now logs the ASID operand but remains a full flush because the
current QEMU TLB is not independently ASID-tagged. `tlb.iv` and Linux's packed
`tlb.iav` operand perform a one-page flush across all QEMU MMU indexes and only
clear BSTART-cache entries on the affected VA page. Validation evidence:
`avs/qemu/out/musl-mprotect-adjacent-tlbiv-pageflush-20260630-r1/summary.json`
passes and its log records `LINX_TLB_TRACE op=iv ... operand=...`;
`workloads/generated/specint-train-smoke-tlbiv-pageflush-20260630-r1/` passes
strict train `999.specrand_ir`; and focused
`workloads/generated/specint-502-tlbiv-pageflush-20260630-r1/` keeps
`502.gcc_r` in heartbeat-backed `live-timeout` with no `LINX_USER_TRAP`. This
closes the QEMU-side boot TLBI overshoot without changing the live-slow SPEC
steady-state owner list.

2026-06-30 scalar tile-commit guard update: a focused post-`LINX_SPEC_START`
host sample of train `531.deepsjeng_r` in
`workloads/generated/specint-profile-531-current-20260630-r1/profile/qemu-531-current.sample.txt`
showed `helper_linx_tile_commit` still visible in scalar SPEC blocks even
though no tile descriptor was pending. `target/linx/translate.c` now emits a
runtime guard around the helper and calls `linx_tile_commit` only when
`tile_iot_valid != 0`; this preserves descriptor state that may have been
decoded in an earlier TB while removing the no-op scalar helper call. The
follow-up sample
`workloads/generated/specint-profile-531-tilecommit-guard-20260630-r1/profile/qemu-531-tilecommit-guard.sample.txt`
has zero `helper_linx_tile_commit` occurrences by string-count comparison.
Validation evidence: `python3 avs/qemu/run_tests.py --all --timeout 20`,
`bash avs/qemu/check_system_strict.sh`, and
`workloads/generated/specint-train-smoke-tilecommit-guard-20260630-r1/` all
pass. The standalone `avs/qemu/run_tests.py --suite tile --timeout 120`
timeout reproduces after rebuilding the baseline without the guard, so that
row remains a pre-existing tile-suite duration/coverage lane rather than this
SPEC scalar fast-path proof.

2026-06-30 9p storage-init runner update: a latest-QEMU all-train 9p rerun at
`workloads/generated/specint-train-all-tilecommit-guard-9p-20260630-r1/`
exposed a false setup failure: every row reached `LINX_SPEC_START`, then failed
`chdir-rundir` after `mount("spec2017", "/spec", "9p", ...)` returned `-ENODEV`.
The missing ingredient was the Linx storage-init bootarg used by the earlier
successful 9p evidence. `tools/spec2017/run_int_rate_qemu.py` now centralizes
kernel command-line construction and auto-adds `linx_storage_init=1` for 9p
transport unless explicitly overridden. Unit coverage in
`tools/spec2017/test_run_int_rate_qemu.py` locks the default, explicit override,
and forced virtio-mmio override behavior. The fixed 9p sentinel
`workloads/generated/specint-999-9p-storageinit-auto-20260630-r1/` proves the
transport setup reaches live execution again; the interrupted all-train followup
`workloads/generated/specint-train-all-storageinit-auto-9p-20260630-r1/` shows
the same command-line fix advancing through multiple train rows with heartbeat
site progress. Post-fix host sampling from that run keeps the QEMU hot list on
`helper_linx_template_step`, BSTART validation, `linx_is_bstart_at_addr`, and
`probe_access_flags`; `helper_linx_tile_commit` remains absent.

Static build command. Rebuild the SPEC-profile C++ runtime overlay after every
phase-b musl sysroot refresh; the musl install step replaces the sysroot
library directory, so a plain SPEC build otherwise fails the C++ benchmarks
with missing `-lc++`, `-lc++abi`, and `-lunwind`.

```bash
MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh

./tools/build_linx_llvm_cpp_runtimes.sh \
  --profile spec \
  --mode phase-b

LINX_SPEC_FORCE_STATIC=1 \
bash tools/spec2017/build_int_rate_linx.sh \
  --mode phase-b \
  --force-static \
  --emit-manifest workloads/generated/specint-build-after-oldmalloc-20260628/build_manifest_final.json
```

Original 600s static train-all run command, superseded for the active loop by
the 300s run below:

```bash
SPECINT_TRAIN_ALL_TIMEOUT=600 \
LINX_SPEC_HEARTBEAT_SEC=30 \
LINX_SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
LINX_SPEC_NO_PROGRESS_TIMEOUT=180 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --out-dir workloads/generated/specint-train-all-20260628-static \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --append-extra norandmaps \
  --guest-heartbeat-sec 0 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 180 \
  --continue-on-fail
```

Earlier rerun after the Linx oldmalloc early-page-size fix and C++ runtime
overlay rebuild. This used the redesigned faster 300s train-all budget:

```bash
SPECINT_TRAIN_ALL_TIMEOUT=300 \
LINX_SPEC_HEARTBEAT_SEC=30 \
LINX_SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
LINX_SPEC_NO_PROGRESS_TIMEOUT=180 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --out-dir workloads/generated/specint-train-all-20260628-after-oldmalloc \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --append-extra norandmaps \
  --guest-heartbeat-sec 0 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 180 \
  --continue-on-fail
```

Diagnostic rerun after the heartbeat-code-byte QEMU extension,
heartbeat-register smoke, PC-watch register/code-byte smoke, the QEMU
nested-CALL header hardening, and focused memtrace context/ACR filtering. This
was the first 180s all-train heartbeat loop:

```bash
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-all-20260628-qemu-dump-regs-r1 \
  --append-extra norandmaps \
  --guest-heartbeat-sec 0 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 50000000 \
  --no-progress-timeout 120 \
  --continue-on-fail
```

Current train-all loop. This rerun uses the same all-ten SPECint train suite,
rebuilt QEMU `v10.2.0-970-g8dd1dcdbde2`, initramfs transport, no guest
heartbeat, QEMU heartbeat every 1B guest instructions, a `2G` stack limit, the
mallocng-default phase-b musl sysroot, and a refreshed spec C++ runtime overlay.
The SPEC runner treats
`LINX_USER_TRAP` as terminal failure evidence and records it as the primary
class even when the parent init process would otherwise keep polling until a
timeout. The generated init wrapper also installs the SPEC stack limit with a
raw `prlimit64` syscall before falling back to libc `setrlimit()`, which
bypasses the current libc return-value bug. The forced-static C++ startup
evidence from `workloads/generated/specint-520-cxx-startup-fix-20260629-r1`
still proves the old `_start`/constructor issue is closed; the latest all-train
run shows C++ rows now stop as child-exit wrapper rows with `sig=9`, not startup
traps.

```bash
python3 tools/spec2017/run_stage_qemu_matrix.py \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --stage b \
  --input-set train \
  --transports initramfs \
  --sysroot out/libc/musl/install/phase-b \
  --timeout 300 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 180 \
  --guest-heartbeat-sec 0 \
  --append-extra norandmaps \
  --dump-prefix-bytes 256 \
  --stack-limit 2G \
  --symbolize-heartbeat \
  --out-dir workloads/generated/specint-train-all-latest-qemu-20260630-r1
```

The refreshed run reports `ok=false` after `2609.965s`: `999.specrand_ir`
passes strict hash `0x973dcfc2`; `500.perlbench_r` run_001 passes
`perfect.b.3.out` by hash and run_002 times out live; `502.gcc_r` is now a
heartbeat-backed live timeout rather than the old `LINX_USER_TRAP`; `505`,
`531`, and `557` are live timeouts; `520`, `523`, and `541` are wrapper
child-exit rows with `sig=9`; and `525.x264_r` is classified as
`kernel-panic-loop-timeout`. That split keeps the 502 compiler correctness lane
closed and routes remaining work to throughput profiling, wrapper/kill cause
capture, and a focused kernel panic-path probe.

Post-branch-fix all-train rerun. QEMU commit `085f20cc8bd` fixes the AVS
branch D0D2 failure where a predicated `FALL` edge skipped a marker-only
`DIRECT` trampoline but then entered the following `COND` header with
`cond/carg` reset. The QEMU rebuild passes `avs/qemu/run_tests.py --suite
branch --timeout 20`, `avs/qemu/run_tests.py --suite system --timeout 20`,
`avs/qemu/check_system_strict.sh`, and `avs/qemu/run_tests.py --all --timeout
20`.

The fresh all-SPECint train loop is
`workloads/generated/specint-train-all-post-branchfix-20260630-r1/`. It uses
the same all-ten train suite, rebuilt QEMU from the branch fix, initramfs
transport, `SPECINT_TRAIN_ALL_TIMEOUT=180`, QEMU heartbeat every 1B guest
instructions, `--no-progress-timeout 180`, `--stack-limit 2G`, and
`LINX_SPEC_SYMBOLIZE_HEARTBEAT=1`. The nested matrix command requested all ten
rows and completed in `1318.613s`; `999.specrand_ir` passed and the other rows
failed as follows:

| Bench | Class | Last BPC | Heartbeat | Current owner |
| --- | --- | --- | --- | --- |
| `500.perlbench_r` | `live-timeout` | `0xffffffff803d3a60` | `site-change`, count `107000000000` | Throughput: kernel maple-tree/mmap hot path after the old compiler bad-target failure is closed. |
| `502.gcc_r` | `user-trap` | `0x15557418b4` | `site-change`, count `6000000001` | Correctness: new trap at `addr=0x3f7fa8d010`, `tpc=0x1556088006`, `bpc=0x1556087ff4`; rerun with syscall/fault trace and symbolize the static-PIE slide before treating 502 as only slow. |
| `505.mcf_r` | `live-timeout` | `0x155555d0c6` | `site-change`, count `49000000005` | Throughput: user-space hot loop; profile post-`LINX_SPEC_START` before changing QEMU helpers. |
| `520.omnetpp_r` | `live-timeout` | `0xffffffff803d3ac0` | `site-change`, count `39000000004` | Throughput/kernel logging or VM path: no longer an immediate wrapper child-exit in this run. |
| `523.xalancbmk_r` | `live-timeout` | `0xffffffff8006c9b2` | `site-change`, count `42000000005` | Throughput/kernel logging path; check repeated printk/vsprintf/ring-buffer activity before blaming C++ runtime. |
| `525.x264_r` | `kernel-panic` | `0x0` | no running heartbeat | Transport/rootfs: initramfs panics with `VFS: Unable to mount root fs`; use 9p or add a block-backed SPEC root instead of growing the CPIO path. |
| `531.deepsjeng_r` | `live-timeout` | `0x15555630a8` | `site-change`, count `44000000009` | Throughput: user-space control-flow hot loop; keep as CPU stress sentinel. |
| `541.leela_r` | `live-timeout` | `0xffffffff803e0e5a` | `site-change`, count `41000000005` | Throughput/kernel string/memset path; investigate kernel log/memory churn after stack-limit traps remain closed. |
| `557.xz_r` | `live-timeout` | `0x155558d218` | `site-change`, count `36000000006` | Throughput: user-space compression loop; profile helper mix and timer/fault heartbeat sites. |
| `999.specrand_ir` | pass | `0x0` | finishes before heartbeat | Keep as the cheap strict-hash train sentinel. |

This run proves the all-row loop itself is not deadlocked: every timeout row
has QEMU BPC heartbeat progress. The next QEMU speed work should therefore use
post-start host sampling and the BPC ledger to avoid boot-biased samples. Start
with user-space rows (`505`, `531`, `557`) for target-helper/TB-cache cost,
then kernel-heavy rows (`500`, `520`, `523`, `541`) for maple-tree, printk, and
string/memset churn. Keep `502` separate as a correctness bug until the new
page-near trap is explained, and keep `525` on the transport/rootfs lane.

Heartbeat-stall train-all rerun. The latest all-ten initramfs loop using the
same branch-fix QEMU plus the heartbeat same-site warning switch is
`workloads/generated/specint-train-all-hbstall-qemu-20260630-r1/`:

```bash
LINX_QEMU_HEARTBEAT_SAME_SITE_WARN=4 \
SPECINT_TRAIN_ALL_TIMEOUT=180 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --suite train-all \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-all-hbstall-qemu-20260630-r1 \
  --append-extra "norandmaps ignore_loglevel loglevel=8 linx_vm_trace=1 linx_vm_trace_addr=0x3f7fa8d000" \
  --guest-heartbeat-sec 0 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 120 \
  --stack-limit 2G \
  --symbolize-heartbeat \
  --continue-on-fail
```

The aggregate finished in `1319.795s` with `ok=false`, but every current
SPECint C/C++ train row was attempted. `999.specrand_ir` passed strict train
hash `0x973dcfc2`. `502.gcc_r` reproduced the current VM correctness stop at
`addr=0x3f7fa8d010`; `525.x264_r` reproduced the initramfs VFS root panic.
The other failed rows were live-slow, not hard-deadlocked:

| Bench | Class | Last BPC | Heartbeat / stall evidence | Current owner |
| --- | --- | --- | --- | --- |
| `500.perlbench_r` | `live-timeout` | `0xffffffff803d3dfa` | site progress | Kernel-heavy throughput/profiling lane. |
| `502.gcc_r` | `user-trap` | `0x15557e88e8` | site progress before `LINX_USER_TRAP` | Linux VM/VMA/mprotect correctness lane, confirmed by focused VM trace. |
| `505.mcf_r` | `live-timeout` | `0x155555cbe2` | site progress | User-space throughput lane. |
| `520.omnetpp_r` | `live-timeout` | `0xffffffff803d407c` | site progress | Kernel-heavy throughput lane; no current wrapper child-exit in this loop. |
| `523.xalancbmk_r` | `live-timeout` | `0xffffffff8006af74` | site progress | Kernel-heavy throughput lane. |
| `525.x264_r` | `kernel-panic` | `0x0` | `LINX_PANIC ... VFS: Unable to mount root fs` | Initramfs/rootfs transport lane; use 9p or block-backed transport for train execution. |
| `531.deepsjeng_r` | `live-timeout` | `0x15555683b2` | site progress plus `LINX_HEARTBEAT_STALL status=same-site-running repeats=4 threshold=4` | CPU throughput lane; same-site warning works, but later site progress means not a proven deadlock. |
| `541.leela_r` | `live-timeout` | `0xffffffff803d1a44` | site progress | Kernel-heavy throughput lane. |
| `557.xz_r` | `live-timeout` | `0x155558d708` | site progress | User-space throughput lane. |
| `999.specrand_ir` | pass | n/a | strict hash pass before heartbeat needed | Keep as cheap correctness sentinel. |

Updated loop rule: use this heartbeat-stall configuration for bounded
all-train diagnostics and reserve `LINX_HEARTBEAT_REGS`,
`LINX_HEARTBEAT_CODE_BYTES`, `LINX_TLB_FILL_TRACE*`, and
`LINX_FAULT_TRACE*` for focused single-row runs. For speed profiling, disable
or coarsen heartbeat and start host sampling after `LINX_SPEC_START`, otherwise
kernel boot, printk/vsprintf, and early page-table setup dominate the sample.

Bounded test+train all-row rerun (2026-07-01). The fast gate now has a
`test-all` suite and `test-train` profile so every supported SPECint C/C++ row
can run with bounded `test` and `train` inputs before refrate-scale work. The
static rebuild manifest is
`workloads/generated/specint-build-all-20260701-r1/build_manifest.json`;
`overall_ok=true` and all ten selected rows were built:
`500.perlbench_r`, `502.gcc_r`, `505.mcf_r`, `520.omnetpp_r`,
`523.xalancbmk_r`, `525.x264_r`, `531.deepsjeng_r`, `541.leela_r`,
`557.xz_r`, and `999.specrand_ir`.

The QEMU run ledger is
`workloads/generated/specint-test-train-all-hashclass-20260701-r1/`, using
`SPECINT_TEST_ALL_TIMEOUT=120`, `SPECINT_TRAIN_ALL_TIMEOUT=180`,
`SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000`,
`LINX_QEMU_HEARTBEAT_SAME_SITE_WARN=4`, initramfs transport, 2 GiB guest
memory, `--stack-limit 2G`, and rebuilt QEMU `v10.2.0-987-g08783bb4572`.
The profile completed in `1452.145s` and attempted all ten rows in both
suites. It is intentionally red:

| Bench | `test` result | `train` result | Current owner |
| --- | --- | --- | --- |
| `500.perlbench_r` | `user-trap`, addr 0 | `user-trap`, addr 0 | Correctness: focused rerun closed the final null-RA frame-restore cause; the remaining failure is a later addr-zero user trap. |
| `502.gcc_r` | `user-trap`, addr 0 | `user-trap`, addr 0 | Correctness: rerun with focused fault/TLB trace and user slide symbols. |
| `505.mcf_r` | wrapper child exit, code 255 | wrapper child exit, code 255 | Wrapper/runtime exit-status lane. |
| `520.omnetpp_r` | `user-trap`, addr 0 | `user-trap`, addr 0 | Correctness: same addr-zero class as 500/502. |
| `523.xalancbmk_r` | live timeout, heartbeat site progress plus same-site warning | live timeout, heartbeat site progress | Throughput; the same-site warning did not prove deadlock. |
| `525.x264_r` | VFS root panic before SPEC start | VFS root panic before SPEC start | Transport/rootfs: use 9p or block-backed SPEC root for large inputs. |
| `531.deepsjeng_r` | guest pass, host hash mismatch (`test.out`, 102 bytes vs 3611) | guest pass, host hash mismatch (`train.out`, 102 bytes vs 35012) | C++ runtime/codegen correctness. Focused trace shows exec succeeds but the child emits `Allocated Workload not found` without a child-side file syscall for `test.txt`; C stdio controls pass while static C++ smoke traps. |
| `541.leela_r` | live timeout, heartbeat site progress | wrapper child exit, signal 9 after BPC progress | Resource/kill-cause plus throughput lane. |
| `557.xz_r` | `user-trap`, addr 0 | `user-trap`, addr 0 | Correctness: same addr-zero class as 500/502/520. |
| `999.specrand_ir` | guest pass, host hash mismatch (`rand.24239.out`, 310 bytes vs 616074) | live timeout, heartbeat site progress | Recheck under no host contention; keep as cheap strict-hash sentinel when stable. |

Loop update: the all-row `test-train` gate is now the preferred bounded
bring-up ledger when a change may affect SPEC broadly. The current runner
records guest-pass/output-verification failures as `hash-mismatch` in the
matrix, so treat those separately from guest execution failures: the guest
reached `LINX_SPEC_PASS`, but host-side output verification failed. For QEMU profiling,
drop `ignore_loglevel loglevel=8` and use coarse or disabled heartbeat after
`LINX_SPEC_START`; the verbose diagnostic shape above is for failure
classification, not speed measurement.

Post-MMIO-hole all-row rerun (2026-07-01): the current broad ledger is
`workloads/generated/specint-test-train-all-mmiohole-qemu-20260701-r1/`, using
rebuilt QEMU `v10.2.0-989-g5cfb672a711`, initramfs transport,
`SPECINT_TEST_ALL_TIMEOUT=120`, `SPECINT_TRAIN_ALL_TIMEOUT=180`,
`SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000`,
`LINX_QEMU_HEARTBEAT_SAME_SITE_WARN=4`, 2 GiB guest memory, and
`--stack-limit 2G`. It completed in `1815.369s` (`test-all` `760.983s`,
`train-all` `1054.386s`) and attempted all ten rows in both suites. It remains
red, but the failure mix changed materially from the pre-MMIO-hole ledger:

| Bench | `test` result | `train` result | Current owner |
| --- | --- | --- | --- |
| `500.perlbench_r` | `live-timeout`, BPC site progress at `0xffffffff800f515c` | `live-timeout`, BPC site progress at `0xffffffff8011217c` | Throughput/live-progress lane. The old stack-MMIO null-RA path is closed; keep focused user-fault symbolization for the later 500 trap from `specint-500-mmio-hole-fix-normal-store-20260701-r1/`, but the broad bounded row is now live-slow. |
| `502.gcc_r` | `live-timeout`, BPC site progress at `0xffffffff803e4288` | `user-trap`, `addr=0x16556734c2`, `tpc=0x155608c714`, `bpc=0x155608c710` | Train correctness lane. Symbolize the static PIE PC and trace TLB/protection state around the final user access; test input is currently live-slow, not trapping. |
| `505.mcf_r` | wrapper child exit, code 255, `inp.out` hash `0xfa8752d1` size 249 | wrapper child exit, code 255, same short `inp.out` | Wrapper/runtime exit-status lane. Add focused child stderr/output prefix and syscall tracing before changing QEMU semantics. |
| `520.omnetpp_r` | `live-timeout`, BPC site progress at `0xffffffff800f9354` | `user-trap`, `addr=0x16555d2c57`, `tpc=0x15557e5abc`, `bpc=0x15557e5ab8` | Train correctness lane, likely shared with 502's late user-access fault class. |
| `523.xalancbmk_r` | `live-timeout`, BPC site progress at `0xffffffff803e47a6` | `live-timeout`, BPC site progress at `0xffffffff800fe658` | Throughput/live-progress lane; heartbeat proves execution is moving, not deadlocked. |
| `525.x264_r` | VFS root panic before SPEC start | VFS root panic before SPEC start | Transport/rootfs lane. Do not keep pushing this through large initramfs; use 9p or a block-backed SPEC root for large inputs. |
| `531.deepsjeng_r` | guest `LINX_SPEC_PASS`, host `test.out` hash mismatch: 102 bytes `0xd442eeea` vs 3611 bytes `0x391c9299` | guest `LINX_SPEC_PASS`, host `train.out` hash mismatch: 102 bytes `0xd442eeea` vs 35012 bytes `0x0aa753bf` | Output/runtime correctness lane; focused trace still points at C++ runtime/codegen rather than input packaging. |
| `541.leela_r` | `live-timeout`, BPC site progress at `0xffffffff803e3112` | `live-timeout`, BPC site progress at `0xffffffff800fcce8` | Throughput/live-progress lane. |
| `557.xz_r` | `live-timeout`, BPC site progress at `0xffffffff803e3112` | wrapper child exit, code 1, `input.combined-40-8.out` hash `0xa80f31ed` size 37 | Split lane: test input is live-slow; train input needs wrapper/benchmark stderr and child-failure tracing. |
| `999.specrand_ir` | guest `LINX_SPEC_PASS`, host `rand.24239.out` hash mismatch: 310 bytes `0xc38a3bc5` vs 616074 bytes `0x64732c02` | guest `LINX_SPEC_PASS`, host `rand.11.out` hash mismatch: 310 bytes `0xc38a3bc5` vs 871 bytes `0x973dcfc2` | Strict output-validation lane; guest execution passes, so keep separate from QEMU/user-trap correctness. |

This rerun confirms the BPC heartbeat switch is useful for triage: every
`live-timeout` row reports `running/site-progress site-change`, so those rows
are slow/profiling work rather than proven deadlocks. The immediate correctness
targets are train `502.gcc_r` and train `520.omnetpp_r`; the immediate harness
targets are `505.mcf_r`, train `557.xz_r`, and the strict-hash output rows.

Focused 500 MMIO-hole update (2026-07-01): the final
`FRET.STK [ra ~ s5], sp!, 80` null-RA failure was rooted in the Linx `virt`
device tree exposing the virtio-mmio page as allocatable RAM when SPEC runs
with large guest memory. The focused evidence is
`workloads/generated/specint-500-tlb-fill-stackpage-20260701-r1/`: the stack
page refill mapped the user stack page to PA `0x30001000`, which is
`LINX_VIRTIO_MMIO_BASE`, so `probe_write()` returned no RAM host pointer and
the saved RA read back as zero. QEMU now splits `/memory@0/reg` around the
UART/exit, test-finisher, and full virtio-mmio windows, rounded to 4 KiB page
boundaries. The validation rerun is
`workloads/generated/specint-500-mmio-hole-fix-normal-store-20260701-r1/`; the
formerly bad FENTRY slot now records `ra@0x3fdd764798 = 0x15558292f0` with
matching `mmu_readback`, `host_readback`, and debug readback while the frame
store still uses the normal QEMU store helper. That run still fails, but the
new failure is later: `LINX_FAULT_TRACE` reports an addr-zero user trap at
`tpc=0x1555622dba`, `bpc=0x1555622db2`, after BPC heartbeat progress to
35.0B guest instructions. Next 500 owner: symbolize the new user PC and trace
the store/load or call path around that later addr-zero fault; do not reopen
the old stack-page MMIO corruption unless it reproduces.

Focused 531 update (2026-07-01): the narrowed filesystem trace under
`workloads/generated/specint-531-test-filesys-trace-20260701-r1/` used
`LINX_SYSCALL_TRACE_NR=48,56,78,79,221,291` and showed wrapper cwd/pre-exec
state is correct, `execve("/spec-run/deepsjeng_r_base.mytest-m64", ...)`
enters the child, and no child-side `openat`/`newfstatat`/`faccessat` for
`test.txt` occurs before the short output. A musl control run under
`workloads/generated/musl-control-stdio-cpp-20260701-r1/` passes static C
`file_stdio` and `printf_string_arg` but fails static `cpp17_smoke` with a user
trap. Keep 531 in the C++ runtime/codegen lane until that control lane is green.

Focused `525.x264_r` follow-up split that panic-path probe into transport work.
The initramfs train lane builds a 1.6 GiB CPIO and never reaches
`LINX_SPEC_START`; a PC-watch run on `panic()`/`vpanic()` with
`LINX_CALL_TRACE_RING=1` and `LINX_DEBUG_PC_WATCH_DUMP_CALL_RING=1` captures
the first panic string as `VFS: Unable to mount root fs on "%s" or %s`, with the
caller ring ending in `init/do_mounts.c`. A 4096 MiB rerun reproduces the same
VFS root panic, so this is not only a 2 GiB guest-memory limit. The SPEC 9p lane
now mounts successfully after the Linx usercopy and virtio feature-read fixes:
`workloads/generated/specint-525-9p-vmgetfeatures-wordfix-20260630-r1/` shows
the 9p mount-tag feature reaching the guest and both SPEC mounts returning zero.
The current 525 9p row reaches `LINX_SPEC_START` and classifies as
`live-timeout`, so its active owner is throughput/output validation on a
large-input transport, not the old `mount()` `-EFAULT` path. If 9p overhead stays
too high for full SPEC correctness, add a virtio-blk/ext2 SPEC transport instead
of duplicating large train inputs into initramfs.

Focused `500.perlbench_r` rerun after adding the scalar FP-compare trace in
QEMU commit `b5e90c7db5f`:

```bash
LINX_FCMP_TRACE=1 \
LINX_FCMP_TRACE_PC_LO=0x15556613ba \
LINX_FCMP_TRACE_PC_HI=0x15556614e0 \
LINX_FCMP_TRACE_OP=flt,fge \
LINX_FCMP_TRACE_LIMIT=128 \
LINX_SPEC_DUMP_PREFIX_BYTES=256 \
python3 tools/spec2017/run_stage_qemu_matrix.py \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --stage b \
  --input-set train \
  --transports initramfs \
  --sysroot out/libc/musl/install/phase-b \
  --timeout 180 \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --no-progress-timeout 180 \
  --guest-heartbeat-sec 0 \
  --append-extra norandmaps \
  --dump-prefix-bytes 256 \
  --stack-limit 2G \
  --strict \
  --out-dir workloads/generated/specint-500-fcmp-trace-20260629-r2 \
  --bench 500.perlbench_r
```

Result: `workloads/generated/specint-500-fcmp-trace-20260629-r2` reproduces
the old `user-arithmetic-range` stop in `27.38s`. The QEMU log records
`LINX_FCMP_TRACE` lines for `S_outside_integer`: `fge.fd`/`flt.fd` compare
`1.0` against raw operands `0xdf000000`, `0x0`, and `0x5f800000`. Static
objdump confirms those operands come from `hl.lwu.pcr` immediately before
`.fd` compares, so 32-bit float bound constants are being interpreted as
64-bit doubles. That classified `500` as a Linx LLVM constant-pool/load-width
bug for double compare constants, not a QEMU FP helper issue. The follow-up
Linx LLVM fix adds a codegen regression and an AVS assembly gate, rebuilds all
SPECint binaries, and moves `500` to the live-timeout lane in
`workloads/generated/specint-train-all-f64-extload-fix-20260629-r1`.
The matrix summary now lifts this evidence into `fcmp_trace_seen`,
`fcmp_trace_count`, `fcmp_trace_last`, and bounded `fcmp_trace_samples` fields.

Artifacts:

- `workloads/generated/specint-build-after-oldmalloc-20260628/build_manifest_final.json`
- `out/cpp-runtime/musl-cxx17-spec/summary_phase-b.json`
- `avs/qemu/out/musl-static-oldmalloc-page-20260628/summary.json`
- `avs/qemu/out/musl-tp-preserve-20260628-r2/summary.json`
- `avs/qemu/out/musl-tp-preserve-debug-r2-20260628/summary.json`
- `workloads/generated/specint-cxx-after-oldmalloc-20260628/run/qemu_matrix_summary.json`
- `workloads/generated/specint-cxx-startup-fix-20260628/build_manifest.json`
- `workloads/generated/specint-cxx-stacklimit-20260628/qemu-focused/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-after-oldmalloc/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-after-oldmalloc/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-after-oldmalloc/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/run/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/run/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/profile/qemu-523-xalancbmk-r.sample.txt`
- `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/profile/qemu-531-deepsjeng-r.sample.txt`
- `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/profile/qemu-557-xz-r.sample.txt`
- `workloads/generated/specint-train-all-20260628-liveness-v2/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-liveness-v2/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-liveness-v2/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-nestedcall-fix-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-nestedcall-fix-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-nestedcall-fix-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-code-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-code-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-heartbeat-code-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-copyout-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-copyout-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-copyout-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-context-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-context-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-context-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-dump-regs-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-dump-regs-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260628-qemu-dump-regs-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260629-raw-prlimit-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260629-raw-prlimit-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260629-raw-prlimit-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260629-pcwatch-offsets-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260629-pcwatch-offsets-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260629-pcwatch-offsets-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-train-all-20260629-stack2g-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260629-stack2g-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260629-stack2g-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-520-cxx-startup-fix-20260629-r1/build_manifest.json`
- `workloads/generated/specint-520-cxx-startup-fix-20260629-r1/ctor-watch/stage_b_summary.json`
- `workloads/generated/specint-520-cxx-startup-fix-20260629-r1/ctor-watch/520_omnetpp_r/run_001/qemu.log`
- `workloads/generated/specint-train-all-20260629-cxx-startup-fix-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260629-cxx-startup-fix-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260629-cxx-startup-fix-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-build-mallocng-cxx-refresh-20260629-r1/build_manifest.json`
- `workloads/generated/specint-train-all-20260629-mallocng-cxx-refresh-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-20260629-mallocng-cxx-refresh-r1/train-all/qemu_matrix_summary.json`
- `workloads/generated/specint-train-all-20260629-mallocng-cxx-refresh-r1/train-all/initramfs/stage_b_summary.json`
- `workloads/generated/specint-500-fcmp-trace-20260629-r2/qemu_matrix_summary.json`
- `workloads/generated/specint-500-fcmp-trace-20260629-r2/initramfs/500_perlbench_r/run_001/qemu.log`
- `workloads/generated/specint-999-prlimit-trace-20260629-r1/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-999-raw-prlimit-20260629-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-502-raw-prlimit-20260629-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-heartbeat-regs-smoke-20260628/qemu_matrix_summary.json`
- `workloads/generated/specint-heartbeat-regs-smoke-20260628/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-pcwatch-regs-smoke-20260628-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-pcwatch-regs-smoke-20260628-r1/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-heartbeat-code-smoke-20260628-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-heartbeat-code-smoke-20260628-r1/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-pcwatch-dump-offsets-smoke-20260629-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-pcwatch-dump-offsets-smoke-20260629-r1/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-pcwatch-width-smoke-20260629-r2/qemu_matrix_summary.json`
- `workloads/generated/specint-pcwatch-width-smoke-20260629-r2/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-pcwatch-ptr-offset-smoke-20260629-r2/qemu_matrix_summary.json`
- `workloads/generated/specint-pcwatch-ptr-offset-smoke-20260629-r2/initramfs/999_specrand_ir/run_001/qemu.log`
- `workloads/generated/specint-500-ppflop-offsets-20260629-r1/initramfs/500_perlbench_r/run_001/qemu.log`
- `workloads/generated/specint-500-ppflop-sv-objects-20260629-r2/initramfs/500_perlbench_r/run_001/qemu.log`
- `workloads/generated/specint-500-ppflop-branch-ptrslots-20260629-r1/initramfs/500_perlbench_r/run_001/qemu.log`
- `workloads/generated/specint-500-ppflop-branch-countwin-20260629-r1/initramfs/500_perlbench_r/run_001/qemu.log`
- `workloads/generated/specint-505-final-faultregs-20260628-r1/initramfs/505_mcf_r/run_001/qemu.log`
- `workloads/generated/specint-505-nestedcall-fix-20260628-r1/qemu_matrix_summary.json`
- `workloads/generated/specint-502-syscall-argstr-smoke-20260628/run/initramfs/502_gcc_r/run_001/qemu.log`
- `workloads/generated/specint-502-static-fulltrace-post-gtod-20260628/run/initramfs/502_gcc_r/run_001/qemu.log`
- `workloads/generated/specint-502-fstat-argdump-20260628-r2/502_gcc_r/run_001/qemu.log`
- `workloads/generated/specint-502-mprotect-tlbfill-20260630-r2/qemu_matrix_summary.json`
- `workloads/generated/specint-502-mprotect-tlbfill-20260630-r2/initramfs/502_gcc_r/run_001/qemu.log`
- `workloads/generated/specint-train-all-tlbfill-debug-qemu-20260630-r1/specint_fast_gate_summary.json`
- `workloads/generated/specint-train-all-tlbfill-debug-qemu-20260630-r1/train-all/qemu_matrix_summary.json`
- `avs/qemu/out/musl-time-syscalls-20260628/summary.json`

Result: all ten train-input benchmarks build in the static phase-b gate.
`999.specrand_ir` passes by hash. The latest all-static diagnostic ledger is
`workloads/generated/specint-train-all-tlbfill-debug-qemu-20260630-r1/`.
It supersedes the older queue-inline/heartbeat-guard, after-callarg, byval, and
latest-qemu tables for current failure ownership while retaining those tables'
performance samples as historical profiling evidence. No timeout row is a
global QEMU deadlock: all timeout rows have `heartbeat_running=true` and
increasing count evidence, and all but `557.xz_r` have recent site changes.
`557.xz_r` is still running by count/BPC evidence, but its last recent window is
same-site and should use a finer heartbeat or PC-watch window before increasing
timeouts. `502.gcc_r` is the active correctness row, and `525.x264_r` is an
immediate initramfs VFS-root panic with no useful BPC heartbeat.

Focused 2026-06-29 502 update: after rebuilding `502.gcc_r` with the Linx LLVM
byval aggregate fix, `workloads/generated/specint-502-byval-fix-train-20260629-r1/`
reclassifies the former `gsi_prev addr=0x8` correctness stop as live-slow. The
run reaches count `61000000006` and BPC `0x155598d706` at the 420s timeout with
`heartbeat_running=true`, `heartbeat_site_progress=true`, and no user trap.

Important 2026-06-29 correction: Linx `prlimit64` succeeds, but the current
libc `setrlimit()` wrapper reports `errno=21` after that successful syscall.
The SPEC init wrapper now calls raw `prlimit64` first and logs
`LINX_SPEC_DBG stack-limit=268435456`, so finite-stack train runs are effective
again. The SPEC runners and fast gate now accept
`--stack-limit <bytes|512M|1G|2G|unlimited>` and record the active define in
JSON summaries. Keep `--stack-limit unlimited` available for reproducing legacy
unlimited-stack mmap layout failures.

| Benchmark | Result | Evidence | Current classification |
| --- | --- | --- | --- |
| `500.perlbench_r` | `live-timeout` | count `107000000000`, BPC `0xffffffff803d3a9c`, `progress=site-change`; recent kernel symbols are in `maple_tree.c` | Old bad branch target is closed. Current owner is live-slow throughput/VMA-maple-tree profiling, not global deadlock. |
| `502.gcc_r` | `user-trap` | all-train row traps at `addr=0x3f7fa8d010`, `tpc=0x1556088006`, `bpc=0x1556087ff4`; focused TLB-fill trace reports `legacy_why=type0`, `legacy_desc=0x0` for the store VA | Active correctness row. Owner is Linx Linux `mprotect()`/VMA/page-fault bring-up, not QEMU stale-TLB or compiler byval. |
| `505.mcf_r` | `live-timeout` | count `48000000005`, BPC `0x155555c482`, `progress=site-change` | Throughput/live-progress lane; reproduce older traps before reopening correctness. |
| `520.omnetpp_r` | `live-timeout` | count `40000000001`, BPC `0xffffffff803e2694`, `progress=site-change`; recent symbols include `string.c`/`memory.c` | Resource-sensitive C++ row is currently live-slow, not the older `sig=9` wrapper failure. Profile kernel memory/string hot paths under <=4 GiB. |
| `523.xalancbmk_r` | `live-timeout` | count `39000000005`, BPC `0xffffffff803e0e5a`, `progress=site-change`; recent symbols include `vsprintf.c` and `string.c` | Live-slow kernel formatting/string lane in this run; old wrapper-output failure is historical unless reproduced. |
| `525.x264_r` | `kernel-panic` | `LINX_PANIC caller=0xffffffff80001648 msg=VFS: Unable to mount root fs on "" or unknown-block(0,0)`; no useful BPC heartbeat | Initramfs packaging/rootfs-size panic sentinel. Use 9p or a disk/rootfs transport for benchmark execution after fixing the initramfs mount path. |
| `531.deepsjeng_r` | `live-timeout` | count `43000000001`, BPC `0x15555593e4`, `progress=site-change` | Throughput/live-progress lane; compare with the passing test-input profile. |
| `541.leela_r` | `live-timeout` | count `42000000001`, BPC `0xffffffff8006bc2a`, `progress=site-change`; recent symbols include `vsprintf.c`/`printk_ringbuffer.c` | Live-slow kernel logging/formatting lane in this run; old child-exit classification is historical unless reproduced. |
| `557.xz_r` | `live-timeout` | count `36000000010`, BPC `0x155558d6da`, last `progress=same-site` but count still advances | Same-site live-slow lane. Use shorter heartbeat interval or PC-watch around `0x155558d6da` before raising timeout. |
| `999.specrand_ir` | pass | `LINX_SPEC_PASS 999.specrand_ir`; FNV-1a `rand.11.out` hash `0x973dcfc2` matches | smoke sentinel closed |

The shared-runtime diagnostic run in
`workloads/generated/specint-train-all-20260628-after-kstat/` currently fails
all ten benchmarks quickly, including `999.specrand_ir`. That route is useful
for loader/libc diagnosis but is not the current SPEC correctness gate. The
static phase-b route is the baseline for benchmark correctness while shared
startup and C++ runtime packaging are being repaired.

The SPEC loop now records bounded failure classes and heartbeat-liveness fields
in both `stage_b_summary.json` and `qemu_matrix_summary.json`. The matrix and
fast-gate wrappers now also expose `--memory-mb` and record `memory_mb` in their
summaries, so resource-sensitive C++ rows can be reproduced without bypassing
the suite flow. A focused
`LINX_QEMU_HEARTBEAT_REGS=1` sentinel run proves the full-register heartbeat
switch without changing behavior: `999.specrand_ir` still passes and the QEMU
log contains `LINX_HEARTBEAT_REGS`. A separate
`LINX_DEBUG_PC_WATCH_REGS=1` smoke proves focused watchpoints can now emit
`LINX_PC_WATCH_REGS` full-GPR records. The new
`LINX_QEMU_HEARTBEAT_CODE_BYTES=16` sentinel run also passes
`999.specrand_ir` and emits `LINX_HEARTBEAT_CODE` records with PC/BPC bytes.
The new `LINX_DEBUG_PC_WATCH_DUMP_REGS=sp,tp,a0` sentinel run passes
`999.specrand_ir` and emits three same-hit guest-word dumps, so allocator and
list traces can capture multiple pointer sources in one long run. The new
`LINX_DEBUG_PC_WATCH_DUMP_OFFSETS=0,8` sentinel also passes
`999.specrand_ir` and emits multiple offsets from one pointer source in a single
hit; focused 500 runs use the same switch to capture several Perl range-frame
slots without rerunning the billion-instruction window. The new
`LINX_DEBUG_PC_WATCH_DUMP_WIDTH=4` sentinel also passes strict
`999.specrand_ir` and emits `width=4` stack words, giving focused runs a
field-width probe for 32-bit flags without changing default 8-byte logs.
The new `LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS=0` sentinel also passes strict
`999.specrand_ir` and emits one-hop pointer-slot dumps such as
`sp+0x0->0x7ffff000`, so focused SPEC runs can keep source slots and pointee
fields in one QEMU log.
The new `LINX_DEBUG_PC_WATCH_DUMP_CALL_RING=1` switch dumps the existing
`LINX_CALL_TRACE_RING=1` call/return ring when a watched PC fires. A focused
8 GiB `999.specrand_ir` panic probe stops at `panic()` before the delay loop
and records the caller path from `schedule()` plus the panic string argument,
which separates first-cause kernel panic evidence from later heartbeat churn.

2026-06-29 QEMU profile update: the queue fast path inlines scalar queue reads
and TQ/UQ pushes when `LINX_DEBUG_LOCAL` is not enabled. The focused
`500.perlbench_r` sample at
`workloads/generated/specint-profile-500-queue-inline-20260629-r2/profile/qemu-500-queue-inline.sample.txt`
shows `helper_linx_scalar_read_reg`, `helper_linx_tq_push`, and
`helper_linx_uq_push` at zero samples. That exposed `helper_linx_heartbeat` as
the next artificial top frame because it still ran once per translated block
even with a 1B-instruction interval. The heartbeat guard adds
`heartbeat_next_count` to the CPU state and skips the helper in translated code
until the next configured bucket. The follow-up sample at
`workloads/generated/specint-profile-500-queue-inline-hbguard-20260629-r1/profile/qemu-500-queue-inline-hbguard.sample.txt`
shows `helper_linx_heartbeat` at zero samples. Remaining top frames are
`helper_linx_tile_set_attr`, `helper_linx_tile_reset_block`,
`helper_linx_template_step`,
`helper_linx_check_bstart_target`, `linx_is_bstart_at_addr`, and
`probe_access_flags`.

Proposed next fixes:

1. Keep the QEMU heartbeat disabled by default, but enable it on long train
   runs to distinguish live progress from deadlock. Use BPC/PC churn plus
   `progress` and `same_site` before increasing timeouts.
2. Treat the current addr-zero rows (`500`, `502`, `520`, and `557`) as a
   shared frame/stack-growth lane until disproved. The latest focused 500 trace
   proves `mprotect()` returns correctly and the final `FRET.STK` restores
   `ra=0` from a zeroed frame slot; prioritize QEMU template save/retry and
   stack-growth fault semantics before changing Linux syscall return or SPEC
   input packaging.
3. Keep the old `500.perlbench_r` BigInt and bad-branch-target failures closed.
   The current static 500 failure has moved to the addr-zero frame lane above;
   use `LINX_FRET_STK_TRACE` and frame-save tracing before returning to Perl
   optimizer or object-state probes.
4. Reclassify the current C++ rows from wrapper child-exit to live-slow unless a
   fresh run reproduces `sig=9`. In the latest all-train matrix,
   `520.omnetpp_r`, `523.xalancbmk_r`, and `541.leela_r` all reach
   heartbeat-backed kernel string/formatting or memory-management sites. Profile
   those rows with a coarser heartbeat or heartbeat disabled, then sample QEMU
   helper hot spots and kernel symbolized BPCs before changing compiler or C++
   runtime code.
5. Treat `525.x264_r` as an initramfs packaging/rootfs-size panic sentinel in
   this flow. The latest initramfs row panics before useful heartbeat evidence
   with `VFS: Unable to mount root fs`; use 9p or a disk/rootfs transport for
   benchmark execution after preserving this panic as a separate rootfs test.
6. Profile live-slow rows with heartbeat off or at a very coarse interval:
   `505.mcf_r`, `523.xalancbmk_r`, `541.leela_r`, plus focused
   `999.specrand_ir` as a transport sentinel. Keep `500`, `502`, `520`, and
   `557` in the addr-zero frame lane until the restore-slot/root cause is
   closed. Remaining QEMU speedups should focus on
   tile set/reset, template stepping, page-local BSTART decode caching,
   TB chaining, `helper_linx_check_bstart_target`, `linx_is_bstart_at_addr`, and
   avoiding helper probes in hot branch-validation paths. Queue/scalar helper
   overhead, heartbeat helper overhead, and scalar no-op tile commit overhead
   are already closed by the queue-inline, heartbeat-guard, and tile-commit
   guard patches.
7. Use count-windowed diagnostics for late SPEC windows. Pair
   `LINX_FAULT_TRACE_COUNT_LO/HI`, `LINX_DEBUG_PC_WATCH_COUNT_LO/HI`,
   `LINX_MEM_TRACE_COUNT_LO/HI`, and `LINX_TLB_FILL_TRACE_COUNT_LO/HI` with
   PC/ACR/address filters so early boot or early stack-slot reuse does not
   consume trace quotas before the final fault.
8. Keep `train-all` opt-in through `--profile train`; the PR gate should stay on
   cheap `999.specrand_ir` smoke while stress workloads run in isolated nightly
   or diagnostic lanes.

## 2026-07-01 500 FRET.STK Frame Evidence

`workloads/generated/specint-test-train-all-hashclass-20260701-r1/` is the
current all-row ledger and shows shared addr-zero user traps for `500`, `502`,
`520`, and `557`. Focused `500.perlbench_r` follow-up narrows the first proven
cause:

- `workloads/generated/specint-500-mprotect-sysret-trace-20260701-r1/` shows
  syscall 226 (`mprotect`) returning normally to `0x155582ea44`; this closes
  the syscall-return hypothesis for the immediate null branch.
- `workloads/generated/specint-500-fret-stk-trace-20260701-r2/` records
  `LINX_FRET_STK_TRACE count=18674966518 pc=0x1555828d20 old_sp=0x3fdd764750
  new_sp=0x3fdd7647a0 stacksize=80 incoming_ra=0x15558292f0
  restored_ra=0x0`. The slot dump shows `ra@0x3fdd764798 = 0` and all restored
  `s0..s5` slots are also zero before QEMU commits the restore.
- `workloads/generated/specint-500-fret-frame-memtrace-20260701-r1/` adds a
  translated user-store trace on `0x3fdd764750..0x3fdd76479f`; it emits no
  `LINX_MEM_TRACE` records before the same zero-slot restore, so the current
  owner is helper/template frame save or stack-growth fault/retry semantics.

Next solution path: add or use frame-save-side tracing around the matching
`FENTRY` at `0x1555828a72`, then verify whether the `ra=0x15558292f0` save lands
at `0x3fdd764798` after any stack-growth fault. If it never lands, fix the
restartable `FENTRY` probe/save path; if it lands and later disappears, trace
helper-side page remap/zeroing before broad user-store instrumentation.

## 2026-06-29 500 BigInt Current Evidence

`500.perlbench_r` now reaches Perl user code deterministically and fails in the
`Math::BigInt` train input, not in Linux dentry lookup and not in SPEC input
packaging. Host `/usr/bin/perl -I./lib perfect.pl b 3` passes in the same run
directory. Ignored, temporary `Devel::Peek` instrumentation immediately before
the failing `1 .. $count` range observed `$count` as a plain scalar with
`FLAGS = (IOK,pIOK)` and `IV = 2`; the source line still dies with
`Range iterator outside integer range`. A Linx C micro-smoke for the
`SVf_IOK|SVf_IVisUV` guard compiles correctly at both `-O0` and `-O2`, so the
visible `andiw 32` in the `pp_flop` window is not a standalone IVisUV mask bug.

Focused PC-watch evidence:

- `workloads/generated/specint-500-ppflop-offsets-20260629-r1/` proves
  multi-offset frame snapshots preserve the same failure class.
- `workloads/generated/specint-500-ppflop-sv-objects-20260629-r2/` captures
  final `pp_flop` GPR and object-word state before the exception.
- `workloads/generated/specint-500-ppflop-width4-watch-20260629-r1/` uses the
  new 4-byte dump width to expose flag-sized lanes in the same deterministic
  failure window.
- `workloads/generated/specint-500-ppflop-branch-ptrslots-20260629-r1/` uses
  `LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS` to dereference selected `pp_flop`
  frame/object slots in the same window. The final watched error-build block
  records `pc=0x1555829792`, `a2=0x2`, and pointer slots such as
  `sp+0x30->0x155588a9b0` plus `s0+0x10->0x1555847268`.
- `workloads/generated/specint-500-ppflop-branch-countwin-20260629-r1/`
  removes the per-PC hit filter and watches the final count window
  `3069000000..3072000000`. It records repeated `0x1555829792` then
  `0x15558297ae` pairs and no watched `0x15558297d4` continuation before the
  `Range iterator outside integer range` exit.

Next solution path: keep 500 out of the deadlock and dcache lanes. The current
blocker is an active `pp_flop` error-path decision: the optimized branch builds
the croak message at runtime `0x1555829792` and enters `Perl_croak` at
`0x15558297ae`, while the watched final window does not reach the post-croak
continuation at `0x15558297d4`. Compare the Linx `pp_ctl.c` optimized
conditions and SV slots against host behavior with a selective compile/probe
before changing SPEC packaging or QEMU control-flow rules.

## 2026-06-29 500 Dcache Oops Triage

The raw-prlimit train-all gate temporarily regressed `500.perlbench_r` from the
intermediate Perl BigInt user-range stop back into a kernel Oops in
`__d_lookup_rcu`. The current QEMU same-ACR frame fix closes that Oops and moves
`500.perlbench_r` back to the BigInt blocker:

- Baseline focused rerun:
  `workloads/generated/specint-500-baseline-20260629-r1/stage_b_summary.json`.
  It reproduces `LINX_DIE msg=Oops` at `tpc=0xffffffff8013c3de`,
  `bpc=0xffffffff8013c3d4`, followed by `LINX_EXIT_INIT code=0xb`. Symbolizing
  `kernel/linux/build-linx-fixed/vmlinux` maps the trap to the byte-compare loop
  in `__d_lookup_rcu`.
- Low-noise PC-watch filter:
  `workloads/generated/specint-500-dlookup-pcwatch-match-a1-20260629-r1/`.
  This reproduces the kernel panic while capturing the active lookup against
  `a1=0xff60000004c02d88`; the compared bytes spell paths such as
  `sec-run.linx_emptystdin`, and heartbeat still reports site progress.
- Ring-only PC-watch:
  `workloads/generated/specint-500-pcwatch-ring-a1-20260629-r1/`.
  `LINX_DEBUG_PC_WATCH_PRINT=0` plus `LINX_DEBUG_PC_WATCH_RING=1` avoids the
  synchronous print perturbation and dumps the last 64 watched hits when
  `LINX_FAULT_TRACE` catches the data exception. The final ring entry before
  the Oops records `pc=0xffffffff8013c3de`, `x1=0x1`,
  `x2=0xff6000007dd40027`, `a0=0xff60000004c020c0`,
  `a1=0xff60000004c02d88`, and `traparg0=0x1`. This proves the fault is a bad
  live-register value reaching the compare loop, not a deadlocked QEMU.
- Ring memory snapshot:
  `workloads/generated/specint-500-pcwatch-ring-mem-a1-20260629-r1/` adds
  `LINX_DEBUG_PC_WATCH_RING_MEM_REG=a1` and
  `LINX_DEBUG_PC_WATCH_RING_MEM_OFFSET=0x20`. The final ring entries show
  `x1=0x1` while `mem_value=0xff60000004c02db8` remains valid at `[a1+0x20]`.
  This rules out the dentry name field as the corrupted state and points at
  live `x1` handling.
- Root cause:
  Linux `arch/linx/kernel/entry.S` expects same-ACR kernel-origin traps and
  IRQs to enter with live `x1=0` and the interrupted `x1` saved in the current
  bank's ETEMP. QEMU saved EBARG/block state but did not populate that same-ACR
  `x1` frame, so a same-ring event could clobber the VFS compare loop's live
  `x1`.
- Fix and evidence:
  QEMU now builds same-ACR exception/IRQ frames before vectoring and TP trace
  emits `sync_same_acr_frame` / `irq_same_acr_frame` records when enabled. The
  focused rerun
  `workloads/generated/specint-500-after-same-acr-x1-20260629-r1/` has no
  kernel panic and reaches `Range iterator outside integer range at
  lib/Math/BigInt.pm line 2675`; the full train-all rerun
  `workloads/generated/specint-train-all-20260629-same-acr-x1-r1/` shows the
  same `user-arithmetic-range` class for `500.perlbench_r`.

Next solution path:

1. Keep the same-ACR `x1` entry contract covered by AVS and do not treat future
   500 BigInt failures as dentry corruption unless the Oops reproduces.
2. Resume the Perl BigInt `Range iterator outside integer range at
   lib/Math/BigInt.pm line 2675` investigation from
   `workloads/generated/specint-500-ppflop-offsets-20260629-r1/`,
   `workloads/generated/specint-500-ppflop-sv-objects-20260629-r2/`, and
   `workloads/generated/specint-500-ppflop-branch-countwin-20260629-r1/`. Map
   the captured `pp_flop` frame/register state to Perl SV flag/value fields,
   then minimize a Linx-native scalar/range smoke before changing SPEC
   packaging or QEMU control-flow rules.

## 2026-06-28 500 Fixup Triage

Focused `500.perlbench_r` runs separated the original loader-looking symptom
from the real kernel/runtime failures:

- `workloads/generated/specint-500-preexec-20260628/` proves the benchmark ELF
  exists in the initramfs and is readable before `execve`
  (`stat=0`, `open=6`, `read4=4`, ELF magic `0x7f454c46`).
- The first focused failure was a Linux Oops in `sys_fcntl` usercopy with BPC
  at `HL.BSTART.STD FALL<, fixup_label>`. The old Linux `fixup_exception`
  path only recognized legacy 128-bit block headers with the fixup attribute.
- `arch/linx/mm/extable.c` now recognizes the current v0.56 32-bit and
  48-bit `BSTART.{STD,SYS,FP} FALL` fixup encodings before falling back to the
  legacy header parser. Zero-offset FALL blocks are deliberately ignored so
  ordinary fallthrough blocks are not converted into recovery handlers.
- `workloads/generated/specint-500-fixup-20260628/` confirms that the first
  usercopy fixup blocker moved: the failure now reaches
  `kmem_cache_alloc_noprof` at `tpc=0xffffffff80102a96`,
  `bpc=0xffffffff80102a74`, with `a0=0`, `a1=0`, and
  `traparg0=0x24`.
- `workloads/generated/specint-500-kmalloc-centered-trace-20260628/` records
  the current QEMU `LINX_FAULT_TRACE` stop. The heartbeat count is still
  advancing until the Oops, so this is a deterministic kernel fault rather
  than a deadlock.
- `workloads/generated/specint-500-callring-20260628/` uses
  `LINX_CALL_TRACE_RING=1` to identify the null slab-cache dereference as
  `fcntl_setlk -> kmem_cache_alloc_noprof`, with `filelock_cache` still zero.
- The Linx curated `CONFIG_LINX_INTC` init path bypasses generic initcalls, so
  `filelock_init` was never reached. Calling `linx_filelock_init()` from the
  curated path initializes the lock-manager slab cache and moves 500 past the
  old kernel Oops.
- `workloads/generated/specint-500-after-filelock-20260628/` then showed a
  false relative-path `execve` failure. The initramfs already contained the
  benchmark ELF, and extracting the cpio proved the path existed; the robust
  runner fix is to exec `/spec-run/<benchmark>` in initramfs mode.
- `workloads/generated/specint-500-syscall-openat-ret-20260628/` proves
  `openat("perfect.pl")` returns fd `3` in the benchmark process. A following
  `LINX_SYSCALL_TRACE_NR=25` run proves `fcntl(3, F_SETFD, ...)` returns `0`;
  the old "Bad file descriptor" was caused by inheriting unusable fd `0`.
- The local SPEC runner now opens the generated `.linx_empty_stdin` file for
  no-stdin runs instead of inheriting initramfs fd `0`. With that fix,
  `workloads/generated/specint-500-stdin-empty-20260628/` reaches Perl BigInt
  user code and exits with `Range iterator outside integer range at
  lib/Math/BigInt.pm line 2675`.

Next 500-specific solution path:

1. Commit the filelock-init and runner stdin/absolute-exec fixes as SPEC flow
   prerequisites. The kernel Oops and false ENOENT/EBADF symptoms are now
   understood and should not be re-triaged as QEMU deadlocks.
2. Treat the BigInt user-code stop captured by
   `workloads/generated/specint-train-all-20260628-qemu-dump-regs-r1/` as
   historical root-cause evidence; the Linx LLVM f64 extload fix closes that
   class. The current 500 path is the run_002 branch-target trap in
   `workloads/generated/specint-train-all-queue-inline-hbguard-20260629-r1/`,
   so the next loop should inspect the symbolized musl `__syscall_cp_c` /
   `sccp` origin before changing kernel/QEMU liveness policy.
3. Keep the v0.56 fixup parser as a prerequisite for all uaccess-heavy SPEC
   work; without it, normal faultable usercopy recovery is misclassified as an
   unhandled kernel page fault.

## Next Speedups

Current train-all live-progress evidence:

- `workloads/generated/specint-train-all-queue-inline-hbguard-20260629-r1/initramfs/stage_b_summary.json`
  is the current all-train ledger. The live timeout rows are `502`, `505`,
  `520`, `523`, `525`, `531`, `541`, and `557`; all have
  `heartbeat_running=true`, `heartbeat_site_progress=true`, and no panic or
  user trap. `500.perlbench_r` has split out of the live-slow lane: run_001
  passes `perfect.b.3.out` by hash, while run_002 traps at a bad branch target
  after entering musl `__syscall_cp_c` / `sccp`.
- Fresh macOS samples:
  `workloads/generated/specint-profile-500-queue-inline-20260629-r2/profile/qemu-500-queue-inline.sample.txt`
  and
  `workloads/generated/specint-profile-500-queue-inline-hbguard-20260629-r1/profile/qemu-500-queue-inline-hbguard.sample.txt`.
  The first sample proves scalar queue reads and TQ/UQ push helpers are gone
  from the hot path. The second proves `helper_linx_heartbeat` is also gone
  from the hot path. Remaining top-of-stack cost is concentrated in
  `helper_linx_tile_commit`, `helper_linx_tile_set_attr`,
  `helper_linx_tile_reset_block`, `helper_linx_template_step`,
  `helper_linx_check_bstart_target`, `linx_is_bstart_at_addr`, and
  `probe_access_flags`.
- Older macOS `sample` captures under
  `workloads/generated/specint-train-all-20260628-heartbeat-stacklimit/profile/`
  for `523.xalancbmk_r`, `531.deepsjeng_r`, and `557.xz_r` show the same broad
  helper families. The latest samples remove queue/scalar helper traffic and
  heartbeat overhead as active explanations; remaining cost is
  tile/template/BSTART/probe/TLB work.
- `workloads/generated/specint-523-acre-finalwindow-reloc-ring-guesthb-qemu-20260702-r1/`
  showed that the heavy guest heartbeat diagnostics could perturb `523` startup:
  the final null store followed a trap-return from the guest `/proc` diagnostic
  path. After making those `/proc` dumps opt-in,
  `workloads/generated/specint-523-guesthb-light-qemu-20260702-r1/` reaches the
  300s timeout as `live-timeout` with `heartbeat_running=true`,
  `heartbeat_site_progress=true`, count `33000000001`, and BPC `0x1555764ecc`.
  Keep 523 in the live-slow throughput lane unless a no-diagnostics run produces
  a fresh user trap.

Prioritized QEMU speedups:

1. Fast-path disabled trace helpers out of hot loops. The call-trace ring path
   now initializes once per event and returns immediately when both text trace
   and ring trace are disabled. `linx_trace_capture_active()` now avoids the
   generic active helpers on every writeback and reads cached
   commit/minst/cosim state after one-time init.
2. Add a page-local BSTART decode cache with explicit TB/text invalidation.
   Positive target caching reduces repeated hits, but cold or colliding targets
   still decode through the helper probe and BSTART byte classification.
3. Reduce helper traffic in the tile/template hot path. Simple scalar queue
   reads and pushes are now inlined into generated TCG, so the next speed lane
   should inline or fuse the common tile commit/set/reset and template-step
   sequence, then retest against the all-train live-slow rows.
4. Keep heartbeat off, or at a very coarse interval, for profiler runs. Use it
   to classify deadlock vs live progress first, then rerun profiling with
   `LINX_QEMU_HEARTBEAT_INTERVAL=0` once the workload is known to be live.
5. Split correctness and instrumentation QEMU builds. The default benchmark
   binary should compile without always-on helper instrumentation; a separate
   diagnostics build can keep dense trace hooks and debug checks.
6. Keep 505 memory stress and `531` CPU stress out of cheap PR smoke. They
   should remain isolated as `test-vm-stress`, `train-vm-stress`,
   `test-cpu-stress`, and `train-cpu-stress` so ordinary regressions do not
   spend their budget on the largest allocation/MMU/control-flow workloads
   first.
7. Keep heartbeat and guest logging off for profiler runs. Use
   `--guest-heartbeat-sec 0` and a low or zero host heartbeat unless the guest
   is suspected of hanging.

## 2026-07-03 Train-All Profile

Latest bounded train-all evidence:

- Run root:
  `workloads/generated/specint-train-all-debug-qemu-20260703-r1/`
- QEMU:
  `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`
- Top-level summary:
  `workloads/generated/specint-train-all-debug-qemu-20260703-r1/specint_fast_gate_summary.json`
- Profile artifact:
  `workloads/generated/specint-train-all-debug-qemu-20260703-r1/profile/qemu-system-sample-20260703-124459.txt`

The run covers every train SPECint row. `999.specrand_ir` passes strict hash
`0x973dcfc2`. The remaining nine rows are heartbeat-backed `live-timeout`
failures, including `525.x264_r` in the generated 9p shard. The final
heartbeats for the failed rows all report `progress=site-change`, so the
current train failure class is live throughput/gate budget, not a hard
deadlock.

The 5 second macOS `sample` taken during a live `505.mcf_r` row shows the CPU
thread dominated by TCG memory translation and Linx page-table walking rather
than disabled tracing:

| Frame | Sample count |
| --- | ---: |
| `cpu_tb_exec` | 3041 |
| `do_ld8_mmu` | 485 in one hot stack, 408 in another |
| `mmu_lookup` | 476 in one hot stack, 404 in another |
| `mmu_lookup1` | 453 in one hot stack, 391 in another |
| `tlb_fill_align` | 437 in one hot stack, 381 in another |
| `linx_cpu_tlb_fill` | 271 in one hot stack, 230 in another |
| `linx_mmu_translate` | 212 in one hot stack, 185 in another |
| `helper_linx_template_fret_stk` | 70 |

Current optimization owners:

1. Reduce TLB fill frequency and page-walk cost before further micro-optimizing
   decode. Candidate work includes larger or better-tagged soft-TLB coverage for
   SPEC user mappings, avoiding unnecessary invalidation after post-start kernel
   activity, and adding counters that separate user text/data misses from kernel
   or 9p misses.
2. Split page-walk profiling by phase. The current sample was taken during a
   live benchmark row, but `525.x264_r` over 9p still samples heavily in kernel
   paths; profile one initramfs live row and one 9p live row separately.
3. Reduce template/frame load traffic. `helper_linx_template_fret_stk` remains
   visible below the TCG memory path and should be inspected for common fast
   cases that can avoid repeated MMU loads or collapse slot reads.
4. Keep heartbeat coarse for classification and off for profiler comparisons.
   The 2026-07-03 heartbeat proves liveness, but performance deltas should be
   collected with `LINX_QEMU_HEARTBEAT_INTERVAL=0` after row class is known.
5. Keep the split `train-all`/`train-all-large-9p` gate as the breadth loop.
   The previous 525 oversized-initramfs panic is no longer the default suite
   result when the wrapper split policy is allowed to run.

## 2026-07-03 MMU Cache Experiment

The first page-walk speed experiment adds an opt-in direct-mapped Linx
page-walk result cache behind `LINX_MMU_CACHE=1` or
`LINX_QEMU_MMU_CACHE=1`. Cache counters are also opt-in with
`LINX_MMU_CACHE_STATS=1` or `LINX_QEMU_MMU_CACHE_STATS=1`; heartbeat records
always carry `mmuc_hit`, `mmuc_miss`, `mmuc_fill`, `mmuc_flush`, and
`mmuc_flush_page`, which remain zero when stats are disabled.

The experiment is intentionally default-off. Focused `505.mcf_r` train-input
120 second runs on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`
showed the cache does not improve the current hot path:

| Run | Artifact | Result |
| --- | --- | --- |
| disabled baseline | `workloads/generated/specint-505-mmu-cache-off-qemu-20260703-r1/` | live timeout at `30000000002` instructions |
| cache on, full-scan page flush | `workloads/generated/specint-505-mmu-cache-on-qemu-20260703-r1/` | live timeout at `26000000003` instructions |
| cache on, O(1) page flush, stats on | `workloads/generated/specint-505-mmu-cache-on-o1flush-qemu-20260703-r1/` | live timeout at `28000000005` instructions |
| cache on, O(1) page flush, stats off | `workloads/generated/specint-505-mmu-cache-on-nostats-qemu-20260703-r1/` | live timeout at `28000000000` instructions |
| default-off rebuild | `workloads/generated/specint-505-mmu-cache-defaultoff-qemu-20260703-r1/` | live timeout at `30000000005` instructions |

The default-off rebuild preserves strict correctness on the cheap train sentinel:
`workloads/generated/specint-999-mmu-cache-defaultoff-qemu-20260703-r1/`
passes `999.specrand_ir` with strict hash validation. The parser false-red seen
when QEMU heartbeat text interleaved a `LINX_SPEC_HASH` line is fixed by
removing heartbeat records before matching hash markers, then scanning bounded
hash-marker segments and preferring the candidate that matches the expected
size and hash. The end-to-end proof with the opt-in cache, cache stats, and
1M-instruction QEMU heartbeat enabled is
`workloads/generated/specint-999-mmu-cache-parserfix-qemu-20260703-r2/`,
which passes strict `999.specrand_ir` train hash validation.

Rejected speed lane: widening `tlb_set_page()` with the large block size
returned by `linx_mmu_translate()`. QEMU's soft-TLB fill still materializes a
single `TARGET_PAGE_SIZE` entry for lookup; the larger size is useful for
invalidation scope, not for coalescing the observed hot per-page miss path.

Current conclusion: keep the MMU cache as a diagnostic/profiling switch only.
Do not enable it in normal SPEC gates. The next useful speed work is to count
why `tlb_flush_page()` is so frequent during SPEC rows, split user text/data
misses from kernel and 9p misses, and reduce template/frame memory traffic that
drives TCG load/store MMU lookups.

## 2026-07-03 TLB Invalidation Counters

The follow-up debug patch adds `LINX_TLB_STATS=1` /
`LINX_QEMU_TLB_STATS=1`, an opt-in counter path for TLB invalidation helpers.
Heartbeat records now include `tlbi_iall`, `tlbi_ia`, `tlbi_iv`,
`tlbi_iav`, and the last invalidation count/PC/BPC/operand/ACR. The counters
do not require the experimental MMU cache, so they can quantify invalidation
pressure without changing page-walk behavior. The SPEC runners expose this as
`--qemu-tlb-stats` / `LINX_SPEC_QEMU_TLB_STATS=1`, record final heartbeat
values under `heartbeat_tlb_invalidation`, and print compact `tlbi=` liveness
tags for failing matrix rows.

Focused evidence on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`:

| Run | Artifact | Result |
| --- | --- | --- |
| strict `999.specrand_ir`, stats on, 1M heartbeat | `workloads/generated/specint-999-tlb-stats-qemu-20260703-r1/` | pass in `9.304s`; final `tlbi_iv=3670859` |
| strict `999.specrand_ir`, stats off/default | `workloads/generated/specint-999-tlb-stats-defaultoff-qemu-20260703-r1/` | pass |
| `505.mcf_r` train, stats on, 120s cap | `workloads/generated/specint-505-tlb-stats-qemu-20260703-r1/` | live timeout at `26000000004` instructions; final `tlbi_iv=3675648` |
| strict `999.specrand_ir`, runner switch on | `workloads/generated/specint-999-tlbi-runner-qemu-20260704-r1/` | pass; `qemu_tlb_stats=true`; `heartbeat_tlb_invalidation.iv=3670859`, `iall=9`, last invalidation `bpc=0xffffffff800d94ea`, operand `0x1555556000` |

The new data changes the interpretation of the earlier MMU-cache page-flush
counter. The million-scale `TLB.IV` traffic is largely boot/startup mapping
work: the strict `999` run already reaches about `3.67M` page invalidations.
The 505 train slice adds only a few thousand more invalidations while the
benchmark remains live. The last 505 invalidation site is
`pc=0xffffffff800db2b6`, `bpc=0xffffffff800db2ac`, symbolized with
`kernel/linux/build-linx-fixed/vmlinux` to Linux `handle_mm_fault` /
`memory.c` around a `tlb.iv a3` loop. The strict 999 last site is
`pc=0xffffffff800d94f4`, `bpc=0xffffffff800d94ea`, symbolized to
`finish_fault` / `memory.c` around a `tlb.iv a2` loop.

Current conclusion: do not spend the next QEMU speed loop on the direct-mapped
page-walk cache. First separate startup invalidation cost from steady-state
SPEC execution cost, then investigate whether Linux can batch or narrow these
fault-time `TLB.IV` loops, and keep QEMU work focused on the remaining sampled
TCG load/store MMU path plus template/frame memory traffic.

## 2026-07-03 TLB Fill Counters

The next debug patch adds `LINX_TLB_FILL_STATS=1` /
`LINX_QEMU_TLB_FILL_STATS=1`, an opt-in aggregate counter path for
`linx_cpu_tlb_fill()`. Heartbeat records now include total, fetch, load, store,
probe, ok, fault, user/kernel/other MMU-index splits, and last-fill
PC/BPC/VA/PA/access/MMU/prot/cause/ACR fields with the `tlbf_` prefix.
`tools/spec2017/run_int_rate_qemu.py` parses the final heartbeat into
`heartbeat_tlb_fill`, and `run_stage_qemu_matrix.py` includes a compact
`tlbf=<total>/f<fetch>/l<load>/s<store>/p<probe>/u<user>/k<kernel>/o<other>`
tag in matrix liveness summaries when the split fields are present.

Validation on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`:

| Run | Artifact / command | Result |
| --- | --- | --- |
| QEMU rebuild | `ninja -C /tmp/linx-qemu-hb-build-20260703-r1 qemu-system-linx64` | pass; only pre-existing Linx warnings |
| AVS full QEMU suite | `python3 avs/qemu/run_tests.py --all --timeout 20 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| strict `999.specrand_ir`, fill stats on | `workloads/generated/specint-999-tlbfill-stats-final-qemu-20260703-r1/` | pass; final `tlbf_total=1861324`, `tlbf_load=1840179`, `tlbf_fault=14` at `508000003` instructions |
| strict `999.specrand_ir`, default-off | `workloads/generated/specint-999-tlbfill-stats-defaultoff-qemu-20260703-r1/` | pass |
| `505.mcf_r` train, fill stats on, 120s cap | `workloads/generated/specint-505-tlbfill-stats-final-qemu-20260703-r1/` | live timeout with BPC site progress at `30000000007` instructions; final `tlbf_total=97899663`, `tlbf_fetch=452898`, `tlbf_load=89920690`, `tlbf_store=7526075`, `tlbf_probe=71383`, `tlbf_fault=4793` |
| all tracked SPECint C/C++ train rows, fill stats on, 300s cap | `workloads/generated/specint-train-all-provenance-clean-qemu-20260703-r1/` | clean QEMU `f690aa1f7daf4fdc3f70802c074b65b633418aa3`; `999.specrand_ir` passes strict hash; the other nine rows are heartbeat-backed `live-timeout` with BPC site progress and compact `tlbf=` evidence |
| strict `999.specrand_ir`, split fields on | `workloads/generated/specint-999-tlbfill-split-qemu-20260703-r1/` | pass; strict train hash `rand.11.out=0x973dcfc2`; runner captures `user`, `kernel`, and `other` split fields under `heartbeat_tlb_fill` |
| `505.mcf_r` train, split fields on, 120s cap | `workloads/generated/specint-505-tlbfill-split-qemu-20260703-r1/` | live timeout with BPC site progress at `32000000009` instructions; final `tlbf_total=102633834`, `tlbf_user=100756933`, `tlbf_kernel=1876901`, `tlbf_other=0`, `tlbf_user_load=92222996` |
| `505.mcf_r`, QEMU soft-TLB default 1024-entry experiment | `workloads/generated/specint-505-tlb-default-1024-qemu-20260703-r1/` | rejected; same 120s shape reached `33000000001` instructions, below the `34000000007` current best, so do not bump `CPU_TLB_DYN_DEFAULT_BITS` as the next speed fix |

Latest all-train fill totals from the clean `f690aa1f7da` QEMU build:

| Benchmark | Transport | Result | `tlbf_total` | Dominant class |
| --- | --- | --- | ---: | --- |
| `500.perlbench_r` | initramfs | `live-timeout` | 7,299,917 | load `4,697,601`, fetch `2,208,685`, user `4,921,019` |
| `502.gcc_r` | initramfs | `live-timeout` | 10,498,172 | load `6,475,564`, fetch `3,291,644`, user `5,550,016` |
| `505.mcf_r` | initramfs | `live-timeout` | 211,542,971 | load `189,545,388`, store `20,653,436`, user `209,665,989` |
| `520.omnetpp_r` | initramfs | `live-timeout` | 15,916,858 | load `10,906,046`, fetch `4,064,551`, user `11,356,510` |
| `523.xalancbmk_r` | initramfs | `live-timeout` | 9,533,917 | load `6,456,597`, fetch `2,548,521`, user `7,090,955` |
| `525.x264_r` | 9p | `live-timeout` | 1,873,788 | load `1,848,143`, kernel `1,873,693` |
| `531.deepsjeng_r` | initramfs | `live-timeout` | 16,834,934 | load `13,429,186`, store `1,557,950`, user `14,747,384` |
| `541.leela_r` | initramfs | `live-timeout` | 2,151,098 | load `2,025,278`, kernel `1,962,581` |
| `557.xz_r` | initramfs | `live-timeout` | 32,601,575 | load `29,914,792`, user `30,105,688` |

Current conclusion: invalidation counters showed `TLB.IV` is mostly
startup/fault-path work, but fill counters show demand TLB fills continue
through the live benchmark window and are data-load dominated on `505.mcf_r`.
The split counters show that this pressure is overwhelmingly user-mode mapping
work in the focused 505 slice, not kernel page-walk churn: `100756933` user
fills versus `1876901` kernel fills. The current clean all-train ledger shows
the same pattern at suite breadth: `505.mcf_r` reaches `211542971` total fills,
`209665989` user fills, and `187698111` user-load fills by the 300s cap. Every
slow row is running, and the highest fill pressure is dominated by data loads
rather than instruction fetch. A simple larger direct-mapped QEMU
soft-TLB default did not help, so the next speed lane should profile and reduce
TCG load/store lookup and translated data-memory traffic before changing global
TLB sizing. Do not make the experimental page-walk cache default-on without a
new timing proof, because the previous cache experiment slowed the comparable
505 slice. Keep 9p-specific work separate: `525.x264_r` has much lower
TLB-fill volume in this 300s shard, so its next speed owner is likely
9p/syscall/transport overhead before generic TLB tuning.

## 2026-07-03 Tile State Helper Inline

The next low-risk hot-path cleanup removes two trivial tile-state helper calls
from translated block setup. `linx_tile_set_attr_const()` now emits direct TCG
stores for `tile_attr_raw`, `tile_attr_dtype`, and `tile_attr_pad`, while
`linx_tile_reset_block_inline()` clears the tile descriptor counters and
argument format directly in `CPULinxState`. The semantic helper implementations
remain available, but hot block headers and constant `B.ATTR` descriptors no
longer call `helper_linx_tile_set_attr` or `helper_linx_tile_reset_block`.

Validation on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`:

| Run | Artifact / command | Result |
| --- | --- | --- |
| QEMU rebuild | `ninja -C /tmp/linx-qemu-hb-build-20260703-r1 qemu-system-linx64` | pass; only the pre-existing `linx_tile_relreg_to_id` warning |
| AVS system smoke | `python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 15 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| AVS tile smoke | `python3 avs/qemu/run_tests.py --suite tile --smoke-source-overrides --timeout 30 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train | `workloads/generated/specint-999-inline-tile-qemu-20260703-r1/` | pass with strict initramfs hash validation |
| `505.mcf_r` train 120s | `workloads/generated/specint-505-inline-tile-qemu-20260703-r1/` | live timeout with site-progress heartbeat at `31000000001` instructions |
| post-patch delayed profile | `workloads/generated/specint-profile-505-inline-tile-nohb-delayed-20260703-r1/qemu-505-inline-tile-nohb-delayed.sample.txt` | no `helper_linx_tile_set_attr` or `helper_linx_tile_reset_block` samples |

The directly comparable default-off 505 baseline was
`workloads/generated/specint-505-mmu-cache-defaultoff-qemu-20260703-r1/`, which
reached `30000000005` instructions in the same 120 second, 1B-heartbeat shape.
The new run reaches `31000000001`, so this is a small positive throughput
movement but not enough to close train `505.mcf_r`.

The full tile AVS suite is not used as green evidence for this patch: it still
times out at the known `PTO tile matmul (8x8 i32)` row under a 120 second cap.
Keep using `--smoke-source-overrides` as the Tier-0 tile QEMU smoke until the
full tile workload is promoted separately.

Current conclusion: the trivial tile setup helpers are closed as SPEC profile
noise. The remaining 505 top-of-stack samples are `pthread_jit_write_protect_np`
host toggling, `helper_linx_template_fentry`, `helper_linx_template_fret_stk`,
`helper_linx_check_bstart_target`, TCG soft-TLB lookup, and
`linx_mmu_translate`. Next QEMU speed work should focus on template frame
memory traffic and BSTART/TLB lookup cost, not tile reset/set helpers.

## 2026-07-03 Template Return Cache-Hit Fast Path

The next low-risk template cleanup keeps the existing restartable frame
save/restore model, but avoids avoidable helper work around it:

- `linx_template_fret_stk` and `linx_template_fret_ra` now skip the full
  `linx_check_bstart_target` helper when the return target is already a hot
  positive BSTART-cache hit.
- The shortcut is disabled when `LINX_CFI_TRACE`,
  `LINX_BSTART_CACHE_REVALIDATE`, or `LINX_BSTART_CACHE_STATS` is active, so
  debug/revalidation/stat modes still enter the full helper.
- Default-disabled FENTRY/FRET trace checks now return before scanning restored
  slots or preserving host readback pointers for trace-only diagnostics. The
  mandatory stack probes and memory loads/stores are unchanged.

Validation on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`:

| Run | Artifact / command | Result |
| --- | --- | --- |
| QEMU rebuild | `ninja -C /tmp/linx-qemu-hb-build-20260703-r1 qemu-system-linx64` | pass; only pre-existing warnings |
| AVS system smoke | `python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| AVS call/ret contract | `python3 avs/qemu/run_callret_contract.py --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| AVS all | `python3 avs/qemu/run_tests.py --all --timeout 20 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train | `workloads/generated/specint-999-template-return-fast-qemu-20260703-r1/` | pass with strict initramfs hash validation |
| strict `999.specrand_ir` train with BSTART stats | `workloads/generated/specint-999-template-return-fast-bstart-stats-qemu-20260703-r1/` | pass with strict initramfs hash validation |
| `505.mcf_r` train 120s | `workloads/generated/specint-505-template-return-fast-qemu-20260703-r1/` | live timeout with site-progress heartbeat at `34000000007` instructions |

The directly comparable 120 second `505.mcf_r` sequence is now:

| QEMU state | Artifact | Final heartbeat count |
| --- | --- | ---: |
| page-walk cache default-off baseline | `workloads/generated/specint-505-mmu-cache-defaultoff-qemu-20260703-r1/` | `30000000005` |
| tile helper inline | `workloads/generated/specint-505-inline-tile-qemu-20260703-r1/` | `31000000001` |
| template return fast hit | `workloads/generated/specint-505-template-return-fast-qemu-20260703-r1/` | `34000000007` |

Current conclusion: this is a positive SPEC throughput move, but it still does
not make `505.mcf_r` train complete within the current gate budget. The next
speed lanes remain TCG soft-TLB/page-walk cost, remaining frame save/restore
memory traffic, and BSTART cold-target classification/cache churn.

## 2026-07-03 FENTRY Save Probe Reuse and Real-QEMU Profiler Wrapper

The next frame-memory experiment narrowed the safe part of the template
optimization. `FENTRY` already probes every save slot before committing `sp` so
that stack-growth faults retry from the original architectural state. QEMU now
reuses that probed host RAM pointer for the actual save when the target is
direct RAM, and falls back to the existing `cpu_stq_le_mmuidx_ra` path for
MMIO/plugin cases. Restore loads stay on `cpu_ldq_le_mmuidx_ra`: a broader
probe-read/direct-load experiment was rejected because the comparable
`505.mcf_r` train run dropped to `32000000006` instructions in 120 seconds.

Validation on `/tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64`:

| Run | Artifact / command | Result |
| --- | --- | --- |
| QEMU rebuild | `ninja -C /tmp/linx-qemu-hb-build-20260703-r1 qemu-system-linx64` | pass; only pre-existing warnings |
| AVS system smoke | `python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| AVS call/ret contract | `python3 avs/qemu/run_callret_contract.py --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| AVS all | `python3 avs/qemu/run_tests.py --all --timeout 20 --qemu /tmp/linx-qemu-hb-build-20260703-r1/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train | `workloads/generated/specint-999-fentry-store-probe-qemu-20260703-r1/` | pass; `rand.11.out` size `871`, hash `0x973dcfc2` |
| `505.mcf_r` train 120s | `workloads/generated/specint-505-fentry-store-probe-qemu-20260703-r1/` | live timeout with site-progress heartbeat at `34000000007` instructions |

The 505 heartbeat metric matches the previous template-return-fast best point
rather than improving it, so this is a local helper-path cleanup, not a SPEC
closure. The current comparable sequence is:

| QEMU state | Artifact | Final heartbeat count |
| --- | --- | ---: |
| page-walk cache default-off baseline | `workloads/generated/specint-505-mmu-cache-defaultoff-qemu-20260703-r1/` | `30000000005` |
| tile helper inline | `workloads/generated/specint-505-inline-tile-qemu-20260703-r1/` | `31000000001` |
| template return fast hit | `workloads/generated/specint-505-template-return-fast-qemu-20260703-r1/` | `34000000007` |
| FENTRY save probe reuse | `workloads/generated/specint-505-fentry-store-probe-qemu-20260703-r1/` | `34000000007` |
| FENTRY same-page range probe | `workloads/generated/specint-505-frame-save-range-qemu-20260703-r1/` | rejected: `32000000004` |

Follow-up negative result: an opt-in restore-side host-TLB-hit experiment kept
faulting behavior on the existing `cpu_ldq_le_mmuidx_ra()` fallback, but used
`tlb_vaddr_to_host(..., MMU_DATA_LOAD, ...)` plus `ldq_le_p()` for already
resident RAM-backed restore slots. The temporary build
`/tmp/linx-qemu-frame-restore-host-build-20260703-r1/qemu-system-linx64`
passed the focused system AVS `0x110F`, `run_callret_contract.py`, and strict
train `999.specrand_ir` under
`workloads/generated/specint-999-frame-restore-hostfast-qemu-20260703-r1/`.
It did not improve the focused 505 slice:
`workloads/generated/specint-505-frame-restore-hostfast-qemu-20260703-r1/`
timed out live at `34000000008` instructions in the same 120 second,
1B-heartbeat train shape. Do not add a default-off restore-host branch to the
hot path without a new profile showing a real win; it preserves correctness but
does not move the current 505 bottleneck.

Follow-up negative result: a frame-save same-page range-probe experiment
collapsed adjacent FENTRY save-slot probes into one `probe_write()` call per
target page, then reused offsets from the returned host pointer for the later
stores. The temporary build
`/tmp/linx-qemu-frame-save-range-build-20260703-r1/qemu-system-linx64`
passed `run_callret_contract.py`, the focused system AVS `0x110F`, and strict
PR `999.specrand_ir` test/train under
`workloads/generated/specint-pr-frame-save-range-qemu-20260703-r1/`. It was
slower on the focused 505 comparison: the clean latest-QEMU baseline
`workloads/generated/specint-505-clean-qemu-baseline-20260703-r2/` reached
`34000000002` instructions in 120 seconds, while
`workloads/generated/specint-505-frame-save-range-qemu-20260703-r1/` reached
only `32000000004` instructions with the same heartbeat, stack, memory, and
TLB-fill-stat knobs. The patch was reverted. Do not reintroduce range probing
as the next frame-template speed lane without a new host profile explaining why
the larger probe should win.

`tools/spec2017/profile_qemu_after_spec_start.py` now wraps SPEC/QEMU profiling
runs so host sampling starts only after the generated QEMU log contains
`LINX_SPEC_START`, and only after the wrapper finds the executable basename
`qemu-system-linx64` in the launched process tree. This avoids matching the
Python parent just because its command line contains a `--qemu` argument.

Validation:

| Run | Artifact / command | Result |
| --- | --- | --- |
| profiler unit tests | `python3 -m unittest tools/spec2017/test_profile_qemu_after_spec_start.py` | pass |
| profiler compile check | `python3 -m py_compile tools/spec2017/profile_qemu_after_spec_start.py tools/spec2017/test_profile_qemu_after_spec_start.py` | pass |
| live 505 profile wrapper | `workloads/generated/specint-profile-505-fentry-store-helper-20260703-r2/profile/report.json` | pass; sampled PID `12966`, marker log under the 505 run directory |
| live 505 sample | `workloads/generated/specint-profile-505-fentry-store-helper-20260703-r2/profile/qemu-505-fentry-store.sample.txt` | header is `Analysis of sampling qemu-system-linx64`; not Python |

Current conclusion: keep using the wrapper for post-start samples. The next
speed lane should not spend more time on direct frame load probes; focus on
soft-TLB lookup shape, page-fault/TLB invalidation pressure, and remaining
BSTART cold-target/cache churn.

## 2026-07-03 Clean QEMU Provenance In SPEC Ledgers

The SPEC runners now make latest-QEMU evidence auditable instead of relying on
a path string. `tools/bringup/qemu_build_paths.py` records the selected QEMU
binary path, `--version` line, QEMU submodule HEAD, tracked dirty state, and
the `.linx_qemu_clean_head` marker emitted by `run_qemu_build_clean.sh`.
`run_stage_qemu_matrix.py` now uses the same clean-build-aware default selector
as `run_specint_fast_gate.py`, and all SPEC summary JSON files carry
`qemu_provenance`. Matrix and fast-gate Markdown summaries also print
`qemu_version`, `qemu_repo_head`, and `qemu_clean_build_for_head`.

Validation:

| Run | Artifact | Result |
| --- | --- | --- |
| Clean QEMU build | `/tmp/linx-qemu-clean-build/qemu-system-linx64` | marker `f690aa1f7daf4fdc3f70802c074b65b633418aa3:worktree`; version `v10.2.0-1006-gf690aa1f7da` |
| Focused `999.specrand_ir` train | `workloads/generated/specint-999-provenance-clean-qemu-20260703-r1/` | pass; strict `rand.11.out` hash `0x973dcfc2`; matrix and stage summaries record `clean_build_for_head=true` |
| SPECint PR smoke | `workloads/generated/specint-pr-provenance-clean-qemu-20260703-r1/` | pass; `999.specrand_ir` test and train strict hashes pass; fast-gate summary records the same clean build provenance |

Current conclusion: require `qemu_provenance.clean_build_for_head=true` for
canonical latest-QEMU SPEC ledgers unless the run is explicitly documented as a
dirty or markerless experiment. This avoids promoting stale
`emulator/qemu/build-linx` results after the QEMU submodule moves.

## 2026-07-03 Latest-QEMU Post-Start 505 Profile

The current latest-QEMU verification binary is
`/tmp/linx-qemu-current-build-20260703-r1/qemu-system-linx64`, built from clean
worktree marker `a3061b963f3a80efd66e7edd5fb746bec140d29e:worktree` and
reporting `v10.2.0-1004-ga3061b963f3`. A focused `505.mcf_r` train profiler
run disabled guest heartbeat, host heartbeat, and QEMU heartbeat output, waited
for `LINX_SPEC_START`, then sampled the real QEMU child for 30 seconds.

Artifacts:

| Artifact | Purpose |
| --- | --- |
| `workloads/generated/specint-profile-505-latest-qemu-20260703-r1/run/qemu_matrix_summary.json` | focused run summary |
| `workloads/generated/specint-profile-505-latest-qemu-20260703-r1/run/initramfs/505_mcf_r/run_001/qemu.log` | guest log proving `LINX_SPEC_START` and child `exec` setup |
| `workloads/generated/specint-profile-505-latest-qemu-20260703-r1/profile/qemu-505-latest-qemu-real.sample.txt` | corrected host sample of the real QEMU process |
| `workloads/generated/specint-profile-505-latest-qemu-20260703-r1/profile/qemu-505-latest-qemu.sample.txt` | discarded control sample of the parent wrapper; do not use for conclusions |

The run is expected red because heartbeat was disabled for profiling:
`qemu_matrix_summary.json` classifies the row as `timeout-no-heartbeat` after
180 seconds. The guest log still proves this is past setup: it emits
`LINX_SPEC_START 505.mcf_r`, validates both relative and `/spec-run/`
executable paths, reads ELF magic `0x7f454c46`, and then runs until the cap
without a trap, panic, wrapper child-exit, benchmark internal error, or missing
executable failure.

Top collapsed stacks from the corrected post-start sample:

| Stack top | Samples |
| --- | ---: |
| `helper_linx_template_fentry` | 1093 |
| `mmu_lookup1` | 897 |
| `helper_linx_template_fret_stk` | 715 |
| `mmu_lookup` | 424 |
| `probe_access_internal` | 370 |
| `probe_access` | 232 |
| `linx_frame_restore_commit` | 210 |
| `linx_template_commit_and_exit` | 100 |
| `cpu_stq_mmu` | 85 |
| `cpu_ldq_mmu` | 59 |
| `linx_cpu_tlb_fill` | 58 |

Current conclusion: the previous tile set/reset helper noise remains closed,
and the hot path is now the interaction between Linx template entry/return
frame traffic and QEMU's generic soft-MMU load/store/probe lookup. The next
speed work should test:

1. Template frame traffic reduction: remove or specialize restartable
   save/restore memory traffic only where the call/return ABI and debug trace
   contracts still hold.
2. Soft-MMU lookup specialization: prototype a safe hot path for known-aligned
   FENTRY/FRET stack loads/stores and probe accesses before changing generic
   QEMU TLB behavior.
3. TLB capacity/lookup-shape experiments: compare focused `505.mcf_r` and
   strict `999.specrand_ir` before promoting anything, because the prior
   page-walk cache experiment slowed the comparable 505 slice.
4. Separate `525.x264_r` transport profiling: the all-train TLB-fill ledger
   shows lower fill volume on the 9p shard, so x264 should be profiled as
   9p/syscall/transport overhead instead of being folded into generic 505 TLB
   work.

## 2026-07-03 SPEC QEMU Extra-Args Provenance And Split-WX Check

The macOS post-start sample included `pthread_jit_write_protect_np`, so the
next host-side check tested whether forcing TCG split-WX off changes focused
`505.mcf_r` train throughput. The SPEC runner already forwards
`LINX_SPEC_QEMU_EXTRA_ARGS` to `qemu-system-linx64`, so the experiment used the
same 120 second initramfs shape as the clean latest-QEMU baseline:

```bash
LINX_QEMU_TLB_FILL_STATS=1 \
LINX_SPEC_QEMU_EXTRA_ARGS='-accel tcg,split-wx=off' \
python3 tools/spec2017/run_stage_qemu_matrix.py \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 \
  --stage b --input-set train --transports initramfs --bench 505.mcf_r \
  --strict --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-505-splitwx-off-qemu-20260703-r2 \
  --timeout 120 --memory-mb 2048 --heartbeat-sec 10 \
  --qemu-heartbeat-interval 1000000000 --no-progress-timeout 120 \
  --guest-heartbeat-sec 0 --append-extra norandmaps --stack-limit 2G
```

Result:

| QEMU state | Artifact | Final heartbeat count | TLB-fill total | Result |
| --- | --- | ---: | ---: | --- |
| clean latest baseline | `workloads/generated/specint-505-clean-qemu-baseline-20260703-r2/` | `34000000002` | `107432023` | `live-timeout`; site-progress |
| `-accel tcg,split-wx=off` | `workloads/generated/specint-505-splitwx-off-qemu-20260703-r2/` | `33000000002` | `105026008` | `live-timeout`; site-progress; summary records `qemu_extra_args` |

Conclusion: `split-wx=off` is not a SPEC throughput lever on this host/QEMU
build. A pre-provenance run under
`workloads/generated/specint-505-splitwx-off-qemu-20260703-r1/` matched the
baseline at `34000000002` instructions, while the provenance-aware rerun
reached `33000000002`; neither result beats the clean baseline. Treat the
`pthread_jit_write_protect_np` samples as host TCG/JIT runtime noise unless a
future profile proves a direct Linx hot-path connection. Do not spend the next
speed iteration on split-WX toggles.

The same investigation exposed a reproducibility gap: earlier SPEC summaries
recorded QEMU binary provenance but not the actual forwarded QEMU extra args.
`run_int_rate_qemu.py` now records `qemu_machine`, `qemu_machine_extra`, and
`qemu_extra_args` in each per-run QEMU object. `run_stage_qemu_matrix.py` and
`run_specint_fast_gate.py` now propagate top-level `qemu_machine_extra` and
`qemu_extra_args` into JSON and Markdown summaries. This makes future
accelerator, device, and debug-option experiments auditable from the generated
ledger alone.

## 2026-07-03 TLB-Fill Hot-Page Sketch

QEMU now has an opt-in hot-page sketch for long SPEC rows where aggregate
TLB-fill volume is high but full `LINX_TLB_FILL_TRACE` output would be too
large. Set `LINX_QEMU_TLB_FILL_HOT=1` (or `LINX_TLB_FILL_HOT=1`) alongside
`LINX_QEMU_TLB_FILL_STATS=1`. QEMU emits `LINX_TLB_FILL_HOT` companion lines at
heartbeat boundaries, and the SPEC runner records the parsed data under
`heartbeat_tlb_fill_hot`. Matrix and fast-gate markdown print a compact
`tlbf-hot=<count>@<page>/a<access>/m<mmu> evict=<evictions>` liveness tag.

Validation used rebuilt QEMU
`/tmp/linx-qemu-tlbf-hot-build-20260703-r1/qemu-system-linx64`. The runtime
checks used the identical pre-commit binary that reported
`v10.2.0-1006-gf690aa1f7da-dirty`; after committing and relinking version
metadata, the binary reports `v10.2.0-1007-gbbcad71a5c9`:

- `python3 avs/qemu/run_callret_contract.py --qemu /tmp/linx-qemu-tlbf-hot-build-20260703-r1/qemu-system-linx64`
  passed.
- `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu /tmp/linx-qemu-tlbf-hot-build-20260703-r1/qemu-system-linx64`
  passed.
- `LINX_QEMU_TLB_FILL_STATS=1 LINX_QEMU_TLB_FILL_HOT=1 python3 tools/bringup/run_specint_fast_gate.py --profile pr ...`
  passed `999.specrand_ir` test and train strict hashes under
  `workloads/generated/specint-pr-tlbf-hot-qemu-20260703-r1/`.
- Focused `505.mcf_r` train under
  `workloads/generated/specint-505-tlbf-hot-qemu-20260703-r1/` stayed
  heartbeat-live and timed out at count `34000000009`, BPC `0x155555cfa0`.
  The final aggregate TLB-fill count was `107430385`, with
  `98282014` loads and `8631328` stores. The hot sketch identified
  `tlbf-hot=2601@0x1555568000/a2/m1 evict=107427582`; the hottest tuple was a
  user MMU probe/fetch-pressure page around `0x1555568000`, not a single
  long-lived data-page store fault. High eviction pressure means this
  16-slot sketch is only a coarse guide; use it to select VA/PC windows for
  full `LINX_QEMU_TLB_FILL_TRACE`, not as exact attribution.

Next speed work should keep using `LINX_QEMU_TLB_FILL_HOT=1` on focused 505
and strict 999 comparisons while prototyping soft-TLB lookup specialization.
If the hottest page stays in stable text/probe traffic, investigate BSTART or
probe-access memoization before changing generic data TLB behavior.

## 2026-07-03 All-Train Hot-Page Ledger

`workloads/generated/specint-train-all-tlbf-hot-qemu-20260703-r1/` reruns the
split train profile on QEMU `v10.2.0-1007-gbbcad71a5c9` with
`LINX_QEMU_TLB_FILL_STATS=1` and `LINX_QEMU_TLB_FILL_HOT=1`. `999.specrand_ir`
still passes strict train hash. Every other supported SPECint row is a
heartbeat-backed `live-timeout` with BPC site progress and no trap, panic,
wrapper child-exit, or no-progress class.

The new hot-page sketch separates the next speed lanes:

| Benchmark | Result | TLB-fill / hot page | Symbolized hot site |
| --- | --- | --- | --- |
| `500.perlbench_r` | live-timeout | `tlbf=5230387`, `tlbf-hot=1464@0x15556eb000/a2/m1` | `Storable.c` retrieve paths |
| `502.gcc_r` | live-timeout | `tlbf=6193472`, `tlbf-hot=9324@0x1556092000/a2/m1` | GCC `insn-emit.c` / `insn-recog.c` |
| `505.mcf_r` | live-timeout | `tlbf=147528309`, `tlbf-hot=2591@0x1555568000/a2/m1` | startup parse plus `spec_qsort` progress |
| `520.omnetpp_r` | live-timeout | `tlbf=11430703`, `tlbf-hot=238540@0x15555fe000/a2/m1` | config/name lookup executable-probe traffic |
| `523.xalancbmk_r` | live-timeout | `tlbf=6164604`, `tlbf-hot=4027@0x1555a60000/a2/m1` | Xerces parser paths |
| `525.x264_r` | live-timeout | `tlbf=1873401`, `tlbf-hot=5@0xffffffff80406000/a2/m0` | kernel context/SLUB on the 9p shard |
| `531.deepsjeng_r` | live-timeout | `tlbf=11811921`, `tlbf-hot=655640@0x1556096000/a0/m1` | `neval.cpp` load traffic |
| `541.leela_r` | live-timeout | `tlbf=1999924`, `tlbf-hot=1147@0x1555623000/a2/m1` | C++ locale / bit-vector paths |
| `557.xz_r` | live-timeout | `tlbf=3644604`, `tlbf-hot=25204@0x3f7feff000/a0/m1` | malloc free-list plus kernel allocator progress |

For this run, user hot PCs symbolize with load base `0x1555155000`; future
focused runs should preserve `/proc/<child>/maps` evidence before assuming the
same base. The next QEMU speed loop should test user data soft-TLB lookup
specialization on `505`/`531`, executable probe/BSTART memoization on `520`,
and a separate kernel/9p transport profile for `525`.

## 2026-07-03 Frame-Template Heartbeat Counters

QEMU now has an opt-in frame-template counter surface for SPEC liveness runs.
Set `LINX_QEMU_FRAME_STATS=1` directly, or pass `--qemu-frame-stats` through
`tools/spec2017/run_int_rate_qemu.py` / `run_stage_qemu_matrix.py`. When QEMU
BPC heartbeat is enabled, the `LINX_HEARTBEAT` line appends:

- `fr_fentry`, `fr_fret_stk`, `fr_fret_ra`, `fr_fexit`
- `fr_save_probe`, `fr_save_slot`, `fr_save_host`, `fr_save_fallback`
- `fr_restore_slot`
- `fr_ret_fast`, `fr_ret_check`

The SPEC runner records these fields under `heartbeat_frame_stats`; matrix
failure details print a compact `frame=` tag. The counters are off by default,
so routine runs keep the existing heartbeat surface unless the switch is set.

Validation on `/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64`:

| Check | Result |
| --- | --- |
| `python3 -m unittest test_run_int_rate_qemu.py` from `tools/spec2017` | pass, 38 tests |
| `ninja qemu-system-linx64` in `emulator/qemu/build-linx` | pass; only pre-existing helper warnings |
| `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train | `workloads/generated/spec-frame-stats-smoke-clean-20260703-r1/train-999/stage_b_summary.json` passes strict hash on QEMU `v10.2.0-1010-g5937d0a2c27` |
| focused `505.mcf_r` train 120s | `workloads/generated/spec-frame-stats-505-clean-20260703-r1/train-505/stage_b_summary.json` is heartbeat-live `live-timeout` on the same clean QEMU head |

The strict `999.specrand_ir` train proof reached final heartbeat count
`508000006` with `fr_fentry=6737765`, `fr_save_slot=21693730`,
`fr_save_host=21693730`, `fr_save_fallback=0`, `fr_fret_stk=6737678`,
`fr_restore_slot=21693250`, `fr_ret_fast=6715182`, and
`fr_ret_check=22496`.

The focused `505.mcf_r` train proof timed out after 120 seconds at heartbeat
count `30700000007`, BPC `0x158c87d6c6`, with
`heartbeat_running=true`, `heartbeat_site_progress=true`, seven recent unique
sites, and no heartbeat stall marker. Its final frame counters are
`fr_fentry=405793989`, `fr_save_slot=434098855`,
`fr_save_host=434098855`, `fr_save_fallback=0`,
`fr_fret_stk=405793915`, `fr_restore_slot=434098433`,
`fr_ret_fast=405736143`, and `fr_ret_check=57772`.

Loop update: `505.mcf_r` is still a throughput timeout, not a deadlock. The
new counters show roughly 1.071 save slots per FENTRY and 1.071 restore slots
per FRET.STK, all save stores using the already-probed host pointer, and a
99.986% return fast-hit rate. Do not spend the next speed pass on fallback
frame stores or return BSTART cache misses without fresh contradictory
evidence. Keep the next QEMU speed loop on generic soft-TLB/probe lookup shape,
translated frame load cost, and benchmark data-memory traffic; keep `999` as
the strict correctness sentinel.

## 2026-07-03 TB Stats Heartbeat Counters And 505 Evidence

QEMU now has an opt-in TCG translation-block counter surface for SPEC
live-timeout runs. Set `LINX_QEMU_TB_STATS=1` directly, or pass
`--qemu-tb-stats` through `tools/spec2017/run_int_rate_qemu.py` /
`run_stage_qemu_matrix.py`. When QEMU BPC heartbeat is enabled,
`LINX_HEARTBEAT` appends:

- `tbs_exec`, `tbs_lookup`, `tbs_jmp_hit`, `tbs_hash_hit`
- `tbs_miss`, `tbs_gen`, `tbs_flush`, `tbs_phys_inv`
- `tbs_code_used`, `tbs_code_size`

The SPEC runner records these fields under `heartbeat_tb_stats`; matrix
failure details print a compact `tb=` tag. The counters are off by default.

The motivating post-`LINX_SPEC_START` 505 profile is
`workloads/generated/specint-profile-505-frame-stats-clean-20260703-r2/`.
The wrapper sampled only the `qemu-system-linx64` child, and the sample still
shows `pthread_jit_write_protect_np` under `cpu_tb_exec`, plus soft-MMU and
Linx frame-template helpers. This made TB dispatch/cache pressure worth
measuring directly instead of guessing from host samples.

Validation on `/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64`:

| Check | Result |
| --- | --- |
| `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py tools/spec2017/run_stage_qemu_matrix.py tools/spec2017/test_run_int_rate_qemu.py` | pass |
| `python3 -m unittest test_run_int_rate_qemu.py` from `tools/spec2017` | pass, 39 tests |
| `ninja qemu-system-linx64` in `emulator/qemu/build-linx` | pass; only pre-existing helper warnings |
| `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train with `--qemu-tb-stats` | `workloads/generated/specint-tbstats-999-clean-20260703-r1/` passes strict hash |
| focused `505.mcf_r` train 120s with `LINX_QEMU_TLB_FILL_STATS=1 --qemu-tb-stats` | `workloads/generated/specint-tbstats-505-clean-20260703-r1/` remains heartbeat-live `live-timeout` |

The strict `999.specrand_ir` train reached final heartbeat count `500000002`
with `tbs_exec=16985603`, `tbs_lookup=20264692`,
`tbs_jmp_hit=17227425`, `tbs_hash_hit=3009457`, `tbs_miss=27809`,
`tbs_gen=25810`, `tbs_flush=0`, `tbs_phys_inv=3480`,
`tbs_code_used=30535720`, and `tbs_code_size=1073725352`.

The focused `505.mcf_r` train reached count `28000000000`, BPC
`0x155555cdb2`, `heartbeat_running=true`, and
`heartbeat_site_progress=true`. Its final TB counters were
`tbs_exec=748895025`, `tbs_lookup=1074296001`,
`tbs_jmp_hit=1060230997`, `tbs_hash_hit=14032554`,
`tbs_miss=32446`, `tbs_gen=30211`, `tbs_flush=0`,
`tbs_phys_inv=3480`, `tbs_code_used=36007384`, and
`tbs_code_size=1073725352`. The final TLB-fill counters were still
data-load dominated: `tlbf_total=93189309`, `tlbf_load=85825683`,
`tlbf_store=6978528`, `tlbf_probe=3287`, `tlbf_user=91315933`,
and `tlbf_kernel=1873376`.

Loop update: `505.mcf_r` is not blocked on TB code-cache capacity or TB churn.
The miss/generation counts plateau early, there are no TB flushes, and only
about 36 MiB of the roughly 1 GiB code buffer is used. Reject larger TCG
`tb-size` as the next lever: the focused
`workloads/generated/specint-505-tbsize512-qemu-20260703-r1/` probe reached
only `30000000004` instructions in 120 seconds, worse than the clean
`34000000002` baseline. The next QEMU speed loop should target per-TB dispatch
and Darwin JIT write-protect transition cost, plus soft-MMU load/probe lookup
specialization; keep `--qemu-tb-stats` on focused comparisons to prove the
change does not introduce TB churn.

## 2026-07-03 Rejected Darwin JIT State Guard

A local QEMU experiment cached the current thread's Darwin
`pthread_jit_write_protect_np()` mode in `qemu_thread_jit_execute()` /
`qemu_thread_jit_write()` to skip redundant same-state transitions. The change
compiled and preserved cheap correctness, but it did not improve the current
SPEC throughput path and was backed out before commit.

Validation on the local dirty guarded binary:

| Check | Artifact | Result |
| --- | --- | --- |
| QEMU build | `emulator/qemu/build-linx/qemu-system-linx64` | `ninja qemu-system-linx64` passed; only pre-existing warnings |
| QEMU call/ret contract | `avs/qemu/out/callret-contract` | pass |
| QEMU system sentinel `0x110F` | `avs/qemu/out/linx-qemu-tests.elf` | pass |
| strict `999.specrand_ir` train | `workloads/generated/specint-jitguard-999-qemu-20260703-r1/` | pass |
| focused `505.mcf_r` train, TB/TLB stats on | `workloads/generated/specint-jitguard-505-qemu-20260703-r1/` | heartbeat-live `live-timeout` at `31000000008` instructions |
| focused `505.mcf_r` train, no TB/TLB stats | `workloads/generated/specint-jitguard-505-nostats-qemu-20260703-r1/` | heartbeat-live `live-timeout` at `30000000007` instructions |

The no-stats run is the apples-to-apples throughput comparison and is worse
than the clean no-stats baseline around `34000000002` instructions in the same
120 second shape. The TB/TLB-stats run improved over the previous stats-heavy
`28000000000` count, but remained below the no-stats baseline and therefore is
not a promotion signal.

Loop update: do not retry a simple TLS-state guard around
`qemu_thread_jit_execute()` / `qemu_thread_jit_write()` as the next SPEC speed
fix. Keep `pthread_jit_write_protect_np` in the profile as a symptom of
per-TB dispatch frequency, but route implementation work toward reducing
dispatch exits, generated helper exits, or soft-MMU load/probe work rather than
memoizing the Apple wrapper call.

## 2026-07-03 Current-Head All-Train Ledger

Clean QEMU head `193c36d8556b6cb072e8e476d933d756428ab4e4`
(`v10.2.0-1011-g193c36d8556`) was rebuilt through
`tools/bringup/run_qemu_build_clean.sh` into
`/tmp/linx-qemu-clean-build/qemu-system-linx64`. The train gate
`workloads/generated/specint-train-all-current-head-qemu-20260703-r1/`
records `qemu_provenance.clean_build_for_head=true`,
`clean_build_marker_matches_head=true`, and `qemu_repo_dirty_tracked=false`.

Command shape:

```bash
LINX_QEMU_TLB_FILL_STATS=1 \
LINX_SPEC_QEMU_TB_STATS=1 \
SPECINT_TRAIN_ALL_TIMEOUT=300 \
SPEC_GUEST_HEARTBEAT_SEC=0 \
SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
SPEC_NO_PROGRESS_TIMEOUT=180 \
QEMU_CLEAN_OUT_DIR=/tmp/linx-qemu-clean-build \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-all-current-head-qemu-20260703-r1 \
  --append-extra norandmaps \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --guest-heartbeat-sec 0 \
  --no-progress-timeout 180 \
  --stack-limit 2G \
  --continue-on-fail
```

Result: the gate is red only because the train rows are bounded to 300s.
`999.specrand_ir` still passes the strict train sentinel. Every other tracked
C/C++ SPECint row is `live-timeout` with `heartbeat_running=true`,
`heartbeat_site_progress=true`, `stalled=false`, no panic, and no user trap.
`525.x264_r` runs in the generated 9p shard and is also live-timeout, not the
old oversized-initramfs VFS panic.

| Benchmark | Transport | Result | Final BPC / pressure counters |
| --- | --- | --- | --- |
| `500.perlbench_r` | initramfs | `live-timeout` | `bpc=0x15556d9620`, `count=87000000002`, `tlbf=5565290`, `tb_lookup=1878886817`, `tb_gen=63743` |
| `502.gcc_r` | initramfs | `live-timeout` | `bpc=0x1555893e3c`, `count=48000000011`, `tlbf=10101255`, `tb_lookup=3237627725`, `tb_gen=219703` |
| `505.mcf_r` | initramfs | `live-timeout` | `bpc=0x155555cc06`, `count=79000000004`, `tlbf=211449824`, `tlbf_load=189522075`, `tb_gen=30246` |
| `520.omnetpp_r` | initramfs | `live-timeout` | `bpc=0x15557cba1e`, `count=32000000028`, `tlbf=14341840`, `tb_hash_hit=652333795`, `tb_gen=70529` |
| `523.xalancbmk_r` | initramfs | `live-timeout` | `bpc=0x155593291a`, `count=38000000000`, `tlbf=7812653`, `tb_hash_hit=660653977`, `tb_gen=82393` |
| `525.x264_r` | 9p | `live-timeout` | `bpc=0xffffffff8011612a`, `count=48000000002`, `tlbf=1869627`, `tb_lookup=3930070800`, `tb_gen=30072` |
| `531.deepsjeng_r` | initramfs | `live-timeout` | `bpc=0x1555559464`, `count=81000000013`, `tlbf=14996831`, `tb_hash_hit=429307975`, `tb_gen=32341` |
| `541.leela_r` | initramfs | `live-timeout` | `bpc=0x155557308a`, `count=37000000002`, `tlbf=2128107`, `tb_lookup=4885024262`, `tb_gen=39744` |
| `557.xz_r` | initramfs | `live-timeout` | `bpc=0x1555577064`, `count=84000000012`, `tlbf=26090642`, `tlbf_load=24080262`, `tb_gen=34175` |
| `999.specrand_ir` | initramfs | pass | strict train hash passes; QEMU exits normally |

Loop update: the all-train current-head sweep continues to split into three
speed lanes. `505.mcf_r` is the dominant soft-MMU data-load translation case:
roughly 211M TLB fills, 189M loads, no TB churn, and only about 36 MiB of the
TCG code buffer used. `520.omnetpp_r`, `523.xalancbmk_r`, `541.leela_r`, and
part of `531.deepsjeng_r` are more TB-dispatch/hash-lookup shaped than
TLB-capacity shaped. `525.x264_r` is a kernel/9p transport lane with frozen
TLB-fill counters after early setup and changing kernel BPCs. The next QEMU
patch loop should therefore prioritize soft-MMU load/probe lookup
specialization and generated helper exit reduction for `505`, separately
profile TB dispatch/hash lookup cost for the C++/game rows, and keep `525` on
a transport or future block-device lane. Keep strict `999.specrand_ir` train
as the correctness sentinel after each hot-path experiment.

## 2026-07-04 Frame Restore Attribution

QEMU now appends `fr_restore_host` and `fr_restore_fallback` to
`LINX_QEMU_FRAME_STATS=1` heartbeats, and the SPEC runner records those fields
under `heartbeat_frame_stats`. This makes frame restore load attribution
visible next to the existing save-store and return-cache counters.

Validation on `/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64`:

| Check | Result |
| --- | --- |
| `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py tools/spec2017/run_stage_qemu_matrix.py tools/spec2017/test_run_int_rate_qemu.py` | pass |
| `python3 -m unittest test_run_int_rate_qemu.py` from `tools/spec2017` | pass, 39 tests |
| `ninja qemu-system-linx64` in `emulator/qemu/build-linx` | pass; only pre-existing helper warnings |
| `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| strict `999.specrand_ir` train with `--qemu-frame-stats` | `workloads/generated/specint-restorefast-999-frame-qemu-20260704-r1/` passes strict hash |
| focused `505.mcf_r` train 60s with `--qemu-frame-stats` | `workloads/generated/specint-restorefields-505-frame-qemu-20260704-r1/` remains heartbeat-live `live-timeout` |

The final 60-second `505.mcf_r` frame-stats probe reached count
`11000000000`, BPC `0x155555c47e`, `heartbeat_running=true`,
`heartbeat_site_progress=true`, `stalled=false`, no panic, and no trap. Frame
stats show that the current save path is already direct-host dominated while
restore remains fully generic: `fr_save_slot=170392325`,
`fr_save_host=170392325`, `fr_save_fallback=0`,
`fr_restore_slot=170391897`, `fr_restore_host=0`, and
`fr_restore_fallback=170391897`.

A local QEMU experiment then tried to convert frame restore loads to
`tlb_vaddr_to_host()` plus direct `ldq_le_p()` for aligned, page-contained
8-byte slots, falling back to `cpu_ldq_le_mmuidx_ra()` otherwise. It preserved
the strict `999.specrand_ir` sentinel, but the comparable no-stats
`505.mcf_r` run in
`workloads/generated/specint-restorefast-505-nostats-qemu-20260704-r1/`
reached only `29000000005` instructions in 120 seconds, below the clean
no-stats baseline around `34000000002`. The direct-host restore-load fast path
was backed out before commit.

Loop update: do not retry a per-slot helper-side `tlb_vaddr_to_host()` restore
load as the next SPEC speed patch. If frame restore is revisited, batch the
translation by page/frame or move restore loads out of the C helper path
instead of adding another TLB probe per saved register. The next QEMU speed
loop should focus on generated helper-exit reduction and TB dispatch/hash
pressure, while using the new `fr_restore_host`/`fr_restore_fallback` fields
to check whether a future restore-load experiment actually changes the frame
traffic mix.

## 2026-07-04 BSTART Inline Cache Probe

QEMU commit `7b6b33df2ca` adds a translated positive-only fast path for cached
BSTART target checks. The generated code skips `helper_linx_check_bstart_target`
only when the cached slot is valid, the tag matches the dynamic target, and the
translated MMU index matches. Misses and debug modes still call the helper;
`LINX_BSTART_INLINE_CACHE=0` disables the translated fast path, and
`LINX_CFI_TRACE`, `LINX_BSTART_CACHE_REVALIDATE`, and
`LINX_BSTART_CACHE_STATS` force the original helper behavior.

Validation on the clean committed binary:

- `qemu-system-linx64 --version` reports
  `v10.2.0-1013-g7b6b33df2ca`.
- `ninja -C emulator/qemu/build-linx qemu-system-linx64` passes.
- `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system
  --require-test-id 0x110F --timeout 20 --qemu
  emulator/qemu/build-linx/qemu-system-linx64` passes.
- `python3 avs/qemu/run_callret_contract.py --qemu
  emulator/qemu/build-linx/qemu-system-linx64` passes.
- `workloads/generated/specint-bstart-inline-999-qemu-clean-20260704-r1/`
  passes the `999.specrand_ir` train hash (`rand.11.out`, 871 bytes,
  `0x973dcfc2`) on QEMU head
  `7b6b33df2ca8c89517b493d7d149c26ea332badc` with
  `qemu_repo_dirty_tracked=false`.

Focused `520.omnetpp_r` train comparison remains performance-neutral in the
90-second no-extra-stats shape:

| Run | Result | Final proof |
| --- | --- | --- |
| `workloads/generated/specint-bstart-inline-520-off-qemu-20260704-r1/` | `live-timeout` | `count=8000000006`, `bpc=0x15555f155a`, site progress true |
| `workloads/generated/specint-bstart-inline-520-on-qemu-20260704-r1/` | `live-timeout` | `count=8000000000`, `bpc=0x15555f0690`, site progress true |

Loop update: keep this as a conservative helper-exit reduction foundation, not
as a claimed SPEC speedup. The short 520 probe is neutral, so the next speed
loop should either measure branch-helper hit rate directly or move to the
already identified soft-MMU/TB-dispatch lanes before further generated-code
complexity.

## 2026-07-04 Block-Aware MMU Cache Probe

Source review rejected the tempting "large TLB mapping" route: QEMU
`tlb_set_page_full()` still materializes one `TARGET_PAGE_SIZE` entry, and the
`size` argument is only used to track large-page invalidation ranges. Passing a
2 MiB or 1 GiB Linx block size to the generic soft-TLB would therefore not
reduce demand TLB misses.

The follow-up QEMU probe keeps the existing page-walk result cache opt-in
behind `LINX_MMU_CACHE=1` / `LINX_QEMU_MMU_CACHE=1`, but makes it block-aware.
Cache lookup now probes 4 KiB, 2 MiB, 1 GiB, and 512 GiB candidate bases, and
TLBI page invalidation clears the matching candidate slots for both MMU
indices. The default path remains cache-off.

Validation on `/Users/zhoubot/linx-isa/emulator/qemu/build-linx/qemu-system-linx64`
after the patch:

| Check | Result |
| --- | --- |
| `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py tools/spec2017/run_stage_qemu_matrix.py tools/spec2017/test_run_int_rate_qemu.py` | pass |
| `python3 -m unittest test_run_int_rate_qemu.py` from `tools/spec2017` | pass, 40 tests |
| `ninja -C emulator/qemu/build-linx qemu-system-linx64` | pass |
| `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_VIRT_TEST_FINISHER=1 python3 avs/qemu/run_tests.py --suite system --require-test-id 0x110F --timeout 20 --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| strict `999.specrand_ir`, default cache-off | `workloads/generated/specint-block-mmu-cache-999-off-qemu-20260704-r1/` passes strict train hash |
| strict `999.specrand_ir`, `LINX_QEMU_MMU_CACHE=1 LINX_QEMU_MMU_CACHE_STATS=1` | `workloads/generated/specint-block-mmu-cache-999-on-qemu-20260704-r1/` passes strict train hash |

Focused `505.mcf_r` train comparison in the same 120-second no-extra-TLB-stats
shape:

| Run | Result | Final proof |
| --- | --- | --- |
| cache disabled | `workloads/generated/specint-block-mmu-cache-505-off-qemu-20260704-r1/` live-timeout | `count=28000000002`, `bpc=0x155555c482`, `mmuc=h0/m0/f0` |
| cache enabled with cache stats | `workloads/generated/specint-block-mmu-cache-505-on-qemu-20260704-r1/` live-timeout | `count=29000000001`, `bpc=0x155555cc20`, `mmuc=h87701206/m7953961/f7949164`, `mmuc_flush=21`, `mmuc_flush_page=3675648` |
| cache enabled without cache stats | `workloads/generated/specint-block-mmu-cache-505-on-nostats-qemu-20260704-r1/` live-timeout | `count=30000000003`, `bpc=0x155555c482` |

Loop update: the block-aware page-walk cache is a real candidate because it
hits heavily and improves the same-binary focused `505.mcf_r` count by about
7% without cache-stat increments. Keep it opt-in until it is checked on at
least `531.deepsjeng_r` and a train-all shard, because the count remains below
older no-stats best runs and the broader SPEC failures are still bounded
throughput live-timeouts, not correct completions.

## 2026-07-04 Block-Aware MMU Cache Follow-Up

QEMU was rebuilt cleanly after the cache commit; `qemu-system-linx64 --version`
reports `v10.2.0-1014-gb37d0a56980`, and generated SPEC summaries record
`qemu_repo_dirty_tracked=false`.

Focused `531.deepsjeng_r` train comparison in the same 120-second shape:

| Run | Result | Final proof |
| --- | --- | --- |
| cache disabled | `workloads/generated/specint-block-mmu-cache-531-off-qemu-20260704-r1/` live-timeout | `count=30000000001`, `bpc=0x155556a8ec`, `mmuc=h0/m0/f0` |
| cache enabled with cache stats | `workloads/generated/specint-block-mmu-cache-531-on-qemu-20260704-r1/` live-timeout | `count=31000000004`, `bpc=0x1555565068`, `mmuc=h3134641/m4383782/f4207941`, `mmuc_flush=20`, `mmuc_flush_page=3849672` |
| cache enabled without cache stats | `workloads/generated/specint-block-mmu-cache-531-on-nostats-qemu-20260704-r1/` live-timeout | `count=30000000002`, `bpc=0x155556d7b4` |

The 531 result is neutral without cache-stat increments, so the cache does not
generalize as a clear 531 speedup. It also does not regress the row in this
bounded run.

The cache-on train-all shard
`workloads/generated/specint-train-all-block-mmu-cache-qemu-20260704-r1/`
uses `LINX_QEMU_MMU_CACHE=1`, `LINX_QEMU_MMU_CACHE_STATS=1`, train input, and
a 120-second per-row cap. `999.specrand_ir` still passes the strict train hash;
all other rows remain heartbeat-backed live-timeouts with site progress, no
panic, and no user trap.

| Benchmark | Transport | Result | Final proof |
| --- | --- | --- | --- |
| `500.perlbench_r` | initramfs | `live-timeout` | `count=31000000002`, `bpc=0x15556df8ee`, `mmuc=h1485024/m2064353/f2051579` |
| `502.gcc_r` | initramfs | `live-timeout` | `count=19000000005`, `bpc=0x1555ec5df8`, `mmuc=h1993232/m2789822/f2744614` |
| `505.mcf_r` | initramfs | `live-timeout` | `count=29000000002`, `bpc=0x155555cbf4`, `mmuc=h87701676/m7953956/f7949159` |
| `520.omnetpp_r` | initramfs | `live-timeout` | `count=12000000005`, `bpc=0xffffffff803e91e4`, `mmuc=h4719642/m3200580/f3141636` |
| `523.xalancbmk_r` | initramfs | `live-timeout` | `count=15000000006`, `bpc=0x155598aea2`, `mmuc=h2405797/m1932869/f1908594` |
| `525.x264_r` | 9p | `live-timeout` | `count=18000000002`, `bpc=0xffffffff80114874`, `mmuc=h16521/m1853214/f1853187` |
| `531.deepsjeng_r` | initramfs | `live-timeout` | `count=30000000002`, `bpc=0x15555614fa`, `mmuc=h3053373/m4319527/f4143686` |
| `541.leela_r` | initramfs | `live-timeout` | `count=12000000001`, `bpc=0x155558e77c`, `mmuc=h35360/m1853834/f1853234` |
| `557.xz_r` | initramfs | `live-timeout` | `count=27000000000`, `bpc=0x155558d700`, `mmuc=h2656007/m2483381/f2327024` |
| `999.specrand_ir` | initramfs | pass | strict train hash passes; normal QEMU exit |

Loop update: keep `LINX_QEMU_MMU_CACHE=1` opt-in. It is promising for
`505.mcf_r` and moderately useful for some parser/C++ rows, but it is neutral
on focused 531 without stats and nearly unused by `541.leela_r` and the 9p
`525.x264_r` shard. Do not make it default-on before a no-stats train-all
comparison shows a clear aggregate win. Next speed work should split by row:
continue soft-MMU/page-walk work for `505`, route `520`/`523`/`557` through
combined cache plus TB/helper-exit profiling, and keep `541`/`525` out of the
generic MMU-cache promotion decision.

## 2026-07-04 No-Stats Train-All MMU Cache Comparison

The follow-up no-stats train-all comparison used the same rebuilt QEMU
`b37d0a5698092b1c9987582c5a925c446811e042`
(`v10.2.0-1014-gb37d0a56980`) with `qemu_repo_dirty_tracked=false`. The
generated summaries are markerless because this is the in-tree
`emulator/qemu/build-linx/qemu-system-linx64` binary, not a `/tmp` clean-build
marker directory.

Cache-off command shape:

```bash
SPECINT_TRAIN_ALL_TIMEOUT=120 \
SPEC_GUEST_HEARTBEAT_SEC=0 \
SPEC_QEMU_HEARTBEAT_INTERVAL=1000000000 \
SPEC_NO_PROGRESS_TIMEOUT=120 \
python3 tools/bringup/run_specint_fast_gate.py \
  --profile train \
  --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 \
  --qemu emulator/qemu/build-linx/qemu-system-linx64 \
  --sysroot out/libc/musl/install/phase-b \
  --out-dir workloads/generated/specint-train-all-block-mmu-cache-off-nostats-qemu-20260704-r1 \
  --append-extra norandmaps \
  --heartbeat-sec 30 \
  --qemu-heartbeat-interval 1000000000 \
  --guest-heartbeat-sec 0 \
  --no-progress-timeout 120 \
  --stack-limit 2G \
  --continue-on-fail
```

Cache-on command shape is identical, with `LINX_QEMU_MMU_CACHE=1` added and
`--out-dir workloads/generated/specint-train-all-block-mmu-cache-on-nostats-qemu-20260704-r1`.
Neither run enabled `LINX_QEMU_MMU_CACHE_STATS`, so this measures the cache
without per-fill hit/miss counter increments.

Both runs cover the split train profile:
`train-all/initramfs/stage_b_summary.json` plus
`train-all-large-9p/9p/stage_b_summary.json`. `999.specrand_ir` passes the
strict train hash in both runs (`rand.11.out`, 871 bytes, `0x973dcfc2`).
Every other row is still a heartbeat-backed `live-timeout` with BPC site
progress and no panic or user trap.

| Benchmark | Transport | Cache off | Cache on | Delta |
| --- | --- | ---: | ---: | ---: |
| `500.perlbench_r` | initramfs | `32000000000` | `32000000005` | neutral |
| `502.gcc_r` | initramfs | `19000000002` | `19000000001` | neutral |
| `505.mcf_r` | initramfs | `28000000002` | `30000000009` | `+7.1%` |
| `520.omnetpp_r` | initramfs | `11000000006` | `11000000006` | neutral |
| `523.xalancbmk_r` | initramfs | `15000000000` | `16000000004` | `+6.7%` |
| `525.x264_r` | 9p | `18000000003` | `18000000003` | neutral |
| `531.deepsjeng_r` | initramfs | `31000000027` | `31000000005` | neutral |
| `541.leela_r` | initramfs | `12000000001` | `13000000006` | `+8.3%` |
| `557.xz_r` | initramfs | `28000000005` | `28000000001` | neutral |
| `999.specrand_ir` | initramfs | pass | pass | strict hash preserved |

Loop update: keep the block-aware MMU cache opt-in/default-off. The no-stats
comparison removes the stats-overhead concern and shows useful row-level gains
for `505`, `523`, and `541`, with no meaningful regression in the bounded
counts. It is still not a broad enough aggregate win to promote by default:
`500`, `502`, `520`, `525`, `531`, and `557` are neutral at this cap, and all
non-999 rows remain throughput live-timeouts rather than correct completions.
Next work should either combine this cache with the TB/helper-exit lane for
`523`/`541`, or focus the cache design on the data-load-heavy `505` path before
retesting promotion.

## 2026-07-04 523 Cache-On Post-Start Profile

`workloads/generated/specint-profile-523-mmucache-qemu-20260704-r1/` profiles
`523.xalancbmk_r` train after `LINX_SPEC_START` with `LINX_QEMU_MMU_CACHE=1`.
The wrapper sampled the actual `qemu-system-linx64` child for 30 seconds:

- report:
  `workloads/generated/specint-profile-523-mmucache-qemu-20260704-r1/profile/qemu-523-mmucache.sample.json`
- sample:
  `workloads/generated/specint-profile-523-mmucache-qemu-20260704-r1/profile/qemu-523-mmucache.sample.txt`
- run summary:
  `workloads/generated/specint-profile-523-mmucache-qemu-20260704-r1/run/initramfs/stage_b_summary.json`

The row remains a bounded `live-timeout` with `heartbeat_running=true`,
`heartbeat_site_progress=true`, no panic, and no trap. The final heartbeat was
`count=15000000000`, `bpc=0xffffffff803e91e4`; the sample itself is valid even
though profiling overhead lowers the count relative to the no-stats comparison.

Top active QEMU frames from "Sort by top of stack" after excluding parked
threads:

| Frame | Samples |
| --- | ---: |
| `pthread_jit_write_protect_np` | 3815 |
| `cpu_exec_setjmp` | 1107 |
| `tb_lookup` | 957 |
| `qht_lookup_custom` | 671 |
| `cpu_exec_loop` | 628 |
| `helper_linx_template_fret_stk` | 597 |
| `helper_linx_template_fentry` | 566 |
| `probe_access_internal` | 499 |
| `mmu_lookup1` | 381 |
| `linx_frame_restore_commit` | 245 |
| `probe_access` | 206 |
| `do_ld8_mmu` | 196 |
| `mmu_lookup` | 192 |
| `helper_lookup_tb_ptr` | 160 |
| `cpu_tb_exec` | 143 |
| `linx_template_commit_and_exit` | 125 |
| `linx_is_bstart_at_addr` | 66 |
| `helper_linx_check_bstart_target` | 56 |

Loop update: for `523` and likely `541`, the next QEMU speed target is not more
MMU-cache statistics. It is the TCG dispatch/helper-exit lane: reduce
template-frame helper exits, TB lookup/hash pressure, and macOS JIT
write-protect transitions. Keep the block-aware MMU cache as an opt-in
component for comparison, then prototype a frame-template fast path or TB
lookup/helper-exit reduction with the same post-start profile wrapper.

## 2026-07-04 Opt-In Frame Template Chain Probe

QEMU commit `51f42d1726c` adds `LINX_QEMU_TEMPLATE_CHAIN=1`. The default path
still uses the original no-return frame-template helpers. With the switch
enabled, successful `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` helpers return
to translated code after completing their existing probes, memory operations,
CFI checks, trace commit, and `env->pc` update; the translated block then uses
`tcg_gen_lookup_and_goto_ptr()` to continue. Fault paths remain inside the same
helper logic, and the feature stays opt-in until a broad all-row run proves it.

Validation:

| Check | Result |
| --- | --- |
| `ninja -C emulator/qemu/build-linx qemu-system-linx64` | pass |
| default `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_TEMPLATE_CHAIN=1 python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_TEMPLATE_CHAIN=1 python3 tools/bringup/run_specint_fast_gate.py --profile pr ...` | pass, `workloads/generated/specint-template-chain-pr-qemu-20260704-r1/` |
| `LINX_QEMU_TEMPLATE_CHAIN=1` Stage-B train `999.specrand_ir` | pass, `workloads/generated/specint-template-chain-999-stageb-qemu-20260704-r1/` |

Focused `523.xalancbmk_r` train comparison with the block-aware MMU cache also
enabled:

| Run | Result | Final proof |
| --- | --- | --- |
| `LINX_QEMU_MMU_CACHE=1`, no template chain | `live-timeout` | `workloads/generated/specint-523-mmucache-focused-baseline-qemu-20260704-r1/`, `count=16000000000`, `bpc=0xffffffff803e91e4`, no panic/trap |
| `LINX_QEMU_TEMPLATE_CHAIN=1 LINX_QEMU_MMU_CACHE=1` | `live-timeout` | `workloads/generated/specint-template-chain-523-mmucache-qemu-20260704-r1/`, `count=22000000002`, `bpc=0x15559aa4a6`, no panic/trap |

The follow-up all-row train comparison used `LINX_QEMU_TEMPLATE_CHAIN=1` alone
with the same 120-second train-all budget, no guest heartbeat, QEMU heartbeat
every 1B guest instructions, `norandmaps`, and the generated split
`train-all-large-9p` shard for `525.x264_r`:
`workloads/generated/specint-train-all-template-chain-qemu-20260704-r1/`.
The summary records QEMU head `51f42d1726c02584e1646bdcc2ee8ca133e290ff` and
`qemu_repo_dirty_tracked=false`.

| Benchmark | Baseline no-cache count | MMU-cache count | Template-chain count | Result |
| --- | ---: | ---: | ---: | --- |
| `500.perlbench_r` | 32000000000 | 32000000005 | 36000000003 | `live-timeout`, no panic/trap |
| `502.gcc_r` | 19000000002 | 19000000001 | 23000000003 | `live-timeout`, no panic/trap |
| `505.mcf_r` | 28000000002 | 30000000009 | 34000000008 | `live-timeout`, no panic/trap |
| `520.omnetpp_r` | 11000000006 | 11000000006 | 16000000012 | `live-timeout`, no panic/trap |
| `523.xalancbmk_r` | 15000000000 | 16000000004 | 21000000001 | `live-timeout`, no panic/trap |
| `525.x264_r` | 18000000003 | 18000000003 | 31000000006 | `live-timeout`, no panic/trap |
| `531.deepsjeng_r` | 31000000027 | 31000000005 | 40000000008 | `live-timeout`, no panic/trap |
| `541.leela_r` | 12000000001 | 13000000006 | 19000000007 | `live-timeout`, no panic/trap |
| `557.xz_r` | 28000000005 | 28000000001 | 34000000005 | `live-timeout`, no panic/trap |
| `999.specrand_ir` | pass | pass | pass | strict train hash passes |

The combined follow-up used the rebuilt in-tree QEMU
`v10.2.0-1015-g51f42d1726c`, with `LINX_QEMU_TEMPLATE_CHAIN=1` and
`LINX_QEMU_MMU_CACHE=1`:

- `workloads/generated/specint-template-chain-mmuc-pr-qemu-20260704-r1/`
  passes the PR `999.specrand_ir` test/train strict hash sentinels.
- `workloads/generated/specint-train-all-template-chain-mmuc-qemu-20260704-r1/`
  covers the same split train-all plus `train-all-large-9p` shape.

| Benchmark | Template-chain count | Template+MMU-cache count | Decision |
| --- | ---: | ---: | --- |
| `500.perlbench_r` | 36000000003 | 37000000000 | combined improves |
| `502.gcc_r` | 23000000003 | 25000000004 | combined improves |
| `505.mcf_r` | 34000000008 | 35000000000 | combined improves |
| `520.omnetpp_r` | 16000000012 | 16000000000 | neutral |
| `523.xalancbmk_r` | 21000000001 | 22000000003 | combined improves |
| `525.x264_r` | 31000000006 | 30000000003 | combined regresses |
| `531.deepsjeng_r` | 40000000008 | 39000000024 | combined regresses |
| `541.leela_r` | 19000000007 | 20000000005 | combined improves |
| `557.xz_r` | 34000000005 | 35000000001 | combined improves |
| `999.specrand_ir` | pass | pass | strict train hash passes |

All non-999 combined rows remain heartbeat-backed `live-timeout` rows with BPC
site progress, no panic, and no trap. Loop update: keep
`LINX_QEMU_TEMPLATE_CHAIN=1` as the broad opt-in dispatch lever. Keep
`LINX_QEMU_MMU_CACHE=1` as a secondary focused component for rows such as
`505`, `523`, `541`, and `557`, not a default companion, because the combined
train-all run regresses `525.x264_r` and `531.deepsjeng_r` relative to
template-chain alone. The next speed lane should profile the template-chain
`531`/`525` cases and reduce the remaining dispatch or kernel/9p overhead
without relying on the MMU cache.

## 2026-07-04 Opt-In Frame Restore Host Loads

QEMU now has a default-off frame restore load fast path controlled by
`LINX_QEMU_FRAME_RESTORE_HOST_LOAD=1` (or
`LINX_FRAME_RESTORE_HOST_LOAD=1`). The SPEC runners expose the same control as
`--qemu-frame-restore-host-load`, and `run_specint_fast_gate.py` also accepts
`SPEC_QEMU_FRAME_RESTORE_HOST_LOAD=1` /
`LINX_SPEC_QEMU_FRAME_RESTORE_HOST_LOAD=1`.

The implementation uses `tlb_vaddr_to_host()` only as a non-faulting, same-page
8-byte hit probe for restore slots. A null host pointer or unsupported access
falls back to the existing faulting `cpu_ldq_le_mmuidx_ra()` path before any
template state is committed, so correctness-sensitive faults stay on the old
path. Frame stats now separate actual restore loads as
`fr_restore_host` and `fr_restore_fallback`.

Validation:

| Check | Result |
| --- | --- |
| `ninja -C emulator/qemu/build-linx qemu-system-linx64` | pass |
| default `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_FRAME_RESTORE_HOST_LOAD=1 LINX_QEMU_FRAME_STATS=1 python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_TEMPLATE_CHAIN=1 LINX_QEMU_FRAME_RESTORE_HOST_LOAD=1` strict train `999.specrand_ir` | pass, `workloads/generated/specint-999-frame-hostload-qemu-20260704-r1/` |
| `python3 tools/bringup/run_specint_fast_gate.py --profile smoke --qemu-frame-stats --qemu-frame-restore-host-load ...` | pass, `workloads/generated/specint-fastgate-frame-hostload-smoke-20260704-r1/` |

Focused `531.deepsjeng_r` train comparison with `LINX_QEMU_TEMPLATE_CHAIN=1`,
`--qemu-frame-stats`, a 60-second cap, and no guest heartbeat:

| Run | Result | Frame proof |
| --- | --- | --- |
| baseline restore loads | `live-timeout`, `count=16000000026` | `fr_restore_slot=175381838`, `fr_restore_host=0`, `fr_restore_fallback=175381838` |
| `LINX_QEMU_FRAME_RESTORE_HOST_LOAD=1` | `live-timeout`, `count=17000000016` | `fr_restore_slot=187411358`, `fr_restore_host=187411358`, `fr_restore_fallback=0` |

The new path is a useful gated frame-template experiment and runner switch, not
a broad SPEC closure. It improves the focused `531` sample by about 6.25% under
the same budget, while previous `505` restore-host experiments remained
negative and the all-row train suite is still live-timeout for every real row.
Loop update: keep the switch opt-in. Use it with frame stats when
`fr_restore_fallback` dominates, then compare focused rows and train-all before
considering default promotion. Keep `505` on the user data-memory/TLB lane and
`525` on the kernel/9p lane until new evidence changes that split.

Follow-up all-row evidence on latest in-tree QEMU `v10.2.0-1016-g8c24b15a343`
used `LINX_QEMU_TEMPLATE_CHAIN=1`, `--qemu-frame-stats`, and
`--qemu-frame-restore-host-load`:
`workloads/generated/specint-train-all-template-chain-frame-hostload-qemu-20260704-r2/`.
The QEMU submodule was clean at head
`8c24b15a3437315be80edc09278cf5786cf1a811`, but the run used the in-tree build
path rather than a `/tmp/linx-qemu-clean-build` marker, so summaries record
`clean_build_for_head=false`. `999.specrand_ir` still passes strict train hash.
Every real row remains a heartbeat-backed `live-timeout` with site progress,
no panic, and no trap.

| Benchmark | Template-chain count | Restore-host count | Delta | Restore host/fallback | Result |
| --- | ---: | ---: | ---: | --- | --- |
| `500.perlbench_r` | 36000000003 | 37000000000 | +999999997 | `280847246/0` | `live-timeout` |
| `502.gcc_r` | 23000000003 | 26000000000 | +2999999997 | `751640543/0` | `live-timeout` |
| `505.mcf_r` | 34000000008 | 35000000001 | +999999993 | `491237016/0` | `live-timeout` |
| `520.omnetpp_r` | 16000000012 | 17000000001 | +999999989 | `820149124/0` | `live-timeout` |
| `523.xalancbmk_r` | 21000000001 | 21000000003 | +2 | `660685206/0` | `live-timeout` |
| `525.x264_r` | 31000000006 | 31000000001 | -5 | `962859238/0` | `live-timeout`, 9p |
| `531.deepsjeng_r` | 40000000008 | 38000000002 | -2000000006 | `445834686/0` | `live-timeout` |
| `541.leela_r` | 19000000007 | 19000000001 | -6 | `929796547/0` | `live-timeout` |
| `557.xz_r` | 34000000005 | 34000000000 | -5 | `809633794/0` | `live-timeout` |
| `999.specrand_ir` | pass | pass | 0 | `0/0` | strict hash passes |

This keeps restore-host loads useful as a focused row experiment, but the broad
frame-stats run is not enough for default promotion. The rows that improved are
still far from completing train input within the bounded gate, and `531` is
worse than the prior template-chain count in this all-row shape.

Post-start profile:
`workloads/generated/specint-profile-531-template-hostload-qemu-20260704-r1/`
profiles `531.deepsjeng_r` with `LINX_QEMU_TEMPLATE_CHAIN=1`,
`--qemu-frame-restore-host-load`, frame stats off, guest and QEMU heartbeat off,
and a 180-second cap. The wrapper sampled the real QEMU PID after
`LINX_SPEC_START`; the row is red only because heartbeat was intentionally
disabled for profiling. Top active frames after excluding parked threads:

| Frame | Samples |
| --- | ---: |
| `probe_access_internal` | 940 |
| `helper_linx_tlb_iv` | 828 |
| `tb_lookup` | 774 |
| `linx_template_fentry_impl` | 707 |
| `linx_template_fret_stk_impl` | 676 |
| `helper_lookup_tb_ptr` | 559 |
| `linx_frame_restore_prepare` | 475 |
| `probe_access` | 337 |
| `linx_get_tb_cpu_state` | 321 |
| `linx_frame_restore_commit` | 229 |
| `qht_lookup_custom` | 214 |
| `tlb_vaddr_to_host` | 159 |
| `mmu_lookup1` | 54 |
| `pthread_jit_write_protect_np` | 39 |

Rejected experiment: an uncommitted opt-in QEMU patch tried to route
`TLB.IV`/`TLB.IAV` through `tlb_flush_page_by_mmuidx()` using an obvious
user-vs-kernel VA split instead of flushing all QEMU MMU indexes. It preserved
the default call/ret contract, passed the opt-in call/ret contract, and passed
strict train `999.specrand_ir` in
`workloads/generated/specint-999-tlbiv-addrmmu-qemu-20260704-r1/`, but focused
`531.deepsjeng_r` with template-chain and restore-host loads stayed neutral:
baseline `workloads/generated/specint-531-template-hostload-baseline-qemu-20260704-r1/`
reached `count=17000000008`, while
`workloads/generated/specint-531-template-hostload-tlbiv-addrmmu-qemu-20260704-r1/`
reached `count=17000000003`. The patch was backed out.

Loop update: do not pursue naive QEMU MMU-index narrowing for `TLB.IV` as the
next speed patch. The useful next lane is TLB invalidation source reduction or
batching: profile the Linux eager `local_flush_tlb_page()` call sites in
`arch/linx/include/asm/pgtable.h` (`update_mmu_cache_range`,
`ptep_set_wrprotect`) and `arch/linx/mm/fault.c`, then decide whether Linx
Linux can reduce fault-time/page-aging flush volume without violating the ISA's
ordering requirement. Keep QEMU work on `probe_access_internal`,
template-helper dispatch, and `tb_lookup` after that Linux-side evidence.

Follow-up TLBI hot-site instrumentation adds an opt-in
`LINX_QEMU_TLB_INV_HOT=1` / `LINX_TLB_INV_HOT=1` QEMU heartbeat companion line
and runner switch `--qemu-tlb-inv-hot`. The line is keyed by invalidation op
and source PC, records last BPC/operand/page/ACR, and includes both cumulative
counts and per-heartbeat deltas; SPEC summaries record it as
`heartbeat_tlb_inv_hot` and print compact `tlbi-hot=` failure details.

Validation:

| Check | Result |
| --- | --- |
| `python3 -m py_compile tools/spec2017/run_int_rate_qemu.py tools/spec2017/run_stage_qemu_matrix.py tools/bringup/run_specint_fast_gate.py tools/spec2017/test_run_int_rate_qemu.py` | pass |
| `cd tools/spec2017 && python3 -m unittest test_run_int_rate_qemu.py` | pass, 42 tests |
| `ninja -C emulator/qemu/build-linx qemu-system-linx64` | pass; only pre-existing unrelated warnings |
| default `python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| `LINX_QEMU_TLB_INV_HOT=1 python3 avs/qemu/run_callret_contract.py --qemu emulator/qemu/build-linx/qemu-system-linx64` | pass |
| strict train `999.specrand_ir` with `--qemu-tlb-stats --qemu-tlb-inv-hot` | pass, `workloads/generated/specint-999-tlbi-hot-delta-initramfs-qemu-20260704-r1/` |

Focused `531.deepsjeng_r` train probe:
`workloads/generated/specint-531-tlbi-hot-delta-qemu-20260704-r1/` uses
`LINX_QEMU_TEMPLATE_CHAIN=1`, `--qemu-frame-stats`,
`--qemu-frame-restore-host-load`, `--qemu-tlb-stats`, and
`--qemu-tlb-inv-hot` with a 120-second cap. It remains a heartbeat-backed
`live-timeout`, not a deadlock: `heartbeat_running=true`,
`heartbeat_site_progress=true`, `count=40000000004`, and recent count delta
`7000000001`. Aggregate TLBI counters show `tlbi_iv=3849672`, `tlbi_iall=9`,
and last steady invalidation at `0xffffffff800db2b6` /
`0xffffffff800db2ac` on operand `0x3ffffe2000`.

Attribution:

| Site | Evidence | Interpretation |
| --- | --- | --- |
| `0xffffffff80405980`, `0xffffffff804059d2` | `tlbi-hot max_delta=458884` at first heartbeat; symbolized to `get_p4d_virt_fixmap` in `arch/linx/mm/init.c`; disassembly shows two `tlb.iv a3` sites | early fixmap/TLB setup burst |
| `0xffffffff800db2b6` / BPC `0xffffffff800db2ac` | repeated `top0_delta` around `32739-32740` for several heartbeats, symbolized to `mm/memory.c` `.LBB50_265`; disassembly is a `tlb.iv a3` loop | Linux eager page-fault/update flush path |
| `arch/linx/include/asm/pgtable.h` | `update_mmu_cache_range()` loops over `local_flush_tlb_page(address + nr * PAGE_SIZE)` and `ptep_set_wrprotect()` flushes one page after write-protect | source-level candidates for batching/reduction |
| `arch/linx/include/asm/tlbflush.h` | `local_flush_tlb_page()` emits `BSTART.sys fall; tlb.iv %[a]`; `flush_tlb_range()` currently falls back to `local_flush_tlb_all()` in the non-SMP path | Linux policy, not QEMU MMU-index selection, is the next lever |

All-train follow-up:
`workloads/generated/specint-train-all-latest-qemu-20260704-r2/` reruns every
supported SPECint train row on clean QEMU head `1db7e12b680` with
`--qemu-tlb-stats`, `--qemu-tlb-inv-hot`, frame stats, and restore-host loads.
`999.specrand_ir` passes strict hash; the other nine rows remain live timeouts
with BPC site progress, no trap, no panic, shared early
`tlbi-hot max_delta=458884` at `get_p4d_virt_fixmap`, and
`fr_restore_fallback=0`. This generalizes the focused `531` result: current
all-train failures are running throughput limits with heavy Linux TLBI volume,
not deadlocks or frame restore fallback regressions.

Loop update: keep `--qemu-tlb-inv-hot` as the default low-volume attribution
tool whenever `helper_linx_tlb_iv` appears in a post-start host profile. The
next speed patch should investigate Linx Linux `update_mmu_cache_range()` /
`ptep_set_wrprotect()` flush frequency, range batching, or architecture
semantics before returning to QEMU cputlb changes. Do not classify current
`531` as stuck; the row is BPC-progressing and throughput-limited.

## Validation Targets

- Rebuild `emulator/qemu/build-linx/qemu-system-linx64`.
- Run `run_specint_fast_gate.py --profile smoke` after each hot-path patch.
- For quick validation, run `train-smoke`; for performance comparisons, sample
  `train-cpu-stress` before and after the patch and compare the
  "Sort by top of stack" section for:
  - `__findenv_locked`
  - `linx_dbg_check_mem`
  - `helper_linx_dbg_check_load`
  - `helper_linx_dbg_check_store`
  - `cpu_memory_rw_debug`
  - `linx_mmu_translate`
