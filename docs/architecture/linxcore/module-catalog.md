<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/module-catalog.md -->

# LinxCore Module Catalog

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/module-catalog.md`.


This chapter defines the canonical module structure for LinxCore under the live
`v0.57` superscalar contract.

It freezes which module families own architectural behavior, which files are
the canonical owners of those behaviors, and how those modules compose into the
full core. Module ownership here is normative; helper utilities do not replace
stage owners.

## Structural rules (LC-MA-STAGE-001)

- Every architecturally visible stage, queue, block-control owner, and engine
  boundary must have a named module owner.
- Top-level wrappers may compose those owners, export probes, or adapt
  testbench integration, but they must not redefine architectural ownership.
- Connection-only top shells are the target structure for `src/linxcore_top.py`,
  `src/top/top.py`, and `src/top/modules/export_core.py`; stage-local state and
  ownership logic belong in dedicated child modules.
- Shared utility files in `src/common/` may define types, decoders, metadata,
  or helpers; they are not substitutes for stage modules.
- Trace visibility must come from real owner modules or dedicated probe
  modules, not parent-level reconstruction.

## Top-level composition modules

### `src/linxcore_top.py`

- Defines the canonical exported top module name `linxcore_top`.
- Attaches the top-level probe modules used by commit, block, and pipeview
  observability.
- Owns top-level configuration parameters such as memory size and fetch-bundle
  width aliases.

### `src/top/modules/export_core.py`

- Defines `LinxCoreTopExport`, the bring-up/export integration shell.
- Composes backend, memory, probe-export, block-control, LSU, and engine
  adapters.
- Owns the host-fed instruction-buffer path used by lockstep and trace lanes.
- When the IFU source is bypassed in bring-up, it still preserves the same
  downstream stage ownership model seen by decode and trace tooling.

### `src/top/top.py`

- Defines `LinxCoreTop`, the full top-level composition with the explicit IFU
  stage chain.
- Must instantiate I-SIDE
  `I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer` plus B-SIDE
  `B-F0 -> B-F1 -> B-F2 -> B-F3 -> B-F4`.
- Serves as the reference composition for stage-to-stage wiring names.
- Must converge toward a connection-only composition shell as stage-local trace
  and bring-up logic is pushed into dedicated children.

### `src/mem/mem2r1w.py` and `src/mem/byte_mem_2r1w.py`

- Own the canonical memory macro wrappers used by instruction and data paths.
- Preserve the split instruction/data access model used by bring-up and
  trace-validation flows.

## Shared specification and metadata modules

### Configuration and structural metadata

- `src/common/config.py`
- `src/common/params.py`
- `src/common/module_specs.py`
- `src/common/meta_specs.py`

These files define structural parameters, typed interface metadata, and
canonical build-time configuration rules.

### ISA and decode ownership

- `src/common/isa.py`
- `src/common/decode.py`
- `src/common/decode16.py`
- `src/common/decode32.py`
- `src/common/decode48.py`
- `src/common/decode64.py`
- `src/common/decode_f4.py` (implementation filename pending replacement; it
  is not the canonical I-F4 owner)

These files define opcode identity and decode behavior consumed by the
frontend/decode stages.

### Architectural metadata and trace metadata

- `src/common/stage_tokens.py`
- `src/common/types.py`
- `src/common/interfaces.py`
- `src/common/exec_uop.py`
- `src/common/uid_allocator.py`

These files define the stage-token catalog, common signal bundles, uop
metadata, and UID allocation required by the stage, block, and trace contracts.

## Frontend and fetch modules

### `src/bcc/ifu/f0.py`

- Must own I-F0 PC/request capture, line alignment, and
  request/epoch/checkpoint identity allocation.
- Launches decoupled I-SIDE and B-SIDE requests.

### `src/bcc/ifu/f1.py`

- Must own I-F1 parallel ITLB and L1I request/lookup launch for the
  I-F0-selected thread and PC.
- Preserves the architecture-facing per-thread fetch-control model even though
  the current physical I-cache read path is single-ported.

### `src/bcc/ifu/icache.py`

- Owns the I-SIDE L1I cache access module.
- Produces bundle, hit/miss, and refill-facing metadata for downstream stages.

### `src/bcc/ifu/f2.py`

- Must own I-F2 translation/L1I result joining, physical-tag and
  permission validation, ITLB-miss inner flush, and L1I miss/refill dispatch.

### `src/bcc/ifu/ctrl.py`

- Owns IFU request identity, checkpoint, inner-flush, and cancellation control
  shared through explicit decoupled channels.

### `src/bcc/ifu/f3.py`

- Must own I-F3 cache-line capture, byte-stream alignment, and
  cross-line carry.
- Does not determine instruction length or perform predecode.

### `src/top/modules/ib.py`

- Owns `LinxCoreTopIb`, the host-fed form of the Instruction Buffer used by the
  export shell.
- Instruction Buffer is a queue after I-F4 and before D1.

### `src/top/modules/xchk.py`

- Owns the explicit `XCHK` verification/export boundary.
- Keeps cross-check correlation as a named module boundary rather than
  synthesizing it out of anonymous top-level glue.

### `src/top/modules/export_store_drain.py`

- Owns the SCB/D-cache-stub store-drain helper used by the export shell.
- Pulls local store-drain state and helper instances out of
  `export_core.py` so the top shell remains closer to pure composition.

### `src/bcc/ifu/f4.py`

- Must converge on I-F4: determine 2/4/6/8-byte length, complete
  instruction assembly, recognize only BSTART/BSTOP, zero-extend to 64 bits,
  and write Instruction Buffer.
- It may not own branch prediction or full decode.

### B-SIDE predictor owner family

- Owns B-F0 L0/NLP plus history snapshot; B-F1 uBTB/RAS; B-F2 PBTB/BTB+BIM;
  B-F3 short/medium TAGE+IBTB; and B-F4
  static+long-TAGE+IBTB/loop/final arbitration.
- Accepts identity-qualified cancellation and backend training.
- Owns per-STID speculative GHR and exact request-owned B-F0 GHRQ rows; all
  later TAGE lookup/training consumes the immutable B-F0 snapshot.
- B-F1..B-F4 correction of an accepted lower-ranked prediction emits an
  identity-qualified inner flush. The correction proposal only marks recovery
  pending; its returned canonical prune restores GHR, applies the corrected
  conditional delta and removes younger rows before I-F0 restart. B-F4 is the
  final such point. Its record passes through every valid D1 lane, and
  post-B-F4 mismatch uses Dispatch/BRU flush/recover.

### `src/bcc/frontend/`

- Contains auxiliary frontend support modules such as `frontend.py`, `bpu.py`,
  `ftq.py`, `ibuffer.py`, and `ifetch.py`.
- These files may support alternative decomposition or experimentation, but
  they do not supersede the canonical stage owners above.

## Decode, rename, and post-rename dispatch modules

### `src/bcc/ooo/dec1.py`

- Owns `D1`.
- Reads up to four contiguous fixed 64-bit Instruction Buffer entries,
  performs the first full opcode/operand/immediate decode and fault detection,
  recognizes split/fuse shapes, and forms the decode group.
- Computes demand but does not mutate ROB/BROB/rename/IQ state.

### `src/bcc/ooo/dec2.py`

- Owns `D2`.
- Resolves boundary metadata and prepares one coherent resource-admission
  request for D3.

### `src/bcc/ooo/ren.py`

- Owns `D3`.
- Owns atomic resource admission and physical rename.
- Receives the ROB RID, BROB `BID_W`-bit BID, and memory-order identities only
  when the complete group can be accepted, then forms dispatch packets.

### `src/bcc/ooo/s1.py`

- Owns `S1`.
- Captures admitted D3 packets into the speculative IQ write-port buffer.

### `src/bcc/ooo/s2.py`

- Owns `S2`.
- Allocates and writes the selected physical IQ row.

### `src/bcc/ooo/renu.py`

- Owns rename-state support structures used by the renamed dispatch path.
- Supplies rename bookkeeping that must remain consistent with the `D3`
  contract.

### `src/bcc/ooo/pc_buffer.py`

- Owns the PC-buffer metadata store used by branch recovery and legal-BSTART
  checks.

### `src/bcc/ooo/flush_ctrl.py`

- Owns the explicit flush and redirect control boundary.
- Provides the architectural flush owner instead of hiding redirect policy
  inside unrelated modules.
- This redirect shell retains one ROB redirect PC/checkpoint event. It is not
  the recovery-class owner and must not be promoted as a recovery fabric.

### `src/bcc/ooo/recovery_class_merge.py`

- Defines `LinxBccOooRecoveryClassMerge`, the pyCircuit recovery-class owner.
- Retains independent global-flush and global-replay slots per STID plus one
  slot per `(STID, PE)`, with parameterized STID, PE, ROB, BID, RID, and TPC
  dimensions.
- Applies same-STID model `CheckOlder` ordering, exact inner/nuke merge
  transformation, completed-oldest replay rejection, fair STID serialization,
  and an irrevocable cleanup-facing output slot.
- R647 adds a parameterized source cause mask, exact payload-owner index,
  retained provenance per class lane, merged-cause union, and resolution pulses
  for dropped, canceled, or replaced reports. The irrevocable output registers
  request and provenance together.
- Treats the full block BID as owner-supplied identity. It never creates a BID,
  compares BIDs across STIDs, or imports foreign-ISA exception, power, or
  exclusive-monitor behavior.
- R647 proves the same named two-STID/two-PE request and provenance scenario set
  in generated Chisel and pyCircuit RTL. pyCircuit multi-source producer arbitration and registered
  cleanup/ROB integration remain open and are not implied by this class owner.

### `src/bcc/ooo/rob.py`

- Owns the Janus/BCC ROB-facing stage boundary for the stage-mapped path.
- Provides ROB-visible state in the stage decomposition without replacing the
  canonical backend ROB owners.

## Backend orchestration modules

### `src/bcc/backend/backend.py`

- Defines `LinxCoreBackend`, the canonical backend wrapper.
- Delegates the live backend composition to the trace-export-backed core build.

### `src/bcc/backend/decode.py`

- Defines `LinxCoreDecodeStage`.
- Owns backend-local decode packing for the functional pipeline.

### `src/bcc/backend/rename.py`

- Defines `LinxCoreRenameStage` and `LinxCoreCommitRenameStage`.
- Owns rename allocation and commit-side rename release.

### `src/bcc/backend/modules/mapq.py`

- Defines the parameterized `LinxCoreScalarMapQ` state owner.
- Records RID/order-qualified old and new scalar-P mappings, reports exact
  commit matches, prunes younger rows on recovery, and publishes physical-tag
  release masks through registered owner events.
- Is unit-proven but not integrated; `LinxCoreRenameBank` remains responsible
  for SMAP/CMAP until it consumes MapQ allocation, commit, and restore events.

### `src/bcc/backend/dispatch.py`

- Defines `LinxCoreDispatchStage`.
- Owns ROB, IQ, and LSU allocation handoff from decode/rename into the backend
  execution machine.

### `src/bcc/backend/issue.py`

- Defines `LinxCoreIssuePicker`, `LinxCoreIssueStage`, and
  `LinxCoreIqUpdateStage`.
- Owns the S3/IQ resident boundary, optional P0 preselect, P1 final pick, I1 RF
  arbitration, I2 issue-confirm coordination, IQ readiness, and `inflight`
  retention.
- Must keep S3 residency distinct from the S2 write event so a newly written
  row becomes pick-visible only at the defined next boundary.

### `src/bcc/backend/prf.py`

- Defines `LinxCorePrf`.
- Owns physical register-file state and read/write visibility used by issue and
  writeback.

### `src/bcc/backend/lsu.py`

- Defines `LinxCoreLsuStage`.
- Owns backend-side LSU stage behavior and its integration with issue/commit.

### `src/bcc/backend/rob.py`

- Defines ROB stage modules such as `LinxCoreRobCommitReadStage`,
  `LinxCoreRobCtrlStage`, and `LinxCoreRobEntryUpdateStage`.
- Owns precise retirement bookkeeping and ROB-side query/update boundaries.

### `src/bcc/backend/commit.py`

- Defines `LinxCoreCommitHeadStage` and `LinxCoreCommitCtrlStage`.
- Owns R1 retire-window decision, R2 CMT/FLS publication, and ordered
  retire-side control. `backend/rob.py` owns R0 intake; `ooo/flush_ctrl.py`
  owns registered R3 recovery processing and R4 restart publication.
- Commit-head logic is not a W1/W2 result-stage owner.

### `src/bcc/backend/wakeup.py`

- Defines `LinxCoreHeadWaitStage`.
- Owns head-wait and replay-side visibility constraints.
- Producer execution pipes own W1/W2/W3 result state; this module may consume
  wakeup but must not synthesize W stages from ROB/commit state.

### `src/bcc/backend/engine.py`

- Defines `LinxCoreCommitSelectStage` and the canonical backend composition
  helpers.
- Owns commit-side selection, block-state updates, and execution-family
  composition glue.

### `src/bcc/backend/code_template_unit.py`

- Defines `CodeTemplateUnit`.
- Owns template-uop generation and template-side trace identity.

### `src/bcc/backend/modules/`

- Contains focused backend module families such as block-fabric bridging,
  commit-trace export, ROB banking, PC-buffer stages, recovery validation,
  memory-read arbitration, execution-pipe clustering, and store-buffer stages.
- These are canonical submodule owners of backend behavior, not optional debug
  wrappers.
- `exec_pipe_cluster.py` owns the E-stage progression and producer-relative
  W1/W2/W3 result/writeback overlay. The current shorter
  `P1/I1/I2/E1/W1/W2` sequence is a migration gap, not the stage contract.

## Integer and scalar execution modules

### `src/bcc/iex/iex.py`

- Owns the top-level integer-execution composition boundary.

### `src/bcc/iex/iex_alu.py`

- Owns ALU execution behavior.

### `src/bcc/iex/iex_bru.py`

- Owns branch-condition and branch-recovery execution behavior.

### `src/bcc/iex/iex_agu.py`

- Owns address-generation execution behavior for LSU-bound operations.

### `src/bcc/iex/iex_std.py`

- Owns store-data preparation behavior.

### `src/bcc/iex/iex_fsu.py`

- Owns scalar functional/system execution behavior not covered by the other
  integer execution units.

## LSU and memory-ordering modules

### `chisel/.../lsu/ScalarLSU.scala`

- Owns the canonical Chisel scalar LSU boundary, the integrated STQ-to-SCB
  store path, and the active-to-resolved scalar load lifecycle.
- Uses `CoreParams.robEntries` for ROB identity and `ScalarLsuParams` for
  independent STQ, commit-queue, issue, SCB, response-buffer, LIQ, ResolveQ,
  MDB SSIT/command/output/wait-plan/recovery queues, failed-wait timeout, line,
  register-tag, and MapQ sizing.
- Consumes Linx typed flush and block/memory-order sidecars. It deliberately
  defines no ARM architectural state or ordering operations.
- `ScalarLSULoadPath` owns `LoadInflightQueue`, `LoadResolveQueue`, typed
  pruning, reserved transfer credit, source-row clear after accepted
  resolved-record transfer, and `ScalarLSUMDBPath`.
- `ScalarLSUMDBPath` owns conflict detection, finite SSIT and command/fanout
  queues, BMDB report intent, retained multi-row wait plans, live LIQ wait
  mutation, per-row failed-wait timeout/delete feedback, registered store
  wakeup, and retained typed Linx conflict-recovery publication.
- `ScalarLSURecoverySource` connects the retained MDB head through
  `RecoveryEligibilityControl` and `RingFullBidRecoveryBridge`. Non-immediate
  reports wait for the supplied oldest BID/RID watermark, then require an exact
  allocator/ROB full-BID lookup before publishing `FullBidFlushReq`.
- `ROBFullBidLookup` uses native RID indexing and exact
  `(BID,GID,RID,PE,STID,TID)` equality to return the allocator-stamped row
  generation sideband. `RingFullBidRecoveryBridge` validates the echoed key and
  ring projection before constructing `FullBidFlushReq`; any blocker retains
  the MDB report.
- `RecoveryCleanupControl` accepts the arbiter-selected exact-pointer report,
  splits canonical `BID_W` from implementation pointer context, retains one
  cleanup intent, and gates ROB pruning on consumer acceptance. Its raw
  ring compatibility input suppresses BCTRL/BROB and scalar rename cleanup and is not used
  by the canonical MDB source path.
  The real ROB consumer always matches STID and conditionally matches PE/TID
  before pruning, so a recovery cannot remove rows from another Linx scope.
- `RecoverySourceArbiter` implements parameterized retained source slots,
  model-oldest same-STID selection, invalid-STID rejection, and fair
  serialization across incomparable STIDs. R639 proves it in the exact-lookup
  real-ROB harness. R640 connects the production ScalarLSU source owner to that
  arbiter in the same harness and removes LSU-local cleanup selection.
- `RecoveryClassMerge` retains global flush, global replay, and per-PE recovery
  classes per STID, performs same-STID `CheckOlder` cancellation and
  `mergeSignal` transformation, rejects completed-oldest global replay, and
  stages cleanup through an irrevocable output slot.
- `RecoveryFabric` composes
  `RecoverySourceArbiter -> RecoveryClassMerge -> RecoveryCleanupControl` for
  the real-ROB proof path.
- `RecoveryBackendControl` owns the production backend composition around that
  fabric. It routes the scalar-LSU full-BID request/result through the resident
  ROB, appends the LSU source after the parameterized non-LSU source set, and
  emits a ROB flush only when the registered cleanup intent is accepted by all
  participating consumers. It does not fabricate readiness for unwired BCTRL,
  rename, frontend, LSU, or PE cleanup sinks.
- `DecodeRenameROBPath` instantiates `RecoveryBackendControl` around its
  resident `DispatchROBAllocator`/`ROBEntryBank`. It exports the registered
  intent and accepts one explicit all-consumer-ready decision. The full
  fetch/RF/ALU composition connects a retained scalar redirect source and
  consumes external replay-queue cleanup on the accepted intent.
  For global block cleanup it resolves the canonical BID against BROB and
  rebuilds one downstream intent with the resolved pointer before rename or
  queue mutation.
- `ROBRecoveryWatermark` and `BrobMetaTracker` are the per-STID oldest-state
  owners. ROB selects the first non-retired resident row in circular commit
  order and preserves its wrap-qualified RID and full block sideband; BROB
  selects the oldest live full block BID and completion state. The allocator
  exports a coherent recovery watermark only when both full block identities
  match, preventing marker-only and younger scalar generations from being
  paired. Recovery arbitration and class merge consume the explicit valid bit;
  diagnostic BID bits alone never authorize oldest-state special handling.
- `ScalarRedirectRecoverySource` retains one execute/marker redirect, requires
  exact full-BID identity whose ring projection matches the supplied BID,
  publishes once, and holds order/LSID sidecars until matched source resolution.
  Cancellation dominates capture; matched resolution may consume and replace.
  Private sidecars are valid only when the consumed intent names this source as
  its exact payload owner.
- `RecoveryProvenance` carries a parameterized cause mask and exact-payload
  source index beside recovery requests. `RecoveryClassMerge` unions causes on
  merge, preserves the owner of copied payload fields, and resolves dropped or
  canceled causes. `RecoveryCleanupControl` registers the metadata and publishes
  separate final cause-resolution and payload-consumption masks.
- The full fetch/RF/ALU composition currently admits execute redirects only.
  Marker-only redirects restart the frontend but do not request backend
  cleanup because the incremented cleanup ring BID lacks an authoritative
  matching full BID. All backend and replay-queue mutation is qualified by
  `recoveryIntentConsumed`, not producer residency.
- Reduced trace shells use `DecodeRenameROBPath.tieOffRecovery` because they
  expose no authoritative producer. `LinxCoreTop` still uses
  `ReducedCommitROB`; it is not a full recovery integration boundary.
- `RecoveryProducerQueue`, `BccRecoverySource`,
  `IexSlowInsertRecoverySource`, `IexIqStallRecoverySource`, and
  `PeMismatchRecoverySource` retain and type the model-derived non-LSU event
  families. Queue depth and IQ-stall threshold are parameters. Exact full block
  BID is an owner input and is never reconstructed from ring identity.
- `RecoveryNonLsuProducerBank` owns four stable retained source lanes and
  `IexIqStallRecoveryIdentity` derives the watchdog replay pointer as the full
  successor of the selected STID's authoritative BROB commit cursor. It blocks
  absent, completed, and out-of-range STID state before watchdog publication.
- The R642 producer probe composes BCC/IEX/PE adapters through
  `RecoveryFabric`. R646 makes backend control live at the real
  decode/rename/allocator seam and connects the first scalar redirect source
  in the full fetch/RF/ALU composition. R657 appends the producer bank to that
  production backend path without renumbering external lanes. Upstream live
  BCC/IEX/PE event generation and replacement of the reduced MDB producer with
  the complete `ScalarLSU` hierarchy remain open.
  R648 supplies the real per-STID oldest BID/RID/completion inputs required by
  the canonical scalar-LSU adapter. R659 instantiates `ScalarLSUMDBPath` in the
  reduced live composition and deletes the former delivery-only owner. Record,
  wait-plan, and recovery publication now share canonical acceptance;
  report-STID watermark selection, exact ROB full-BID promotion, and central
  source acceptance use `ScalarLSURecoveryBoundary` directly.
- `ScalarLSULoadPath` now owns live scoped IEX load-return publication through
  `ScalarLSULoadReturnQueueBank`, including per-lane launch reservation, scalar
  data extraction, atomic ResolveQ+LRET acceptance, fair drain, typed precise
  pruning, and the parameterized `ScalarLSULoadReturnPipeline` W1/W2 owner.
  The reduced timing top retains its detailed single-pipe sink proof until its
  live ROB/RF/wakeup arbiters consume the canonical outputs. R673 adds the
  cacheable scalar load miss queue and R674 adds bounded dual-ingress refill
  transport beneath this owner. R675 adds one-row sequential cross-line scalar
  execution, per-line forwarding/miss/refill ownership, and one final assembled
  return. R676 adds the canonical parameterized `ScalarL1D` array beneath this
  path and shares its SCB write-side port through `ScalarLSU`. Memory-attribute
  classification, translation/protection, and the complete coherence fabric
  remain outside `ScalarLSU`, so this is not yet a complete LSU.

### `chisel/.../lsu/ScalarL1D.scala`

- Owns the only canonical scalar L1D tag, line-data, write-permission, dirty,
  and LRU state. Set and way counts are independent `ScalarLsuParams` fields.
- Provides one active-phase scalar load lookup and one SCB tag/permission
  lookup. A writable SCB hit applies a full-line byte mask and marks the line
  dirty.
- Installs retained read refills with duplicate-line preservation. Replacement
  is invalid-first then LRU; every valid victim is held on an explicit eviction
  interface until accepted.
- Does not consume Linx recovery identity. Cache state survives typed recovery
  and backend hard restart because it is physical, non-speculative state.
- Does not define ARM memory types, exception levels, exclusives, barriers,
  acquire/release semantics, or any ISA-specific coherence state.

### `chisel/.../lsu/ScalarLSULoadReturnQueue.scala`

- Owns a retained queue per `(STID, return pipe)` and carries PE/STID/TID plus
  BID/GID/RID/load-LSID identity into the registered IEX E4/W1/W2 path.
- Separates STID-local pre-admission credit from exact selected-pipe acceptance
  so pipe selection cannot create a combinational capacity loop.
- Uses round-robin shared-port drain and compacts only entries selected by the
  typed Linx precise-flush contract. Reset/start/restart retain a separate hard
  clear.
- Canonical `ScalarLSULoadPath` reserves exact lane credit at launch and
  replaces the reservation with a resident entry only when ResolveQ accepts the
  same E4 hit. The reduced top currently exposes one shared scalar W1/W2 pipe;
  the canonical owner and queue bank are parameterized and tested with multiple
  lanes.

### `chisel/.../lsu/ScalarLSULoadPath.scala`

- Owns one canonical LIQ-to-ResolveQ lifecycle beneath `ScalarLSU`.
- Shares hard and typed precise flush across active and resolved rows, carries
  PE/STID/TID identity, and requires three free ResolveQ slots for two prior
  registered E3/E4 arrivals plus the newly accepted launch.
- Carries return-pipe identity in each LIQ row, reserves exact lane credit at
  launch, extracts final scalar data at E4, and transfers the hit atomically to
  ResolveQ plus LRET before clearing the exact source LIQ row.
- Generates MDB lookup on accepted scalar allocation, applies accepted MDB wait
  plans and atomic failed-wait releases through the LIQ-native mutation port,
  and includes MDB transient state in quiescence.
- Reserves worst-case miss capacity at launch, transfers every E4 data miss to
  `LoadMissQueue`, and routes exact miss responses back through LIQ refill.
  Miss queue state and reservations participate in quiescence.
- Owns `ScalarL1D`, sources E2 base-line validity only from its lookup or a
  retained LIQ refill, and installs each accepted read refill before LIQ wakeup.
  Duplicate refills use resident cache data so a stale response cannot erase a
  newer committed-store byte update.

### `chisel/.../lsu/LoadMissQueue.scala`

- Owns parameterized cacheable scalar unique-line miss residency beneath
  `ScalarLSULoadPath`.
- Coalesces same-line LIQ dependents, emits one irrevocable FIFO lower-memory
  request, and matches responses by miss slot plus generation and line address.
- Stores complete PE/STID/TID/BID/GID/RID/full-LSID dependent identity so typed
  Linx recovery prunes exact loads. Issued empty entries remain orphaned until
  their response drains; unissued empty entries cancel without traffic.
- Does not implement cache arrays, replacement/coherence, Device/MMIO,
  cache-maintenance, tile memory, or ARM architectural behavior.

### `chisel/.../lsu/LoadRefillTransport.scala`

- Owns parameterized retained serialization between exact miss responses,
  external cache refills, and LIQ line wakeup.
- Accepts both sources in one cycle with deterministic miss-then-external FIFO
  order and uses post-dequeue capacity for independent ready signals.
- Backpressures exact read-response retirement until refill retention is
  guaranteed. Typed recovery holds buffered physical data; hard flush clears
  it. Simultaneous legal ingress is diagnostic, not an error.
- Does not own cache arrays, coherence/replacement, memory classes, Device/MMIO,
  cross-line assembly, or ARM architectural behavior.

### `chisel/.../lsu/ScalarLSULoadReturnPipeline.scala`

- Owns one scoped W1 and W2 slot per configured scalar return pipe. Every slot
  retains PE/STID/TID plus BID/GID/RID/load-LSID, destination, data, and source
  trace metadata.
- Queries exact ROB-row validity before dequeue, holds a missing row, and drops
  a row already marked `NeedFlush` without publishing side effects.
- Completes W2 only when resolve and every required GPR-writeback/wakeup sink
  are simultaneously ready. All fire outputs are one atomic rendezvous and the
  W2 slot clears in that same cycle.
- Applies typed Linx precise recovery independently to W1 and W2 while freezing
  survivor movement during the recovery cycle. It does not import ARM paired
  load, exception-level, exclusive-monitor, barrier, or return-state behavior.

### `chisel/.../top/ScalarLoadCompletionROBBridge.scala`

- Owns the reduced top's single physical ROB-completion arbitration boundary.
  Existing external execute completion has fixed priority; a colliding scalar
  W2 candidate remains resident because its resolve-ready input is withheld.
- Routes the queue-head RID lookup to `ReducedCommitROB` and returns exact
  slot-plus-wrap row-valid evidence to canonical LRET admission.
- Selects scalar completion only on canonical resolve fire, preserves the full
  RID, and requires the ROB to revalidate the resident generation at the
  completion side-effect point. Free/stale identities hold W2. Collision and
  protocol diagnostics remain explicit; same-slot external/scalar candidates
  are duplicate-owner violations, not retryable contention. RF and wakeup
  remain atomic readiness inputs at the scalar-load boundary.

### `chisel/.../execute/ScalarGPRFile.scala`

- Owns parameterized scalar physical GPR data and the non-speculative P-tag
  ready table. The 24 architectural identity tags reset ready; additional
  physical tags reset not-ready.
- Separates write request from write commit. Independent tags may commit on
  different configured ports, while same-tag requests use fixed port priority.
  Duplicate committed writes and clear/write collision are protocol errors.
- Supplies combinational physical-tag reads and the ready mask consumed by
  issue. Both live RF/issue tops instantiate this owner directly; the former
  compatibility wrapper has been removed and remains available only in git
  history.

### `chisel/.../execute/ReducedScalarIssueQueue.scala`

- Is the resident row bank used beneath `ScalarIssueFabric`. It retains renamed
  uops, per-source readiness, and the `inflight` lock until exact release.
- Forms one oldest-ready candidate per represented STID, then round-robins
  across those candidates without comparing unrelated per-STID RIDs.
- Consumes a committed P writeback event from `ScalarGPRFile.write.fire` and
  matches it against every valid, non-issued P source by physical tag. The IQ
  next state and global ready table therefore observe one accepted producer
  event together, matching model `IssueQueue::WakeupIQTag` ordering.
- A request-only or uncommitted write cannot wake an IQ row. A committed P
  wakeup is pick-visible on the next cycle, never in the current selection.
- Publishes resident BRU/Linx redirect and store rows to the fabric without
  surrendering exact row/release ownership.

### `chisel/.../execute/ScalarIssueCandidateArbiter.scala`

- Accepts one candidate per physical bank, suppresses every candidate except
  the oldest RID within each matching STID, and round-robins across surviving
  banks. It never compares RIDs from different STIDs.
- Advances fairness only when the selected read or issue transaction advances.
  Invalid candidate RIDs are protocol errors rather than implicit bank zero.

### `chisel/.../execute/ScalarIssueFabric.scala`

- Partitions total scalar issue capacity evenly across a parameterized
  power-of-two bank count and routes each one-uop enqueue to the least-occupied
  non-full bank with stable lower-bank tie priority.
- Broadcasts committed P wakeup and exact primary/secondary release identities
  to every resident bank while retaining one aggregate compatibility surface
  for the live RF/ALU tops.
- Arbitrates simultaneous bank I1 attempts atomically onto one three-source RF
  read group. A loser clears only its bank-local `inflight` attempt and retries;
  a bank held behind a full I2 does not issue a false cancellation.
- Arbitrates resident I2 outputs separately, preserving oldest-within-STID and
  fair cross-STID selection. Bank occupancy, simultaneous pick, read loss,
  cancellation, and I2 contention are top-visible proof counters.
- Blocks younger same-STID work behind resident BRU/Linx `FRET.STK` control
  frontiers and blocks only younger stores behind the oldest resident store.
  Cross-STID RID comparison remains forbidden.

### `chisel/.../execute/ScalarIssueExternalControlFence.scala`

- Retains the exact `(STID, BID, RID)` of a redirecting scalar control row after
  its resident IQ row releases and until central recovery accepts cleanup.
- Extends the issue control frontier across the Linx marker-restart gap without
  globally clearing unrelated or older IQ/store ownership.

### `chisel/.../top/ScalarLoadGPRCompletionSink.scala`

- Connects canonical scalar W2 completion to `ScalarGPRFile`. Existing external
  writeback uses the first port; scalar W2 uses an independent port when
  configured and when tags differ, otherwise it holds behind external
  priority.
- Presents writeback and P-tag wakeup readiness before completion, but mutates
  data/readiness only from W2 fire. It checks resolve, writeback, and wakeup
  fire coherence and exposes committed-write and wakeup diagnostics.
- Rejects T/U destinations at this GPR boundary. Their local-bank write and
  qtag wakeup remain a separate Linx-specific integration packet.

### `chisel/.../lsu/ScalarLSUMDBPath.scala`

- Owns the canonical scalar memory-dependence predictor beneath
  `ScalarLSULoadPath`.
- Converts active LIQ and ResolveQ rows into one conflict scan, retains every
  unresolved wait target, records the oldest resolved violation, and trains a
  parameterized PC-keyed SSIT through finite command queues.
- Holds atomic LU/SU lookup fanout until live LIQ mutation accepts, registers
  store-ready wakeup, ages each stable predicted-store wait independently,
  atomically clears expired waits while enqueueing SSIT delete feedback, and
  enqueues row-owned Linx `InnerFlush`/`NukeFlush` reports without importing
  ARM architectural ordering behavior. The report remains stable until the
  outer recovery owner accepts it.
- In the reduced live top, MDB lookup credit is part of LIQ allocation
  readiness and the accepted allocation payload is forwarded without
  reconstruction. The canonical owner also supplies conflict diagnostics,
  lookup/delete/record observability, failed-wait feedback, registered store
  wakeup, and the retained recovery report to `ScalarLSURecoveryBoundary`.

### `chisel/.../lsu/LoadWaitStoreTimeout.scala`

- Owns parameterized, saturating per-LIQ-row age for failed MDB-predicted waits.
- Keys age by load generation plus predicted store BID/LSID/PC, serializes
  simultaneous expiries deterministically, and retains expiry until the
  canonical MDB owner accepts both row release and delete enqueue.
- Replaces the model's ineffective shared `oldestPending` ageing enable with a
  deterministic hardware contract; it does not add an ISA-visible timer.

### `src/bcc/lsu/lsu.py`

- Owns the LSU composition boundary.
- Integrates queue, cache-side, store-drain, and memory-dataflow owners.

### `src/bcc/lsu/liq.py`

- Owns the pyCircuit bring-up `LIQ` shell. The canonical concept is the active
  load-inflight window that tracks miss, wait-store, replay, refill, and
  relaunch state; the C++/Chisel owners are `LDQInfo`/`LoadInflightQueue`.

### `src/bcc/lsu/lhq.py`

- Owns the pyCircuit bring-up `LHQ` shell. The canonical resolved-load owner is
  `ResolveQ`/`LoadResolveQueue`, which retains address and byte metadata for
  late older-store conflict detection.

### `src/bcc/lsu/stq.py`

- Owns `STQ`, the speculative store queue.

### `src/bcc/lsu/scb.py`

- Owns `SCB`, the committed-store coalescing buffer.
- Parameterizes row and transaction-ID capacity, coalesces only consecutive
  SIDs on the same cache line, and freezes any row already presented to the
  downstream ready/valid interface.
- Uses one priority-ordered next-state assignment per row field so allocation,
  merge, issue, response, and dequeue updates cannot overwrite one another.

### `src/bcc/lsu/mdb.py`

- Owns the pyCircuit bring-up Memory Disambiguation Buffer boundary.
- The canonical MDB is a PC-keyed store-set/conflict predictor with lookup,
  record, decay/delete, wait-store wakeup, and same-BID versus cross-BID
  recovery classification. It is not a generic miss/data buffer.

### `src/bcc/lsu/l1d.py`

- Owns `L1D`, the data-cache-side interface boundary.

### `src/bcc/lsu/store_pack.py`

- Owns store-payload line packing for the committed-store path.

### `src/bcc/lsu/lsu_store_drain.py`

- Owns the committed-store drain pipeline feeding the D-cache-side path.

### `src/bcc/lsu/dcache_stub.py`

- Owns the functional D-cache stub used by current bring-up flows.

## Block-control modules

### `src/bcc/bctrl/bisq.py`

- Owns `BISQ`, the block-issue queue.

### `src/bcc/bctrl/bctrl.py`

- Owns `BCTRL`, the block command/control routing boundary.

### `src/bcc/bctrl/brenu.py`

- Owns block-side rename and resource metadata handling.

### `src/bcc/bctrl/brob.py`

- Owns `BROB`, including `BID` allocation, block completion, block exception
  capture, and oldest-block retirement gating.

### `chisel/.../bctrl/BIDRingOrder.scala`

- Defines the parameterized per-STID ring-order primitive for canonical BID
  wrap, with the default 256-entry ring producing an 8-bit BID.
- Is unit-proven but not yet consumed by `BrobMetaTracker`; the existing
  64-bit linear BID helper remains a declared promotion blocker, not an
  alternative architecture contract.

### `chisel/.../bctrl/BrobOrderState.scala`

- Owns independent parameterized allocation-tail, commit-head, and bounded
  live-count state per STID.
- Uses `BrobLiveBidResolver` to resolve the external canonical BID slot against
  the selected STID live window. The unique internal pointer defines the same
  metadata suffix: inclusive for miss-predict, successor-of-pivot for
  retained-target nuke/inner/fast flush.
- Supplies commit-head/live-count context so metadata classifies that suffix by
  bounded modular distance, including windows spanning implementation BID
  rollover.
- Resolves only exact resident metadata heads and holds one fair STID-selected
  full-BID retire identity irrevocably until downstream acceptance.
- Shares allocation and retirement admission with ROB/BROB metadata mutation,
  rejects invalid identities and recovery pivots, and has generated Chisel
  proof.

### `chisel/.../bctrl/BrobLiveBidResolver.scala`

- Resolves one canonical `BID_W` slot against a selected STID's bounded
  head/live-count window and returns the unique internal wrap-qualified pointer
  plus its distance from head.
- Rejects zero-match requests, asserts impossible multiple matches, and treats
  migration-era upper BID transport bits as diagnostics rather than age or
  recovery authority.

### `chisel/.../bctrl/BrobNonFlushFrontier.scala`

- Derives one exact consecutive strong-safe prefix per STID from BROB commit
  head, live count, resident full BID, completion, and exception metadata.
- Publishes head plus bounded count as the ordering proof, blocks on holes or
  unsafe rows, and supports implementation-BID rollover without unsigned age
  comparisons.
- Feeds `ReducedStoreCommitFreeOwner`, which retains committed store identity
  until the full block BID enters the prefix. Early branch/tile predicates,
  multi-block retirement, and replay-state mutation remain open.

### `chisel/.../bctrl/BrobStoreRangeState.scala`

- Owns one contiguous block store-range cursor and next store ID per STID,
  separate from scalar decode-time `sid` assignment and non-flush authority.
- Records scalar store counts by exact full BID, accepts explicit counts only
  from authoritative template/tile producers, and advances through consecutive
  count-certain resident rows without unsigned BID comparisons.
- Restores the first killed row's saved start ID on accepted suffix recovery,
  shares allocation/retirement admission with BROB order state, and has
  generated Chisel proof across independent STIDs and rollover.

### `chisel/.../bctrl/BrobStoreCountPublisher.scala`

- Retains scalar closure and explicit CTU/tile count events independently,
  admits exact identities only inside the authoritative per-STID live window,
  and applies accepted suffix recovery to both pending sources.
- Gives same-block explicit counts authority, serializes different-block
  collisions scalar-first, and preserves explicit payload under sink
  backpressure.
- Treats agreeing duplicate counts as idempotent, reports conflicting frozen
  counts as integration errors, and prevents exact-head retirement until count
  certainty reaches the range row.
- Defines a future producer handoff; current reduced top ties the explicit
  source inactive because no canonical Chisel CTU/tile count calculator exists.

### `src/bcc/block_struct/`

- Contains focused block-structure models and tests for ROB/BROB behavior.
- This package supports block-structure validation and must remain consistent
  with the live block-control contract.

## Engine and accelerator modules

### `src/vec/vec.py`

- Owns the `VEC` engine boundary.

### `src/tma/tma.py`

- Owns the current reduced `TMA` Tile Memory Access command, completion, and
  block-identity facade.
- The target architecture splits southbound memory transport into the shared
  CSU/L2 boundary; that owner is not yet promoted in this repository.
- Its present 64-bit BID ports and unsigned numeric flush comparison are
  legacy implementation behavior; convergence must replace them with
  `BID_W` ports and BROB-provided kill context.

### `src/cube/cube.py`

- Owns the `CUBE` engine boundary.

### `src/tau/tau.py`

- Owns the current `TAU` typed tile-to-tile template/tile-operation boundary.

### TEPL owner status

- LinxISA `v0.57` `TEPL` targets the `TAU` typed tile-to-tile
  template/tile-operation boundary through `TileOpcode`.
- Current `src/tau/tau.py` is a reduced fixed-latency shell without promoted
  TileOpcode, descriptor, STID, rejection, or tile-state behavior. BCTRL must
  fail TEPL explicitly until that behavior and its single non-scalar completion
  are integrated; it must not silently route TEPL to the reduced shell.

### FIXP owner status

- LinxISA `v0.57` defines `FIXP` as a non-scalar block type, but this
  repository does not yet have a promoted FIXP execution-owner module.
- BCTRL/BROB must preserve its `{non-scalar}` completion obligation and reject
  unsupported execution explicitly; FIXP must not alias a scalar or unrelated
  engine path.

### `src/tmu/noc/node.py` and `src/tmu/noc/pipe.py`

- Own the TMU NoC transport boundaries.

### `src/tmu/sram/tilereg.py`

- Owns tile-register SRAM state used by tile-oriented engines.

## Observability and export modules

### `src/probes/pipeview_probe.py`

- Owns pipeline-stage observability export.

### `src/probes/block_probe.py`

- Owns block lifecycle observability export.

### `src/probes/commit_probe.py`

- Owns commit-stream observability export.

The observability modules must consume real owner state. They must not invent a
parallel architectural pipeline.
