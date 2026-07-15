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
| `LC-MA-PIPE-001` | Pipeline | F0 controls thread/PC selection; fetch is `F1..F4/IB`; decode/dispatch is `D1..D3/S1..S3`; E stages are absolute execute cycles; W alignment is declared per producer; precise completion/commit/recovery uses R0..R4 with CMT/FLS at R2 and restart at R4 |
| `LC-MA-RES-001` | Resource admission | Decode groups reserve ROB/BROB, rename, IQ, and memory-order resources atomically or make no state change |
| `LC-MA-ROB-001` | ROB/retirement | Instruction rows allocate in order, commit contiguously, retain cleanup sidecars through deallocation, and recover precisely |
| `LC-MA-HAZ-001` | Hazards/replay | Replay, redirect, wakeup, and issue behavior do not violate correctness |
| `LC-MA-BLK-001` | Block control flow | `BSTART`/`BSTOP`, separate STID plus `BID_W=ceil(log2(BROB_ENTRIES))`, per-STID BROB ring-qualified age/flush, and recovery-to-boundary legality are preserved |
| `LC-MA-PRV-001` | Privilege/traps | ACR service-request entry/return, `BI=1` block-state restore, and SSR-visible side effects are precise |
| `LC-MA-MMU-001` | MMU | Translation and fault behavior are precise and gate-validated |
| `LC-MA-IRQ-001` | Interrupts | Timer IRQ delivery and entry/return behavior are deterministic under strict gates |
| `LC-MA-MEM-001` | Memory ordering | Load/store forwarding, replay, and commit-visible ordering stay legal |
| `LC-MA-ENG-001` | Engine integration | Engine-backed execution remains visible through the lowered block stream and canonical block/BID completion model |
| `LC-MA-FWD-001` | Forward progress | Branch, flush, load-miss, and replay paths preserve progress |
| `LC-MA-STAGE-001` | Stage ownership | Every documented stateful boundary maps to a named `@module` state owner; service contributors and shared per-pipe E/W or R coordinate owners are explicit |
| `LC-IF-PYC-001` | pyCircuit interface versioning | pyCircuit-LinxCore contract follows SemVer with gate-enforced compatibility |
| `LC-IF-PYC-002` | pyCircuit commit payload | Required commit fields and env controls stay compatible with trace tooling |
| `LC-IF-TRACE-001` | Trace schema | LinxTrace schema stays synchronized across producer and consumer tools |
| `LC-IF-TRACE-002` | Trace compatibility | Breaking trace changes require major-version bump and compatibility checks |
| `LC-IF-SYNC-001` | Cross-tool sync | Emitter, linter, and viewer contracts remain synchronized and gate-validated |
| `LC-IF-MODEL-001` | LinxCoreModel reference | LinxCore behavior changes identify the current LinxCoreModel commit, build path, and `gfsim` comparison evidence when the model lane is relevant |

## Gate-to-contract traceability (required PR gates)

