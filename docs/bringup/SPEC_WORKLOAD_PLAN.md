# SPEC Workload Plan

This page is the canonical planning surface for SPEC CPU2017 on LinxISA.

Legacy script flags such as `--stage a`, `--stage b`, `phase-b`, and `phase-c`
remain implementation details of existing helpers. They are not the canonical
planning taxonomy anymore.

The canonical taxonomy is capability-based:

- **Control Path**: wrapper, QEMU path, artifact handoff, reproducible launch.
- **Userspace Entry**: trivial firmwareless Linux + initramfs userspace startup.
- **Bringup Subset**: first useful SPEC subset for runtime debugging.
- **Hosted Runtime**: shared musl / dynamic-loader path for hosted benches.
- **Subset Closure**: bringup subset passes qemu + specdiff on required transports.
- **Scale-Out**: promotion set closure and LinxCore xcheck.

## Policy Sets

- `spec_policy.bringup_subset`
  Current set: `999.specrand_ir`, `505.mcf_r`, `531.deepsjeng_r`
- `spec_policy.promotion_required`
  Current set: full required SPECint promotion set excluding policy exclusions
- `spec_policy.excluded_benchmarks`
  Current policy exclusion: `548.exchange2_r`

## Milestones

### SPEC-M01 Control Path Ready

Goal:
- The canonical Stage-A/bringup matrix command runs from the superproject with
  an explicit or inherited QEMU path and produces per-transport run staging.

Done means:
- `tools/spec2017/run_stage_qemu_matrix.py` forwards `QEMU=...` or `--qemu ...`
  to `run_int_rate_qemu.py`.
- Per-transport run directories are created under the chosen out dir.

Primary evidence:
- matrix summary JSON/MD
- transport logs

### SPEC-M02 Firmwareless Linux Userspace Entry

Goal:
- A trivial static initramfs userspace payload starts visibly under the same
  firmwareless Linux/QEMU path that SPEC uses.

Done means:
- Static hello control lane emits guest-visible start/pass markers.
- Failure, if any, is no longer a zero-output timeout.

Primary evidence:
- corrected control-lane summary
- corrected `qemu_hello_static.log`

### SPEC-M03 Bringup Subset Output Generation

Goal:
- The benches in `spec_policy.bringup_subset` create their expected output
  files before specdiff runs.

Done means:
- `rand.24239.out`, `inp.out`, `mcf.out`, and `test.out` exist in the Linx run
  directories for the bringup subset.

Primary evidence:
- per-transport Stage-A summaries
- output files present in run dirs

### SPEC-M04 Hosted Runtime Restoration

Goal:
- The shared musl / dynamic-loader route is restored and reproducible.

Done means:
- `MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  is green again.
- Dynamic hello or equivalent hosted control lane reaches guest-visible output.
- Shared-runtime SPEC benches no longer fail at setup because of missing
  `libc.so` / loader artifacts.

Primary evidence:
- `phase-c` build summary
- hosted control-lane summary

### SPEC-M05 Bringup Subset Closure

Goal:
- The bringup subset passes qemu + specdiff on required transports.

Done means:
- `spec_policy.bringup_subset` is green on `9p` and `initramfs`.
- aggregate matrix summary reports `ok=true`.

Primary evidence:
- matrix summary JSON/MD
- per-transport summaries
- specdiff logs

### SPEC-M06 Promotion Set Closure And XCheck

Goal:
- The promotion set runs successfully on the runtime lane and is ready for
  LinxCore trace/xcheck expansion.

Done means:
- `spec_policy.promotion_required` is green on the promoted transport policy.
- phase-b static image prep is reproducible for the promotion set.
- LinxCore xcheck suite generation and report lane are green enough for
  promotion.

Primary evidence:
- promotion-set matrix summary
- phase-b image manifest
- xcheck suite/report artifacts

### SPEC-P01 Policy Exclusion

Goal:
- Keep `548.exchange2_r` explicitly excluded until the project deliberately
  expands scope to Fortran/runtime support.

Done means:
- exclusion remains documented in the manifest and checklists.
- promotion-set helpers do not silently reintroduce it.

## Current Live Interpretation

As of 2026-05-21:

- `SPEC-M01` is resolved.
- `SPEC-M02` is the first unresolved runtime milestone.
- `SPEC-M03` and `SPEC-M05` are blocked downstream of `SPEC-M02`.
- `SPEC-M04` remains separately open for the shared-runtime path.
- `SPEC-M06` is not actionable until `SPEC-M02` through `SPEC-M05` are green.
