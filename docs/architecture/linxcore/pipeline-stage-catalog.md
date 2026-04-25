<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md -->

# LinxCore Pipeline Stage Catalog

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`.


This chapter defines the architecturally visible LinxCore stage set and the
module that owns each stage.

The stage names in this document align with the canonical stage-token catalog
in `src/common/stage_tokens.py` and the LinxTrace stage order. If a stage name
is visible in trace, compare tooling, or stage-connectivity checks, it must
remain backed by a real owner module.

## Stage ownership rules

- Every architecturally visible stage is a module.
- A stage may be implemented as a dedicated top-level stage module or as a
  dedicated owner module inside a backend family, but it must retain an
  explicit structural boundary.
- Stage wrappers may adapt interfaces or export probes, but they must not merge
  multiple architectural stages into anonymous glue.
- Bring-up bypass paths may replace the producer of a stage input, but they may
  not delete the stage boundary seen by downstream logic and trace tooling.

## Frontend stages

### F0

- Owner module: `src/bcc/ifu/f0.py` (`JanusBccIfuF0`)
- Design role: PC-select stage that chooses the next fetch PC from multiple
  candidate PCs and presents a registered `F0 -> F1` boundary.

### F1

- Owner module: `src/bcc/ifu/f1.py` (`JanusBccIfuF1`)
- Design role: I-cache lookup stage that owns tag/data lookup control and
  miss/backpressure generation.
- Architectural note: control is per-thread, while the current physical
  implementation arbitrates a single I-cache read port across threads.

### F2

- Owner module: `src/bcc/ifu/f2.py` (`JanusBccIfuF2`)
- Design role: I-cache data staging and ECC-check stage.
- Forwards only ECC-clean raw cache data and thread/PC context toward `F3`.

### F3

- Owner module: `src/bcc/ifu/f3.py` (`JanusBccIfuF3`)
- Design role: variable-length stitch/assembly, static prediction,
  block-boundary annotation, and template recognition/expansion control.

### IB

- Owner modules:
  - full IFU path: `src/bcc/ifu/f3.py`
  - export/bring-up path: `src/top/modules/ib.py` (`LinxCoreTopIb`)
- Design role: per-thread instruction-buffer banks feeding aligned decode
  groups.

### F4

- Owner module: `src/bcc/ifu/f4.py` (`JanusBccIfuF4`)
- Design role: 4-slot decode window generation with continuous per-slot 64-bit
  view from the slot PC.

## Decode and pre-issue stages

### D1

- Owner module: `src/bcc/ooo/dec1.py` (`JanusBccOooDec1`)
- Design role: decode, contiguous-group formation, and `RID/BID/LSID`
  allocation.

### D2

- Owner module: `src/bcc/ooo/dec2.py` (`JanusBccOooDec2`)
- Design role: rename request/translation stage and ROB-visible boundary
  resolution.
- `BSTART` and `BSTOP` become architecturally visible here.

### D3

- Owner module: `src/bcc/ooo/ren.py` (`JanusBccOooRen`)
- Design role: renamed-uop latch point carrying the resolved backend tag form.

### S1

- Owner module: `src/bcc/ooo/s1.py` (`JanusBccOooS1`)
- Design role: post-rename dispatch preparation, execution-class routing, and
  ready-state query.

### S2

- Owner module: `src/bcc/ooo/s2.py` (`JanusBccOooS2`)
- Design role: actual IQ entry write into the selected physical queue.

### IQ

- Owner modules:
  - `src/bcc/backend/dispatch.py` (`LinxCoreDispatchStage`)
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`,
    `LinxCoreIqUpdateStage`, `LinxCoreIssuePicker`)
- Design role: queue allocation, ready tracking, oldest-first pick, and
  `inflight` residency.

## Issue, execution, and wakeup stages

### P1

- Owner modules:
  - `src/bcc/backend/issue.py` (`LinxCoreIssuePicker`, `LinxCoreIssueStage`)
- Design role: IQ pick stage selecting ready, non-`inflight` entries and
  asserting `inflight`.

### I1

- Owner modules:
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`)
  - `src/bcc/backend/prf.py` (`LinxCorePrf`)
- Design role: operand-read planning and RF read-port arbitration.

### I2

- Owner modules:
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`)
  - `src/bcc/backend/modules/exec_pipe_cluster.py` (`LinxCoreBackendExecPipe`)
- Design role: issue-confirm boundary and IQ deallocation point.

### E1

- Owner modules:
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/iex/iex.py` and family modules
  - `src/bcc/backend/lsu.py` for load-spec wakeup entry
- Design role: first execute stage in the promoted baseline slice.

### W1

- Owner modules:
  - `src/bcc/backend/wakeup.py` (`LinxCoreHeadWaitStage`)
  - `src/bcc/backend/commit.py` (`LinxCoreCommitHeadStage`)
- Design role: baseline late wakeup and resolve stage.

## Later execute and memory stages

### E2

- Owner modules:
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/iex/iex_alu.py`, `iex_bru.py`, `iex_agu.py`, `iex_fsu.py`,
    `iex_std.py`
- Design role: later scalar execute stage used by multi-cycle pipelines.

### E3

