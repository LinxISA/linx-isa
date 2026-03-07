# pyCircuit ↔ LinxCore Interface Contract

Version: `1.0`

## Scope

This contract controls pyCircuit integration behavior consumed by LinxCore bring-up gates.

Canonical machine-readable file:

- `docs/bringup/contracts/pyc_linxcore_interface_contract.json`

## Compatibility policy

- Contract version format: `MAJOR.MINOR`
- Breaking interface changes require `MAJOR` bump.
- Additive backward-compatible changes require `MINOR` bump.
- Unversioned interface breaks are rejected by gate tooling.

## Required producer paths

- `tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh`
- `tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh`
- `tools/pyCircuit/contrib/linx/flows/tools/linx_trace_diff.py`

## Required commit fields

The required commit trace fields must remain compatible with:

- `tools/bringup/validate_trace_schema.py`
- `tools/pyCircuit/contrib/linx/flows/tools/linx_trace_diff.py`

Current scalar/base required set:

- `cycle`
- `pc`
- `insn`
- `len`
- `next_pc`
- `wb_valid`
- `wb_rd`
- `wb_data`
- `mem_valid`
- `mem_addr`
- `mem_wdata`
- `mem_rdata`
- `mem_size`
- `trap_valid`
- `trap_cause`

Any producer-side changes must update contract version and migration notes.
