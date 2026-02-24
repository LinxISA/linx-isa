# Emulator / QEMU Checklist

- [x] ID: QEMU-001 Pass strict-system gate with timer IRQ policy required by strict runs.
  Command: `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 ./check_system_strict.sh`
  Done means: strict system suite passes with no trap-noise regressions.
  Status: ✅ PASS (2026-02-23) - strict system re-verified in run `2026-02-23-r6-pin-linux-stability-fix` with `*** REGRESSION PASSED ***` (log: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/emu_strict_system.log`).

- [x] ID: QEMU-002 Pass runtime AVS suites (`--all`) with timeout budget.
  Command: `cd avs/qemu && ./run_tests.sh --all --timeout 10`
  Done means: all runtime suites pass and logs are attached to gate evidence.
  Status: ✅ PASS (2026-02-23) - `run_tests.sh --all --timeout 10` re-verified in run `2026-02-23-r6-pin-linux-stability-fix` (log: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/emu_all_suites.log`).

- [ ] ID: QEMU-003 Keep regenerated opcode meta/id tables synchronized with decode sources.
  Files: `emulator/qemu/target/linx/linx_opcode_ids_gen.h`, `emulator/qemu/target/linx/linx_opcode_meta_gen.h`
  Done means: generated opcode artifacts match decode definitions used in the run.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [x] ID: QEMU-004 Validate trap semantics match strict v0.3 clarifications for CFI/BLOCKFMT/BFETCH.
  Done means: no conflicting trap behavior is observed in strict-system and model-diff gates.
  Status: ✅ PASS (2026-02-23) - strict system with required `0x110F` remains green and call/ret contract trap checks pass in run `2026-02-23-r6-pin-linux-stability-fix` (logs: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/emu_strict_system.log`, `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/emu_callret_contract.log`).

- [ ] ID: QEMU-005 ISA spec vs QEMU implementation gap analysis.
  Done means: Document all instructions in ISA spec that are not implemented in QEMU decode files.
  Status: ⚠️ NOT TESTED (2026-02-23) - legacy gap note exists but this run did not refresh a canonical instruction-coverage report.

- [ ] ID: QEMU-006 QEMU can boot full Linux with complete runtime APIs.
  Done means: Linux kernel boots with timer interrupts working, full syscalls available.
  Status: ❌ FAIL (2026-02-23) - emulator suites are green, but full-OS closure is still blocked by Linux BusyBox rootfs instability: userspace marker is missing and logs show `_start` re-entry/hartid corruption signature before handoff. The same signature reproduces in timer-off rootfs run (`kernel_busybox_rootfs_timeroff.log`), so current blocker is broader than timer-on policy (run `2026-02-23-r6-pin-linux-stability-fix`).

---

## ISA vs QEMU Implementation Gap Analysis

### Summary
- ISA spec: 710 unique mnemonics
- QEMU decode entries: 295 unique mnemonics
- Gap: ~415 instructions not implemented in QEMU

### Categories of Missing Instructions
1. **Compressed instructions (C.)**: Many C.* variants missing
2. **Vector instructions (V.)**: Most vector instructions not implemented
3. **Block instructions (BSTART variants)**: Many BSTART.* variants missing
4. **HL prefix instructions**: 48-bit compressed forms partially implemented

### Key Findings
- Basic RISC-like ALU ops (ADD, SUB, etc.) are implemented
- Block control flow (BSTART/BSTOP) is implemented
- Atomic operations (AMO) are implemented
- System instructions (ACRC, ACRE, SSRGET/SRRSET) are implemented
- Vector and tile operations are largely missing
