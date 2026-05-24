# SPECint / QEMU Checklist

## Live Blockers (2026-05-21)

- [x] BLOCK-SPEC-A-001 Keep the canonical Stage-A matrix command runnable from the superproject.
  Command: `QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 python3 tools/spec2017/run_stage_qemu_matrix.py --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 --stage a --input-set test --strict --out-dir workloads/generated/spec_stage_a_wrapper_verify_env`
  Resolution: `tools/spec2017/run_stage_qemu_matrix.py` now accepts `--qemu` and defaults from `QEMU` in the environment, then forwards that path to `run_int_rate_qemu.py`.
  Evidence: the earlier failure is still captured in `workloads/generated/spec_stage_a_livecheck/qemu_matrix_summary.json`, while the fixed wrapper now successfully stages a transport run under `workloads/generated/spec_stage_a_wrapper_verify_env/9p/999_specrand_ir/run_001/`.

- [ ] BLOCK-SPEC-A-002 `999.specrand_ir` must complete under both Stage-A transports.
  Command: `python3 tools/spec2017/run_int_rate_qemu.py --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 --stage a --transport <9p|initramfs> --input-set test --sysroot out/libc/musl/install/phase-c --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --out-dir workloads/generated/spec_stage_a_livecheck_direct/<transport>`
  Blocker: the original shared-runtime route times out on both transports, and the narrowed static fallback still stalls before any guest-visible output. This is now evidence of a broader firmwareless Linux initramfs/userspace-entry blocker, not just a benchmark-local runtime issue.
  Evidence:
  - shared route: `workloads/generated/spec_stage_a_livecheck_direct/9p/stage_a_summary.json`, `.../initramfs/stage_a_summary.json`
  - static fallback: `workloads/generated/spec_stage_a_phaseb_static_999/stage_a_summary.json` (`guest_shared_runtime=false`, `stalled=true`, zero-byte `qemu.log`)
  - libc control lane: `avs/qemu/out/musl-smoke-spec-debug3/summary.json` (`hello_static_runtime_timeout`)
  - no-libc control lane: `kernel/linux/tools/linxisa/initramfs/smoke.py` now also fails against both dirty and sanitized local QEMU builds, so the blocker is below SPEC userspace logic.

- [ ] BLOCK-SPEC-A-003 `505.mcf_r` must complete under both Stage-A transports.
  Command: same as `BLOCK-SPEC-A-002`.
  Blocker: both transports hit the full 240-second guest timeout with no benchmark output files (`inp.out`, `mcf.out`) produced.
  Evidence: `workloads/generated/spec_stage_a_livecheck_direct/9p/stage_a_summary.json`, `.../initramfs/stage_a_summary.json`, and missing-output specdiff logs `.../505_mcf_r_specdiff_1.log` / `..._2.log`.

- [ ] BLOCK-SPEC-A-004 `531.deepsjeng_r` must complete under both Stage-A transports.
  Command: same as `BLOCK-SPEC-A-002`.
  Blocker: both transports hit the full 240-second guest timeout with no benchmark output file (`test.out`) produced.
  Evidence: `workloads/generated/spec_stage_a_livecheck_direct/9p/stage_a_summary.json`, `.../initramfs/stage_a_summary.json`, and missing-output specdiff log `.../531_deepsjeng_r_specdiff_1.log`.

- [ ] BLOCK-SPEC-A-005 The Stage-A subset must reach output generation before specdiff.
  Done means: `rand.24239.out`, `inp.out`, `mcf.out`, and `test.out` exist in the Linx run directories before specdiff executes.
  Blocker: all current Stage-A failures are pre-output guest runtime stalls, not specdiff mismatches after partial progress, and the same silent behavior now reproduces with the static hello control lane.
  Evidence: every current specdiff log reports `Can't open input file ... No such file or directory`.

- [ ] BLOCK-SPEC-A-006 Reconcile stale checklist/docs that still describe `531.deepsjeng_r` as first blocked by missing shared musl.
  Done means: SPEC bring-up docs reflect the current May 21, 2026 stop path.
  Blocker: the stop path has changed twice in one day: earlier shared `phase-c` artifacts were present, then the install tree disappeared, `phase-b` had to be repaired, and the static fallback still hit the same silent runtime stall. The docs need to stop treating the problem as only "`531.deepsjeng_r` needs `libc.so`".
  Evidence: `out/libc/musl/logs/phase-b-summary.txt`, `workloads/generated/spec_stage_a_phaseb_static_999/stage_a_summary.json`, and `avs/qemu/out/musl-smoke-spec-debug3/summary.json`.

- [x] ID: SPEC-M01 Control path ready.
  Canonical plan: `docs/bringup/SPEC_WORKLOAD_PLAN.md`
  Done means: the canonical matrix command is runnable from the superproject, forwards the active QEMU path, and creates per-transport run staging.
  Status: ✅ RESOLVED (2026-05-21) - `run_stage_qemu_matrix.py` now forwards `QEMU=...` / `--qemu ...` to the transport runner.

- [ ] ID: SPEC-M02 Firmwareless Linux userspace entry.
  Canonical plan: `docs/bringup/SPEC_WORKLOAD_PLAN.md`
  Done means: a trivial static initramfs userspace payload emits guest-visible start/pass markers under the same firmwareless Linux/QEMU boot path that SPEC uses.
  Status: ❌ CURRENT FIRST RUNTIME BLOCKER (2026-05-22) - both the corrected static hello control lane and the repo's own no-libc initramfs smoke fail under firmwareless Linux+initramfs boot, so the next runtime blocker is the broader Linux userspace-entry path rather than SPEC harness logic.

- [ ] ID: SPEC-M03 Bringup subset output generation.
  Bringup subset: `spec_policy.bringup_subset`
  Done means: the bringup subset produces its expected output files before specdiff runs.
  Status: ❌ BLOCKED BY SPEC-M02 (2026-05-21) - shared and static narrowed runs still fail before output generation.

- [ ] ID: SPEC-M04 Hosted shared-runtime restoration.
  Command: `MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  Done means: the shared musl route is restored and dynamic SPEC benches can run against a valid `phase-c` sysroot.
  Status: ❌ OPEN (2026-05-21) - `phase-c` is not the current closure baseline; `phase-b` was repaired first and the shared-runtime path still needs canonical rebuild/revalidation.

- [ ] ID: SPEC-M05 Bringup subset closure.
  Canonical command: `python3 tools/spec2017/run_stage_qemu_matrix.py --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 --stage a --input-set test --transports 9p,initramfs --strict --out-dir workloads/generated/spec_stage_a`
  Done means: the bringup subset passes qemu + specdiff on required transports and aggregate summary reports `ok=true`.
  Status: ❌ BLOCKED BY SPEC-M02 / SPEC-M03 (2026-05-21) - transport summaries still show `ok=false` for every bringup-subset bench.

- [ ] ID: SPEC-M06 Promotion-set closure and xcheck readiness.
  Promotion set: `spec_policy.promotion_required`
  Done means: the promotion set passes the promoted transport policy, phase-b static image prep is reproducible, and LinxCore xcheck promotion is actionable.
  Status: ⚠️ NOT STARTED (2026-05-21) - blocked behind SPEC-M02 through SPEC-M05.

- [ ] ID: SPEC-P01 Fortran exclusion policy.
  Done means: `548.exchange2_r` stays explicitly excluded from Linx intrate scope until the project intentionally expands to Fortran/runtime support.
  Status: ✅ POLICY ACTIVE (2026-05-21)
