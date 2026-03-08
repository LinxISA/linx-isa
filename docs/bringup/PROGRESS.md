# Bring-up Progress (v0.4 workspace)

Last updated: 2026-03-08

## Closure Snapshot

- `v0.4` golden/spec is canonical and validated.
- AVS is now the only live public bring-up contract.
- Pinned build closure is now green for the current propagation workspace: compiler AVS stays at 100% for `linx64`/`linx32`, QEMU builds, Linux produces `build-linx-fixed/vmlinux`, musl phase-b passes, and glibc G1a/G1b pass.
- Tier closure is not complete yet: `20/54` active AVS entries are currently marked `pass`.
- Checked-in QEMU decode coverage is `524/710` unique legal `v0.4` mnemonics (`73.80%`) and `521/740` legal forms (`70.41%`).
- Sail strict verification is now closed at the parser/status-gate level: the active model parses through the real top-level entry and the stale stub list has been removed.

## Phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 1. Canonical `v0.4` golden + manual freeze | ✅ Passed | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| 2. AVS public contract cutover | ✅ Source complete | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| 3. LLVM MC/CodeGen baseline alignment | ✅ Baseline pass | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100` |
| 4. QEMU runtime/system baseline | ✅ Baseline pass | `avs/qemu/check_system_strict.sh`; `avs/qemu/run_tests.sh --all` |
| 5. Linux userspace boot path | ✅ Baseline pass | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`; `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| 6. musl/glibc baseline runtime | ✅ Baseline pass | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both`; `bash lib/glibc/tools/linx/build_linx64_glibc.sh` |
| 7. Sail strict verification | ✅ Passed | `python3 tools/bringup/check_sail_model.py --require-parser` |
| 8. AVS tier closure | 🚧 In progress | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` |
| 9. Full QEMU decode-spectrum closure | 🚧 In progress | `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` |
| 10. Workload and SPEC hard closure | 🚧 In progress | AVS workload/SPEC entries are active but not yet all validated |

## Gate Snapshot

| Gate | Status | Command |
| --- | --- | --- |
| Golden/spec validation | ✅ | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| AVS contract schema | ✅ | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| AVS matrix status audit | ✅ | `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json` |
| AVS tier closure | ❌ Open work | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` |
| Sail model status | ✅ | `python3 tools/bringup/check_sail_model.py --require-parser` |
| Compiler AVS (`linx64`/`linx32`) | ✅ | `./avs/compiler/linx-llvm/tests/run.sh` |
| Compiler coverage (`linx64`/`linx32`) | ✅ | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --fail-under 100` |
| LLVM auxiliary tool suite (`llvm-ar`/`llvm-nm`/`llvm-readelf`/`llvm-strip`) | ✅ | `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| QEMU runtime suites | ✅ Baseline | `./avs/qemu/run_tests.sh --all` |
| QEMU pinned binary build | ✅ | `ninja -C emulator/qemu/build qemu-system-linx64` |
| QEMU decode coverage | ❌ Open work | `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` |
| Linux `vmlinux` build closure | ✅ | `env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH /opt/homebrew/bin/gmake -C kernel/linux ARCH=linx LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ 'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' HOSTCC=/usr/bin/clang HOSTCXX=/usr/bin/clang++ O=$PWD/kernel/linux/build-linx-fixed vmlinux` |
| Linux initramfs smoke/full | ✅ | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`; `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| musl build closure (`phase-b`) | ✅ | `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh` |
| musl runtime (`R1`/`R2`) | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc (`G1a`/`G1b`) | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` |

## Current Closure Blockers

- AVS tier status shows only `20/54` active entries validated.
- QEMU full-decode closure is still at `524/710` mnemonics and `521/740` forms; mnemonic-level and per-form closure are not complete.
- Workload, PolyBench, TSVC, PTO parity, curated ctuning, and SPEC entries are present in AVS but not all validated in machine-readable form.
- Pre-canonical architecture notebook migration remains open; notebook deletion is blocked until each retained note has a canonical destination or an explicit historical disposition.

## Canonical Gate Artifacts

- `avs/linx_avs_v1_test_matrix.yaml` is the public contract source.
- `avs/linx_avs_v1_test_matrix_status.json` is the canonical AVS status artifact.
- `docs/bringup/gates/qemu_isa_coverage_latest.json` records the latest checked-in QEMU decode coverage snapshot, including mnemonic and per-form gaps.
- `docs/bringup/gates/latest.json` remains the per-run multi-gate evidence artifact and must be refreshed by a full strict run before it is treated as release evidence.
