# Bring-up Progress (v0.4 workspace)

Last updated: 2026-04-18

## Closure Snapshot

- `v0.4` golden/spec is canonical and validated.
- AVS is now the only live public bring-up contract.
- The latest checked-in canonical report is still `docs/bringup/gates/latest.json` generated at `2026-03-15 02:38:42Z` from pin-lane run `2026-03-15-r2-pin`; it is stale relative to the current workspace and not release-closed.
- Active governance phase remains `G0`, and `docs/bringup/agent_runs/waivers.yaml` still carries zero waivers.
- The latest pin-lane run recovered the Architecture, Compiler, Emulator, Linux initramfs/full-boot/BusyBox, musl build/runtime, glibc G1a/G1b, and workload benchmark/polybench/portfolio/ctuning rows.
- April 11, 2026 spot checks refreshed two stale March 15 rows:
  - `python3 tools/bringup/check_sail_model.py --require-parser` is green again, and `python3 tools/isa/gen_sail_decode.py --check` also passes.
  - `python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120` is green again and writes `workloads/generated/pto_kernel_parity_latest.json` with `all_match=true` across 27 kernels.
- April 18, 2026 local recovery work closed the stale PR-lane blockers:
  - `python3 tools/bringup/check_avs_profile_closure.py --tier pr` is now green with `required_tests=31`.
  - `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json` passes again after restoring the compatibility wrapper.
  - direct PR-lane `strict_cross_repo.sh` reruns now pass with `RUN_SPEC_PR_GATES=0`, compile-only TSVC, and the narrowed AVS PR subset.
- The current active blockers are now concentrated in nightly/runtime breadth:
  - AVS nightly breadth remains `31/54` implemented/pass.
  - Linux `vmlinux` build hygiene and glibc dynamic runtime asset packaging still need a fresh full convergence rerun.
  - SPEC Stage A remains blocked (`9p` kernel `E_BLOCK` in `___slab_alloc`; initramfs child startup still broken).
  - TSVC QEMU runtime remains blocked on scalar-replay recurrence kernels in `auto` mode.
  - Some call/ret negative-contract and C++ runtime-overlay follow-up work remains outside the PR closure subset.

## Phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 1. Canonical `v0.4` golden + manual freeze | ✅ Passed | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| 2. AVS public contract cutover | ✅ Source complete | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| 3. LLVM MC/CodeGen baseline alignment | ✅ Current pin pass | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100`; `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| 4. QEMU runtime/system baseline | ✅ Current pin pass | `avs/qemu/check_system_strict.sh`; `avs/qemu/run_tests.sh --all`; `ninja -C emulator/qemu/build qemu-system-linx64` |
| 5. Linux userspace boot path | ⚠️ Partial regression | Initramfs smoke/full and BusyBox rootfs are green again in `2026-03-15-r2-pin`, but `Kernel::Linux \`vmlinux\` build closure` is currently failing on source-tree cleanliness. |
| 6. musl/glibc baseline runtime | ⚠️ Partial regression | musl build/runtime and glibc G1a/G1b are green in `2026-03-15-r2-pin`, but `python3 avs/qemu/run_glibc_smoke.py --timeout 30` currently fails the asset check. |
| 7. Sail strict verification | ⚠️ March failure diagnosis is stale; strict rerun needed | The March 15, 2026 pin-lane report still records a Sail decode-generator failure, but the April 11, 2026 spot checks for `check_sail_model.py --require-parser` and `gen_sail_decode.py --check` both pass. |
| 8. AVS tier closure | ✅ Current PR pass | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` now reports `required_tests=31`, `failure_count=0`; nightly breadth remains `31/54`. |
| 9. LinxCore/Testbench/Trace/pyCircuit closure | ❌ Open blocker | Latest pin-lane failures are dominated by `workspace_paths.sh` missing, `pycc`/`pyc-compile` missing, and fallback `.memh` assets missing. |
| 10. Workload and SPEC hard closure | ❌ Nightly/runtime blocker | Benchmark/PolyBench/portfolio artifact publication and PTO kernel parity are green in the PR lane, but SPEC Stage A remains `ok=false` and TSVC QEMU runtime still hangs in `auto` mode. |

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
| Linux `vmlinux` build closure | ❌ Regression | `env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH /opt/homebrew/bin/gmake -C kernel/linux ARCH=linx LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ 'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' HOSTCC=/usr/bin/clang HOSTCXX=/usr/bin/clang++ O=$PWD/kernel/linux/build-linx-fixed vmlinux` |
| Linux initramfs smoke/full | ✅ | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`; `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| musl build closure (`phase-b`) | ✅ | `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh` |
| musl runtime (`R1`/`R2`) | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc (`G1a`/`G1b`) | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` |
| glibc dynamic runtime on Linux/QEMU | ❌ Regression | `python3 avs/qemu/run_glibc_smoke.py --timeout 30` |

## Current Closure Blockers

- The PR recovery lane itself is now green from fresh April 18, 2026 local evidence, but the checked-in canonical gate report has not yet been refreshed to capture that state.
- `Kernel::Linux \`vmlinux\` build closure` and `Library::glibc runtime dynamic hello` still need a fresh full convergence rerun to replace the stale March 15, 2026 rows.
- LinxCore/Testbench/Trace/pyCircuit still have independent prerequisite and asset drift outside the AVS/strict-cross subset.
- SPEC Stage A remains a real runtime blocker behind the now-opt-in PR gate: `9p` trips kernel `E_BLOCK` in `___slab_alloc`, and initramfs child-process startup is still broken.
- TSVC QEMU runtime remains a nightly/runtime blocker; the PR lane now holds only the compile-only strict-coverage contract at `148/151`.

## Canonical Gate Artifacts

- `avs/linx_avs_v1_test_matrix.yaml` is the public contract source.
- `avs/linx_avs_v1_test_matrix_status.json` is the canonical AVS status artifact.
- `docs/bringup/gates/qemu_isa_coverage_latest.json` records the latest checked-in QEMU decode coverage snapshot, including mnemonic and per-form gaps.
- `docs/bringup/gates/latest.json` is the current per-run multi-gate evidence artifact; the latest checked-in refresh is `2026-03-15-r2-pin`, and it is not yet release evidence because required gates still fail.
