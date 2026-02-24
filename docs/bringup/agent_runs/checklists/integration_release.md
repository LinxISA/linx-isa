# Integration / Release Checklist

- [x] ID: INT-001 Validate ISA check26 contract before cross-repo runtime gates.
  Command: `python3 tools/bringup/check26_contract.py --root .`
  Done means: contract gate passes and canonical patterns are present.
  Status: ✅ PASS (2026-02-23) - `check26_contract.py` is pass in run `2026-02-23-r4-pin-qemu-linux-ctxfix` (log: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/isa_check26.log`), and canonical checks remain `OK`.

- [x] ID: INT-002 Verify all required gate rows are assigned to a known agent checklist.
  Done means: multi-agent static validator reports no unassigned required gate keys.
  Status: ✅ PASS (2026-02-23) - `check_multi_agent_gates.py --strict-always --mode static` returns `ok: multi-agent static validation passed (agents=6, assignments=18)`.

- [ ] ID: INT-003 Require model differential suite pass in strict runtime closure.
  Command: `python3 tools/bringup/run_model_diff_suite.py ...`
  Done means: model diff row is `pass` or explicitly waived via ledger.
  Status: ❌ FAIL (2026-02-23) - model-diff gate fails in run `2026-02-23-r4-pin-qemu-linux-ctxfix` because pyCircuit runner is missing executable (`tools/pyCircuit/tools/run_linx_cpu_pyc_cpp.sh`) (log: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/model_diff_suite.log`).

- [ ] ID: INT-004 Require `strict_cross_repo.sh` pass in strict closure.
  Command: `bash tools/regression/strict_cross_repo.sh`
  Done means: regression row is `pass` or explicitly waived via ledger.
  Status: ❌ FAIL (2026-02-23) - `strict_cross_repo.sh` still fails in run `2026-02-23-r6-pin-linux-stability-fix` (`RC=2`); Linux initramfs gates are stable, but BusyBox rootfs remains unstable with `_start` re-entry/hartid corruption signature before userspace marker, and timer-off reproduction shows the same failure class (`reg_strict_cross_repo.log`, `kernel_busybox_rootfs_timeroff.log`).

- [ ] ID: INT-005 Emit per-run multi-agent closure summary JSON.
  Artifact: `docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json`
  Done means: summary exists, `ok=true`, and includes waiver decisions.
  Status: ❌ FAIL (2026-02-23) - strict run `2026-02-23-r6-pin-linux-stability-fix` does not produce an `ok=true` closure artifact because required gates are still failing; keep non-closed status until strict closure is green.

- [x] ID: INT-006 Keep `docs/bringup/GATE_STATUS.md` generated from canonical JSON report.
  Command: `python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`
  Done means: markdown timestamp matches report timestamp.
  Status: ✅ PASS (2026-02-23) - timestamp check passes: `latest.json` and `GATE_STATUS.md` both report `2026-02-23 08:14:19Z`.
