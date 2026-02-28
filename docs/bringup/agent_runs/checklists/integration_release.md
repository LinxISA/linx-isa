# Integration / Release Checklist

- [x] ID: INT-001 Validate ISA check26 contract before cross-repo runtime gates.
  Command: `python3 tools/bringup/check26_contract.py --root .`
  Done means: contract gate passes and canonical patterns are present.
  Status: ✅ PASS (2026-02-25) - `check26_contract.py` is pass in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/isa_check26.log`).

- [x] ID: INT-002 Verify all required gate rows are assigned to a known agent checklist.
  Done means: multi-agent static validator reports no unassigned required gate keys.
  Status: ✅ PASS (2026-02-25) - `check_multi_agent_gates.py --strict-always --mode static` returns `ok: multi-agent static validation passed (agents=6, assignments=21)` after adding ownership for virtio-disk and QEMU maturity audit gate keys.

- [x] ID: INT-003 Require model differential suite pass in strict runtime closure.
  Command: `python3 tools/bringup/run_model_diff_suite.py ...`
  Done means: model diff row is `pass` or explicitly waived via ledger.
  Status: ✅ PASS (2026-02-25) - model-diff strict profile passes in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log`).

- [x] ID: INT-004 Require `strict_cross_repo.sh` pass in strict closure.
  Command: `bash tools/regression/strict_cross_repo.sh`
  Done means: regression row is `pass` or explicitly waived via ledger.
  Status: ✅ PASS (2026-02-25) - `strict_cross_repo.sh` passes in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/reg_strict_cross_repo.log`).

- [x] ID: INT-005 Emit per-run multi-agent closure summary JSON.
  Artifact: `docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json`
  Done means: summary exists, `ok=true`, and includes waiver decisions.
  Status: ✅ PASS (2026-02-25) - runtime closure summary exists with `ok=true` for run `2026-02-25-r2-pin-lanefix` (artifact: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/multi_agent_summary.strict_cross.json`).

- [x] ID: INT-006 Keep `docs/bringup/GATE_STATUS.md` generated from canonical JSON report.
  Command: `python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`
  Done means: markdown timestamp matches report timestamp.
  Status: ✅ PASS (2026-02-25) - timestamp check passes: `latest.json` and `GATE_STATUS.md` both report `2026-02-25 12:41:30Z`.

- [ ] ID: INT-007 Enforce explicit agent module ownership and canonical skill names.
  Command: `python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  Done means: every agent declares `modules[]` + `skill`, and `skill` is in canonical list.

- [ ] ID: INT-008 Allow multi-module ownership only for approved cross-module agents.
  Command: `python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  Done means: agents with multiple modules are explicitly listed in `cross_module_agents`.

- [ ] ID: INT-009 Sync installed skills from canonical map and prune deprecated aliases.
  Command: `bash skills/linx-skills/scripts/install_canonical_skills.sh`
  Done means: local `$CODEX_HOME/skills` keeps only canonical `linx-*` skills (plus protected utility skills).

- [ ] ID: INT-010 Pull latest skills submodule before each bring-up cycle.
  Command: `bash tools/bringup/sync_canonical_skills.sh --pull-latest`
  Done means: `skills/linx-skills` is on latest `origin/main` and installed into Codex skills.

- [ ] ID: INT-011 Summarize evolved skills after bring-up work.
  Command: `bash tools/bringup/finalize_skill_updates.sh --base origin/main`
  Done means: summary markdown exists in `docs/bringup/agent_runs/skills_evolution/` with touched skills + SHA + rationale.

- [ ] ID: INT-012 Guard against destructive skill churn before skill commit.
  Command: `python3 skills/linx-skills/scripts/check_skill_change_scope.py --repo-root skills/linx-skills --base origin/main`
  Done means: change scope guard passes and only intended skill directories changed.
