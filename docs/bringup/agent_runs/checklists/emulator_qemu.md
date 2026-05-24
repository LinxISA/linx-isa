# Emulator / QEMU Checklist

## Closure Categories

### Scalar

- Status: active closure lane
- Scope:
  - strict-system/runtime AVS baseline
  - scalar block legality and call/ret contract behavior
  - generic-C scalar call/ret closure aligned with fused direct `CALL ..., ra=...`
- Current evidence:
  - `QEMU-001`, `QEMU-002`, `QEMU-004`, `QEMU-006`, `QEMU-007`
- Remaining scalar-specific gap:
  - fused handwritten `ICALL ra=` source syntax is not yet portable on the
    current compiler branch, so QEMU contract coverage still needs explicit
    `setret/c.setret` for indirect-call source tests

### SIMT

- Status: partial / subset-only
- Scope:
  - runtime support for the currently documented SIMT compiler subset
  - no claim of full grouped divergent closure
- Current evidence:
  - baseline runtime/system gates are green
  - broader SIMT runtime maturity remains tracked separately in
    `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
- Remaining gap:
  - QEMU runtime breadth for grouped divergent kernels and many `V.*` decode
    forms remains incomplete

### Tile

- Status: partial
- Scope:
  - tile/template decode surface and strict legality/trap behavior
- Current evidence:
  - opcode/meta sync is green (`QEMU-003`)
- Remaining gap:
  - tile/template decode-spectrum and semantic coverage are still materially
    behind the spec catalog

- [x] ID: QEMU-001 Pass strict-system gate with timer IRQ policy required by strict runs.
  Command: `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 ./check_system_strict.sh`
  Done means: strict system suite passes with no trap-noise regressions.
  Status: ✅ PASS (2026-02-25) - strict system re-verified in run `2026-02-25-r2-pin-lanefix` with `*** REGRESSION PASSED ***` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`).

- [x] ID: QEMU-002 Pass runtime AVS suites (`--all`) with timeout budget.
  Command: `cd avs/qemu && ./run_tests.sh --all --timeout 10`
  Done means: all runtime suites pass and logs are attached to gate evidence.
  Status: ✅ PASS (2026-02-25) - `run_tests.sh --all --timeout 10` re-verified in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_all_suites.log`).

- [x] ID: QEMU-003 Keep regenerated opcode meta/id tables synchronized with decode sources.
  Command: `python3 tools/bringup/check_qemu_opcode_meta_sync.py --allowlist docs/bringup/qemu_opcode_sync_allowlist.json --report-out docs/bringup/gates/qemu_opcode_sync_latest.json --out-md docs/bringup/gates/qemu_opcode_sync_latest.md`
  Files: `emulator/qemu/target/linx/block16.decode`, `block32.decode`, `block48.decode`, `block32_private_fvec.decode`
  Done means: opcode audit reports no unexpected live decode-surface drift for the current QEMU line; legacy generated opcode meta/id headers are treated as optional when absent.
  Status: ✅ PASS (2026-05-21) - the audit surface is updated to the current decode files and no longer depends on removed legacy header paths.

- [x] ID: QEMU-004 Validate trap semantics match the live v0.56 clarifications for CFI/BLOCKFMT/BFETCH.
  Done means: no conflicting trap behavior is observed in strict-system and model-diff gates.
  Status: ✅ PASS (2026-02-25) - strict system and model-diff are both green in run `2026-02-25-r2-pin-lanefix` (logs: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`, `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log`).

- [x] ID: QEMU-005 ISA spec vs QEMU implementation gap analysis.
  Command: `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md`
  Done means: Canonical machine-generated coverage report is refreshed and captures missing spec mnemonics and forms.
  Status: ✅ PASS (2026-05-21) - the live decoder/translator coverage bridge now measures the current `block16/block32/block48/block32_private_fvec` sources directly and reports `mnemonics=710/710`, while per-form closure remains open at `forms=453/740` (artifacts: `docs/bringup/gates/qemu_isa_coverage_latest.json`, `docs/bringup/gates/qemu_isa_coverage_latest.md`).

- [ ] ID: QEMU-005A AVS translation coverage reaches 100% at the per-source object level.
  Command: `python3 tools/bringup/report_qemu_translation_coverage.py --obj-dir avs/qemu/out/obj --llvm-objdump compiler/llvm/build-linxisa-clang/bin/llvm-objdump --report-out docs/bringup/gates/qemu_translation_coverage_latest.json --out-md docs/bringup/gates/qemu_translation_coverage_latest.md --require-full`
  Done means: Every canonical v0.56 instruction mnemonic is covered by at least one AVS QEMU unit-test object, and the machine-generated report exits 0 in hard-fail mode.
  Status: ✅ PASS (2026-05-21) - the framework now builds a compile-only `translation_corpus` suite from generated spec-decode vectors plus canonical hand-written forms, and the machine-generated report reaches `710/710` canonical mnemonics (`100.0%`) from `84` AVS QEMU object files.

