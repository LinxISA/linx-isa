# LinxTrace Checklist

- [ ] ID: TRACE-001 Pass LinxTrace contract sync lint gate.
  Command: `python3 rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py`
  Done means: stage token/emitter/linter/viewer contract sync passes.

- [ ] ID: TRACE-002 Pass LinxTrace sample lint gate.
  Command: `bash rtl/LinxCore/tests/test_konata_sanity.sh`
  Done means: sample trace validates schema/stage requirements.

- [ ] ID: TRACE-003 Pass trace SemVer compatibility gate.
  Command: `python3 tools/bringup/check_trace_semver_compat.py --root . --strict`
  Done means: trace schema contract + tool defaults remain SemVer-compatible.

- [ ] ID: TRACE-004 Pass DFX trace nightly gate.
  Command: `bash rtl/LinxCore/tests/test_konata_dfx_pipeview.sh`
  Done means: DFX trace lane validates successfully.

- [ ] ID: TRACE-005 Pass template trace nightly gate.
  Command: `bash rtl/LinxCore/tests/test_konata_template_pipeview.sh`
  Done means: template trace lane validates successfully.

- [ ] ID: TRACE-006 Keep breaking trace changes major-versioned with migration checks.
  Done means: no incompatible trace changes are merged without major bump and validation evidence.
