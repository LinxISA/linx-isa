# Bring-up Progress (v0.57 workspace)

Last updated: 2026-07-15

## Closure Snapshot

- `v0.57` golden/spec is canonical and validated.
- AVS is now the only live public bring-up contract.
- The v0.57 maintenance packet replaces the April aggregate with one
  SHA-manifested run; it must remain non-green while BusyBox/MMU, QEMU semantic
  breadth, and unrun nightly gates are open.
- Active governance phase remains `LINUX-RUNTIME`, and `docs/bringup/agent_runs/waivers.yaml` still carries zero waivers.
- The latest pin-lane run recovered the Architecture, Compiler, Emulator, Linux `vmlinux`, initramfs smoke/full boot, musl build/runtime, glibc G1a/G1b/runtime, LinxCore/Testbench/Trace/pyCircuit leaf PR gates, and workload benchmark/polybench/portfolio/ctuning/PTO/TSVC-compile rows.
- April 11, 2026 spot checks first cleared the stale March Sail/PTO diagnosis; the April 18 canonical report now records model-diff and PTO parity as green.
- April 18, 2026 canonical recovery work closed the stale PR-lane blockers:
  - `python3 tools/bringup/check_avs_profile_closure.py --tier pr` is now green with `required_tests=31`.
  - `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json` passes again after restoring the compatibility wrapper.
  - the canonical `strict_cross_repo.sh` row still fails because the checked-in
    canonical report predates the June 30 local BusyBox rootfs pass; refresh
    convergence/strict closure before treating the old row as current.
  - the LinxCore/Testbench/Trace/pyCircuit leaf regressions that were blocking the pin lane are locally green again: `test_runner_protocol.sh`, `test_trace_schema_and_mem.sh`, `test_konata_sanity.sh`, `test_cosim_smoke.sh`, `run_linx_cpu_pyc_cpp.sh`, and `run_linx_qemu_vs_pyc.sh` now pass.
  - the pinned `vmlinux` build gate is green again via `tools/bringup/run_linux_vmlinux_build_clean.sh`, and the pin lane now has a matching clean-QEMU helper in `tools/bringup/run_qemu_build_clean.sh` so runtime convergence no longer depends on dirty emulator worktrees.
- The current active blockers are now concentrated in canonical report refresh,
  hosted runtime/SPEC correctness, and nightly/runtime breadth:
  - AVS nightly breadth remains `32/54` implemented/pass.
  - BusyBox rootfs runtime has a fresh failure on clean QEMU: two 120-second
    attempts produced no UART output.
  - `musl` and `glibc` runtime smokes both pass again on the clean pinned QEMU path; the stale `r8` failures were replaced by the `r9` rerun.
- BusyBox rootfs now boots locally with firmwareless QEMU and a clean rebuilt
  rootfs. The prior PID1 `addr=0x10000004` trap was from a stale rootfs binary
  that still performed direct UART MMIO in user mode; the clean rebuild reaches
  shell commands, shows `linx-timer` IRQ progress, and powers off.
  - `Regression::strict_cross_repo.sh` remains red in the checked-in canonical
    run because the canonical report has not yet been refreshed with this local
    BusyBox proof.
- SPEC bringup-subset runtime remains a nightly/runtime blocker; the static train-all lane now reaches SPEC userspace, builds all supported C/C++ rows, and passes `999.specrand_ir`, but remaining rows split into throughput, C++ resource/kill, and kernel panic-loop classes.
  - TSVC QEMU runtime is green in the required batched auto lane: 8/8 batches,
    `150/151` strict-vectorized and `151/151` executed kernels; `s451` is the
    intentional scalar transcendental-call case.
  - Some call/ret negative-contract and C++ runtime-overlay follow-up work remains outside the PR closure subset.

## Capability Status

