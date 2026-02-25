# LinxISA Bring-up (Public v0.3)

This directory tracks v0.3 architecture/implementation alignment and public bring-up checkpoints.

## Start Here

- Onboarding and workspace setup: `docs/bringup/GETTING_STARTED.md`

## Normative Contract

- Architecture contract: `docs/architecture/v0.3-architecture-contract.md`
- check26 contract file: `docs/bringup/check26_contract.yaml`
- contract gate: `python3 tools/bringup/check26_contract.py --root .`

## Key References

- `docs/bringup/CHECK26_CONTRACT.md`
- `docs/bringup/CPP_BRINGUP_CONTRACT.md`
- `docs/bringup/PROGRESS.md`
- `docs/bringup/gates/latest.json` (canonical machine-readable gate report)
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

Checked-in gate reports under `docs/bringup/gates/` use `${...}` placeholders
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

Multi-agent strict static checklist gate:

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists`

Multi-agent strict runtime closure gate (per lane/run):

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode runtime --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists --report docs/bringup/gates/latest.json --lane pin --run-id <run-id> --out docs/bringup/gates/logs/<run-id>/pin/multi_agent_summary.json`

Release-strict bring-up consistency checks:

- `python3 tools/bringup/check_check26_coverage.py --matrix avs/linx_avs_v1_test_matrix.yaml --contract docs/bringup/check26_contract.yaml --status avs/linx_avs_v1_test_matrix_status.json --profile release-strict`
- `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json`
- `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --report-out docs/bringup/gates/avs_matrix_status_audit.json`
- `python3 tools/bringup/check_qemu_opcode_meta_sync.py --allowlist docs/bringup/qemu_opcode_sync_allowlist.json --report-out docs/bringup/gates/qemu_opcode_sync_latest.json --out-md docs/bringup/gates/qemu_opcode_sync_latest.md`
- `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md`
- `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
- `python3 tools/bringup/check_gate_consistency.py --report docs/bringup/gates/latest.json --progress docs/bringup/PROGRESS.md --gate-status docs/bringup/GATE_STATUS.md --libc-status docs/bringup/libc_status.md --avs-matrix-audit docs/bringup/gates/avs_matrix_status_audit.json --qemu-opcode-sync docs/bringup/gates/qemu_opcode_sync_latest.json --qemu-isa-coverage docs/bringup/gates/qemu_isa_coverage_latest.json --linux-defconfig-audit docs/bringup/gates/linxisa_virt_defconfig_audit.json --require-maturity-artifacts --profile release-strict --lane-policy external+pin-required --trace-schema-version 1.0 --multi-agent-summary docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json --max-age-hours 24`
