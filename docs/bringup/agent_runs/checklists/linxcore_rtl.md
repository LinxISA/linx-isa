# LinxCore RTL Checklist

- [ ] ID: LC-001 Pass stage/connectivity lint gate.
  Command: `bash rtl/LinxCore/tests/test_stage_connectivity.sh`
  Done means: stage naming, no-stub lint, and connectivity checks pass.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run reports a `tb kTraceStageNames` mismatch between the reduced testbench stage list and the expected full pipeline catalog (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_stage_connectivity.log`).

- [x] ID: LC-002 Pass opcode parity gate.
  Command: `bash rtl/LinxCore/tests/test_opcode_parity.sh`
  Done means: decode/opcode metadata parity checks pass.
  Status: ✅ PASS (2026-03-15) - `LinxCore::opcode parity` is green in the latest pin-lane report `2026-03-15-r2-pin`.

- [ ] ID: LC-003 Pass runner protocol gate.
  Command: `bash rtl/LinxCore/tests/test_runner_protocol.sh`
  Done means: protocol handshake and mismatch-fail paths pass.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run fails immediately with `error: fallback benchmark memh not found` (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_runner_protocol.log`).

- [ ] ID: LC-004 Pass trace schema and memory smoke gate.
  Command: `bash rtl/LinxCore/tests/test_trace_schema_and_mem.sh`
  Done means: commit trace schema checks pass and memory event coverage is observed.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run fails immediately with `error: fallback benchmark memh not found` (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_trace_mem_smoke.log`).

- [ ] ID: LC-005 Pass cosim smoke gate.
  Command: `bash rtl/LinxCore/tests/test_cosim_smoke.sh`
  Done means: QEMU↔LinxCore smoke co-sim passes with fail-fast behavior intact.
  Status: ❌ FAIL (2026-03-15) - generated LinxCore update scripts abort because `rtl/LinxCore/tools/lib/workspace_paths.sh` is missing in the pinned tree (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_cosim_smoke.log`).

- [ ] ID: LC-006 Pass CoreMark crosscheck nightly gate.
  Command: `bash rtl/LinxCore/tests/test_coremark_crosscheck_1000.sh`
  Done means: 1000-commit crosscheck has zero mismatches.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves nightly LinxCore gates disabled (`RUN_LINXCORE_NIGHTLY_GATES=0`).

- [ ] ID: LC-007 Pass CBSTOP inflation guard nightly gate.
  Command: `bash rtl/LinxCore/tests/test_cbstop_inflation_guard.sh`
  Done means: first-window histogram guard reports no inflation regression.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves nightly LinxCore gates disabled (`RUN_LINXCORE_NIGHTLY_GATES=0`).

- [ ] ID: LC-008 Keep superscalar retire ordering and ROB invariants stable.
  Done means: ROB/testbench gates stay green in both lanes.

- [ ] ID: LC-009 Keep block/flush/nuke semantics precise under replay/redirect paths.
  Done means: required branch/block/memory gates pass with no waiver.
