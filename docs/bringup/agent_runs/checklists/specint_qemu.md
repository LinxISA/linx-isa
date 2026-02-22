# SPECint / QEMU Checklist

- [ ] ID: SPEC-001 Build SPEC CPU2017 intrate binaries for Linx (`phase-c`) without patching SPEC sources.
  Command: `MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  Done means: expected Linx executables are produced under each bench `exe/` directory.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-002 Verify produced executables are Linx machine type.
  Command: `llvm-readelf -h benchspec/CPU/<bench>/exe/<binary>`
  Done means: headers report `Machine: Linx`.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-003 Stage A fast subset run under QEMU (9p/virtfs).
  Benches: `999.specrand_ir`, `505.mcf_r`, `531.deepsjeng_r`
  Done means: all subset jobs complete with host-side specdiff pass.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-004 Stage A summary artifact is written.
  Artifact: `workloads/spec2017/.../tmp/linx-qemu-results/stage_a_summary.json`
  Done means: qemu exit, trap detection, and specdiff verdict are recorded per benchmark.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-005 Stage B full int-rate run under QEMU (excluding Fortran policy exclusions).
  Done means: all required Stage B intrate benchmarks run and emit validation outputs.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-006 Stage B host-side specdiff validation passes for required compares.
  Done means: every required compare command returns pass.
  Status: ⚠️ NOT TESTED

- [ ] ID: SPEC-007 Explicitly exclude `548.exchange2_r` from required Linx intrate closure.
  Done means: exclusion is documented in manifest policy and enforced by gate review.
  Status: ⚠️ NOT TESTED