| Phase | Status | Evidence |
| --- | --- | --- |
| 1. Canonical `v0.57` golden + manual freeze | ✅ Passed | `python3 tools/isa/build_golden.py --profile v0.57 --check`; `python3 tools/isa/validate_spec.py --profile v0.57` |
| 2. AVS public contract cutover | ✅ Source complete | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| 3. LLVM MC/CodeGen baseline alignment | ✅ Current pin pass | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100`; `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| 4. QEMU runtime/system baseline | ✅ Current pin pass | `avs/qemu/check_system_strict.sh`; `avs/qemu/run_tests.sh --all`; `bash tools/bringup/run_qemu_build_clean.sh --qemu-root $PWD/emulator/qemu --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64` |
| 5. Linux userspace boot path | ❌ Current-pin BusyBox failure | The v0.57 clean-QEMU run produced no UART output in two 120-second attempts. Older green rootfs evidence is historical and does not override this result. |
| 6. musl/glibc baseline runtime | ✅ Current clean-QEMU pass | musl build/runtime and glibc G1a/G1b are green, and both `run_musl_smoke.py` and `run_glibc_smoke.py` now pass again on the clean pinned QEMU path. |
| 7. Sail/model verification | ✅ Sail pass; model breadth open | Sail 0.20.2 parses, typechecks, generates C, and executes directed tests for all 747 form-ID records. Full current-pin cross-model/nightly breadth was not run. |
| 8. AVS tier closure | ✅ Current PR pass | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` now reports `required_tests=31`, `failure_count=0`; nightly breadth remains `32/54`. |
| 9. LinxCore/Testbench/Trace/pyCircuit closure | ✅ Current pin pass | Runner protocol, trace schema/memory smoke, LinxTrace sanity, cosim smoke, ROB bookkeeping, block-struct pyc flow, and pyCircuit CPU/QEMU smokes pass in the latest canonical pin run. |
| 10. Workload and SPEC hard closure | ❌ Nightly/runtime blocker | Benchmark/PolyBench/portfolio/ctuning artifact publication, PTO kernel parity, TSVC compile-only PR coverage, and local BusyBox rootfs boot are green. Static SPECint train-all now builds all supported C/C++ rows and passes `999.specrand_ir`; remaining SPEC work is split into heartbeat-backed QEMU throughput rows, wrapper `sig=9` child-exit rows, `525.x264_r` panic-loop capture, and hosted/shared-runtime gaps. |

## Gate Snapshot

| Gate | Status | Command |
| --- | --- | --- |
| Golden/spec validation | ✅ | `python3 tools/isa/build_golden.py --profile v0.57 --check`; `python3 tools/isa/validate_spec.py --profile v0.57` |
| AVS contract schema | ✅ | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| AVS matrix status audit | ✅ | `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json` |
| AVS tier closure | ✅ PR subset green (`31/31` required) | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` |
| Sail/model path in strict closure | ✅ Sail 0.20.2 exact-version pass | `opam exec --switch=sail-4.14.3 -- python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend` validates 747 form IDs and directed semantics. |
| Compiler AVS (`linx64`/`linx32`) | ✅ | `./avs/compiler/linx-llvm/tests/run.sh` |
| Compiler coverage (`linx64`/`linx32`) | ✅ | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --fail-under 100` |
| LLVM auxiliary tool suite (`llvm-ar`/`llvm-nm`/`llvm-readelf`/`llvm-strip`) | ✅ | `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| QEMU runtime suites | ✅ Current pin pass | `./avs/qemu/run_tests.sh --all` |
| QEMU pinned binary build | ✅ | `bash tools/bringup/run_qemu_build_clean.sh --qemu-root $PWD/emulator/qemu --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64` |
| QEMU decode coverage | ❌ Open work | `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` |
| Linux `vmlinux` build closure | ✅ Current helper path passes | `bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux` |
| Linux initramfs smoke/full | ✅ | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`; `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| musl build closure (`phase-b`) | ✅ | `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh` |
| musl runtime (`R1`/`R2`) | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc (`G1a`/`G1b`) | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` |
| glibc dynamic runtime on Linux/QEMU | ✅ Current clean-QEMU pass | `python3 avs/qemu/run_glibc_smoke.py --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 30` |

## Current Closure Blockers

- The PR recovery lane needs a refreshed canonical report; local BusyBox rootfs
  evidence is green as of 2026-06-30.
- `Library::glibc runtime dynamic hello` is green in the latest canonical run.
- The LinxCore/Testbench/Trace/pyCircuit leaf blockers are cleared in the
  latest canonical run; the old BusyBox rootfs row should be revalidated with
  the clean rebuilt rootfs before strict closure is judged current.
- `Regression::strict_cross_repo.sh` remains red in
  `2026-04-18-r9-pin-linuxlibc-refresh` because that checked-in report includes
  the older BusyBox rootfs failure.
- SPEC remains a real runtime blocker behind the opt-in PR gate, but the blocker has moved past firmwareless userspace entry. The matrix-wrapper QEMU handoff bug is fixed, static phase-b SPECint train-all reaches guest execution, and `999.specrand_ir` passes strict hash. The current live blockers are heartbeat-backed throughput rows, C++ resource rows such as `520.omnetpp_r`, `523.xalancbmk_r`, and `541.leela_r`, the `525.x264_r` panic-loop row, and separate shared-runtime packaging gaps.
- TSVC QEMU runtime remains a nightly/runtime blocker; the PR lane holds only the compile-only strict-coverage contract at `148/151`.

## Canonical Gate Artifacts

- `avs/linx_avs_v1_test_matrix.yaml` is the public contract source.
- `avs/linx_avs_v1_test_matrix_status.json` is the canonical AVS status artifact.
- `docs/bringup/gates/qemu_isa_coverage_latest.json` records the latest checked-in QEMU decode coverage snapshot, including mnemonic and per-form gaps.
- `docs/bringup/gates/latest.json` is the current per-run multi-gate evidence artifact; the latest checked-in refresh is `2026-04-18-r9-pin-linuxlibc-refresh`, and it is not yet release evidence because BusyBox rootfs and the aggregate strict-cross row still fail.