| Gate key | Contract IDs covered |
|---|---|
| `LinxCore::microarchitecture contract harness` | `LC-ARCH-DOC-001`, `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001`, `LC-MA-ENG-001`, `LC-MA-FWD-001`, `LC-MA-STAGE-001`, `LC-IF-PYC-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001`, `LC-IF-TRACE-002`, `LC-IF-SYNC-001`, `LC-IF-MODEL-001` |
| `LinxCore::pyCircuit architecture adapter` | `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-MEM-001`, `LC-MA-ENG-001`, `LC-MA-FWD-001` |
| `LinxCore::Chisel architecture adapter` | `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-MEM-001`, `LC-MA-ENG-001`, `LC-MA-FWD-001`, `LC-MA-STAGE-001`, `LC-IF-TRACE-001` |
| `LinxCore::shared microarchitecture conformance` | `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-PRV-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001`, `LC-MA-ENG-001`, `LC-MA-FWD-001` |
| `LinxCore::focused OOO promotion` | `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-FWD-001` |
| `LinxCore::focused LSU promotion` | `LC-MA-MEM-001`, `LC-MA-RES-001`, `LC-MA-HAZ-001`, `LC-MA-FWD-001` |
| `Architecture::LinxCore architecture contract lint` | `LC-ARCH-DOC-001`, `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-BLK-001`, `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001`, `LC-MA-ENG-001`, `LC-MA-FWD-001`, `LC-MA-STAGE-001`, `LC-IF-PYC-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001`, `LC-IF-TRACE-002`, `LC-IF-SYNC-001`, `LC-IF-MODEL-001` |
| `Architecture::mkdocs architecture nav/docs` | `LC-ARCH-DOC-001` |
| `LinxCore::stage/connectivity lint` | `LC-MA-PIPE-001`, `LC-MA-STAGE-001` |
| `LinxCore::opcode parity` | `LC-MA-PIPE-001`, `LC-MA-BLK-001` |
| `LinxCore::runner protocol` | `LC-MA-BLK-001`, `LC-MA-FWD-001`, `LC-MA-IRQ-001` |
| `LinxCore::trace schema and memory smoke` | `LC-MA-HAZ-001`, `LC-MA-MEM-001`, `LC-IF-TRACE-001` |
| `LinxCore::cosim smoke` | `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-IRQ-001`, `LC-MA-MEM-001` |
| `Testbench::ROB bookkeeping` | `LC-MA-PIPE-001`, `LC-MA-RES-001`, `LC-MA-ROB-001`, `LC-MA-HAZ-001`, `LC-MA-FWD-001` |
| `Testbench::block struct pyc flow smoke` | `LC-MA-BLK-001`, `LC-MA-HAZ-001`, `LC-MA-ENG-001` |
| `pyCircuit::CPU C++ smoke` | `LC-IF-PYC-001`, `LC-IF-PYC-002` |
| `pyCircuit::QEMU vs pyCircuit trace diff` | `LC-MA-PRV-001`, `LC-MA-MMU-001`, `LC-MA-MEM-001`, `LC-IF-PYC-002`, `LC-IF-TRACE-001` |
| `pyCircuit::interface contract gate` | `LC-IF-PYC-001`, `LC-IF-PYC-002` |
| `LinxTrace::contract sync lint` | `LC-IF-TRACE-001`, `LC-IF-SYNC-001` |
| `LinxTrace::sample trace lint` | `LC-IF-TRACE-001`, `LC-IF-SYNC-001` |
| `LinxTrace::semver compatibility gate` | `LC-IF-TRACE-002`, `LC-IF-TRACE-001` |
| `LinxCoreModel::gfsim build` | `LC-IF-MODEL-001` |
| `LinxCoreModel::gfsim workload comparison` | `LC-MA-ENG-001`, `LC-MA-FWD-001`, `LC-IF-MODEL-001` |

## PR mandatory matrix

