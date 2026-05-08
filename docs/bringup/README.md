# LinxISA Bring-up (Public v0.56)

This directory tracks `v0.56` architecture and implementation alignment, with AVS as the only live public bring-up contract.

## Start Here

- Onboarding and workspace setup: `docs/bringup/GETTING_STARTED.md`
- Execution-order blocker runbook: `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`

## Normative Contract

- Architecture contract: `docs/architecture/v0.56-architecture-contract.md`
- AVS contract page: `docs/bringup/AVS_CONTRACT.md`
- canonical AVS matrix: `avs/linx_avs_v1_test_matrix.yaml`
- contract gate: `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
- closure gate: `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier ${LINX_GATE_TIER:-pr}`

## Key References

- `docs/bringup/AVS_CONTRACT.md`
- `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`
- `docs/bringup/MATURITY_PLAN.md`
- `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`
- `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
- `docs/bringup/rendering_vulkan_bringup.md`
- `docs/bringup/CPP_BRINGUP_CONTRACT.md`
- `docs/bringup/PROGRESS.md`
- `docs/bringup/gates/latest.json` (canonical machine-readable gate report)
- `docs/bringup/gate_registry.json` (canonical profile/tier gate registry)
- `docs/bringup/GATE_STATUS.md` (generated from gate report JSON)
- `docs/bringup/LINX_ASM_ABI_UNWIND_CONTEXT_CHECKLIST.md`
- `docs/bringup/CROSSSTACK_SKILLS_SUMMARY.md`
- `docs/bringup/agent_runs/manifest.yaml` (machine-readable multi-agent gate ownership map)
- `docs/bringup/agent_runs/waivers.yaml` (tracked explicit waiver ledger)
- `docs/bringup/agent_runs/checklists/` (per-domain execution checklists with stable IDs)
- `docs/reference/linxisa-call-ret-contract.md`
- `docs/bringup/phases/`
- `docs/bringup/contracts/`

## Path Variables in Gate Reports (portable)

Checked-in gate reports under `docs/bringup/gates/` use `${...}` variables
instead of machine-specific absolute paths.

Recommended defaults for an in-tree (pinned) checkout:

- `LINXISA_ROOT` = repo root
- `LLVM_ROOT` = `${LINXISA_ROOT}/compiler/llvm`
- `QEMU_ROOT` = `${LINXISA_ROOT}/emulator/qemu`
- `LINUX_ROOT` = `${LINXISA_ROOT}/kernel/linux`
- `PYCIRCUIT_ROOT` = `${LINXISA_ROOT}/tools/pyCircuit`
- `LINXCORE_ROOT` = `${LINXISA_ROOT}/rtl/LinxCore`
- `GLIBC_ROOT` = `${LINXISA_ROOT}/lib/glibc`
- `MUSL_ROOT` = `${LINXISA_ROOT}/lib/musl`

For the "external" lane, set these variables to point at your external clones/builds
if you intentionally keep toolchains outside the superproject.

Gate status markdown refresh command:

`python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`

Canonical profile/tier runner:

`python3 tools/bringup/run_gates.py --profile release-strict --tier pr`

Compatibility entrypoints:

- `bash tools/regression/run.sh`
- `bash tools/regression/strict_cross_repo.sh`

Use `LINX_GATE_DRY_RUN=1` with either wrapper to inspect the selected gate
commands without running toolchain, emulator, or Linux boot work.

Multi-agent strict static checklist gate:

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists`

Multi-agent strict runtime closure gate (per lane/run):

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode runtime --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists --report docs/bringup/gates/latest.json --lane pin --run-id <run-id> --out docs/bringup/gates/logs/<run-id>/pin/multi_agent_summary.json`

Release-strict bring-up consistency checks:

- `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
- `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json`
- `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --report-out docs/bringup/gates/avs_matrix_status_audit.json`
- `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier ${LINX_GATE_TIER:-pr}`
- `python3 tools/bringup/check_sail_model.py`
- `python3 tools/bringup/check_qemu_opcode_meta_sync.py --allowlist docs/bringup/qemu_opcode_sync_allowlist.json --report-out docs/bringup/gates/qemu_opcode_sync_latest.json --out-md docs/bringup/gates/qemu_opcode_sync_latest.md`
- `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` (mnemonic + per-form closure)
- `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
- `python3 tools/bringup/check_gate_consistency.py --report docs/bringup/gates/latest.json --progress docs/bringup/PROGRESS.md --gate-status docs/bringup/GATE_STATUS.md --libc-status docs/bringup/libc_status.md --avs-matrix-audit docs/bringup/gates/avs_matrix_status_audit.json --qemu-opcode-sync docs/bringup/gates/qemu_opcode_sync_latest.json --qemu-isa-coverage docs/bringup/gates/qemu_isa_coverage_latest.json --linux-defconfig-audit docs/bringup/gates/linxisa_virt_defconfig_audit.json --require-maturity-artifacts --profile release-strict --lane-policy external+pin-required --trace-schema-version 1.0 --multi-agent-summary docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json --max-age-hours 24`
