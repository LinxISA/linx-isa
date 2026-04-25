# pyCircuit Model Checklist

- [ ] ID: PYC-001 Pass pyCircuit CPU C++ smoke gate.
  Command: `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh`
  Done means: pyCircuit C++ CPU flow passes smoke execution.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run fails with `missing pycc` before the smoke flow can start (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_cpu_cpp_smoke.log`).

- [ ] ID: PYC-002 Pass QEMU vs pyCircuit trace diff gate.
  Command: `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh`
  Done means: schema checks pass and trace diff has no mismatches for gated sample.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run reaches trace generation but aborts with `missing pycc` before the pyCircuit side can compile the sample (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_trace_diff.log`).

- [x] ID: PYC-003 Pass pyCircuit interface contract gate.
  Command: `python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict`
  Done means: contract file, required fields, and flow script compatibility checks pass.
  Status: ✅ PASS (2026-03-15) - the latest pin-lane contract report records `ok=true` with no errors (artifact: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_interface_contract_report.json`).

- [ ] ID: PYC-004 Pass pyCircuit examples nightly gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_examples.sh`
  Done means: examples compile/run suites complete successfully.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves pyCircuit nightly gates disabled (`RUN_PYC_NIGHTLY_GATES=0`).

- [ ] ID: PYC-005 Pass pyCircuit simulation nightly gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_sims.sh`
  Done means: simulation suite passes without regressions.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves pyCircuit nightly gates disabled (`RUN_PYC_NIGHTLY_GATES=0`).

- [ ] ID: PYC-006 Pass pyCircuit deep nightly simulation gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh`
  Done means: nightly simulation lane closes.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves pyCircuit nightly gates disabled (`RUN_PYC_NIGHTLY_GATES=0`).

- [ ] ID: PYC-007 Keep API evolution versioned and backward-compatible unless major bump is declared.
  Done means: no unversioned breaking API changes bypass the interface contract gate.