| Domain | Gate Key | Command | Contract intent |
|---|---|---|---|
| LinxCore | `LinxCore::microarchitecture contract harness` | `bash rtl/LinxCore/tests/test_microarchitecture_contract.sh` | one golden definition per contract, explicit dual-RTL ownership, top-shell roles, scenario coverage, and migration-input safety |
| LinxCore | `LinxCore::pyCircuit architecture adapter` | `bash rtl/LinxCore/tests/test_pycircuit_architecture_adapter.sh` | AST-backed top, parameter, state-owner, promotion, known-gap, and rejected-architecture evidence for the pyCircuit lane |
| LinxCore | `LinxCore::Chisel architecture adapter` | `bash rtl/LinxCore/tests/test_chisel_architecture_adapter.sh` | reduced-top role safety, parameter, named-owner, focused-test, known-gap, and rejected-architecture evidence for the Chisel lane |
| LinxCore | `LinxCore::shared microarchitecture conformance` | `bash rtl/LinxCore/tests/test_microarchitecture_conformance.sh` | normalized event schema, shared invariant vectors, architectural commit fields, owner-source mappings, and deterministic cross-lane mismatch detection |
| LinxCore | `LinxCore::focused OOO promotion` | `bash rtl/LinxCore/tests/test_ooo_promotion.sh` | parameterized pyCircuit MapQ allocation/commit/flush and Chisel per-STID BID ring-order wrap semantics |
| LinxCore | `LinxCore::focused LSU promotion` | `bash rtl/LinxCore/tests/test_lsu_promotion.sh` | pyCircuit SCB coalescing, request stability, and completion in C++/Verilator plus focused Chisel forwarding, replay, STQ/SCB, and MDB suites, including unequal physical STQ/ROB/full-LSID widths and typed full-LSID STQ recovery |
| LinxCore | `LinxCore::canonical scalar MDB probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_scalar_lsu_mdb_path_probe.sh` | generated-RTL same/cross-BID typed recovery, SSIT learning/suppression, LU/SU fanout hold, and accepted LIQ wait mutation |
| LinxCore | `LinxCore::cross-RTL MDB transaction` | `bash rtl/LinxCore/tests/test_lsu_mdb_transaction_cross_rtl.sh` | identical named Chisel/pyCircuit scenarios for conflict-sink backpressure, atomic record/recovery publication, and conflict-free bypass; Chisel additionally proves retained report identity, per-STID watermark selection, exact full-BID promotion, and accepted dequeue |
| LinxCore | `LinxCore::MDB recovery to ROB probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_recovery_cleanup_rob_probe.sh` | non-oldest retention, wrong-RID lookup retention, exact allocator-stamped pointer recovery split into canonical `BID_W` plus pointer context, retained multi-source same-STID oldest selection, recovery-fabric class staging, invalid-STID rejection, cross-STID fairness, event-based replacement, accepted block authority, matched cause/payload provenance, and scoped resident ROB prune |
| LinxCore | `LinxCore::recovery class merge probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_recovery_class_merge_probe.sh` | generated-RTL class-lane proof for per-STID global flush/replay, per-PE retention, same-STID cancellation, completed-block replay drop, merge transformation, dropped/canceled cause resolution, merged payload ownership, invalid STID/PE blocking, irrevocable request/provenance stability, and cross-STID serialization |
| LinxCore | `LinxCore::non-LSU recovery producer probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_recovery_producer_probe.sh` | generated-RTL four-lane bank proof for independent BCC/IEX/PE retention, stable lane provenance, exact full-pointer payloads, typed miss/nuke/replay/inner classes, absent-oldest watchdog suppression, `0xffff -> 0` replay-pointer rollover, restart TPC preservation, and accepted drain through the canonical fabric |
| LinxCore | `LinxCore::cross-RTL recovery class merge` | `bash rtl/LinxCore/tests/test_ooo_recovery_class_merge_cross_rtl.sh` | identical named recovery-class scenario set in generated Chisel and pyCircuit RTL, including two STIDs, two PE lanes, cancellation, merge, cause resolution, payload ownership, invalid-scope rejection, blocked-output stability, and full drain |
| LinxCore | `LinxCore::BROB order-state probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_brob_order_state_probe.sh` | generated Chisel proof for independent per-STID allocation/commit/count windows, exact-head completion ordering, irrevocable retire backpressure, fair cross-STID retirement, simultaneous allocate/retire, canonical BID slot resolution, diagnostic-only legacy upper-bit mismatch, modular metadata reuse, exact strong non-flush prefixes across rollover, unsafe-head blocking, and exception exclusion |
| LinxCore | `LinxCore::BROB store-range probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_brob_store_range_state_probe.sh` | generated Chisel proof for independent per-STID contiguous store ranges, unknown-count blocking, authoritative explicit counts, exact suffix recovery/reallocation, and BID/store-ID rollover |
| LinxCore | `LinxCore::BROB store-count publisher probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_brob_store_count_publisher_probe.sh` | generated Chisel proof for live-window admission, retained scalar/explicit sources, same- and different-block collision policy, idempotent/conflicting duplicates, accepted-recovery cancellation, sink backpressure, and count-known head gating |
| LinxCore | `LinxCore::decode memory-ID probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_decode_load_store_id_assign_probe.sh` | generated Chisel proof for independent per-STID LSID/load-ID/store-ID lanes, scoped restore, invalid-STID rejection, and all-lane restart clear |
| LinxCore | `LinxCore::store non-flush gate probe` | `bash rtl/LinxCore/tools/chisel/run_chisel_store_non_flush_gate_probe.sh` | generated Chisel proof that a committed store remains retained outside the strong BROB prefix, releases after prefix advance, and clears on accepted recovery |
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
| LinxCoreModel | `LinxCoreModel::gfsim build` | `cd model/LinxCoreModel && python3 build.py all --target gfsim -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc)"` | current executable-reference build remains available for comparison |

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
| LinxCoreModel | `LinxCoreModel::gfsim workload comparison` | `model/LinxCoreModel/bin/gfsim -f <qemu-passing-linx.elf>` | model-lane comparison for Janus-Core-visible workload behavior |

