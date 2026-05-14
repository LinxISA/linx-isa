# Integration / Release Checklist

- [x] ID: INT-001 Validate the canonical AVS contract before cross-repo runtime gates.
  Command: `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
  Done means: the AVS schema is canonical, all active entries carry `spec_refs` and tier metadata, and no legacy contract tokens remain.
  Status: ✅ PASS (2026-03-08) - `check_avs_contract.py` validates the canonical matrix with `tests=54` and `active=54` before the merged submodule repin cycle.

- [ ] ID: INT-016 Require AVS tier closure before strict runtime signoff.
  Command: `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr`
  Done means: every active AVS entry required for PR closure is implemented and validated with machine-readable evidence.
  Status: ✅ PASS (2026-04-18) - the refreshed PR-tier matrix/status pair now reports `required_tests=31` and `failure_count=0` (artifact: `docs/bringup/gates/avs_tier_closure_pr.json`).

- [x] ID: INT-002 Verify all required gate rows are assigned to a known agent checklist.
  Done means: multi-agent static validator reports no unassigned required gate keys.
  Status: ✅ PASS (2026-03-20) - `check_multi_agent_gates.py --strict-always --mode static` now returns `ok: multi-agent static validation passed (agents=11, assignments=62)` after refreshing the manifest/checklist map for the March 15 gate set.

- [ ] ID: INT-003 Require model differential suite pass in strict runtime closure.
  Command: `python3 tools/bringup/run_model_diff_suite.py ...`
  Done means: model diff row is `pass` or explicitly waived via ledger.
  Status: ✅ PASS (2026-04-18) - the compatibility wrapper again accepts the legacy gate CLI and the underlying `tools/model` suite passes for all required fixtures (artifact: `docs/bringup/gates/model_diff_summary.json`).

- [ ] ID: INT-004 Require `strict_cross_repo.sh` pass in strict closure.
  Command: `bash tools/regression/strict_cross_repo.sh`
  Done means: regression row is `pass` or explicitly waived via ledger.
  Status: ❌ FAIL (2026-04-18) - the latest canonical run `2026-04-18-r9-pin-linuxlibc-refresh` still records `Regression::strict_cross_repo.sh` as fail because the required BusyBox rootfs gate fails in the same run. Ad hoc direct reruns that skip the BusyBox blocker are not release evidence.

- [ ] ID: INT-005 Emit per-run multi-agent closure summary JSON.
  Artifact: `docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json`
  Done means: summary exists, `ok=true`, and includes waiver decisions.
  Status: ❌ FAIL (2026-04-18) - the latest summary exists, but it records `ok=false` because `Kernel::Linux busybox rootfs boot` is still failing without a waiver (artifact: `docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/multi_agent_summary.json`).

- [x] ID: INT-006 Keep `docs/bringup/GATE_STATUS.md` generated from canonical JSON report.
  Command: `python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`
  Done means: markdown timestamp matches report timestamp.
  Status: ✅ PASS (2026-04-18) - the rendered page matches the latest canonical report timestamp `2026-04-18 02:11:34Z` after the `2026-04-18-r9-pin-linuxlibc-refresh` refresh.

- [x] ID: INT-007 Enforce explicit agent module ownership and canonical skill names.
  Command: `python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  Done means: every agent declares `modules[]` + `skill`, and `skill` is in canonical list.
  Status: ✅ PASS (2026-03-20) - `check_multi_agent_gates.py --strict-always --mode static` passes after refreshing the manifest/checklist map for the current gate set.

