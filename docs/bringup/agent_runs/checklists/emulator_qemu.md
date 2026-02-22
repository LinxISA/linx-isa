# Emulator / QEMU Checklist

- [x] ID: QEMU-001 Pass strict-system gate with timer IRQ policy required by strict runs.
  Command: `cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 ./check_system_strict.sh`
  Done means: strict system suite passes with no trap-noise regressions.
  Status: ✅ PASS (2026-02-22) - All 15 system tests pass

- [x] ID: QEMU-002 Pass runtime AVS suites (`--all`) with timeout budget.
  Command: `cd avs/qemu && ./run_tests.sh --all --timeout 10`
  Done means: all runtime suites pass and logs are attached to gate evidence.
  Status: ✅ PASS (2026-02-22) - All test suites pass

- [ ] ID: QEMU-003 Keep regenerated opcode meta/id tables synchronized with decode sources.
  Files: `emulator/qemu/target/linx/linx_opcode_ids_gen.h`, `emulator/qemu/target/linx/linx_opcode_meta_gen.h`
  Done means: generated opcode artifacts match decode definitions used in the run.
  Status: ⚠️ NOT TESTED

- [ ] ID: QEMU-004 Validate trap semantics match strict v0.3 clarifications for CFI/BLOCKFMT/BFETCH.
  Done means: no conflicting trap behavior is observed in strict-system and model-diff gates.
  Status: ⚠️ NOT TESTED