## Acceptance scenarios

Mandatory scenario families:

- `ACRE`/`ACRC` service requests, ACR transitions, and `BI=0/1` return-state
  restoration
- MMU translation and page or permission fault paths
- timer interrupt delivery and boundary interactions
- branch, block, and recovery legality
- stage taxonomy: F0 owns frontend PC/thread control but is not one of the four
  fetch-data stages, F4 aliases IB and owns final predecode/prediction, decode
  width does not name F4, S3 is IQ visibility, W alignment is declared per
  producer, CMT/FLS publish at R2, and restart state publishes at R4
- atomic decode-group admission failure with no partial RID/BID/rename/store
  allocation
- contiguous ROB commit, delayed deallocation, precise head fault/nuke, and
  ring-qualified BID flush across wrap without unsigned BID comparisons
- default 256-entry BROB per STID with 8-bit BID, separate STID and pointer
  wrap, stale response rejection, and safe `(STID,BID)`-slot reuse
- two STIDs simultaneously using the same BID without response/cleanup alias,
  one-ring flush isolation, independent faulting heads, and fair shared
  issue/completion/retire arbitration
- lossless simultaneous engine responses with hold-until-fire backpressure,
  full trap envelope preservation, and no priority-mux drops
- one-command-per-`(STID,BID)` enforcement, or transaction-ID/count handling
  for multiple same-block commands including duplicate-response rejection
- CTU D3 parent/child reservation, child-before-final-row retirement and trace
  ordering, partial-expansion flush, and adjacent-boundary/BID allocation
- target TEPL-to-TAU and FIXP unsupported paths fail explicitly until their
  execution/completion owners are promoted
- split-store identity, strong non-flush SCB admission, byte-granular
  nearest-older forwarding, response retry, and replay ordering
- MDB same-BID inner recovery versus cross-BID head-taken nuke
- superscalar multi-issue, multi-commit, and flush ordering
- trace schema, contract ID sync, and SemVer policy

## Focused implementation evidence

Focused module gates support review of individual mechanisms but do not replace
the mandatory PR matrix or prove full-core promotion.

