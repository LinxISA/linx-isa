# Bring-up Gate Status (Canonical)

This file is generated from `docs/bringup/gates/latest.json` via `python3 tools/bringup/gate_report.py render`.

Last generated (UTC): `2026-02-17 19:41:53Z`

## Lane `external` (`2026-02-17-r1-external`)

- Timestamp (UTC): `2026-02-17 04:32:23Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `04e750e75b73957cf1c791535a3f4319534a52fc` (``)
  - `linux`: `9e37586596e85a1985bef53f597d0c75e4a9a215` (`${LINUX_ROOT}`)
  - `linxcore`: `fbb0450d98db2d9d33fb2e339cf32bc1a6c91493` (`${LINXCORE_ROOT}`)
  - `llvm`: `8ee471fd9882e4d0099ff5425f12528e98fe8aaf` (`${LLVM_ROOT}`)
  - `musl`: `missing` (``)
  - `pycircuit`: `edc3ef51110b339d64d034db39acb26e0a9a6c53` (`${PYCIRCUIT_ROOT}`)
  - `qemu`: `712f581e9a13f664118b3cf8c509b919c3ec4b87` (`${QEMU_ROOT}`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ❌ fail (`trap_loop_pc_0x31f85c`) | `terminal: repeated [linx trap] pc=0x000000000031f85c` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ❌ fail (`trap_loop_pc_0x31f85c`) | `terminal: repeated [linx trap] pc=0x000000000031f85c` |
| RTL | LinxCore co-sim smoke | yes | no | `unowned` | `bash ${LINXCORE_ROOT}/tests/test_cosim_smoke.sh` | ✅ pass (`cosim_smoke_pass`) | `terminal: test_cosim_smoke.sh PASS` |

## Lane `external` (`2026-02-17-r1-external-phase2c`)

- Timestamp (UTC): `2026-02-17 11:12:06Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `04e750e75b73957cf1c791535a3f4319534a52fc` (``)
  - `linux`: `9e37586596e85a1985bef53f597d0c75e4a9a215` (`${LINUX_ROOT}`)
  - `linxcore`: `b3bbe65ee5fcecc69631b46554d4789122c57f2c` (`${LINXCORE_ROOT}`)
  - `llvm`: `5289c65ce582a8d71fdaecc95b5a16eae43f9fcc` (`${LLVM_ROOT}`)
  - `musl`: `missing` (``)
  - `pycircuit`: `273eff570b670aec8795c85c5c7223f2cd6b22a5` (`${PYCIRCUIT_ROOT}`)
  - `qemu`: `712f581e9a13f664118b3cf8c509b919c3ec4b87` (`${QEMU_ROOT}`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/kernel_smoke.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu ${QEMU_ROOT}/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=external QEMU=${QEMU_ROOT}/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 ALLOW_GLIBC_G1_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase2c/external/reg_strict_cross_repo.log` |

## Lane `external` (`2026-02-17-r1-external-phase3`)

- Timestamp (UTC): `2026-02-17 11:37:03Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `04e750e75b73957cf1c791535a3f4319534a52fc` (``)
  - `linux`: `9e37586596e85a1985bef53f597d0c75e4a9a215` (`${LINUX_ROOT}`)
  - `linxcore`: `b3bbe65ee5fcecc69631b46554d4789122c57f2c` (`${LINXCORE_ROOT}`)
  - `llvm`: `5289c65ce582a8d71fdaecc95b5a16eae43f9fcc` (`${LLVM_ROOT}`)
  - `musl`: `missing` (``)
  - `pycircuit`: `273eff570b670aec8795c85c5c7223f2cd6b22a5` (`${PYCIRCUIT_ROOT}`)
  - `qemu`: `712f581e9a13f664118b3cf8c509b919c3ec4b87` (`${QEMU_ROOT}`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_or_allowed_blocked`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/lib_glibc_g1b.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu ${QEMU_ROOT}/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=external QEMU=${QEMU_ROOT}/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase3/external/reg_strict_cross_repo.log` |

## Lane `external` (`2026-02-17-r1-external-phase4`)

- Timestamp (UTC): `2026-02-17 11:50:29Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `04e750e75b73957cf1c791535a3f4319534a52fc` (``)
  - `linux`: `9e37586596e85a1985bef53f597d0c75e4a9a215` (`${LINUX_ROOT}`)
  - `linxcore`: `b3bbe65ee5fcecc69631b46554d4789122c57f2c` (`${LINXCORE_ROOT}`)
  - `llvm`: `5289c65ce582a8d71fdaecc95b5a16eae43f9fcc` (`${LLVM_ROOT}`)
  - `musl`: `missing` (``)
  - `pycircuit`: `273eff570b670aec8795c85c5c7223f2cd6b22a5` (`${PYCIRCUIT_ROOT}`)
  - `qemu`: `712f581e9a13f664118b3cf8c509b919c3ec4b87` (`${QEMU_ROOT}`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_or_allowed_blocked`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/lib_glibc_g1b.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu ${QEMU_ROOT}/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=external QEMU=${QEMU_ROOT}/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4/external/reg_strict_cross_repo.log` |

## Lane `external` (`2026-02-17-r1-external-phase4b`)

- Timestamp (UTC): `2026-02-17 19:09:56Z`
- Profile: `release-strict`
- Lane policy: `external+pin-required`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `04e750e75b73957cf1c791535a3f4319534a52fc` (``)
  - `linux`: `812f083bc29e075577b1a5ec7782b4ae9cebd428` (`${LINUX_ROOT}`)
  - `linxcore`: `d9898156083b2174931ccf4c634421784fc1c881` (`${LINXCORE_ROOT}`)
  - `llvm`: `55a7e27b80ba06bd3db9a098703256802d8fb9ea` (`${LLVM_ROOT}`)
  - `musl`: `missing` (``)
  - `pycircuit`: `5fe8de17b648a997d49fa863d11418aa06abdea3` (`${PYCIRCUIT_ROOT}`)
  - `qemu`: `712f581e9a13f664118b3cf8c509b919c3ec4b87` (`${QEMU_ROOT}`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=${QEMU_ROOT}/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=${QEMU_ROOT}/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_shared_libc_so_built`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/lib_glibc_g1b.log`; `summary:out/libc/glibc/logs/g1b-summary.txt` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu ${QEMU_ROOT}/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/lib_musl_both.log` |
| Model | QEMU vs model differential suite | yes | no | `bringup` | `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/model_diff_summary.json` | ✅ pass (`model_diff_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/model_diff_suite.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=external QEMU=${QEMU_ROOT}/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin`)

- Timestamp (UTC): `2026-02-17 19:41:53Z`
- Profile: `release-strict`
- Lane policy: `external+pin-required`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `5d20f2c3a1f33b5d81720638fee82ac091a635ff` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `bringup` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `bringup` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `bringup` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `bringup` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `bringup` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `bringup` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `bringup` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `bringup` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `bringup` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `glibc` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=0 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_shared_libc_so_built`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/lib_glibc_g1b.log`; `summary:out/libc/glibc/logs/g1b-summary.txt` |
| Library | musl runtime static+shared | yes | no | `bringup` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/lib_musl_both.log` |
| Model | QEMU vs model differential suite | yes | no | `bringup` | `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/logs/2026-02-17-r1-pin/pin/model_diff_summary.json` | ✅ pass (`model_diff_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/model_diff_suite.log` |
| Regression | strict_cross_repo.sh | yes | no | `bringup` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=1 RUN_MODEL_DIFF=1 RUN_CPP_GATES=1 CPP_MODE=phase-b RUN_CONSISTENCY_CHECKS=0 ALLOW_GLIBC_G1_BLOCKED=0 GLIBC_G1B_ALLOW_BLOCKED=0 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase2`)

- Timestamp (UTC): `2026-02-17 10:47:22Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ❌ fail (`all_suites_fail_or_timeout`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ❌ fail (`strict_system_fail`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/kernel_smoke.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 RUN_GLIBC_G1=0 ALLOW_GLIBC_G1_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ❌ fail (`strict_cross_repo_fail`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase2b`)