- Owner modules:
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/backend/lsu.py`
- Design role: later execute stage used by multi-cycle scalar work and LSU
  progression.

### E4

- Owner modules:
  - `src/bcc/backend/lsu.py` (`LinxCoreLsuStage`)
  - `src/bcc/lsu/l1d.py`, `src/bcc/lsu/mdb.py`
- Design role: load-data return visibility, miss detection, and the forwarding
  point used by `E4 -> consumer-I2`.

### W2

- Owner modules:
  - `src/bcc/backend/modules/commit_trace_stage.py`
  - `src/bcc/backend/modules/macro_trace_prep_stage.py`
- Design role: late writeback/trace preparation stage. It must not be
  synthesized from commit-only bookkeeping.

## ROB, commit, and redirect stages

### ROB

- Owner modules:
  - `src/bcc/ooo/rob.py` (`JanusBccOooRob`)
  - `src/bcc/backend/rob.py`
  - `src/bcc/backend/modules/rob_bank.py`
- Design role: precise retirement ordering, completion tracking, and ROB-side
  metadata ownership.

### CMT

- Owner modules:
  - `src/bcc/backend/commit.py`
  - `src/bcc/backend/engine.py` (`LinxCoreCommitSelectStage`)
  - `src/bcc/backend/modules/commit_slot_step.py`
- Design role: ordered architectural commit, block-visible retirement, and
  commit payload generation.

### FLS

- Owner modules:
  - `src/bcc/ooo/flush_ctrl.py`
  - `src/bcc/backend/modules/recovery_checks.py`
- Design role: architectural redirect, replay, and flush ownership.

## LSU stage family

### LIQ

- Owner module: `src/bcc/lsu/liq.py` (`JanusBccLsuLiq`)
- Design role: load-issue queue ordering and eligible-load selection.

### LHQ

- Owner module: `src/bcc/lsu/lhq.py` (`JanusBccLsuLhq`)
- Design role: hit/return tracking for in-flight loads.

### STQ

- Owner module: `src/bcc/lsu/stq.py` (`JanusBccLsuStq`)
- Design role: speculative store ordering, forwarding visibility, and flushable
  store state.

### SCB

- Owner module: `src/bcc/lsu/scb.py` (`JanusBccLsuScb`)
- Design role: committed-store coalescing and downstream drain management.

### MDB

- Owner module: `src/bcc/lsu/mdb.py` (`JanusBccLsuMdb`)
- Design role: miss/data-buffer ownership for load miss handling.

### L1D

- Owner module: `src/bcc/lsu/l1d.py` (`JanusBccLsuL1D`)
- Design role: data-cache-side interface boundary.

## Block-control stages

### BISQ

- Owner module: `src/bcc/bctrl/bisq.py` (`JanusBccBctrlBisq`)
- Design role: block-issue queue ownership and BID-carrying enqueue state.

### BCTRL

- Owner module: `src/bcc/bctrl/bctrl.py` (`JanusBccBctrl`)
- Design role: block command routing, engine command launch, and response path
  coordination.

### TMU

- Owner module: `src/tmu/noc/node.py` (`JanusTmuNocNode`)
- Design role: tile-network issue/response boundary used by block-control
  command transport.

### TMA

- Owner modules:
  - `src/csu/subsystem.py` (`JanusCsuSubsystem`)
  - `src/csu/tma_cmd_frontend.py` (`JanusCsuTmaCmdFrontend`)
  - `src/csu/tma_ctx_tracker.py` (`JanusCsuTmaCtxTracker`)
  - `src/csu/tma_l2_client.py` (`JanusCsuTmaL2Client`)
- Design role: tile-matrix command/response boundary remains block-visible, but
  southbound transport is owned inside the CSU subsystem.

### CUBE

- Owner module: `src/cube/cube.py` (`JanusCube`)
- Design role: cube-engine command/response boundary.

### VEC

- Owner module: `src/vec/vec.py` (`LinxCoreVec`)
- Design role: vector-engine command/response boundary.

### TAU

- Owner module: `src/tau/tau.py` (`JanusTau`)
- Design role: tensor/auxiliary engine command/response boundary.

### BROB

- Owner module: `src/bcc/bctrl/brob.py` (`JanusBccBctrlBrob`)
- Design role: BID allocation, block completion, block exception capture, and
  oldest-block retirement gating.

### XCHK

- Owner module: `src/top/modules/xchk.py` (`LinxCoreXchkStage`)
- Design role: strict cross-check/export correlation boundary used by commit
  verification and LinxTrace annotation.

## Engine stages

### TMU

- Owner modules:
  - `src/tmu/noc/node.py`
  - `src/tmu/noc/pipe.py`
  - `src/tmu/sram/tilereg.py`
- Design role: tile-movement and tile-state transport ownership.

### TMA

- Owner modules:
  - `src/csu/subsystem.py`
  - `src/csu/tma_cmd_frontend.py`
  - `src/csu/tma_ctx_tracker.py`
  - `src/csu/tma_l2_client.py`
- Design role: matrix/tile accelerator execution boundary under block control
  with CSU-owned L2 transport and completion aggregation.

### CUBE

- Owner module: `src/cube/cube.py` (`JanusCube`)
- Design role: cube-engine execution boundary under block control.

### VEC

- Owner module: `src/vec/vec.py` (`LinxCoreVec`)
- Design role: programmable SIMT engine boundary under block control.

### TAU

- Owner module: `src/tau/tau.py` (`JanusTau`)
- Design role: tile-oriented engine boundary under block control.
