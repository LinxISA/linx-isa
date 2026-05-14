# Compiler / LLVM Checklist

- [x] ID: LLVM-001 Build pinned toolchain and pass the active baremetal AVS compile suite for the targets registered by the current compiler branch.
  Command: `cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh`
  Done means: every required active baremetal target in the current compiler branch compiles cleanly and logs are archived under the active gate run directory. Archived targets that are not registered by the live compiler are not part of current required closure.
  Status: ✅ PASS (2026-05-14) - Bisheng LLVM `631961c3988f` passes the in-workspace `linx64` AVS compile suite. `clang --print-targets` in this branch registers `linx64`/`linx64be` only, so `linx32` is no longer part of the active baremetal gate surface.

- [x] ID: LLVM-002 Verify mnemonic coverage stays at 100% for the active baremetal AVS outputs.
  Command: `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100`
  Done means: every required active baremetal target reports 100% mnemonic coverage with no missing mnemonics.
  Status: ✅ PASS (2026-05-14) - `analyze_coverage.py --fail-under 100` reports `Coverage: 100.0%` for `out-linx64` (710/710 unique mnemonics). No current `linx32` output is required because the branch does not register that target.

- [x] ID: LLVM-003 Confirm canonical v0.56 TEPL tile opcodes in LLVM stay aligned with the manual and other consumers.
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

- [x] ID: LLVM-006 Keep the pinned tool build complete enough for Linux/libc closure.
  Command: `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf`
  Done means: auxiliary LLVM binutils required by kernel/libc integration are present next to the pinned `clang` and `ld.lld`.
  Status: ✅ PASS (2026-03-08) - auxiliary tools were rebuilt in-place for pinned LLVM `e6ce4b78faaa`, producing `compiler/llvm/build-linxisa-clang/bin/llvm-ar`, `llvm-nm`, `llvm-readelf`, and `llvm-strip`.
