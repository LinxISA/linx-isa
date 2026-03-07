# pyCircuit Model Checklist

- [ ] ID: PYC-001 Pass pyCircuit CPU C++ smoke gate.
  Command: `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh`
  Done means: pyCircuit C++ CPU flow passes smoke execution.

- [ ] ID: PYC-002 Pass QEMU vs pyCircuit trace diff gate.
  Command: `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh`
  Done means: schema checks pass and trace diff has no mismatches for gated sample.

- [ ] ID: PYC-003 Pass pyCircuit interface contract gate.
  Command: `python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict`
  Done means: contract file, required fields, and flow script compatibility checks pass.

- [ ] ID: PYC-004 Pass pyCircuit examples nightly gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_examples.sh`
  Done means: examples compile/run suites complete successfully.

- [ ] ID: PYC-005 Pass pyCircuit simulation nightly gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_sims.sh`
  Done means: simulation suite passes without regressions.

- [ ] ID: PYC-006 Pass pyCircuit deep nightly simulation gate.
  Command: `bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh`
  Done means: nightly simulation lane closes.

- [ ] ID: PYC-007 Keep API evolution versioned and backward-compatible unless major bump is declared.
  Done means: no unversioned breaking API changes bypass the interface contract gate.
