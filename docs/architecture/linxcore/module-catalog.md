<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/module-catalog.md -->

# LinxCore Module Catalog

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/module-catalog.md`.


This chapter defines the canonical module structure for LinxCore under the live
`v0.56` superscalar contract.

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
- Instantiates the current IFU implementation modules and must converge them to
  the canonical `F0 -> F1 -> F2 -> F3 -> F4/IB` chain before claiming
  frontend stage ownership.
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
- `src/common/decode_f4.py` (legacy filename for a D1-ingress compatibility
  helper; not an F4 stage owner)

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

- Owns canonical F0 thread arbitration, redirect/next-PC selection, and the
  registered request context handed to F1.
- F0 is frontend control and is not counted as a fifth fetch-data stage.

### `src/bcc/ifu/f1.py`

- Must converge on canonical F1 iTLB/I-cache request/lookup launch for the
  F0-selected thread and PC.
- Preserves the architecture-facing per-thread fetch-control model even though
  the current physical I-cache read path is single-ported.

### `src/bcc/ifu/icache.py`

- Owns the fetch-cache access module used by the IFU path.
- Produces bundle, hit/miss, and refill-facing metadata for downstream stages.

### `src/bcc/ifu/f2.py`

- Current mixed fetch-return/decode-window helper. Its cache-return,
  integrity/ECC-facing work contributes to F2; assembly work belongs to F3.
- Any four-lane window extraction in this module is D1-ingress behavior, not a
  reason to name the module F4.

### `src/bcc/ifu/ctrl.py`

- Owns IFU control metadata such as checkpoint flow and flush interaction.
- Coordinates frontend-side control decisions without redefining stage
  ownership.

### `src/bcc/ifu/f3.py`

- Contributes variable-length assembly, cross-line carry, and byte-stream
  ordering to F3. Its prediction, boundary-predecode, and template-ordering
  logic must converge under F4/IB ownership.
- Its internal instruction-buffer instance is target F4/IB state and must be
  separated from F3 combinational ownership in the final stage mapping.

### `src/top/modules/ib.py`

- Owns `LinxCoreTopIb`, the host-fed form of canonical F4/IB used by the export
  shell.
- `IB` aliases F4; host injection must not create a serial `IB -> F4` stage.

### `src/top/modules/xchk.py`

- Owns the explicit `XCHK` verification/export boundary.
- Keeps cross-check correlation as a named module boundary rather than
  synthesizing it out of anonymous top-level glue.

### `src/top/modules/export_store_drain.py`

- Owns the SCB/D-cache-stub store-drain helper used by the export shell.
- Pulls local store-drain state and helper instances out of
  `export_core.py` so the top shell remains closer to pure composition.

### `src/bcc/ifu/f4.py`

- Legacy-misnamed register/window slicer. Its continuous-view extraction is a
  D1 ingress helper; it is not the canonical F4 stage.
- New code must not extend the `F4DecodeWindow` naming. The target F4 owner is
  the instruction-buffer state described above.

### `src/bcc/frontend/`

- Contains auxiliary frontend support modules such as `frontend.py`, `bpu.py`,
  `ftq.py`, `ibuffer.py`, and `ifetch.py`.
- These files may support alternative decomposition or experimentation, but
  they do not supersede the canonical stage owners above.

## Decode, rename, and post-rename dispatch modules

### `src/bcc/ooo/dec1.py`

- Owns `D1`.
- Reads contiguous F4/IB entries, performs early decode/fault detection,
  recognizes split/fuse shapes, and forms the decode group.
- Computes demand but does not mutate ROB/BROB/rename/IQ state.

### `src/bcc/ooo/dec2.py`

- Owns `D2`.
- Extracts operands/immediates, resolves boundary metadata, and prepares one
  coherent resource-admission request for D3.

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
  MDB SSIT/command/output/wait-plan, line, register-tag, and MapQ sizing.
- Consumes Linx typed flush and block/memory-order sidecars. It deliberately
  defines no ARM architectural state or ordering operations.
- `ScalarLSULoadPath` owns `LoadInflightQueue`, `LoadResolveQueue`, typed
  pruning, reserved transfer credit, source-row clear after accepted
  resolved-record transfer, and `ScalarLSUMDBPath`.
- `ScalarLSUMDBPath` owns conflict detection, finite SSIT and command/fanout
  queues, BMDB report intent, retained multi-row wait plans, live LIQ wait
  mutation, registered store wakeup, and typed Linx conflict-flush publication.
- Cache/miss queues, failed-wait delete timing, final recovery arbitration, and
  IEX load-return publication are not yet children of this boundary; this must
  not be reported as a complete integrated LSU.

### `chisel/.../lsu/ScalarLSULoadPath.scala`

- Owns one canonical LIQ-to-ResolveQ lifecycle beneath `ScalarLSU`.
- Shares hard and typed precise flush across active and resolved rows, carries
  PE/STID/TID identity, and requires three free ResolveQ slots for two prior
  registered E3/E4 arrivals plus the newly accepted launch.
- Transfers the E4 hit record with row-owned thread sidecars and clears the
  exact source LIQ row after queue acceptance.
- Generates MDB lookup on accepted scalar allocation, applies accepted MDB wait
  plans through the LIQ-native mutation port, and includes MDB transient state
  in quiescence.

### `chisel/.../lsu/ScalarLSUMDBPath.scala`

- Owns the canonical scalar memory-dependence predictor beneath
  `ScalarLSULoadPath`.
- Converts active LIQ and ResolveQ rows into one conflict scan, retains every
  unresolved wait target, records the oldest resolved violation, and trains a
  parameterized PC-keyed SSIT through finite command queues.
- Holds atomic LU/SU lookup fanout until live LIQ mutation accepts, registers
  store-ready wakeup, and emits row-owned Linx `InnerFlush`/`NukeFlush`
  requests without importing ARM architectural ordering behavior.

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

- LinxISA `v0.56` `TEPL` targets the `TAU` typed tile-to-tile
  template/tile-operation boundary through `TileOpcode`.
- Current `src/tau/tau.py` is a reduced fixed-latency shell without promoted
  TileOpcode, descriptor, STID, rejection, or tile-state behavior. BCTRL must
  fail TEPL explicitly until that behavior and its single non-scalar completion
  are integrated; it must not silently route TEPL to the reduced shell.

### FIXP owner status

- LinxISA `v0.56` defines `FIXP` as a non-scalar block type, but this
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
