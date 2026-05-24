# SPEC CPU + LinxCore XCheck Flow

## Scope

This document defines the dual-lane SPEC CPU2017 workflow used for LinxISA/LinxCore validation:

- Bringup subset: `spec_policy.bringup_subset`
- Promotion-set expansion: `spec_policy.promotion_required` (excluding policy exclusions)
- Functional transport policy:
  - bringup subset: `9p` + `initramfs`
  - promotion set: `9p` only
- XCheck target: first 1,000 commits parity between QEMU trace and LinxCore C++ TB

The flow intentionally separates:

- hosted-runtime build lane (current helpers still use `phase-c`)
- static image lane (current helpers still use `phase-b`)

Legacy helper flags `--stage a`, `--stage b`, `phase-b`, and `phase-c` remain
script implementation details. The canonical planning surface is
`docs/bringup/SPEC_WORKLOAD_PLAN.md`.

## Profile A: Bringup Subset

Run:

```bash
bash rtl/LinxCore/tests/test_specint_stage_a_xcheck.sh
```

Pipeline:

1. hosted-runtime build for bringup-subset benches
2. QEMU matrix (`9p` + `initramfs`, `--input-set test`, strict)
3. static image preparation (`LINX_SPEC_FORCE_STATIC=1`, auto-restore original exes)
4. suite generation (`linxcore-xcheck-suite-v1`)
5. xcheck execution (`failfast`, 1K commits)

## Profile B: Promotion Set Nightly (Report Lane)

Run (report-only default):

```bash
SPEC_NIGHTLY_REPORT_ONLY=1 bash rtl/LinxCore/tests/test_specint_full_xcheck_nightly.sh
```

Pipeline:

1. hosted-runtime build for promotion-set benches
2. QEMU matrix (`9p`, `--input-set test`)
3. static image preparation
4. suite generation (promotion-set policy)
5. xcheck execution (`diagnostic`, `--continue-on-fail`, report-only)

Exit behavior:

- report-only mode: parity mismatches do not fail the job (`summary.ok=false` is reported)
- infrastructure/tool failures still return non-zero

## Artifact Contract

Stage-A and nightly wrappers emit:

- QEMU matrix:
  - `.../qemu_matrix/qemu_matrix_summary.json`
  - `.../qemu_matrix/qemu_matrix_summary.md`
  - transport subdirs with `stage_<stage>_summary.json`
- phase-b image export:
  - `.../phaseb_static_images/phaseb_image_manifest.json`
- xcheck suite:
  - `.../linxcore_suite_stage_<a|b>.json`
- xcheck aggregate:
  - `.../xcheck/summary.json`
  - `.../xcheck/summary.md`
- per-case bundle:
  - `.../xcheck/<case>/qemu_trace.jsonl`
  - `.../xcheck/<case>/dut_trace.jsonl`
  - `.../xcheck/<case>/report/crosscheck_report.json`
  - `.../xcheck/<case>/report/crosscheck_report.md`
  - `.../xcheck/<case>/report/crosscheck_mismatches.json`

## Strict Regression Integration

`tools/regression/strict_cross_repo.sh` exposes opt-in toggles:

- `RUN_SPEC_PR_GATES=1` -> Stage-A blocking wrapper
- `RUN_SPEC_NIGHTLY_GATES=1` -> full nightly wrapper
- `SPEC_NIGHTLY_REPORT_ONLY` (`1` default)
- `SPEC_INPUT_SET` (`test` default)

## Promotion Criteria (Report -> Blocking Nightly)

Nightly promotion to blocking should require all of:

1. 7 consecutive nightly runs with zero infrastructure failures.
2. At least 95% benchmark parity pass rate over that 7-run window.
3. No unresolved deterministic regressions in Stage-A benches.
