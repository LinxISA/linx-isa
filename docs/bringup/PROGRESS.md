# Bring-up Progress (v0.4 workspace)

Last updated: 2026-04-25

## Closure Snapshot

- `v0.4` golden/spec is canonical and validated.
- AVS is now the only live public bring-up contract.
- The latest checked-in canonical report is `docs/bringup/gates/latest.json` generated at `2026-04-18 02:11:34Z`; its latest run is `2026-04-18-r9-pin-linuxlibc-refresh`.
- Active governance phase remains `G0`, and `docs/bringup/agent_runs/waivers.yaml` still carries zero waivers.
- The latest pin-lane run recovered the Architecture, Compiler, Emulator, Linux `vmlinux`, initramfs smoke/full boot, musl build/runtime, glibc G1a/G1b/runtime, LinxCore/Testbench/Trace/pyCircuit leaf PR gates, and workload benchmark/polybench/portfolio/ctuning/PTO/TSVC-compile rows.
- April 11, 2026 spot checks first cleared the stale March Sail/PTO diagnosis; the April 18 canonical report now records model-diff and PTO parity as green.
- April 18, 2026 canonical recovery work closed the stale PR-lane blockers:
  - `python3 tools/bringup/check_avs_profile_closure.py --tier pr` is now green with `required_tests=31`.
  - `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json` passes again after restoring the compatibility wrapper.
  - the canonical `strict_cross_repo.sh` row still fails because it includes the required BusyBox rootfs gate; ad hoc direct reruns without the BusyBox blocker are not release evidence.
  - the LinxCore/Testbench/Trace/pyCircuit leaf regressions that were blocking the pin lane are locally green again: `test_runner_protocol.sh`, `test_trace_schema_and_mem.sh`, `test_konata_sanity.sh`, `test_cosim_smoke.sh`, `run_linx_cpu_pyc_cpp.sh`, and `run_linx_qemu_vs_pyc.sh` now pass.
  - the pinned `vmlinux` build gate is green again via `tools/bringup/run_linux_vmlinux_build_clean.sh`, and the pin lane now has a matching clean-QEMU helper in `tools/bringup/run_qemu_build_clean.sh` so runtime convergence no longer depends on dirty emulator worktrees.
- The current active blockers are now concentrated in Linux/userspace runtime and nightly/runtime breadth:
  - AVS nightly breadth remains `32/54` implemented/pass.
  - BusyBox rootfs runtime is the only remaining required leaf blocker in the refreshed PR pin lane.
  - `musl` and `glibc` runtime smokes both pass again on the clean pinned QEMU path; the stale `r8` failures were replaced by the `r9` rerun.
  - BusyBox rootfs is now confirmed as a Linux runtime regression, not a dirty-emulator artifact: the wrapper no longer crashes, the pin lane can build a clean pinned QEMU binary, and the gate still reproduces `linx: kernel E_BLOCK`. The current verbose failing site is `__submit_bio` at `pc=0x1cb034` on `FRET.STK [ra ~ s4], sp!, 128` with `cause=0x101` and `ra=0`. A clean-worktree `switch_to` experiment that drops EBARG context save/restore reaches the BusyBox shell only under verbose boot.
  - `Regression::strict_cross_repo.sh` is red because BusyBox rootfs is red in the canonical run.
  - SPEC Stage A remains a nightly/runtime blocker (`9p` kernel `E_BLOCK` in `___slab_alloc`; initramfs child startup still broken).
  - TSVC QEMU runtime remains a nightly/runtime blocker on scalar-replay recurrence kernels in `auto` mode; PR closure uses compile-only strict coverage at `148/151`.
  - Some call/ret negative-contract and C++ runtime-overlay follow-up work remains outside the PR closure subset.

## Phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 1. Canonical `v0.4` golden + manual freeze | ✅ Passed | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| 2. AVS public contract cutover | ✅ Source complete | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| 3. LLVM MC/CodeGen baseline alignment | ✅ Current pin pass | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100`; `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| 4. QEMU runtime/system baseline | ✅ Current pin pass | `avs/qemu/check_system_strict.sh`; `avs/qemu/run_tests.sh --all`; `ninja -C emulator/qemu/build qemu-system-linx64` |
| 5. Linux userspace boot path | ⚠️ Recovery in progress | Initramfs smoke/full and pinned `vmlinux` build are green, and the pin lane can build clean QEMU/rootfs artifacts, but BusyBox rootfs is still regressed with a kernel `E_BLOCK` after `Run /sbin/init as init process`. |
| 6. musl/glibc baseline runtime | ✅ Current clean-QEMU pass | musl build/runtime and glibc G1a/G1b are green, and both `run_musl_smoke.py` and `run_glibc_smoke.py` now pass again on the clean pinned QEMU path. |
| 7. Sail/model verification | ✅ Current PR pass | The stale March Sail decode-generator failure is superseded; the current PR lane records model-diff as green, and the April 11 spot checks for `check_sail_model.py --require-parser` and `gen_sail_decode.py --check` both pass. |
| 8. AVS tier closure | ✅ Current PR pass | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` now reports `required_tests=31`, `failure_count=0`; nightly breadth remains `32/54`. |
| 9. LinxCore/Testbench/Trace/pyCircuit closure | ✅ Current pin pass | Runner protocol, trace schema/memory smoke, LinxTrace sanity, cosim smoke, ROB bookkeeping, block-struct pyc flow, and pyCircuit CPU/QEMU smokes pass in the latest canonical pin run. |
| 10. Workload and SPEC hard closure | ❌ Nightly/runtime blocker | Benchmark/PolyBench/portfolio/ctuning artifact publication, PTO kernel parity, and TSVC compile-only PR coverage are green in the PR lane, but SPEC Stage A remains opt-in and TSVC QEMU runtime still hangs in `auto` mode. |

## Gate Snapshot

| Gate | Status | Command |
| --- | --- | --- |
| Golden/spec validation | ✅ | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| AVS contract schema | ✅ | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| AVS matrix status audit | ✅ | `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json` |
| AVS tier closure | ✅ PR subset green (`31/31` required) | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` |
| Sail/model path in strict closure | ⚠️ Stale March failure; rerun needed | The March 15, 2026 report aborts in `tools/isa/gen_sail_decode.py`, but the April 11, 2026 spot checks for `python3 tools/bringup/check_sail_model.py --require-parser` and `python3 tools/isa/gen_sail_decode.py --check` both pass. |
| Compiler AVS (`linx64`/`linx32`) | ✅ | `./avs/compiler/linx-llvm/tests/run.sh` |
| Compiler coverage (`linx64`/`linx32`) | ✅ | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --fail-under 100` |
| LLVM auxiliary tool suite (`llvm-ar`/`llvm-nm`/`llvm-readelf`/`llvm-strip`) | ✅ | `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| QEMU runtime suites | ✅ Current pin pass | `./avs/qemu/run_tests.sh --all` |
| QEMU pinned binary build | ✅ | `ninja -C emulator/qemu/build qemu-system-linx64` |
| QEMU decode coverage | ❌ Open work | `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` |
| Linux `vmlinux` build closure | ✅ Current helper path passes | `bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux` |
| Linux initramfs smoke/full | ✅ | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`; `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| musl build closure (`phase-b`) | ✅ | `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh` |
| musl runtime (`R1`/`R2`) | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc (`G1a`/`G1b`) | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` |
| glibc dynamic runtime on Linux/QEMU | ✅ Current clean-QEMU pass | `python3 avs/qemu/run_glibc_smoke.py --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 30` |

## Current Closure Blockers

- The PR recovery lane is nearly closed in the checked-in canonical report; BusyBox rootfs is the remaining required failing leaf row.
- `Library::glibc runtime dynamic hello` is green in the latest canonical run.
- The LinxCore/Testbench/Trace/pyCircuit leaf blockers are cleared in the latest canonical run, leaving BusyBox rootfs as the only required leaf blocker before `strict_cross_repo.sh` can turn green.
- BusyBox rootfs no longer fails in the Python wrapper; it now consistently exposes a real kernel `E_BLOCK` even against a clean pinned QEMU build, and a clean-worktree `switch_to` experiment that drops EBARG context save/restore reaches the BusyBox shell only under verbose boot. The remaining bug is therefore in the Linux runtime path, not the wrapper or dirty-emulator artifacts.
- `Regression::strict_cross_repo.sh` remains red in `2026-04-18-r9-pin-linuxlibc-refresh` because it includes the BusyBox rootfs failure.
- SPEC Stage A remains a real runtime blocker behind the opt-in PR gate: `9p` trips kernel `E_BLOCK` in `___slab_alloc`, and initramfs child-process startup is still broken.
- TSVC QEMU runtime remains a nightly/runtime blocker; the PR lane holds only the compile-only strict-coverage contract at `148/151`.

## Canonical Gate Artifacts

- `avs/linx_avs_v1_test_matrix.yaml` is the public contract source.
- `avs/linx_avs_v1_test_matrix_status.json` is the canonical AVS status artifact.
- `docs/bringup/gates/qemu_isa_coverage_latest.json` records the latest checked-in QEMU decode coverage snapshot, including mnemonic and per-form gaps.
- `docs/bringup/gates/latest.json` is the current per-run multi-gate evidence artifact; the latest checked-in refresh is `2026-04-18-r9-pin-linuxlibc-refresh`, and it is not yet release evidence because BusyBox rootfs and the aggregate strict-cross row still fail.
