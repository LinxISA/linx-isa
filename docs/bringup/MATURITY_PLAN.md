# LinxISA Maturity Plan (Tier-1 Track vs ARM/x86)

Last updated: 2026-04-18

## Baseline

- Latest canonical run: `2026-03-15-r2-pin` (`2026-03-15 02:38:42Z`)
- Canonical report: `docs/bringup/gates/latest.json`
- The latest checked-in canonical report is still the stale `2026-03-15-r2-pin` snapshot, but fresh April 18, 2026 local recovery evidence now clears the PR-lane false blockers: AVS PR tier closure is green, model-diff passes again, and direct `strict_cross_repo.sh` PR reruns complete successfully.
- Two April 11, 2026 spot checks supersede stale March 15 failure narratives:
  - `python3 tools/bringup/check_sail_model.py --require-parser` and `python3 tools/isa/gen_sail_decode.py --check` are both green again.
  - `python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120` is green again and reports `all_match=true` for 27 kernels.

## Gap Snapshot

- AVS PR-tier closure is now complete (`31/31` required tests pass), while nightly breadth remains `31/54`.
- The current recovery work is infrastructure-first:
  - kernel tree hygiene for out-of-tree `vmlinux` builds,
  - glibc smoke asset packaging,
  - LinxCore fallback benchmark assets,
  - LinxCore `workspace_paths.sh` restore,
  - pyCircuit `pycc`/`pyc-compile` availability in the pinned workspace,
  - fresh strict-closure rerun after clearing the stale Sail decode first-failure narrative.
- Hosted workload hardening is now split cleanly by tier:
  - PR lane: benchmark/polybench/portfolio artifact publication and PTO parity are green.
  - Nightly/runtime lane: SPEC Stage A and TSVC QEMU runtime remain blocked.
- ISA-vs-QEMU implementation breadth, ABI/unwind/TLS hardening, privileged/MMU/debug scope, and SIMT/compiler maturity still remain after the current recovery lane.

## Immediate Recovery Lane (March-April 2026)

Status: Active

1. Refresh the checked-in canonical report so it matches the April 18, 2026 local PR-lane recovery evidence.
2. Restore shared prerequisites for LinxCore/Testbench/Trace/pyCircuit follow-up lanes:
   - recover `rtl/LinxCore/tools/lib/workspace_paths.sh`,
   - restore fallback `.memh` assets for runner/trace smoke gates,
   - build or point the pinned workspace at `pycc` and `pyc-compile`.
3. Re-close kernel/libc integration basics:
   - restore clean-source-tree handling for `Kernel::Linux \`vmlinux\` build closure`,
   - restore the missing glibc wrapper asset for `Library::glibc runtime dynamic hello`.
4. Re-run the runtime-heavy workload lanes that still block nightly closure:
   - re-run SPEC Stage A QEMU matrix,
   - re-run the TSVC strict QEMU gate,
   - reclassify the next Linux/userspace runtime fault after each fix.
5. Resume nightly AVS breadth work on decode/block edge cases, atomics, FP, vector runtime, and Linux workload launch semantics.

## Milestones

### M1 (1-2 weeks): Recovery of broken strict-gate prerequisites

Status: In progress

- Completed in this refresh:
  - checklist/manifest ownership now includes AVS normalize/audit plus the workload regression rows recorded in the March 15 canonical report.
  - the execution-order runbook now lives in `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`.
  - the April 11, 2026 PTO parity spot check is green again, so `INT-020` is no longer an active engineering blocker pending canonical report refresh.
- Remaining for M1:
  - canonical report refresh via `run_runtime_convergence.sh`,
  - `LINUX-005`,
  - `LIBC-006`,
  - `LC-001`, `LC-003`, `LC-004`, `LC-005`,
  - `TB-001`, `TB-002`,
  - `TRACE-001`, `TRACE-002`,
  - `PYC-001`, `PYC-002`,
  - nightly/runtime follow-up for `INT-025`, `SPEC-003`, `SPEC-004`.

### M2 (3-6 weeks): AVS core coverage expansion

Status: Partially complete for PR tier; nightly breadth still open

- Keep the April 18, 2026 PR subset fixed at the evidenced `31` required IDs.
- Implement the remaining nightly AVS IDs next: `DEC/BLK edge cases`, `BR exact scaling`, `MEM endianness/misalignment`, `ATOM`, `FP`, `VEC`, runtime histogram semantics, and SPEC/workload launch semantics.
- Add a dedicated SIMT kernel compile matrix for grouped-lane launch, inner
  control flow, and `.local` scratch usage once the contract pages above are
  frozen.
- Promote AVS matrix status validation as strict maturity artifact:
  - checker: `tools/bringup/check_avs_matrix_status.py`
  - artifact: `docs/bringup/gates/avs_matrix_status_audit.json`

### M3 (4-8 weeks): Emulator/model completeness gates

Status: Started (coverage reporting landed; PR-lane compatibility wrapper restored)

- Keep canonical ISA-vs-QEMU coverage report machine-generated:
  - `tools/bringup/report_qemu_isa_coverage.py`
- Expand `run_model_diff_suite.py` required coverage from scalar/basic to vector/tile + restart/fault scenarios.
- Add SIMT body execution/runtime coverage for:
  - grouped launch mapping,
  - branch-heavy kernels,
  - partial-lane progress,
  - compiler-generated `.local` state.
- Keep unsupported instructions deterministic via explicit illegal traps until implemented.

### M4 (4-10 weeks): Hosted toolchain/runtime workload maturity

Status: Planned (PR compile/artifact lanes green; runtime execution lanes still open)

- Close `SPEC-001..SPEC-007` in `docs/bringup/agent_runs/checklists/specint_qemu.md`.
- Refresh the canonical workload report so the April 11, 2026 PTO parity recovery is reflected in `docs/bringup/gates/latest.json`.
- Keep 9p/virtfs compatibility (`LINUX-003`) as hard prerequisite for SPEC lane.
- Evolve C++ runtime policy beyond current no-EH/no-RTTI baseline once dual-lane evidence is stable.
- Convert ABI/unwind/TLS checklist into executable runtime gates.

### M5 (6-12 weeks): Privileged/MMU/debug parity

Status: Planned

- Close privileged/MMU/debug gaps in `docs/bringup/ISA_GAP_ANALYSIS.md`.
- Add Linux selftests for restartable tile faults and bridged memory ordering.
- Define minimal debug architecture contract (single-step, breakpoints/watchpoints, privilege interactions).

### M6 (ongoing): Performance and release-grade parity

Status: Planned

- Keep benchmark methodology and artifact discipline under `workloads/generated/`.
- Track static/dynamic instruction trends and optimization roadmap closure.
- Expand CI-like orchestration for full-stack, cross-repo reproducibility.

## SIMT-Specific Planning Pages

- Architecture detail plan:
  `docs/architecture/v0.4-simt-compiler-contract-plan.md`
- Compiler maturation plan:
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

These pages refine the `VEC`/SIMT lane of the broader maturity effort. They do
not replace the main maturity plan; they provide the missing depth for the
current LLVM/QEMU/AVS SIMT subset.

## Required Policy Defaults

- No new waivers by default for required strict gates.
- Dual-lane promotion remains required (`pin` + `external`).
- Existing strict green gates remain mandatory while maturity gates are added incrementally.
