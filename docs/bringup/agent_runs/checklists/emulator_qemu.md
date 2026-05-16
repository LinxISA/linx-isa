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
  Files: `emulator/qemu/target/linx/linx_opcode_ids_gen.h`, `emulator/qemu/target/linx/linx_opcode_meta_gen.h`
  Done means: opcode audit reports no unexpected decode/meta drift and no enum/meta op-id mismatch.
  Status: ✅ PASS (2026-03-07) - opcode sync audit returns `qemu_opcode_meta_sync_ok` with `decode_only_unexpected=0`, `meta_only_unexpected=0`, and `id_mismatch_count=0` after regenerating the LinxCore/QEMU opcode tables from the normalized `insn48.decode` catalog (artifacts: `docs/bringup/gates/qemu_opcode_sync_latest.json`, `docs/bringup/gates/qemu_opcode_sync_latest.md`).

- [x] ID: QEMU-004 Validate trap semantics match the live v0.56 clarifications for CFI/BLOCKFMT/BFETCH.
  Done means: no conflicting trap behavior is observed in strict-system and model-diff gates.
  Status: ✅ PASS (2026-02-25) - strict system and model-diff are both green in run `2026-02-25-r2-pin-lanefix` (logs: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`, `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log`).

- [x] ID: QEMU-005 ISA spec vs QEMU implementation gap analysis.
  Command: `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md`
  Done means: Canonical machine-generated coverage report is refreshed and captures missing spec mnemonics and forms.
  Status: ✅ PASS (2026-05-08) - coverage report generated with `mnemonics=616/710`, `forms=612/740`, `missing_mnemonics=94`, and explicit missing/unmapped lists (artifacts: `docs/bringup/gates/qemu_isa_coverage_latest.json`, `docs/bringup/gates/qemu_isa_coverage_latest.md`).

- [x] ID: QEMU-006 QEMU can boot full Linux with complete runtime APIs.
  Done means: Linux kernel boots with timer interrupts working, full syscalls available.
  Status: ✅ PASS (2026-02-25) - full-OS closure gate is green in run `2026-02-25-r2-pin-lanefix` (`strict_cross_repo.sh` pass and BusyBox rootfs boot pass evidence in `kernel_busybox_rootfs.log`).

- [x] ID: QEMU-007 Build pinned `qemu-system-linx64` after v0.56 decode/translate propagation.
  Command: `ninja -C emulator/qemu/build qemu-system-linx64`
  Done means: the pinned QEMU workspace compiles the Linx system emulator binary with the current decode/translator state.
  Status: ✅ PASS (2026-03-08) - pinned QEMU `043390f788da` builds `emulator/qemu/build/qemu-system-linx64` successfully after the v0.56 propagation fixes and opcode-sync refresh.

- [ ] ID: QEMU-008 Keep scalar call/ret contract coverage aligned with fused direct-call source syntax.
  Command: `python3 avs/qemu/run_callret_contract.py`
  Done means: scalar direct-call source cases use fused `CALL ..., ra=...`, malformed or missing setret lowerings still fault, and positive scalar direct-call cases remain no-fault.
  Status: ✅ PASS (2026-05-15) - `run_callret_contract.py` passed after converting the scalar direct-call source cases to fused `BSTART.STD CALL, ..., ra=...`. Negative malformed/missing setret cases still trapped, and the positive fused direct-call cases remained no-fault.

---

## ISA vs QEMU Implementation Gap Analysis

### Summary
- ISA spec: 710 unique mnemonics
- QEMU mapped spec coverage: 616 unique mnemonics
- QEMU mapped spec forms: 612 legal forms
- Gap: 94 mnemonics and 128 forms currently outside mapped QEMU decode coverage

### Categories of Missing Instructions
1. **Vector instructions (`V.*`)**: still the largest uncovered set, especially at per-form granularity
2. **Block/tile families**: additional `BSTART.*`, tile/template forms remain uncovered
3. **Compressed/HL and accounting drift**: some remaining report gaps are still decode-mapping/reporting issues rather than proven translator absence
4. **MMU/debug/system breadth**: privileged/system families beyond current bring-up subset remain uncovered

### Key Findings
- Basic RISC-like ALU ops (ADD, SUB, etc.) are implemented
- Block control flow (BSTART/BSTOP) is implemented
- Atomic operations (AMO) are implemented
- System instructions (ACRC, ACRE, SSRGET/SRRSET) are implemented
- Vector and tile operations remain the dominant decode-spectrum gap
