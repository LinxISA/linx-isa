# LinxCore v0.4 Verification Matrix

This matrix is the contract that ties architecture intent to strict required gates.

## G1 contract rows (normative)

| Contract ID | Area | Normative statement |
|---|---|---|
| `LC-ARCH-DOC-001` | Architecture docs | LinxCore architecture pages are canonical, linked, and nav-wired in LinxArch docs |
| `LC-MA-PIPE-001` | Pipeline | Stage ownership and precise superscalar retirement are preserved |
| `LC-MA-HAZ-001` | Hazards/replay | Replay/redirect/wakeup behavior does not violate issue legality or correctness |
| `LC-MA-BLK-001` | Block control flow | `BSTART`/`BSTOP` and recovery-to-boundary legality are preserved |
| `LC-MA-PRV-001` | Privilege/traps | U/S trap entry/return and CSR-visible side effects are precise |
| `LC-MA-MMU-001` | MMU | Translation/fault behavior is precise and gate-validated |
| `LC-MA-IRQ-001` | Interrupts | Timer IRQ delivery and entry/return behavior are deterministic under strict gates |
| `LC-MA-MEM-001` | Memory ordering | Load/store forwarding, replay, and commit-visible ordering stay legal |
| `LC-MA-FWD-001` | Forward progress | Branch/flush/load-miss/replay paths preserve progress (no deadlock) |
| `LC-IF-PYC-001` | pyCircuit interface versioning | pyCircuit-LinxCore contract follows SemVer with gate-enforced compatibility |
| `LC-IF-PYC-002` | pyCircuit commit payload | Required commit fields/env controls stay compatible with trace tooling |
| `LC-IF-TRACE-001` | Trace schema | LinxTrace schema contract remains synchronized across producer/consumer tools |
| `LC-IF-TRACE-002` | Trace compatibility | Breaking trace changes require major-version bump and compatibility checks |
| `LC-IF-SYNC-001` | Cross-tool sync | Emitter/linter/viewer contracts remain synchronized and gate-validated |

## Gate-to-contract traceability (required PR gates)

| Gate key | Contract IDs covered |
|---|---|
| `Architecture::LinxCore architecture contract lint` | `LC-ARCH-DOC-001`, `LC-MA-PIPE-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001`, `LC-MA-FWD-001`, `LC-IF-PYC-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001`, `LC-IF-TRACE-002`, `LC-IF-SYNC-001` |
| `Architecture::mkdocs architecture nav/docs` | `LC-ARCH-DOC-001` |
| `LinxCore::stage/connectivity lint` | `LC-MA-PIPE-001` |
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
| Architecture | `Architecture::LinxCore architecture contract lint` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict` | LinxArch pages are present, complete, and cross-linked |
| Architecture | `Architecture::mkdocs architecture nav/docs` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict --require-mkdocs` | Published docs include LinxCore contract pages |
| LinxCore | `LinxCore::stage/connectivity lint` | `bash rtl/LinxCore/tests/test_stage_connectivity.sh` | pipeline naming/connectivity invariants |
| LinxCore | `LinxCore::opcode parity` | `bash rtl/LinxCore/tests/test_opcode_parity.sh` | decode/opcode parity with reference |
| LinxCore | `LinxCore::runner protocol` | `bash rtl/LinxCore/tests/test_runner_protocol.sh` | co-sim protocol safety and mismatch fail-fast |
| LinxCore | `LinxCore::trace schema and memory smoke` | `bash rtl/LinxCore/tests/test_trace_schema_and_mem.sh` | commit/trace schema + memory event presence |
| LinxCore | `LinxCore::cosim smoke` | `bash rtl/LinxCore/tests/test_cosim_smoke.sh` | commit stream alignment with reference entrypoint |
| Testbench | `Testbench::ROB bookkeeping` | `bash rtl/LinxCore/tests/test_rob_bookkeeping.sh` | superscalar retirement ordering invariants |
| Testbench | `Testbench::block struct pyc flow smoke` | `bash rtl/LinxCore/tests/test_block_struct_pyc_flow.sh` | block-structure pyCircuit pipeline integration |
| pyCircuit | `pyCircuit::CPU C++ smoke` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh` | pyCircuit CPU flow functionality |
| pyCircuit | `pyCircuit::QEMU vs pyCircuit trace diff` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh` | architectural trace equivalence |
| pyCircuit | `pyCircuit::interface contract gate` | `python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict` | versioned pyCircuit↔LinxCore interface control |
| LinxTrace | `LinxTrace::contract sync lint` | `python3 rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py` | emitter/linter/viewer pipeline contract sync |
| LinxTrace | `LinxTrace::sample trace lint` | `bash rtl/LinxCore/tests/test_konata_sanity.sh` | trace validity and stage presence |
| LinxTrace | `LinxTrace::semver compatibility gate` | `python3 tools/bringup/check_trace_semver_compat.py --root . --strict` | schema version compatibility policy enforcement |

## PR opt-in extensions

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| SPEC/LinxCore | `SPEC::Stage-A dual-transport + 1K xcheck` | `bash rtl/LinxCore/tests/test_specint_stage_a_xcheck.sh` | Stage-A (`999.specrand_ir`, `505.mcf_r`, `531.deepsjeng_r`) closure across QEMU (`9p` + `initramfs`, `--input-set test`) and 1K commit parity check against LinxCore C++ TB |

## Nightly mandatory extensions

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| LinxCore | `LinxCore::CoreMark crosscheck 1000` | `bash rtl/LinxCore/tests/test_coremark_crosscheck_1000.sh` | long-run architectural convergence |
| LinxCore | `LinxCore::CBSTOP inflation guard` | `bash rtl/LinxCore/tests/test_cbstop_inflation_guard.sh` | block boundary behavior regression guard |
| LinxTrace | `LinxTrace::DFX trace smoke` | `bash rtl/LinxCore/tests/test_konata_dfx_pipeview.sh` | DFX trace path validity |
| LinxTrace | `LinxTrace::template trace smoke` | `bash rtl/LinxCore/tests/test_konata_template_pipeview.sh` | template-flow trace visibility |
| pyCircuit | `pyCircuit::examples regression` | `bash tools/pyCircuit/flows/scripts/run_examples.sh` | flow breadth smoke |
| pyCircuit | `pyCircuit::simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims.sh` | regression simulation lane |
| pyCircuit | `pyCircuit::nightly simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh` | deep nightly flow closure |
| Integration | `Integration::LinxCore performance floor` | `python3 tools/bringup/check_linxcore_perf_floor.py --root . --max-regression 10.0` | <=10% regression cap enforcement |

## Nightly opt-in report lane

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| SPEC/LinxCore | `SPEC::full SPECint 9p + 1K xcheck (report)` | `bash rtl/LinxCore/tests/test_specint_full_xcheck_nightly.sh` | Full `spec_policy.stage_b_required` breadth on QEMU `9p` (`--input-set test`) plus 1K parity reports; report-only mode keeps closure green on benchmark parity mismatches while surfacing `summary.ok=false` |

## Acceptance scenarios

Mandatory scenario families:

- privilege transitions and SRET behavior
- MMU translation and page/permission fault paths
- timer interrupt delivery and boundary interactions
- branch/block legality and precise trap behavior
- load/store forwarding and replay ordering
- superscalar multi-issue/commit/flush ordering
- trace schema, contract ID sync, and SemVer policy
