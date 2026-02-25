# Compiler / LLVM Checklist

- [x] ID: LLVM-001 Build pinned toolchain and pass AVS compile suites for `linx64` and `linx32`.
  Command: `cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang ./run.sh`
  Done means: both targets compile cleanly and logs are archived under the active gate run directory.
  Status: ✅ PASS (2026-02-23) - convergence run `2026-02-23-r4-pin-qemu-linux-ctxfix` passes both targets (logs: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/compiler_linx64.log`, `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/compiler_linx32.log`).

- [x] ID: LLVM-002 Verify mnemonic coverage stays at 100% for `linx64` and `linx32` outputs.
  Command: `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir ... --fail-under 100`
  Done means: both coverage checks pass with no missing mnemonics.
  Status: ✅ PASS (2026-02-23) - both coverage checks report `Coverage: 100.0%` (logs: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/compiler_cov_linx64.log`, `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/compiler_cov_linx32.log`).

- [x] ID: LLVM-003 Confirm v0.3 TEPL encodings in LLVM stay aligned with manual and QEMU.
  Command: `python3 tools/bringup/check_tepl_encoding.py --root .`
  Done means: script returns `OK` and no legacy TEPL encoding is present.
  Status: ✅ PASS (2026-02-23) - `check_tepl_encoding.py` returns `OK` (log: `docs/bringup/gates/logs/2026-02-23-r2-pin-reassess/pin/compiler_tepl.log`).

- [x] ID: LLVM-004 Rebuild C++ runtime overlay for target mode when runtime gates require it.
  Command: `bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-c`
  Done means: runtime overlay artifacts are present and linkable in the sysroot.
  Status: ✅ PASS (2026-02-23) - C++ runtime overlay build completes with `ok: Linx C++ runtimes ready` (log: `docs/bringup/gates/logs/2026-02-23-r2-pin-reassess/pin/compiler_cpp_runtime_phasec.log`).

- [x] ID: LLVM-005 Record commit SHA and submodule bump evidence for LLVM changes.
  Done means: SHA is captured in gate report lane manifest and referenced in change notes.
  Status: ✅ PASS (2026-02-25) - strict run `2026-02-25-r2-pin-lanefix` captures LLVM SHA in `docs/bringup/gates/latest.json` (`runs[-1].sha_manifest.llvm.sha`) and rendered lane manifest in `docs/bringup/GATE_STATUS.md`.
