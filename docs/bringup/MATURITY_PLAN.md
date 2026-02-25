# LinxISA Maturity Plan (Tier-1 Track vs ARM/x86)

Last updated: 2026-02-25

## Baseline

- Strict baseline run: `2026-02-25-r2-pin-lanefix` (`2026-02-25 12:41:30Z`)
- Canonical report: `docs/bringup/gates/latest.json`
- Current strict required gates are green across compiler, emulator, kernel, libc, model diff, and regression.

## Gap Snapshot

- Bring-up closure is complete for core strict gates.
- Remaining maturity gap is depth and breadth:
  - AVS breadth (current status file: `13/39` implemented).
  - ISA-vs-QEMU implementation breadth (`311/710` mapped mnemonics; tracked in machine report).
  - SPEC hosted workload closure (`SPEC-*` checklist still open).
  - ABI/unwind/TLS runtime hardening gates (checklist exists; executable gating expansion still pending).
  - Privileged/MMU/debug completeness beyond current release-strict subset.

## Milestones

### M1 (1-2 weeks): Gate hygiene and open non-SPEC checklist closure

Status: In progress (closure artifacts landed in this workspace update)

- Close open non-SPEC checklist IDs:
  - `LLVM-005`
  - `QEMU-003`
  - `QEMU-005`
  - `LINUX-003`
- Keep cross-doc truth aligned:
  - `docs/bringup/gates/latest.json`
  - `docs/bringup/GATE_STATUS.md`
  - `docs/bringup/ALIGNMENT_MATRIX.md`
- Added machine artifacts for this milestone:
  - `docs/bringup/gates/linxisa_virt_defconfig_audit.json`
  - `docs/bringup/gates/qemu_opcode_sync_latest.json`
  - `docs/bringup/gates/qemu_isa_coverage_latest.json`

### M2 (3-6 weeks): AVS core coverage expansion

Status: Planned

- Implement missing core AVS IDs first: `DEC/BLK/BR/MEM/ALU/ATOM`.
- Implement `FP` and `VEC` IDs next.
- Promote AVS matrix status validation as strict maturity artifact:
  - checker: `tools/bringup/check_avs_matrix_status.py`
  - artifact: `docs/bringup/gates/avs_matrix_status_audit.json`

### M3 (4-8 weeks): Emulator/model completeness gates

Status: Started (coverage reporting landed; suite expansion pending)

- Keep canonical ISA-vs-QEMU coverage report machine-generated:
  - `tools/bringup/report_qemu_isa_coverage.py`
- Expand `run_model_diff_suite.py` required coverage from scalar/basic to vector/tile + restart/fault scenarios.
- Keep unsupported instructions deterministic via explicit illegal traps until implemented.

### M4 (4-10 weeks): Hosted toolchain/runtime workload maturity

Status: Planned

- Close `SPEC-001..SPEC-007` in `docs/bringup/agent_runs/checklists/specint_qemu.md`.
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

## Required Policy Defaults

- No new waivers by default for required strict gates.
- Dual-lane promotion remains required (`pin` + `external`).
- Existing strict green gates remain mandatory while maturity gates are added incrementally.

