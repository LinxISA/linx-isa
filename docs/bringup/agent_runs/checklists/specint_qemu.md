# SPECint / QEMU Checklist

- [ ] ID: SPEC-001 Build SPEC CPU2017 intrate binaries for Linx (`phase-c`) without patching SPEC sources.
  Command: `MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  Done means: expected Linx executables are produced under each bench `exe/` directory.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-002 Verify produced executables are Linx machine type.
  Command: `llvm-readelf -h benchspec/CPU/<bench>/exe/<binary>`
  Done means: headers report `Machine: Linx`.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-003 Stage A fast subset run under QEMU matrix (9p + initramfs).
  Benches: `999.specrand_ir`, `505.mcf_r`, `531.deepsjeng_r`
  Command: `python3 tools/spec2017/run_stage_qemu_matrix.py --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 --stage a --input-set test --transports 9p,initramfs --strict --out-dir workloads/generated/spec2017/stage_a_xcheck/qemu_matrix`
  Done means: both transports pass Stage-A subset and aggregate summary reports `ok=true`.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-004 Stage A matrix summary artifacts are written.
  Artifacts:
    - `.../qemu_matrix/qemu_matrix_summary.json`
    - `.../qemu_matrix/qemu_matrix_summary.md`
    - `.../qemu_matrix/9p/stage_a_summary.json`
    - `.../qemu_matrix/initramfs/stage_a_summary.json`
  Done means: aggregate and per-transport qemu/specdiff verdicts are recorded per benchmark.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-005 Stage B full int-rate run under QEMU (excluding Fortran policy exclusions).
  Done means: all required Stage B intrate benchmarks run and emit validation outputs.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-006 Stage B host-side specdiff validation passes for required compares.
  Done means: every required compare command returns pass.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: SPEC-007 Explicitly exclude `548.exchange2_r` from required Linx intrate closure.
  Done means: exclusion is documented in manifest policy and enforced by gate review.
  Status: ⚠️ NOT TESTED (2026-02-23)
