# Integration / Release Checklist

- [x] ID: INT-001 Validate ISA check26 contract before cross-repo runtime gates.
  Command: `python3 tools/bringup/check26_contract.py --root .`
  Done means: contract gate passes and canonical patterns are present.
  Status: ✅ PASS (2026-02-22) - check26 contract OK

- [ ] ID: INT-002 Verify all required gate rows are assigned to a known agent checklist.
  Done means: multi-agent static validator reports no unassigned required gate keys.
  Status: ⚠️ NOT TESTED

- [ ] ID: INT-003 Require model differential suite pass in strict runtime closure.
  Command: `python3 tools/bringup/run_model_diff_suite.py ...`
  Done means: model diff row is `pass` or explicitly waived via ledger.
  Status: ⚠️ NOT TESTED

- [ ] ID: INT-004 Require `strict_cross_repo.sh` pass in strict closure.
  Command: `bash tools/regression/strict_cross_repo.sh`
  Done means: regression row is `pass` or explicitly waived via ledger.
  Status: ⚠️ NOT TESTED

- [ ] ID: INT-005 Emit per-run multi-agent closure summary JSON.
  Artifact: `docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json`
  Done means: summary exists, `ok=true`, and includes waiver decisions.
  Status: ⚠️ NOT TESTED

- [ ] ID: INT-006 Keep `docs/bringup/GATE_STATUS.md` generated from canonical JSON report.
  Command: `python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`
  Done means: markdown timestamp matches report timestamp.
  Status: ⚠️ NOT TESTED
