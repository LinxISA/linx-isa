# LinxCore RTL Checklist

- [ ] ID: LC-001 Pass stage/connectivity lint gate.
  Command: `bash rtl/LinxCore/tests/test_stage_connectivity.sh`
  Done means: stage naming, no-stub lint, and connectivity checks pass.

- [ ] ID: LC-002 Pass opcode parity gate.
  Command: `bash rtl/LinxCore/tests/test_opcode_parity.sh`
  Done means: decode/opcode metadata parity checks pass.

- [ ] ID: LC-003 Pass runner protocol gate.
  Command: `bash rtl/LinxCore/tests/test_runner_protocol.sh`
  Done means: protocol handshake and mismatch-fail paths pass.

- [ ] ID: LC-004 Pass trace schema and memory smoke gate.
  Command: `bash rtl/LinxCore/tests/test_trace_schema_and_mem.sh`
  Done means: commit trace schema checks pass and memory event coverage is observed.

- [ ] ID: LC-005 Pass cosim smoke gate.
  Command: `bash rtl/LinxCore/tests/test_cosim_smoke.sh`
  Done means: QEMU↔LinxCore smoke co-sim passes with fail-fast behavior intact.

- [ ] ID: LC-006 Pass CoreMark crosscheck nightly gate.
  Command: `bash rtl/LinxCore/tests/test_coremark_crosscheck_1000.sh`
  Done means: 1000-commit crosscheck has zero mismatches.

- [ ] ID: LC-007 Pass CBSTOP inflation guard nightly gate.
  Command: `bash rtl/LinxCore/tests/test_cbstop_inflation_guard.sh`
  Done means: first-window histogram guard reports no inflation regression.

- [ ] ID: LC-008 Keep superscalar retire ordering and ROB invariants stable.
  Done means: ROB/testbench gates stay green in both lanes.

- [ ] ID: LC-009 Keep block/flush/nuke semantics precise under replay/redirect paths.
  Done means: required branch/block/memory gates pass with no waiver.
