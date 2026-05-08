<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/verification-matrix.md -->

# LinxCore v0.56 Verification Matrix

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/verification-matrix.md`.


This matrix ties LinxCore architecture intent to strict required gates.

It is the normative mapping between:

- the LinxCore contract pages,
- contract identifiers,
- required validation commands,
- acceptance scenarios used for promotion.

## G1 contract rows (normative)

| Contract ID | Area | Normative statement |
|---|---|---|
| `LC-ARCH-DOC-001` | Architecture docs | Canonical LinxCore docs live in `rtl/LinxCore/docs/architecture`, are mirrored into `docs/architecture/linxcore`, and stay nav-wired in LinxArch docs |
| `LC-MA-PIPE-001` | Pipeline | Stage ownership and precise superscalar retirement are preserved |
| `LC-MA-HAZ-001` | Hazards/replay | Replay, redirect, wakeup, and issue behavior do not violate correctness |
| `LC-MA-BLK-001` | Block control flow | `BSTART`/`BSTOP`, BID, and recovery-to-boundary legality are preserved |
| `LC-MA-PRV-001` | Privilege/traps | U/S trap entry/return and CSR-visible side effects are precise |
| `LC-MA-MMU-001` | MMU | Translation and fault behavior are precise and gate-validated |
| `LC-MA-IRQ-001` | Interrupts | Timer IRQ delivery and entry/return behavior are deterministic under strict gates |
| `LC-MA-MEM-001` | Memory ordering | Load/store forwarding, replay, and commit-visible ordering stay legal |
| `LC-MA-FWD-001` | Forward progress | Branch, flush, load-miss, and replay paths preserve progress |
| `LC-MA-STAGE-001` | Stage ownership | Every documented pipeline stage maps to a dedicated owner file and `@module` boundary |
| `LC-IF-PYC-001` | pyCircuit interface versioning | pyCircuit-LinxCore contract follows SemVer with gate-enforced compatibility |
| `LC-IF-PYC-002` | pyCircuit commit payload | Required commit fields and env controls stay compatible with trace tooling |
| `LC-IF-TRACE-001` | Trace schema | LinxTrace schema stays synchronized across producer and consumer tools |
| `LC-IF-TRACE-002` | Trace compatibility | Breaking trace changes require major-version bump and compatibility checks |
| `LC-IF-SYNC-001` | Cross-tool sync | Emitter, linter, and viewer contracts remain synchronized and gate-validated |

## Gate-to-contract traceability (required PR gates)

| Gate key | Contract IDs covered |
|---|---|
| `Architecture::LinxCore architecture contract lint` | `LC-ARCH-DOC-001`, `LC-MA-PIPE-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001`, `LC-MA-FWD-001`, `LC-MA-STAGE-001`, `LC-IF-PYC-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001`, `LC-IF-TRACE-002`, `LC-IF-SYNC-001` |
| `Architecture::mkdocs architecture nav/docs` | `LC-ARCH-DOC-001` |
| `LinxCore::stage/connectivity lint` | `LC-MA-PIPE-001`, `LC-MA-STAGE-001` |
| `LinxCore::opcode parity` | `LC-MA-PIPE-001`, `LC-MA-BLK-001` |
| `LinxCore::runner protocol` | `LC-MA-BLK-001`, `LC-MA-FWD-001`, `LC-MA-IRQ-001` |
| `LinxCore::trace schema and memory smoke` | `LC-MA-HAZ-001`, `LC-MA-MEM-001`, `LC-IF-TRACE-001` |
| `LinxCore::cosim smoke` | `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001` |
| `Testbench::ROB bookkeeping` | `LC-MA-PIPE-001`, `LC-MA-HAZ-001`, `LC-MA-FWD-001` |
| `Testbench::block struct pyc flow smoke` | `LC-MA-BLK-001`, `LC-MA-HAZ-001` |
| `pyCircuit::CPU C++ smoke` | `LC-IF-PYC-001`, `LC-IF-PYC-002` |
| `pyCircuit::QEMU vs pyCircuit trace diff` | `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-MEM-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001` |
| `pyCircuit::interface contract gate` | `LC-IF-PYC-001`, `LC-IF-PYC-002` |
| `LinxTrace::contract sync lint` | `LC-IF-TRACE-001`, `LC-IF-SYNC-001` |
| `LinxTrace::sample trace lint` | `LC-IF-TRACE-001`, `LC-IF-SYNC-001` |
| `LinxTrace::semver compatibility gate` | `LC-IF-TRACE-002`, `LC-IF-TRACE-001` |

## PR mandatory matrix

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| Architecture | `Architecture::LinxCore architecture contract lint` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict` | canonical submodule docs, mirrors, and cross-links are present and synchronized |
| Architecture | `Architecture::mkdocs architecture nav/docs` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict --require-mkdocs` | published docs include the mirrored LinxCore contract pages |
| LinxCore | `LinxCore::stage/connectivity lint` | `bash rtl/LinxCore/tests/test_stage_connectivity.sh` | pipeline naming, stage-spec ownership, and connectivity invariants |
| LinxCore | `LinxCore::opcode parity` | `bash rtl/LinxCore/tests/test_opcode_parity.sh` | decode and opcode parity with reference |
| LinxCore | `LinxCore::runner protocol` | `bash rtl/LinxCore/tests/test_runner_protocol.sh` | co-sim protocol safety and mismatch fail-fast |
| LinxCore | `LinxCore::trace schema and memory smoke` | `bash rtl/LinxCore/tests/test_trace_schema_and_mem.sh` | commit and trace schema plus memory event presence |
| LinxCore | `LinxCore::cosim smoke` | `bash rtl/LinxCore/tests/test_cosim_smoke.sh` | commit stream alignment with reference entrypoint |
| Testbench | `Testbench::ROB bookkeeping` | `bash rtl/LinxCore/tests/test_rob_bookkeeping.sh` | superscalar retirement ordering invariants |
| Testbench | `Testbench::block struct pyc flow smoke` | `bash rtl/LinxCore/tests/test_block_struct_pyc_flow.sh` | block-structure pyCircuit pipeline integration |
| pyCircuit | `pyCircuit::CPU C++ smoke` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh` | pyCircuit CPU flow functionality |
| pyCircuit | `pyCircuit::QEMU vs pyCircuit trace diff` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh` | architectural trace equivalence |
| pyCircuit | `pyCircuit::interface contract gate` | `python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict` | versioned pyCircuit↔LinxCore interface control |
| LinxTrace | `LinxTrace::contract sync lint` | `python3 rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py` | emitter, linter, and viewer pipeline contract sync |
| LinxTrace | `LinxTrace::sample trace lint` | `bash rtl/LinxCore/tests/test_konata_sanity.sh` | trace validity and stage presence |
| LinxTrace | `LinxTrace::semver compatibility gate` | `python3 tools/bringup/check_trace_semver_compat.py --root . --strict` | schema version compatibility policy enforcement |

## PR opt-in extensions

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| SPEC/LinxCore | `SPEC::Stage-A dual-transport + 1K xcheck` | `bash rtl/LinxCore/tests/test_specint_stage_a_xcheck.sh` | Stage-A closure across QEMU transport lanes and 1K commit parity against LinxCore C++ TB |

## Nightly mandatory extensions

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| LinxCore | `LinxCore::CoreMark crosscheck 1000` | `bash rtl/LinxCore/tests/test_coremark_crosscheck_1000.sh` | long-run architectural convergence |
| LinxCore | `LinxCore::CoreMark crosscheck full` | `bash rtl/LinxCore/tests/test_coremark_crosscheck_full.sh` | full-run architectural convergence with strict source/data correlation |
| LinxCore | `LinxCore::CBSTOP inflation guard` | `bash rtl/LinxCore/tests/test_cbstop_inflation_guard.sh` | block boundary behavior regression guard |
| LinxTrace | `LinxTrace::DFX trace smoke` | `bash rtl/LinxCore/tests/test_konata_dfx_pipeview.sh` | DFX trace path validity |
| LinxTrace | `LinxTrace::template trace smoke` | `bash rtl/LinxCore/tests/test_konata_template_pipeview.sh` | template-flow trace visibility |
| pyCircuit | `pyCircuit::examples regression` | `bash tools/pyCircuit/flows/scripts/run_examples.sh` | flow breadth smoke |
| pyCircuit | `pyCircuit::simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims.sh` | regression simulation lane |
| pyCircuit | `pyCircuit::nightly simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh` | deep nightly flow closure |
| Integration | `Integration::LinxCore performance floor` | `python3 tools/bringup/check_linxcore_perf_floor.py --root . --max-regression 10.0` | <=10% regression cap enforcement |

## Acceptance scenarios

Mandatory scenario families:

- privilege transitions and `SRET` behavior
- MMU translation and page or permission fault paths
- timer interrupt delivery and boundary interactions
- branch, block, and recovery legality
- load/store forwarding and replay ordering
- superscalar multi-issue, multi-commit, and flush ordering
- trace schema, contract ID sync, and SemVer policy

## Matrix maintenance rules

- Every contract-visible behavior in `overview.md`, `microarchitecture.md`, and
  `interfaces.md` must map to at least one gate row here.
- Every required gate used for promotion must appear in this matrix.
- A contract change without a corresponding matrix update is incomplete.
- A gate rename must update this matrix and any checker or publication tooling
  that parses the gate key.