| Mechanism | Focused evidence |
|---|---|
| Decode/resource reservation | `FrontendDecodeStage`, `DecodeRenameROBPath`, `DispatchROBAllocator`, `DecodeLoadStoreIdAssign`; current allocation timing must be checked against canonical D1/D2/D3 ownership |
| Scalar and local rename | `GPRRenameCheckpoint`, `ScalarDecodeRenameBridge`, `TULinkRename`, `TULinkRetireCommandPath` |
| ROB/BROB/recovery | `ROBEntryBank`, `ROBRecoveryWatermark`, `ROBFlushPrune`, `ReducedCommitROB`, `BROB`, `BrobLiveBidResolver`, `BrobOrderState`, `FullBidRecoveryBridge`, `ScalarLSURecoveryBoundary`, `ScalarLSURecoverySource`, `ScalarRedirectRecoverySource`, `RecoveryProducerQueue`, `RecoveryNonLsuProducerBank`, `IexIqStallRecoveryIdentity`, `BccRecoverySource`, `IexSlowInsertRecoverySource`, `IexIqStallRecoverySource`, `PeMismatchRecoverySource`, `RecoveryProvenance`, `RecoverySourceArbiter`, `RecoveryClassMerge`, `RecoveryFabric`, `RecoveryBackendControl`, `DecodeRenameROBPath`; verify per-STID circular RID selection, retired-row exclusion, exact ROB/BROB watermark matching, full-pointer watchdog successor selection, `BID_W` cleanup width, separate pointer qualification, canonical BID slot resolution inside the owner head/live-count window, retained producer backpressure, typed event mapping, accepted-intent-only state mutation, cause resolution, matched payload-sidecar authorization, and missing-identity blocking; remaining wide producer/storage pointers are implementation context until migrated |
| IQ/speculative load readiness | `ReducedScalarIssueQueue`, `ReducedScalarIssuePick`, `LoadReplayWakeup` |
| Store/STQ/SCB | `LSIDOrder`, `StoreDispatchSTQPath`, `STQEntryBank`, `STQCommitQueue`, `STQCommitDrain`, `SCBRowBank`, `STQSCBCommitPath`, `ScalarLSU` |
| Load forwarding/replay | `LoadStoreForwarding`, `LoadForwardPipeline`, `LoadInflightQueue`, `LoadMissQueue`, `LoadRefillTransport`, `LoadResolveQueue`, `ScalarLSULoadPath`, `LoadRefillWakeup`; verify exact miss-response retention, dual-ingress FIFO order, post-dequeue refill credit, active-line cross-phase masks, first-phase publication suppression, one final cross-line assembly, stable blocked output, hard clear, and typed-recovery survival |
| Memory disambiguation | `MDBConflictDetect`, `MDBSSIT`, `MDBQueueFanout`, `LoadReplayMdbLookupWaitPlan`, `LoadWaitStoreTimeout`, `ScalarLSUMDBPath`, `ScalarLSURecoveryBoundary`, `ScalarLSURecoverySource`, `RecoveryProvenance`, `RecoverySourceArbiter`, `RecoveryClassMerge`, `RecoveryFabric`, `RecoveryCleanupControl`; verify intent/commit separation, allocation/lookup atomicity from one payload, exactly one integrated conflict/fanout owner, Wait/Repick mutation arbitration, registered store-wakeup delivery and collision hold, retained multi-row waits, generation-keyed timeout restart, atomic wait-clear/delete enqueue, SSIT decay/release, retained typed inner/nuke reports, oldest BID/RID eligibility, exact source promotion, absence of LSU-local cleanup priority, same-STID oldest selection, class cancellation/merge, matched cause/payload provenance, cross-STID fairness, registered ROB-prune acceptance, and flush-cleared transient queues |

For Chisel modules, run the repository wrapper serially, for example
`bash tools/chisel/run_chisel_tests.sh --only <Module>`. A unit pass proves the
named owner in its harness. Full replacement evidence additionally requires
integrated owner visibility and a neutral generated-RTL/QEMU cross-check.

## Matrix maintenance rules

- Every contract-visible behavior in `overview.md`, `microarchitecture.md`, and
  `interfaces.md` must map to at least one gate row here.
- Every required gate used for promotion must appear in this matrix.
- A contract change without a corresponding matrix update is incomplete.
- A gate rename must update this matrix and any checker or publication tooling
  that parses the gate key.
