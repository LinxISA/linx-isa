# Testbench Verification Checklist

- [ ] ID: TB-001 Pass ROB bookkeeping gate.
  Command: `bash rtl/LinxCore/tests/test_rob_bookkeeping.sh`
  Done means: multi-commit ROB ordering and bookkeeping checks pass.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run aborts while regenerating LinxCore collateral because `rtl/LinxCore/tools/lib/workspace_paths.sh` is missing (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/testbench_rob_bookkeeping.log`).

- [ ] ID: TB-002 Pass block-structure pyCircuit flow smoke gate.
  Command: `bash rtl/LinxCore/tests/test_block_struct_pyc_flow.sh`
  Done means: block-structure flow integration completes without contract drift.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run aborts with `missing pycc` before the pyCircuit flow can compile the sample (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/testbench_block_struct_pyc.log`).

- [ ] ID: TB-003 Keep replay/redirect/flush edge scenario coverage active in nightly suites.
  Done means: extended stress suites are executed and linked in gate evidence.

- [ ] ID: TB-004 Maintain forward-progress guarantees across superscalar hazard scenarios.
  Done means: no hang/deadlock regressions in required verification runs.
