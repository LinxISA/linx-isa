<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md -->

# LinxCore Pipeline Stage Catalog

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`.


This chapter defines the canonical LinxCore stage names, their timing
coordinates, and the behavior owned at each boundary. I-SIDE uses
`I-F0..I-F4`; B-SIDE uses `B-F0..B-F4`. The pipelines are independently
backpressured and do not advance in lockstep.

The normative IFU decomposition and interface payloads are defined in
[`ifu.md`](./ifu.md).

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
I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer -> D1 -> D2 -> D3
                                                              |
                                                              v
                                                     S1 -> S2 -> S3/IQ
                                                              |
                                                              v
                                                     [P0] -> P1 -> I1 -> I2
                                                                       |
                                                                       v
                                                              E1 -> E2 -> E3 -> ...
                                                               \---- W1/W2/W3 overlay

resolve/ROB -> R0 -> R1 -> R2 -> R3 -> R4
                            |               |
                         CMT/FLS       restart -> I-F0
```

`P0` is optional unless it is a registered, trace-visible preselect boundary.
All other named stages above are canonical.

## IFU organization

The IFU contains decoupled I-SIDE and B-SIDE engines. I-SIDE owns I-F0..I-F4,
translation, L1I, predecode, and Instruction Buffer production. B-SIDE owns
B-F0..B-F4, BTB/uBTB/PBTB, GHR/GHRQ, TAGE, BIM, RAS, IBTB,
loop predictor/buffer, and prediction checkpoints. The engines communicate through
explicit request, prediction, training, and redirect channels correlated by
request ID, STID, PC, and epoch.

## I-SIDE stages

### I-F0

- Accepts/selects a PC and allocates request/STID/epoch identity.
- Launches a registered request context toward I-F1.
- Is literally stage zero.

### I-F1

- Launches ITLB and L1I access in parallel for the same PC and request.
- Carries fetch-packet and checkpoint identity.

### I-F2

- Joins ITLB and L1I lookup state.
- Generates an I-SIDE inner flush on ITLB miss and suppresses stale L1I
  responses for the affected STID/epoch.
- Retains L1I miss/refill identity and matching thread/PC context.
- Physical port arbitration may be parameterized; it must not collapse
  per-thread architectural state.

### I-F3

- Captures one cacheline, integrity/ECC and refill state, byte cursor, and
  cross-line carry context.
- Presents ordered cacheline bytes and carry state to I-F4.
- Does not perform full instruction decode or branch prediction.

### I-F4

- Is literally stage four and is distinct from the Instruction Buffer it
  writes.
- Parses 2/4/6/8-byte lengths, assembles complete instructions, zero-extends
  every instruction into a 64-bit container, and recognizes only
  `BSTART`/`BSTOP`-class boundaries.
- Does not perform full opcode, operand, immediate, branch-kind, target, or
  template decode.
- Writes program-order `insn64` entries and metadata into the Instruction
  Buffer.

### Instruction Buffer

- Is a per-STID queue after I-F4 and before D1.
- Stores PC, original byte length, fixed `insn64`, boundary bits,
  request/checkpoint identity, fetch-fault state, and correlated B-SIDE
  prediction metadata.
- Presents up to four contiguous entries to D1 each cycle.
- Applies backpressure to I-F4 and prunes entries by STID/epoch on redirect or
  I-SIDE inner flush.

### B-F0

- Runs L0/NLP next-line prediction.
- Allocates the speculative prediction checkpoint and snapshots GHR/GHRQ.

### B-F1

- Looks up uBTB target/type information.
- Performs speculative RAS push/pop/read.

### B-F2

- Looks up PBTB/BTB target/type information.
- Produces the BIM base direction prediction.

### B-F3

- Looks up short- and medium-history TAGE providers.
- Launches IBTB indirect-target lookup.

### B-F4

- Collects long-history TAGE, IBTB, and loop predictor/buffer results.
- Performs final prediction arbitration.
- Applies provider rank
  `B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`.
- Within B-F4, exact RAS return or high-confidence IBTB wins the matching
  target; direction rank is `loop > long-TAGE > short-TAGE > BIM`, and BTB
  supplies direct targets.

Backend restart has priority above every provider but is a typed-recovery
source, not a prediction provider. A later B-stage correction that has already
driven fetch inner-flushes I-SIDE and restarts I-F0. A backend-resolved
misprediction enters typed recovery and also publishes the frontend restart.
B-SIDE does not own ITLB, L1I, refill, predecode, or Instruction Buffer.

## Decode, rename, and dispatch stages

### D1

- Owner family: `src/bcc/ooo/dec1.py` and the canonical decode helpers.
- Reads up to four contiguous 64-bit Instruction Buffer entries in program
  order.
- Performs full opcode/operand/immediate decode, detects illegal encodings and
  early exceptions, identifies split/fuse forms, and forms the decode group.
- With one BROB allocation port, stops before a second new-block boundary and
  starts a non-leading BSTART/template in the next group.
- May compute resource demand, but does not mutate rename, ROB, BROB, or IQ
  state.

### D2

- Owner family: `src/bcc/ooo/dec2.py`.
- Extracts architectural operands and immediates, resolves Linx boundary
  metadata, and calculates ROB/BROB/rename/IQ/memory-order demand.
- Produces one coherent admission request for the D3 group.
- Marks which single boundary allocates BID and assigns that new BID to the
  boundary plus following rows in slot order.
- Does not claim physical tags or advance architectural ordering pointers.

### D3

- Owner family: `src/bcc/ooo/ren.py` plus the ROB/BROB admission owners.
- Atomically accepts all required resources or accepts none.
- Allocates at most `BROB_ALLOC_PER_CYCLE` BIDs and stamps boundary ownership in
  decode-slot order; the baseline admits adjacent BSTARTs in separate groups.
- Performs scalar `P` and local `T/U` physical rename, receives ROB-owned RID,
  BROB-owned `BID_W`-bit BID, and memory-order identities, and writes the
  corresponding speculative side structures.
- Selects the dispatch route and forms the admitted renamed-uop packet.

### S1

- Owner family: `src/bcc/ooo/s1.py`.
- Captures admitted D3 packets in the per-IQ speculative write-port buffer.
- Carries execution class, route, readiness seed, age, and cancellation state.

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

## Trace naming rules

- Trace producers emit separate I-F4 and Instruction Buffer events when each
  boundary is observed.
- B-SIDE predictor events use B-F0..B-F4 plus training and recovery names;
  I-SIDE events use I-F0..I-F4.
- The IQ entry becomes resident and pick-visible at S3; IQ is the structure,
  not a serial stage before S1 or S2.

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
