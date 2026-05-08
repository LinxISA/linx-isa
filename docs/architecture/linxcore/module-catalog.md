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

## Structural rules

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
- Instantiates the IFU modules `F0` through `F4`, the backend, block-control
  path, LSU, memory, and engine adapters.
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
- `src/common/decode_f4.py`

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

- Owns the `F0` boundary.
- Selects the next fetch PC from boot, redirect, or sequential candidates.
- Presents a registered `F0 -> F1` boundary.

### `src/bcc/ifu/f1.py`

- Owns the `F1` boundary.
- Holds I-cache lookup/tag-check control and frontend miss/backpressure
  generation.
- Preserves the architecture-facing per-thread fetch-control model even though
  the current physical I-cache read path is single-ported.

### `src/bcc/ifu/icache.py`

- Owns the fetch-cache access module used by the IFU path.
- Produces bundle, hit/miss, and refill-facing metadata for downstream stages.

### `src/bcc/ifu/f2.py`

- Owns the `F2` boundary.
- Stages raw cache-read data and ECC status before variable-length assembly.

### `src/bcc/ifu/ctrl.py`

- Owns IFU control metadata such as checkpoint flow and flush interaction.
- Coordinates frontend-side control decisions without redefining stage
  ownership.

### `src/bcc/ifu/f3.py`

- Owns the `F3` boundary and the full IFU instruction-buffer ingress behavior.
- Performs variable-length stitch/assembly, static prediction, block-boundary
  annotation, and template-stream control before instruction-buffer delivery.

### `src/top/modules/ib.py`

- Owns `LinxCoreTopIb`, the host-fed instruction-buffer module used by the
  export shell.
- Preserves the same downstream instruction-buffer ownership model when
  QEMU/host injection replaces the native IFU source in bring-up lanes.

### `src/top/modules/xchk.py`

- Owns the explicit `XCHK` verification/export boundary.
- Keeps cross-check correlation as a named module boundary rather than
  synthesizing it out of anonymous top-level glue.

### `src/top/modules/export_store_drain.py`

- Owns the SCB/D-cache-stub store-drain helper used by the export shell.
- Pulls local store-drain state and helper instances out of
  `export_core.py` so the top shell remains closer to pure composition.

### `src/bcc/ifu/f4.py`

- Owns the `F4` boundary.
- Presents the 4-slot decode window used by the architectural decode contract.

### `src/bcc/frontend/`

- Contains auxiliary frontend support modules such as `frontend.py`, `bpu.py`,
  `ftq.py`, `ibuffer.py`, and `ifetch.py`.
- These files may support alternative decomposition or experimentation, but
  they do not supersede the canonical stage owners above.

## Decode, rename, and post-rename dispatch modules

### `src/bcc/ooo/dec1.py`

- Owns `D1`.
- Decodes the `F4` slot window into uop candidates and allocates `RID`, `BID`,
  and `LSID`.

### `src/bcc/ooo/dec2.py`

- Owns `D2`.
- Performs rename request/translation preparation and resolves ROB-visible
  boundary metadata for `BSTART` and `BSTOP`.

### `src/bcc/ooo/ren.py`

- Owns `D3`.
- Maps architectural operands into renamed/tagged operand form and serves as
  the renamed-uop latch boundary.

### `src/bcc/ooo/s1.py`

- Owns `S1`.
- Performs post-rename dispatch preparation, execution-class routing, and ready
  query against the non-spec ready tables.

### `src/bcc/ooo/s2.py`

- Owns `S2`.
- Performs the actual IQ entry write into the selected physical IQ.

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

### `src/bcc/backend/dispatch.py`

- Defines `LinxCoreDispatchStage`.
- Owns ROB, IQ, and LSU allocation handoff from decode/rename into the backend
  execution machine.

### `src/bcc/backend/issue.py`

- Defines `LinxCoreIssuePicker`, `LinxCoreIssueStage`, and
  `LinxCoreIqUpdateStage`.
- Owns IQ readiness, oldest-first pick, `inflight` retention, and issue
  legality.

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
- Owns architectural commit selection and ordered retire-side control.

### `src/bcc/backend/wakeup.py`

- Defines `LinxCoreHeadWaitStage`.
- Owns wakeup, head-wait, and replay-side visibility constraints.

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

### `src/bcc/lsu/lsu.py`

- Owns the LSU composition boundary.
- Integrates queue, cache-side, store-drain, and memory-dataflow owners.

### `src/bcc/lsu/liq.py`

- Owns `LIQ`, the load-issue queue.

### `src/bcc/lsu/lhq.py`

- Owns `LHQ`, the load-hit/load-return queue state.

### `src/bcc/lsu/stq.py`

- Owns `STQ`, the speculative store queue.

### `src/bcc/lsu/scb.py`

- Owns `SCB`, the committed-store coalescing buffer.

### `src/bcc/lsu/mdb.py`

- Owns `MDB`, the miss/data-buffer tracking boundary.

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

### `src/bcc/block_struct/`

- Contains focused block-structure models and tests for ROB/BROB behavior.
- This package supports block-structure validation and must remain consistent
  with the live block-control contract.

## Engine and accelerator modules

### `src/csu/subsystem.py`

- Owns the unified CSU parent subsystem that absorbs IFU refill traffic and
  CSU-internal TMA transport ownership.

### `src/csu/{tma_cmd_frontend,tma_ctx_tracker,tma_l2_client,client_arb}.py`

- Own the CSU-internal TMA command ingress, context tracking, L2-client
  translation, and refill-versus-TMA arbitration boundaries.

### `src/vec/vec.py`

- Owns the `VEC` engine boundary.

### `src/tma/tma.py`

- Remains the standalone compatibility facade for isolated TMA unit tests.
- Janus top-level integration no longer treats it as the normative southbound
  transport owner.

### `src/cube/cube.py`

- Owns the `CUBE` engine boundary.

### `src/tau/tau.py`

- Owns the `TAU` engine boundary.

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
