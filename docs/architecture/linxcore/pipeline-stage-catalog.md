<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md -->

# LinxCore Pipeline Stage Catalog

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`.


This chapter defines the canonical LinxCore stage names, their timing
coordinates, and the behavior owned at each boundary. The names follow the
ARM-reference taxonomy where that taxonomy is ISA-neutral, while the behavior
is rebound to LinxISA block, BID, recovery, and memory contracts.

The catalog is a target contract. Current pyCircuit, Chisel, and LinxTrace
names that disagree with it are legacy implementation aliases and must not be
used to redefine the stage meanings below.

## Stage ownership rules

- Every architecturally visible stateful boundary has one named state owner.
  A service contributor (for example, I-cache or PRF) does not become a second
  owner, and one pipe module may own several separately visible E/W or R
  coordinates. Pure timing coordinates need a named owner family, not a
  one-file-per-cycle implementation.
- A lane count never determines a stage name. In particular, `I-F4` does not mean
  “four-slot decode.”
- `E` and `W` are coordinate systems, not one serial stage chain. `E1..En`
  count absolute execute cycles after `I2`; `W1..Wn` count producer-relative
  actual data-bypass/result/writeback age.
- `CMT` and `FLS` are semantic events published coherently at R2. The physical
  completion/commit/flush/restart pipeline uses `R0..R4`.
- Stage wrappers may adapt interfaces or export probes, but they must not merge
  multiple architectural stages into anonymous glue.

## Canonical pipeline overview

```text
I-SIDE: I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer -> D1 -> D2 -> D3
                                                                      |
                                                                      v
                                                             S1 -> S2 -> S3/IQ
                                                                      |
                                                                      v
                                                             [P0] -> P1 -> I1 -> I2 -> E1 -> E2 -> E3 -> ...
                                                                                        \---- W1/W2/W3 overlay

B-SIDE: B-F0 -> B-F1 -> B-F2 -> B-F3 -> B-F4 -> response/correction

resolve/ROB -> R0 -> R1 -> R2 -> R3 -> R4
                            |               |
                         CMT/FLS       typed restart -> I-F0