- Timestamp (UTC): `2026-02-17 10:59:27Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ❌ fail (`all_suites_fail_or_timeout`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ❌ fail (`strict_system_fail`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/kernel_smoke.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2b/pin/lib_musl_both.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase2c`)

- Timestamp (UTC): `2026-02-17 11:07:09Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/kernel_smoke.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 ALLOW_GLIBC_G1_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase2c/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase3`)

- Timestamp (UTC): `2026-02-17 11:31:36Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_or_allowed_blocked`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/lib_glibc_g1b.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase3/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase4`)

- Timestamp (UTC): `2026-02-17 11:45:52Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_or_allowed_blocked`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/lib_glibc_g1b.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-phase4b`)

- Timestamp (UTC): `2026-02-17 11:57:59Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/kernel_smoke.log` |
| Library | glibc G1b shared libc.so | yes | no | `unowned` | `cd . && GLIBC_G1B_ALLOW_BLOCKED=1 bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` | ✅ pass (`glibc_g1b_pass_shared_libc_so_built`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/lib_glibc_g1b.log`; `summary:out/libc/glibc/logs/g1b-summary.txt` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 LINX_EMU_DISABLE_TIMER_IRQ=0 RUN_GLIBC_G1=0 RUN_GLIBC_G1B=0 ALLOW_GLIBC_G1_BLOCKED=1 GLIBC_G1B_ALLOW_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ✅ pass (`strict_cross_repo_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-phase4b/pin/reg_strict_cross_repo.log` |

## Lane `pin` (`2026-02-17-r1-pin-stable`)

- Timestamp (UTC): `2026-02-17 10:38:57Z`
- Profile: `dev`
- Lane policy: `legacy`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `28633bc1a719ef4fa27c63f827b07cf7d1f6f7c6` (`lib/glibc`)
  - `linux`: `37a93dd5c49b5fda807fd204edf2547c3493319c` (`kernel/linux`)
  - `linx-isa`: `10f457bf75996c96901b91b2bd05e39fee20ab1c` (`.`)
  - `linxcore`: `d390d4890d5863697935275a3aa2598759b7cc00` (`rtl/LinxCore`)
  - `llvm`: `a079402e5d09e5a86bc703eb203d735ed057708f` (`compiler/llvm`)
  - `musl`: `f9e7978f67374572cc1b0f032fd1ed85470e1f11` (`lib/musl`)
  - `pycircuit`: `feee44880b063477a4908c496ffb8139096a574e` (`tools/pyCircuit`)
  - `qemu`: `d8bfcfcb7909a261a689f19d469cb77f59ba940a` (`emulator/qemu`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Compiler | AVS compile suites (linx32) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx32-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx32 ./run.sh` | ✅ pass (`compile_pass_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/compiler_linx32.log` |
| Compiler | AVS compile suites (linx64) | yes | no | `unowned` | `cd avs/compiler/linx-llvm/tests && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh` | ✅ pass (`compile_pass_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/compiler_linx64.log` |
| Compiler | Coverage 100% (linx32) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx32 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx32`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/compiler_cov_linx32.log` |
| Compiler | Coverage 100% (linx64) | yes | no | `unowned` | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100` | ✅ pass (`mnemonic_coverage_100_linx64`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/compiler_cov_linx64.log` |
| Emulator | QEMU all suites | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./run_tests.sh --all --timeout 10` | ✅ pass (`all_suites_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/emu_all_suites.log` |
| Emulator | QEMU strict system | yes | no | `unowned` | `cd avs/qemu && CLANG=${LLVM_ROOT}/build-linxisa-clang/bin/clang LLD=${LLVM_ROOT}/build-linxisa-clang/bin/ld.lld QEMU=emulator/qemu/build/qemu-system-linx64 ./check_system_strict.sh` | ✅ pass (`strict_system_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/emu_strict_system.log` |
| ISA | check26 contract | yes | no | `unowned` | `python3 tools/bringup/check26_contract.py --root .` | ✅ pass (`contract_ok`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/isa_check26.log` |
| Kernel | Linux initramfs full boot | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` | ✅ pass (`linux_full_boot_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/kernel_full_boot.log` |
| Kernel | Linux initramfs smoke | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 QEMU=emulator/qemu/build/qemu-system-linx64 python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py` | ✅ pass (`linux_smoke_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/kernel_smoke.log` |
| Library | musl runtime static+shared | yes | no | `unowned` | `LINX_DISABLE_TIMER_IRQ=1 python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --qemu emulator/qemu/build/qemu-system-linx64 --timeout 90` | ✅ pass (`runtime_pass`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/lib_musl_both.log` |
| Regression | strict_cross_repo.sh | yes | no | `unowned` | `cd . && SKIP_BUILD=1 TOOLCHAIN_LANE=external QEMU_LANE=pin QEMU=emulator/qemu/build/qemu-system-linx64 LINX_DISABLE_TIMER_IRQ=1 RUN_GLIBC_G1=0 ALLOW_GLIBC_G1_BLOCKED=1 bash tools/regression/strict_cross_repo.sh` | ❌ fail (`strict_cross_repo_fail`) | `log:docs/bringup/gates/logs/2026-02-17-r1-pin-stable/pin/reg_strict_cross_repo.log` |