- [x] ID: QEMU-005B Keep the whole-stack coverage report free of translation-only anomalies.
  Command: `python3 tools/bringup/report_isa_llvm_qemu_coverage.py --compiler-analyzer avs/compiler/linx-llvm/tests/analyze_coverage.py --compiler-out-dir avs/compiler/linx-llvm/tests/out-linx64 --qemu-isa-report docs/bringup/gates/qemu_isa_coverage_latest.json --qemu-translation-report docs/bringup/gates/qemu_translation_coverage_latest.json --report-out docs/bringup/gates/isa_llvm_qemu_coverage_latest.json --out-md docs/bringup/gates/isa_llvm_qemu_coverage_latest.md --require-coherent`
  Done means: no mnemonic appears in AVS translation coverage without also appearing in mapped QEMU implementation coverage.
  Status: ✅ PASS (2026-05-21) - AVS translation coverage, LLVM coverage, and mapped QEMU implementation coverage all now reach `710/710` canonical mnemonics, so the whole-stack mnemonic mismatch bucket is empty.

- [x] ID: QEMU-006 QEMU can boot full Linux with complete runtime APIs.
  Done means: Linux kernel boots with timer interrupts working, full syscalls available.
  Status: ✅ PASS (2026-02-25) - full-OS closure gate is green in run `2026-02-25-r2-pin-lanefix` (`strict_cross_repo.sh` pass and BusyBox rootfs boot pass evidence in `kernel_busybox_rootfs.log`). Note for current recovery work: the merged Linx64 recovery lane now expects direct kernel/rootfs boot to run firmwareless (`-bios none`), so local rootfs/SPEC reruns should preserve that QEMU invocation policy.

- [x] ID: QEMU-007 Build pinned `qemu-system-linx64` after v0.56 decode/translate propagation.
  Command: `bash tools/bringup/run_qemu_build_clean.sh --qemu-root $PWD/emulator/qemu --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64`
  Done means: the pinned QEMU workspace compiles the Linx system emulator binary with the current decode/translator state, reusing the same output directory incrementally across iterations.
  Status: ✅ PASS (2026-05-21) - the clean helper remains reproducible while still reusing its configured out dir incrementally; the local bring-up lane also builds successfully at `/tmp/linx-qemu-local-build/qemu-system-linx64`.

- [ ] ID: QEMU-008 Keep scalar call/ret contract coverage aligned with fused direct-call source syntax.
  Command: `python3 avs/qemu/run_callret_contract.py`
  Done means: scalar direct-call source cases use fused `CALL ..., ra=...`, malformed or missing setret lowerings still fault, and positive scalar direct-call cases remain no-fault.
  Status: ✅ PASS (2026-05-15) - `run_callret_contract.py` passed after converting the scalar direct-call source cases to fused `BSTART.STD CALL, ..., ra=...`. Negative malformed/missing setret cases still trapped, and the positive fused direct-call cases remained no-fault.

---

## ISA vs QEMU Implementation Gap Analysis

### Summary
- ISA spec: 710 unique mnemonics
- QEMU mapped spec coverage: 710 unique mnemonics
- QEMU mapped spec forms: 453 legal forms
- Gap: 0 mnemonics and 287 forms currently outside mapped QEMU decode coverage

### Categories of Remaining Work
1. **Per-form closure**: mnemonic closure is complete, but many legal form encodings still are not represented in the current QEMU decode/meta surface.
2. **Runtime evidence**: the new scalar prefetch and expanded 48-bit HL-family surface still need clean AVS/runtime proof with the refreshed LLVM toolchain.

### Key Findings
- Basic RISC-like ALU ops (ADD, SUB, etc.) are implemented
- Block control flow (BSTART/BSTOP) is implemented
- Atomic operations (AMO) are implemented
- System instructions (ACRC, ACRE, SSRGET/SRRSET) are implemented
- The previous `V.*`, scalar prefetch, `XB`, `C.SETRET`, `BWT`, `B.ARG`, `ERCOV`, `ESAVE`, and 48-bit HL immediate/control gaps are now closed at the mnemonic level in the machine-generated report
