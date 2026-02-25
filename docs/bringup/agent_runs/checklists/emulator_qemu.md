# Emulator / QEMU Checklist

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
  Files: `emulator/qemu/target/linx/linx_opcode_ids_gen.h`, `emulator/qemu/target/linx/linx_opcode_meta_gen.h`
  Done means: opcode audit reports no unexpected decode/meta drift and no enum/meta op-id mismatch.
  Status: ✅ PASS (2026-02-25) - opcode sync audit returns `qemu_opcode_meta_sync_ok` with `decode_only_unexpected=0`, `meta_only_unexpected=0`, and `id_mismatch_count=0` (artifacts: `docs/bringup/gates/qemu_opcode_sync_latest.json`, `docs/bringup/gates/qemu_opcode_sync_latest.md`).

- [x] ID: QEMU-004 Validate trap semantics match strict v0.3 clarifications for CFI/BLOCKFMT/BFETCH.
  Done means: no conflicting trap behavior is observed in strict-system and model-diff gates.
  Status: ✅ PASS (2026-02-25) - strict system and model-diff are both green in run `2026-02-25-r2-pin-lanefix` (logs: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`, `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log`).

- [x] ID: QEMU-005 ISA spec vs QEMU implementation gap analysis.
  Command: `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md`
  Done means: Canonical machine-generated coverage report is refreshed and captures missing spec mnemonics.
  Status: ✅ PASS (2026-02-25) - coverage report generated with `coverage=311/710`, `missing=399`, and explicit missing/unmapped lists (artifacts: `docs/bringup/gates/qemu_isa_coverage_latest.json`, `docs/bringup/gates/qemu_isa_coverage_latest.md`).

- [x] ID: QEMU-006 QEMU can boot full Linux with complete runtime APIs.
  Done means: Linux kernel boots with timer interrupts working, full syscalls available.
  Status: ✅ PASS (2026-02-25) - full-OS closure gate is green in run `2026-02-25-r2-pin-lanefix` (`strict_cross_repo.sh` pass and BusyBox rootfs boot pass evidence in `kernel_busybox_rootfs.log`).

---

## ISA vs QEMU Implementation Gap Analysis

### Summary
- ISA spec: 710 unique mnemonics
- QEMU mapped spec coverage: 311 unique mnemonics
- Gap: 399 mnemonics currently outside mapped QEMU decode coverage

### Categories of Missing Instructions
1. **Vector instructions (`V.*`)**: large uncovered set remains
2. **Compressed/HL variants**: many `C.*` and `HL.*` forms remain uncovered
3. **Block/tile families**: additional `BSTART.*`, tile/template forms remain uncovered
4. **MMU/debug/system breadth**: privileged/system families beyond current bring-up subset remain uncovered

### Key Findings
- Basic RISC-like ALU ops (ADD, SUB, etc.) are implemented
- Block control flow (BSTART/BSTOP) is implemented
- Atomic operations (AMO) are implemented
- System instructions (ACRC, ACRE, SSRGET/SRRSET) are implemented
- Vector and tile operations are largely missing