```

`P0` is optional unless it is a registered, trace-visible preselect boundary.
All other named stages above are canonical.

## IFU engines

The IFU architecture is defined normatively in `ifu.md`. I-SIDE and B-SIDE
are independently backpressured engines joined only by decoupled,
identity-qualified request, response, cancellation, boundary, and training
channels. I-SIDE uses `I-F0..I-F4`; B-SIDE uses `B-F0..B-F4`. The two
pipelines are not lockstep.

### I-F0

- Owner module: `src/bcc/ifu/f0.py`.
- Is I-SIDE stage 0.
- Captures the selected STID/PC, aligns the cache-line address, and allocates
  request/epoch/checkpoint identity.
- Launches independent I-SIDE and B-SIDE requests through decoupled channels.

### I-F1

- Target owner: `src/bcc/ifu/f1.py` after responsibility convergence.
- Is I-SIDE stage 1.
- Launches ITLB and L1I lookups in parallel for the same I-F0 request.
- Carries request ID, STID, PC, epoch, and checkpoint identity.

### I-F2

- Target state owner: `src/bcc/ifu/f2.py`; `src/bcc/ifu/icache.py` is the cache
  service owner after stage-boundary convergence.
- Is I-SIDE stage 2.
- Joins ITLB and L1I results by request identity and validates translation,
  permission, physical tag, integrity, and hit/miss state.
- An ITLB miss produces an identity-qualified inner flush and translation
  replay for that STID. It is frontend-local and does not flush architectural
  backend state.
- An L1I miss allocates or joins an instruction-refill transaction.

### I-F3

- Target state owner: `src/bcc/ifu/f3.py`.
- Is I-SIDE stage 3.
- Captures one complete L1I cache line, aligns the byte stream from the
  requested PC, and retains/joins cross-line carry.
- Presents ordered bytes to I-F4 without determining instruction length or
  performing predecode.

### I-F4

- Target state owner: `src/bcc/ifu/f4.py` after responsibility convergence.
- Is I-SIDE stage 4.
- Determines 2/4/6/8-byte encoded length, completes instruction assembly,
  zero-extends each instruction to 64 bits, and predecodes only
  `BSTART`/`BSTOP`.
- Writes complete 64-bit instruction records and metadata into the
  Instruction Buffer.
- Does not own branch prediction, general opcode decode, operand decode,
  immediate extraction, split/fuse analysis, or template expansion.
- Holds its output stable under Instruction Buffer backpressure.

### Instruction Buffer

- Owner module: `src/top/modules/ib.py` after interface convergence.
- Is a queue boundary between I-F4 and D1; it is not another name for I-F4.
- Stores a 64-bit instruction payload, PC, encoded length, STID, request ID,
  epoch/checkpoint, BSTART/BSTOP hints, prediction metadata, and fetch fault.
- Presents up to four consecutive same-STID records to D1 and never compacts
  past an invalid, cancelled, faulting, or different-STID entry.

### B-F0

- Owns B-SIDE L0/NLP lookup and GHR/GHRQ/RAS history snapshot.
- Accepts decoupled PC/request/epoch/checkpoint identity from I-F0.

### B-F1

- Owns uBTB and RAS lookup.
- May publish an early identity-qualified target prediction.

### B-F2

- Owns PBTB/BTB and BIM lookup.
- Carries the B-F0 history snapshot rather than resampling live history.

### B-F3

- Owns short/medium-history TAGE providers and IBTB lookup.
- Produces the current direction/target/confidence candidate.

### B-F4

- Runs static prediction from matched I-F4 boundary metadata, owns
  long-history TAGE, final IBTB/loop predictor/loop-buffer results, and final
  provider arbitration.
- Provider rank is `B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`.
- Exact RAS return and high-confidence IBTB indirect target are same-rank B-F4
  target authorities. Direction override order is
  `loop > long-TAGE > short-TAGE > BIM > static`; BTB supplies direct
  targets.
- Backend typed restart is not a provider and has highest restart priority.
- Publishes the retained final prediction response and speculative GHR/GHRQ/
  RAS recovery intent. Live speculative-state updates occur only when the same
  redirect returns as the canonical prune.
- Any B-F1..B-F4 result that corrects an accepted lower-ranked prediction emits an
  identity-qualified inner flush; canonical prune restores the immutable B-F0
  GHR/RAS snapshots, appends the corrected conditional direction or applies the
  corrected Call/Return delta once, kills younger history rows, and restarts
  I-F0 at the corrected PC. B-F4 is the final such
  point.
- B-F4 seals the record carried by every valid D1 lane. Dispatch validates
  direct/call properties, while BRU E1 validates conditional direction and
  indirect/return targets; mismatch enters BRU flush/recover and publishes its
  restart to I-F0.
- Chisel `IfuBackendFeedbackBridge` implements that type-specific comparison
  and atomically publishes actual-result training plus exact-keyed backend
  restart. Dispatch/BRU event production and full-BID ROB/BROB cleanup remain
  production composition owners; the wrapper does not close those paths by
  itself.

## Decode, rename, and dispatch stages

### D1

- Owner family: `src/bcc/ooo/dec1.py`, Chisel
  `frontend/D1InstructionDecodeStage.scala`, and their canonical decode helpers.
- Reads up to `instructionDecodeWidth` contiguous Instruction Buffer entries
  from one STID; supported OOO widths are 2, 4, and 6.
- Receives fixed 64-bit instruction payloads; no byte-window
  reconstruction or neighboring-entry concatenation is allowed.
- Each Chisel lane preserves the final B-F4 prediction sidecar and dynamic
  instruction UID; `FrontendDecodeStage` remains a packet/window verification
  fixture and is not the production D1 composition boundary.
- Performs the first full opcode/operand/immediate decode, detects illegal
  encodings and early exceptions, identifies split/fuse forms, and forms the
  decode group.
- With one BROB allocation port, stops before a second new-block boundary and
  starts a non-leading BSTART/template in the next group.
- May compute resource demand, but does not mutate rename, ROB, BROB, or IQ
  state.

### D2

- Owner family: `src/bcc/ooo/dec2.py`.
- Extracts architectural operands and immediates, resolves Linx boundary
  metadata, and calculates ROB/BROB/rename/IQ/memory-order demand.
- Produces one coherent virtual RID/group and resource-demand plan for D3.
- Marks which single boundary allocates BID and assigns that new BID to the
  boundary plus following rows in slot order.
- Does not claim physical tags or advance architectural ordering pointers.

### D3

- Owner family: `src/bcc/ooo/ren.py` plus the ROB/BROB admission owners.
- Provisionally reserves all required resources or reserves none.
- Allocates at most `BROB_ALLOC_PER_CYCLE` BIDs and stamps boundary ownership in
  decode-slot order; the baseline admits adjacent BSTARTs in separate groups.
- Performs scalar `P` and local `T/U` physical rename, receives grouped
  ROB-owned RID,
  BROB-owned `BID_W`-bit BID, and memory-order identities, and writes the
  corresponding speculative side structures.
- Selects the dispatch route and retains the complete reservation transaction
  until S1 publication.

### S1

- Owner family: `src/bcc/ooo/s1.py`.
- Atomically publishes the grouped ROB members, speculative rename/MapQ state,
  and retained IEX speculative slots.
- Carries execution class, route, readiness seed, exact reservation identity,
  age, and cancellation state until IEX acceptance.

### S2

- Owner family: `src/bcc/ooo/s2.py` and `src/bcc/backend/dispatch.py`.
- Selects a free physical IQ entry and writes the packet plus initial source
  readiness.

### S3 / IQ — resident and pick-visible boundary

- Owner family: `src/bcc/backend/issue.py`.
- Makes the S2-written row valid, resident, wakeable, and eligible for later
  pick.
- Owns source readiness, speculative readiness, age, and `inflight` state.

## Pick and issue stages

### P0 — optional queue-local preselect

- Target state owner when registered: `src/bcc/backend/issue.py`.
- May reduce a large IQ to a smaller candidate set.
- Is named only when implemented as a registered boundary. Combinational
  preselection remains part of P1.

### P1

- Owner module: `src/bcc/backend/issue.py`.
- Selects the oldest ready, non-`inflight` candidate within each STID, then
  arbitrates fairly across eligible STIDs for each shared legal pipe.
- Marks the selected resident row `inflight`; it does not deallocate the row.

### I1

- Owner modules: `src/bcc/backend/issue.py` and `src/bcc/backend/prf.py`.
- Determines which operands require RF access, performs global read-port
  arbitration, and reads physical sources.
- A losing attempt cancels back to resident S3/IQ state.

### I2

- Owner modules: `src/bcc/backend/issue.py` and
  `src/bcc/backend/modules/exec_pipe_cluster.py`.
- Selects the newest legal RF/bypass value, performs final cancellation checks,
  and transfers the uop to its execution pipe.
- A confirmed non-speculative/non-cancellable transfer is the IQ deallocation
  point. A uop with live load-dependence state remains resident and inflight
  until all producer loads resolve hit at E5; miss/replay cancels the pipe copy
  and clears inflight for repick.

## Execute and result coordinates

#### E-stage rules

- `E1` is the first cycle after I2 issue confirmation.
- `E2`, `E3`, and later `E` labels retain absolute position even when a result
  is not yet available.
- Pipe behavior is named explicitly, for example `bru_e1` decision,
  `bru_e2` resolve, `ld_e2` tag lookup, or `ld_e4` data return.

### E1

- Owner modules: `src/bcc/backend/modules/exec_pipe_cluster.py` and
  `src/bcc/iex/iex.py`.
- First absolute execute cycle after I2.

### E2

- Owner modules: `src/bcc/backend/modules/exec_pipe_cluster.py` and the
  `src/bcc/iex/iex_alu.py`/`iex_bru.py` families.
- Second absolute execute cycle; baseline branch resolve is E2.

### E3

- Owner modules: `src/bcc/backend/modules/exec_pipe_cluster.py` and
  `src/bcc/backend/lsu.py`.
- Third absolute execute cycle for longer scalar and memory work.

### E4

- Owner modules: `src/bcc/backend/lsu.py` and `src/bcc/lsu/l1d.py`.
- Baseline load-result cycle and the first load result/writeback age.

### E5 — load resolve

- Owner modules: `src/bcc/backend/lsu.py` and the ROB/LSU completion boundary.
- Publishes stable load hit/miss/fault/replay classification and final
  ROB-visible load resolve after the E4 data/forwarding point.

### E6 — load RF-visible retention

- Target owners: `src/bcc/backend/lsu.py` and `src/bcc/backend/prf.py`.
- Retains a baseline hit result through the load W3/RF-visible age after E5
  resolve. It does not delay the E4/W1 consumer bypass.

#### W-stage rules

- Every pipe declares `{spec_wakeup, data_bypass, rf_write, resolve}` against
  its E and W coordinates. Speculative wakeup is a separate cancellable
  E-stage event that predicts a future W1.
- `W1` is the first age with actual producer data available to the bypass/
  result network.
- `W2` and `W3` are later producer-relative ages. For the baseline integer
  pipe they cover RF write and RF-visible/retained-bypass timing.
- Special pipes may deliver data later or write RF at W4; they must not force
  the baseline scalar convention onto unrelated pipelines.
- Control-only operations without a data result use E-stage resolve names and
  do not invent a W stage.

### W1

- Owner module: `src/bcc/backend/modules/exec_pipe_cluster.py`.
- First actual data-bypass/result age for each result-producing pipe.

### W2

- Owner modules: `src/bcc/backend/modules/exec_pipe_cluster.py` and
  `src/bcc/backend/prf.py`.
- Second result age and baseline RF-write coordinate.

### W3 — RF-visible result age

- Target owners: `src/bcc/backend/modules/exec_pipe_cluster.py` and
  `src/bcc/backend/prf.py`.
- Third result age and baseline RF-visible coordinate. Current implementation
  and LinxTrace tokens do not yet expose this required stage.

Baseline alignment examples:

| Producer | Baseline data result | Next age | RF-visible age |
|---|---|---|---|
| 1-cycle scalar ALU | `E1/W1` | `E2/W2` | `E3/W3` |
| 2-cycle scalar ALU | `E2/W1` | `E3/W2` | `E4/W3` |
| 3-cycle scalar/MAC | `E3/W1` | `E4/W2` | `E5/W3` |
| Baseline load hit | `E4/W1` | `E5/W2` | `E6/W3` |
| Branch/control | decision at `E1` | resolve at `E2` | no W label unless it writes data |

This table defines baseline scalar data-result alignment, not universal
latency. A pipe may wake speculatively at an earlier E stage, use a
later RF-write age such as W4, or change latency only when its declared tuple
and dependency/recovery timing are updated consistently.

## ROB, commit, and recovery stages

### ROB

- Owner modules: `src/bcc/ooo/rob.py`, `src/bcc/backend/rob.py`, and
  `src/bcc/backend/modules/rob_bank.py`.
- Owns precise row state, completion, exception/nuke metadata, and the separate
  commit and deallocation walks.

### R0 — completion and resolve intake

- Target state owner: `src/bcc/backend/rob.py`.
- Captures execute, LSU, block, exception, and replay resolve inputs into
  ROB-visible state.

### R1 — retire-window decision

- Target state owner: `src/bcc/backend/commit.py`.
- Reads the contiguous ROB head window, gathers completion/exception/memory/
  block/cleanup eligibility, and generates the maximal legal in-order commit
  prefix plus any precise trap, interrupt, nuke, or boundary-flush decision.

### R2 — commit and flush publication

- Target state owner: `src/bcc/backend/commit.py`.
- Publishes ordered commit rows (`CMT`) and the coherent `FLS` flush broadcast.
- Advances commit/flush state and launches rename, local-register, LSU, trace,
  and block-last cleanup from one R1 decision snapshot.

### R3 — registered recovery processing

- Target state owner: `src/bcc/ooo/flush_ctrl.py`.
- Consumes the registered recovery/exception classification and performs
  owner-side recovery processing and cleanup.
- Retired rows remain resident until the deallocation contract is satisfied.

### R4 — restart and restored state

- Target state owner: `src/bcc/ooo/flush_ctrl.py`; I-F0 consumes its registered
  restart output.
- Publishes the legal restart PC and restored architectural/frontend state to
  I-F0.
- Completes recovery-visible side effects that require the R2/R3 work. Later
  ROB deallocation is allowed and is not renamed as a W stage.

### CMT

- Owner modules: `src/bcc/backend/commit.py` and
  `src/bcc/backend/modules/commit_slot_step.py`.
- Semantic ordered-commit event published at R2; not a W stage.

### FLS

- Owner modules: `src/bcc/ooo/flush_ctrl.py` and
  `src/bcc/backend/modules/recovery_checks.py`.
- Semantic flush broadcast published coherently with CMT at R2; not a W stage.
  The corresponding restart PC/restored state becomes visible at R4.

## Current implementation-name migration

| Current implementation name | Canonical interpretation |
|---|---|
| `src/bcc/ifu/f0.py` | Target I-F0 owner |
| `src/bcc/ifu/f3.py` internal `ibuffer` | Instruction Buffer implementation contributor |
| `src/bcc/ifu/f4.py`, Chisel `F4DecodeWindow` | Non-conforming implementation names; replace with I-F4 predecode/write and fixed-width D1 decode owners |
| incorrectly ordered frontend trace tokens | Migrate to ordered `I-F4 -> IB -> D1` events |
| commit-head or trace-prep `W1/W2` probes | Incorrect W ownership; move to producer result/writeback state |
| missing `S3`, `E5`, `E6`, `W3`, and `R0..R4` tokens | Trace/implementation promotion gap |

Specifications and new interfaces must use only the canonical meanings above.

### IB

- Owner module: `src/top/modules/ib.py`.
- Canonically IB is the queue after I-F4 and before D1.

### IQ

- Legacy trace owner: `src/bcc/backend/issue.py`.
- Compatibility-only token for the current schema. Canonically the IQ entry
  becomes resident and pick-visible at S3; IQ is the structure, not a serial
  stage before S1 or S2.

## LSU stage family

### LIQ

- Owner module: `src/bcc/lsu/liq.py` (`JanusBccLsuLiq`)
- Design role: bring-up shell for the active load-inflight window. The
  canonical C++/Chisel owners are `LDQInfo`/`LoadInflightQueue`, which retain
  miss, wait-store, replay, refill, and relaunch state.

### LHQ

- Owner module: `src/bcc/lsu/lhq.py` (`JanusBccLsuLhq`)
- Design role: bring-up shell for resolved-load state. The canonical
  C++/Chisel owners are `ResolveQ`/`LoadResolveQueue`, which retain resolved
  address and byte metadata for late ordering-conflict detection.

### STQ

- Owner module: `src/bcc/lsu/stq.py` (`JanusBccLsuStq`)
- Design role: speculative store ordering, forwarding visibility, and flushable
  store state.

### SCB

- Owner module: `src/bcc/lsu/scb.py` (`JanusBccLsuScb`)
- Design role: committed-store coalescing and downstream drain management.

### MDB

- Owner module: `src/bcc/lsu/mdb.py` (`JanusBccLsuMdb`)
- Design role: memory-disambiguation/store-set prediction, recurring-conflict
  learning, wait-store classification, and recovery-candidate publication.
- MDB does not own precise nuke timing; the ROB/recovery owner does.

### L1D

- Adapter owner module: `src/bcc/lsu/l1d.py` (`JanusBccLsuL1D`).
- Golden owner: `chisel/src/main/scala/linxcore/lsu/ScalarL1D.scala`
  (`ScalarL1D`). The reduced pyCircuit module is an adapter, not a second
  architectural definition.
- Design role: parameterized scalar data-cache tag/data/permission owner.
  `ScalarLSULoadPath` supplies the active LIQ phase lookup and retained refill;
  `ScalarLSU` connects SCB write-side lookup and byte update to the same owner.
- Port priority is refill, committed SCB update/lookup, then scalar load LRU
  touch. Refill blocks new array launches until duplicate installation or
  victim eviction is accepted. The E2 lookup result is registered and merged
  with SCB/STQ data in E3.
- `LoadMissQueue` separately owns unique-line lower requests and exact response
  identity. `LoadRefillTransport` separately owns refill retention. The
  lower-memory fabric, coherence acquisition, explicit invalidation, and cache
  maintenance remain separate interfaces.

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

- Owner module: `src/tma/tma.py` (`JanusTma`)
- Design role: reduced Tile Memory Access command/completion facade. The target
  architecture keeps this block-visible frontend but moves southbound memory
  transport to a shared CSU/L2 owner that is not yet promoted here.

### CUBE

- Owner module: `src/cube/cube.py` (`JanusCube`)
- Design role: cube-engine command/response boundary.

### VEC

- Owner module: `src/vec/vec.py` (`LinxCoreVec`)
- Design role: vector-engine command/response boundary.

### TAU

- Owner module: `src/tau/tau.py` (`JanusTau`)
- Design role: typed tile-to-tile template/tile-operation command/response
  boundary; memory access remains tile-to-tile.

### TEPL — target TAU selector

- Target route: BCTRL preserves the architectural selector and dispatches it to
  a promoted `src/tau/tau.py` (`JanusTau`) by `TileOpcode`.
- Design role: preserve TEPL block identity through BCTRL/BROB while TAU owns
  typed tile-to-tile execution and one non-scalar completion. Current TAU is a
  reduced shell, so TEPL remains unsupported until this route is promoted.

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

- Owner module: `src/tma/tma.py` (`JanusTma`)
- Design role: current Tile Memory Access frontend/completion boundary under
  block control. Southbound memory transport converges to the shared CSU/L2
  owner rather than remaining hidden in a peer engine.

### CUBE

- Owner module: `src/cube/cube.py` (`JanusCube`)
- Design role: cube-engine execution boundary under block control.

### VEC

- Owner module: `src/vec/vec.py` (`LinxCoreVec`)
- Design role: programmable SIMT engine boundary under block control.

### TAU

- Owner module: `src/tau/tau.py` (`JanusTau`)
- Design role: typed tile-to-tile template/tile-operation boundary under block
  control.

### TEPL — TAU-selected execution

- Target owner module: `src/tau/tau.py` (`JanusTau`).
- Design role: `TileOpcode`-selected typed tile-to-tile execution. Unsupported
  or not-yet-promoted selector values fail explicitly and never alias another
  engine.
