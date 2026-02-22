# Compiler / LLVM Checklist

- [ ] ID: LLVM-001 Build pinned toolchain and pass AVS compile suites for `linx64` and `linx32`.
  Command: `cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang ./run.sh`
  Done means: both targets compile cleanly and logs are archived under the active gate run directory.

- [ ] ID: LLVM-002 Verify mnemonic coverage stays at 100% for `linx64` and `linx32` outputs.
  Command: `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir ... --fail-under 100`
  Done means: both coverage checks pass with no missing mnemonics.

- [ ] ID: LLVM-003 Confirm v0.3 TEPL encodings in LLVM stay aligned with manual and QEMU.
  Command: `python3 tools/bringup/check_tepl_encoding.py --root .`
  Done means: script returns `OK` and no legacy TEPL encoding is present.

- [ ] ID: LLVM-004 Rebuild C++ runtime overlay for target mode when runtime gates require it.
  Command: `bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-c`
  Done means: runtime overlay artifacts are present and linkable in the sysroot.

- [ ] ID: LLVM-005 Record commit SHA and submodule bump evidence for LLVM changes.
  Done means: SHA is captured in gate report lane manifest and referenced in change notes.