- [x] ID: INT-008 Allow multi-module ownership only for approved cross-module agents.
  Command: `python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  Done means: agents with multiple modules are explicitly listed in `cross_module_agents`.
  Status: ✅ PASS (2026-03-20) - static validation confirms only the approved cross-module agents are multi-module (`libc`, `integration`).

- [ ] ID: INT-009 Sync installed skills from canonical map and prune deprecated aliases.
  Command: `bash skills/linx-skills/scripts/install_canonical_skills.sh`
  Done means: local `$CODEX_HOME/skills` keeps only canonical `linx-*` skills (plus protected utility skills).

- [x] ID: INT-010 Pull latest skills submodule before each bring-up cycle.
  Command: `bash tools/bringup/sync_canonical_skills.sh --pull-latest`
  Done means: `skills/linx-skills` is on latest `origin/main` and installed into Codex skills.
  Status: ✅ PASS (2026-03-08) - `sync_canonical_skills.sh --pull-latest` advanced `skills/linx-skills` to merged commit `5b4799f` and refreshed `/Users/zhoubot/.codex/skills`.

- [ ] ID: INT-011 Summarize evolved skills after bring-up work.
  Command: `bash tools/bringup/finalize_skill_updates.sh --base origin/main`
  Done means: summary markdown exists in `docs/bringup/agent_runs/skills_evolution/` with touched skills + SHA + rationale.

- [x] ID: INT-012 Guard against destructive skill churn before skill commit.
  Command: `python3 skills/linx-skills/scripts/check_skill_change_scope.py --repo-root skills/linx-skills --base origin/main`
  Done means: change scope guard passes and only intended skill directories changed.
  Status: ✅ PASS (2026-03-08) - scope guard reports `changed=0, removed=0` after the merged skills PR was pulled back into the superproject workspace.
- [ ] ID: INT-013 Enforce phase-bound waiver policy in runtime closure.
  Command: `python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode runtime ...`
  Done means: waivers are active only within the manifest active phase and expire automatically after phase transition.

- [ ] ID: INT-014 Require dual-lane required-gate parity (`pin` + `external`) for strict closure.
  Command: `python3 tools/bringup/check_gate_consistency.py --profile release-strict --lane-policy external+pin-required ...`
  Done means: both lanes pass with identical required gate key sets and fresh evidence.

- [ ] ID: INT-015 Enforce LinxCore nightly performance floor (<=10% regression).
  Command: `python3 tools/bringup/check_linxcore_perf_floor.py --root . --max-regression 10.0 ...`
  Done means: measured throughput regression is within configured threshold or run is rejected.

- [ ] ID: INT-017 Require pinned build closure for compiler, QEMU, Linux, and libc after v0.56 propagation.
  Command: `cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=out-linx64 ./run.sh`; `ninja -C emulator/qemu/build qemu-system-linx64`; `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`; `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh`; `env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH /opt/homebrew/bin/gmake -C kernel/linux ARCH=linx LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ 'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' HOSTCC=/usr/bin/clang HOSTCXX=/usr/bin/clang++ O=$PWD/kernel/linux/build-linx-fixed vmlinux -j$(sysctl -n hw.ncpu 2>/dev/null || nproc)`
  Done means: the pinned workspace compiles the propagated toolchain/emulator stack and produces Linux + libc artifacts without build failures, with compiler AVS closure evaluated over the baremetal targets that are still registered by the active compiler branch.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records compiler, QEMU, musl, glibc, and clean-helper Linux `vmlinux` build closure as pass.

- [x] ID: INT-018 Normalize the canonical AVS matrix status file before closure checks.
  Command: `python3 tools/bringup/gen_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --source-status avs/linx_avs_v1_test_matrix_status.json --out avs/linx_avs_v1_test_matrix_status.json`
  Done means: the checked-in AVS status file is normalized in place before downstream closure/audit gates consume it.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane report records `ISA::AVS status normalize` as `pass` in run `2026-04-18-r9-pin-linuxlibc-refresh`.

- [x] ID: INT-019 Audit AVS matrix status consistency against the canonical matrix.
  Command: `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --report-out docs/bringup/gates/avs_matrix_status_audit.json`
  Done means: every matrix entry is represented exactly once in the status file and implemented/pass counts are machine-reported.
  Status: ✅ PASS (2026-04-18) - the latest audit reports `ok=true` with no missing/extra status entries (artifact: `docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/avs_matrix_status_audit.json`).

- [x] ID: INT-020 Keep PTO kernel parity green in the pinned workload lane.
  Command: `python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --out-dir workloads/generated`
  Done means: the parity runner reports `ok=true` and the generated latest markdown/json artifacts agree with the current pinned lane.
  Status: ✅ PASS (2026-04-18) - the latest canonical run records `Regression::PTO kernel parity` as pass.

- [x] ID: INT-021 Keep benchmark workload regression green against the pinned phase-b sysroot.
  Command: `LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_benchmarks.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --json-out workloads/generated/benchmarks_result.json`
  Done means: the benchmark regression finishes successfully and writes the canonical JSON artifact.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records `Regression::Workload benchmarks` as `pass`.

- [x] ID: INT-022 Keep PolyBench workload regression green against the pinned phase-b sysroot.
  Command: `LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_polybench.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --json-out workloads/generated/polybench_result.json`
  Done means: the PolyBench regression finishes successfully and writes the canonical JSON artifact.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records `Regression::Workload polybench` as `pass`.

- [x] ID: INT-023 Keep portfolio workload regression green against the pinned phase-b sysroot.
  Command: `LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_portfolio.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --polybench --ctuning-limit 5 --json-out workloads/generated/portfolio_report.json`
  Done means: the portfolio regression finishes successfully and writes the canonical JSON artifact.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records `Regression::Workload portfolio` as `pass`.

- [x] ID: INT-024 Keep the curated ctuning subset green in the pinned workload lane.
  Command: `python3 workloads/ctuning/run_milepost_codelets.py --ctuning-root workloads/ctuning --target linx64-unknown-linux-musl --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --qemu emulator/qemu/build/qemu-system-linx64 --limit 5 --run --summary-json workloads/generated/ctuning_result.json`
  Done means: the curated ctuning subset completes under QEMU and writes the canonical summary JSON.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records `Regression::ctuning curated subset` as `pass`.

- [x] ID: INT-025 Keep TSVC strict compile coverage green at the required pass floor.
  Command: `python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --vector-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --no-run-qemu --out-dir workloads/generated`
  Done means: the compile-only TSVC lane completes and meets the strict pass floor without requiring QEMU runtime.
  Status: ✅ PASS (2026-04-18) - the latest pin-lane run records `Regression::TSVC strict coverage gate` as `pass` at `148/151`.

- [ ] ID: INT-026 Keep TSVC strict QEMU regression green at the runtime pass floor.
  Command: `python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --qemu emulator/qemu/build/qemu-system-linx64 --vector-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --out-dir workloads/generated`
  Done means: the TSVC lane completes under QEMU and meets the configured strict pass floor.
  Status: ❌ FAIL (2026-04-18) - runtime remains blocked on scalar-replay recurrence kernels in `auto` mode; the fresh PR lane only proves compile-only strict coverage.
