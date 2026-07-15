<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/interfaces.md -->

# LinxCore External Interface Contracts

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/interfaces.md`.


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

The current payload is a reduced `N_STID=1` contract. A multi-STID producer
must add canonical `stid` to every commit event and synchronize the JSON
contract, emitter, viewer, comparator, fixtures, and SemVer major. Identical
PC/RID/BID values from different STIDs must never be merged or inferred from
event order.

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
- LinxTrace v1's missing STID and legacy 64-bit `block_bid` container are valid
  only for the current single-STID compatibility lane. Multi-STID and the
  canonical `{stid, BID_W-bit block_bid, block_uid}` identity require a v2
  schema; v1 must not be silently reinterpreted.

## Cross-tool synchronization contract (LC-IF-SYNC-001)

The following must stay synchronized when trace/pipeline contracts change:

- `rtl/LinxCore/src/common/stage_tokens.py`
- `rtl/LinxCore/src/common/interfaces.py`
- `rtl/LinxCore/tb/tb_linxcore_top.cpp`
- `rtl/LinxCore/tools/trace/build_linxtrace_view.py`
- `rtl/LinxCore/tools/linxcoresight/lint_linxtrace.py`
- `rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py`

Viewer-side contract sync is validated through LinxTrace gates.

The canonical stage taxonomy is `F0` control followed by `F1..F4/IB`,
`D1..D3`, `S1..S3`, optional
`P0`, `P1/I1/I2`, per-pipe `E1..En` with `W1..Wn` result overlays, and
`R0..R4`. The current LinxTrace v1 `F0` token is canonical, but its separate
serial `IB/F4` tokens and incomplete `W`/`R` coverage are legacy. Removing or
reordering fields is a breaking trace change and requires a new schema major
plus synchronized producer, linter, viewer, sample, and compatibility
evidence.

## LinxCoreModel simulator contract (LC-IF-MODEL-001)

`LinxISA/LinxCoreModel` is the current executable reference for the most
accurate Janus Core simulation lane. LinxCore changes that alter
architecture-visible execution, direct-boot workload flow, block/engine
completion, BFU recovery, ELF loading, or MMIO finisher behavior must identify
whether LinxCoreModel already implements the intended behavior.

Required model checkout:

- Repository: `https://github.com/LinxISA/LinxCoreModel.git`
- Branch: `main`
- Reviewed commit: `793722e85c62eade9ab4e8481c9577dc5b9c98f7`
- Review date: 2026-07-10

Current build contract from the aligned model:

```bash
cd tools/LinxCoreModel  # from the superproject root
python3 build.py all --target gfsim -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc)"
```

The build helper is the preferred path because it carries the model's current
multi-platform policy:

- CMake minimum is 3.10.
- C++17 requires GCC 8+ or Clang 10+.
- Linux uses the selected system GCC/Clang through `CC` and `CXX`.
- macOS uses Clang and requires Homebrew `libelf`; non-interactive runs may use
  `python3 build.py ... -y` to allow dependency installation.
- `rapidjson` is vendored under `third_party/rapidjson` and should not require
  a host package.

Manual CMake remains legal when the build helper is unsuitable, but it must
preserve the same options and dependency assumptions. Optimized workload
promotion should build `gfsim` with `-DOPT_LEVEL=O3` and
`-DDISABLE_DEBUG_SYMBOLS=ON` when comparing against the AI workload final
target.

## Scope boundary

This document covers **external** LinxCore interface governance only:

- pyCircuit contract
- trace schema contract
- cross-tool synchronization rules
- LinxCoreModel executable-reference build and comparison contract

Detailed LinxCore **microarchitectural** interface contracts (two-layer block machine, BROB-facing resolve,
raw engine fabric, engine/block-type mapping) belong under:

- `rtl/LinxCore/docs/architecture/`
- `docs/architecture/linxcore/microarchitecture.md`

The exact command/response envelope and BID/tag routing live in
`rtl/LinxCore/docs/architecture/block_fabric_contract.md`. Internal ROB/LSU
sidecars such as all-row LSID watermarks, local-register sequences, native
ring RIDs, BROB wrap/age state, and transaction epochs are not automatically
architectural commit fields. BID itself is `BID_W` bits and shared block
interfaces carry STID separately. Promoting any sidecar
into the external trace schema requires the
SemVer and compatibility process above.

The complete canonical stage meanings are captured normatively in
`docs/architecture/linxcore/microarchitecture.md` and
`docs/architecture/linxcore/pipeline-stage-catalog.md`; this document remains
limited to external/tool-facing interface governance.

## Interface change control

- Interface-visible changes must update contract artifacts first.
- Gate rows in `docs/architecture/linxcore/verification-matrix.md` are the release blocker for interface promotion.
- Any contract-major bump must include migration notes and dual-lane evidence.
- LinxCoreModel-visible behavior changes must record the model commit and the
  exact `gfsim` build/run command used for comparison.
