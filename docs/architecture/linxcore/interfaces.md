# LinxCore External Interface Contracts

## pyCircuit-LinxCore interface contract (LC-IF-PYC-001)

The pyCircuit/LinxCore integration contract is versioned and gate-enforced.

Contract artifacts:

- `docs/bringup/contracts/pyc_linxcore_interface_contract.json`
- `docs/bringup/contracts/pyc_linxcore_interface_contract.md`

Rules:

- Contract version follows `MAJOR.MINOR`.
- Backward-compatible additions increment `MINOR`.
- Breaking field removals/renames or semantic redefinitions increment `MAJOR`.
- Gate tooling rejects unversioned interface breaks.

## Required commit payload contract (LC-IF-PYC-002)

Required commit fields from `pyc_linxcore_interface_contract.json`:

- `cycle`, `pc`, `insn`
- `wb_valid`, `wb_rd`, `wb_data`
- `mem_valid`, `mem_addr`, `mem_wdata`, `mem_rdata`, `mem_size`
- `trap_valid`, `trap_cause`, `next_pc`

Required environment controls:

- `PYC_COMMIT_TRACE`
- `PYC_BOOT_PC`
- `PYC_MEM_BYTES`
- `PYC_MAX_CYCLES`

## LinxTrace schema contract (LC-IF-TRACE-001)

Trace schema governance:

- canonical contract: `docs/bringup/contracts/trace_schema.md`
- producer-side schema validation: `tools/bringup/validate_trace_schema.py`
- SemVer compatibility gate: `tools/bringup/check_trace_semver_compat.py`

Rules:

- `MAJOR` mismatch is a hard failure.
- `MINOR` must be producer >= consumer expectation.
- Breaking trace changes require major bump and migration checks.

## Trace compatibility contract (LC-IF-TRACE-002)

- `linxtrace.v1` remains stable for additive changes.
- Major-version bump is mandatory for incompatible field/semantics changes.
- Compatibility checks must fail fast on major mismatch.

## Cross-tool synchronization contract (LC-IF-SYNC-001)

The following must stay synchronized when trace/pipeline contracts change:

- `rtl/LinxCore/src/common/stage_tokens.py`
- `rtl/LinxCore/tb/tb_linxcore_top.cpp`
- `rtl/LinxCore/tools/trace/build_linxtrace_view.py`
- `rtl/LinxCore/tools/linxcoresight/lint_linxtrace.py`
- `rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py`

Viewer-side contract sync is validated through LinxTrace gates.

## Interface change control

- Interface-visible changes must update contract artifacts first.
- Gate rows in `docs/architecture/linxcore/verification-matrix.md` are the release blocker for interface promotion.
- Any contract-major bump must include migration notes and dual-lane evidence.
