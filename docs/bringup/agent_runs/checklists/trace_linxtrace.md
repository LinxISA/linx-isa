# LinxTrace Checklist

- [ ] ID: TRACE-001 Pass LinxTrace contract sync lint gate.
  Command: `python3 rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py`
  Done means: stage token/emitter/linter/viewer contract sync passes.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane run reports the same `tb kTraceStageNames` mismatch seen in the LinxCore stage/connectivity gate (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxtrace_contract_sync.log`).

- [ ] ID: TRACE-002 Pass LinxTrace sample lint gate.
  Command: `bash rtl/LinxCore/tests/test_konata_sanity.sh`
  Done means: sample trace validates schema/stage requirements.
  Status: ❌ FAIL (2026-03-15) - the latest pin-lane sample lint aborts with `error: fallback benchmark memh not found` (log: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxtrace_sample_lint.log`).

- [x] ID: TRACE-003 Pass trace SemVer compatibility gate.
  Command: `python3 tools/bringup/check_trace_semver_compat.py --root . --strict`
  Done means: trace schema contract + tool defaults remain SemVer-compatible.
  Status: ✅ PASS (2026-03-15) - the latest pin-lane report records `ok=true` with no SemVer/default-version drift (artifact: `docs/bringup/gates/logs/2026-03-15-r2-pin/pin/trace_semver_report.json`).

- [ ] ID: TRACE-004 Pass DFX trace nightly gate.
  Command: `bash rtl/LinxCore/tests/test_konata_dfx_pipeview.sh`
  Done means: DFX trace lane validates successfully.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves nightly trace gates disabled (`RUN_TRACE_NIGHTLY_GATES=0`).

- [ ] ID: TRACE-005 Pass template trace nightly gate.
  Command: `bash rtl/LinxCore/tests/test_konata_template_pipeview.sh`
  Done means: template trace lane validates successfully.
  Status: ⚪ NOT RUN (2026-03-15) - the latest strict pin run leaves nightly trace gates disabled (`RUN_TRACE_NIGHTLY_GATES=0`).

- [ ] ID: TRACE-006 Keep breaking trace changes major-versioned with migration checks.
  Done means: no incompatible trace changes are merged without major bump and validation evidence.
