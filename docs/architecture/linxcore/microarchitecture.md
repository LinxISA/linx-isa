# LinxCore v0.56 Microarchitecture Contract
## Baseline superscalar contract

LinxCore is the canonical superscalar out-of-order core for LinxISA `v0.56`.
It retires precisely, executes out of order, and preserves a block-ordered
architectural control model across scalar and engine-backed work.

Current baseline limits:

- fetch width: 4
- dispatch width: 4
- issue width: up to 4
- commit width: up to 4
- LSU width: 1

These limits are the live `v0.56` closure baseline. Wider issue or multi-LSU
scaling is a follow-on track, not part of the normative contract here.

## Architectural state model

LinxCore must preserve the following architectural state classes:

- scalar, control, and privilege state defined by LinxISA `v0.56`,
- CSR, trap, MMU, and interrupt-visible state,
- block-visible architectural state for `BSTART`, `BSTOP`, and
  boundary-authoritative redirect,
- dynamic block identity through `block_uid` and `block_bid`,
- precise retirement order through the ROB,
- trace-visible dynamic identity through uop- and block-level metadata.

Implementation-private predictor, queue, replay, or scheduling state may exist,
but it must not create a second retirement, recovery, or block machine.

## Machine organization

LinxCore is partitioned into these major architectural domains:

- frontend fetch and instruction delivery,
- decode, ordering-id allocation, and rename,
- post-rename dispatch, issue, and execution clusters,
- LSU and memory-ordering machinery,
- ROB and precise commit machinery,
- block-control machinery (`BISQ`, `BCTRL`, `BROB`, `BID` flow),
- integrated engines selected through the block fabric,
- trace and observability producers.

The remainder of this document freezes the contract across those domains.

## Module decomposition contract

LinxCore is specified as a hierarchy of named modules. The module decomposition
is part of the architectural contract because pipeline ownership, block
ownership, and trace ownership must remain inspectable across pyCircuit, RTL
generation, trace production, and bring-up tooling.

### Stage-to-module rule

- Every architecturally visible stage token must map to a dedicated module
  owner.
- Integration wrappers may compose stage modules, but they must not absorb
  stage state into anonymous glue.
- Shared helper files may provide types, combinational helpers, or packed
  metadata, but stage-local state must stay in the owning stage module.
- If a bring-up shell bypasses a stage source, the replacement source must
  still present the same named stage boundary to downstream decode, trace, and
  compare tooling.

The detailed structural catalog is normative in:

- `rtl/LinxCore/docs/architecture/module-catalog.md`
- `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`

## Pipeline contract (LC-MA-PIPE-001)

- Stage ownership must remain explicit across frontend, decode, rename, issue,
  execute, and commit; no hidden pass-through collapse is allowed.
- Each architecturally visible stage must remain a module in the pyCircuit
  hierarchy, either as a direct stage module or as a dedicated owner module
  inside the backend family.
- Commit behavior must remain precise and ordered by architectural retirement.
- ROB bookkeeping must remain coherent across multi-commit cycles.
- `BSTART` and `BSTOP` are ROB-visible boundary uops resolved by `D2`; they do
  not require IQ or FU issue to become architecturally visible.

### Current promoted closure slice

The current promoted stage contract covers the frontend/decode path, the
post-rename dispatch path, and the baseline issue/wakeup slice from `F0`
through `W1`:

- `F0`, `F1`, `F2`, `F3`, `IB`, `F4`
- `D1`, `D2`, `D3`
- `S1`, `S2`, `IQ`
- `P1`, `I1`, `I2`, `E1`, `W1`

Later execute/writeback detail beyond that promoted slice may be refined by
future canonical updates, but it must not contradict the rules below.

### Frontend contract details (`F0` to `F4`)

#### F0

- `F0` is a dedicated PC-select stage.
- `F0` receives multiple candidate PCs and selects one under control logic.
- `F0 -> F1` is a registered pipeline boundary.
- The architecture-facing `F0 -> F1` interface is per-thread rather than a
  single shared port with explicit thread multiplexing.

#### F1

- `F1` owns I-cache lookup and tag-check semantics.
- `F1` determines hit or miss and applies frontend backpressure on miss.
- The architectural model reserves per-thread miss independence.
- The current physical I-cache read path is single-ported, so `F1` arbitrates
  among threads and services at most one thread lookup per cycle.
- `F1 -> F2` is a registered boundary.

#### F2

- `F2` receives cache-read data plus thread and PC context from `F1`.
- `F2` performs ECC checking and stages the raw cache-read result.
- On ECC error, `F2` blocks normal delivery to `F3` and reports a fetch-side
  fault instead of forwarding a normal bundle-with-flag form.
- `F2` does not own variable-length stitching or cross-line assembly.

#### F3

- `F3` owns variable-length instruction assembly and per-thread carry/stitch
  buffering.
- `F3` performs static prediction.
- `F3` must recognize at least `BSTART` and `BSTOP` and annotate explicit
  block-boundary metadata.
- The primary boundary metadata is semantic `start_of_block` and
  `end_of_block`, not raw opcode-tag residue.
- Template instructions (`FENTRY`, `FEXIT`, `FRET.*`) may be consumed by the
  CTU without forcing later instructions in the same fetch bundle to disappear.
  Those later instructions may remain in frontend queues, but they must not
  enter `IB` before the CTU-expanded child stream for that template.
- While a CTU child stream is actively injecting instructions, `IB` write-port
  source selection is CTU-priority and ordinary IFU writes wait until the
  active child stream completes.

#### IB

- `IB` is partitioned by thread; each thread owns an independent bank or FIFO.
- An `IB` entry may legally straddle a block boundary.
- Block metadata is carried per instruction, not as one summary bit per entry.
- Each stored instruction carries its own length metadata.
- PC encoding uses `entry_base_pc` plus per-instruction offset and length
  rather than a full explicit PC for every instruction.
- Each per-thread `IB` bank provides up to `decodeWidth` lane reads per cycle
  so `D1` can assemble a decode-width-aligned contiguous decode group.

#### F4

- `F4` provides a 4-slot window per cycle.
- Each slot is a continuous 64-bit view from its own PC.
- Decode consumes slots strictly in order.
- Decode must not concatenate across slots to form 48-bit or 64-bit
  instructions.
- Slot consumption stops at the first invalid or killed slot; no slot
  compaction or skipping is allowed.

### Decode and renamed-uop contract (`D1` to `D3`)

#### D1

- `D1` reads a program-order contiguous decode group from `IB`.
- `D1` performs instruction decode and allocates `RID`, `BID`, and `LSID`.
- Allocation for a decode group is all-or-nothing; if the full group cannot
  allocate successfully, the pipeline stalls and retries the whole group.
- `D1` may split or fuse decoded work, but older split work must be emitted
  before younger instructions are consumed.
- `D1` output uops already carry decoded opcode or uop semantics, fixed operand
  slots, architectural operand tags, extended immediate values, and block/order
  metadata.

#### D2

- `D2` is the rename request and translation stage.
- `D2` preserves decode-slot program order across one decode group.
- `D2` resolves boundary metadata and prepares ROB-visible boundary uops.
- `D2` carries the canonical architectural uop shape:

```text
{
  valid,
  thread_id,
  pc,
  opcode,
  uop_type,
  src[3],
  dst[1],
  imm,
  imm_type,
  imm_valid,
  rid,
  bid,
  lsid,
  sob,
  eob,
  boundary_type,
  boundary_target,
  pred_taken,
  insn_len,
  insn_raw
}
```

- Source slots use operand classes `{P, T, U, CARG}`.
- Destination slots use `{P, T, U}`; `CARG` is source-only.
- `P` carries architectural `atag`.
- `T` carries `t_rel`.
- `U` carries `u_rel`.
- `CARG` carries only `type=CARG`; the actual block argument is resolved via
  `bid` rather than an independent operand id.

#### D3

- `D3` is the renamed-uop latch boundary.
- `D3` retains semantic operand identity while also carrying the resolved
  backend tag form needed by later stages.
- `P` retains `atag` and adds `ptag`.
- `T` retains `t_rel` and adds resolved `ttag`.
- `U` retains `u_rel` and adds resolved `utag`.
- `CARG` is resolved at `D3` into the block-scoped `CARG` file indexed by
  `bid`; it does not continue as an IQ-visible operand payload.

#### Rename rules

- `P` rename is map-based.
- `CMAP` is the committed rename map.
- `SMAP` is the speculative map visible to rename.
- `MapQ` records speculative `P` rename increments against `CMAP`.
- `MapQ` applies only to `P`-type destinations.
- Recovery is instruction-precise: `MapQ` cut points are keyed by `rid`, not
  just `bid`.
- The default flush replay boundary keeps mappings up to and including the
  flushing instruction (`<= flush_rid`) for the younger-squash redirect path.
- Same-cycle `P` rename bookkeeping uses stable FIFO insertion order derived
  from `rid + decode_slot`.
- `T` and `U` do not use `CMAP`, `SMAP`, or `MapQ`.
- `T` allocates from `T_FIFO`; `U` allocates from `U_FIFO`.
- Same-cycle `T` and `U` allocations are performed in decode-slot order.
- There is exactly one `CARG` per block.
- `CARG` is identified implicitly by `bid` and is not independently renamed.

### Post-rename dispatch contract (`S1`, `S2`, and `IQ`)

#### S1

- `S1` is the first post-rename dispatch-preparation stage.
- `S1` receives renamed uops from `D3`, classifies each uop by its execution
  or issue class, selects the target physical IQ, and queries the operand ready
  state used to initialize the eventual IQ entry.

#### S2

- `S2` is the actual IQ write stage.
- `S2` receives the routed and annotated uops from `S1` and performs the real
  enqueue into the selected downstream IQ.

#### IQ routing and enqueue rules

- The architectural routing rule is type-directed: the destination physical IQ
  is a function of the decoded or renamed execution class plus a fixed-priority
  physical-queue selection policy for classes with multiple legal queues.
- `S1` performs routing selection and ready-state query.
- `S2` performs the actual IQ entry write.
- `CARG` does not participate in `S1` or `S2` IQ routing; it has already been
  materialized into the `CARG` file at `D3`.
- `S1` and `S2` preserve program order within one decode or rename group when
  presenting multiple same-cycle enqueue attempts.
- `BBD` does not enter an IQ; boundary handling must be resolved before `S2`
  writes uops into the IQ fabric.

#### Physical IQ layout

- External naming visible to trace and tooling must preserve the golden
  `uop_kind` mapping (`issq_alu`, `issq_bru`, `issq_agu`, `issq_std`,
  `issq_fsu`, `issq_sys`, `issq_cmd`, ...).
- Physical IQs may be merged or split internally, but they must preserve the
  architectural class carried by the uop.
- The current physical IQ set is:
  - `alu_iq0`
  - `shared_iq1`
  - `bru_iq`
  - `agu_iq0`
  - `agu_iq1`
  - `std_iq0`
  - `std_iq1`
  - `cmd_iq`
- Baseline physical implementation provides two enqueue/write ports per
  physical IQ.
- Baseline architectural-class to physical-IQ mapping is:
  - `ALU -> alu_iq0`, else spill to `shared_iq1`
  - `BRU -> bru_iq`
  - `AGU -> agu_iq0`, else spill to `agu_iq1`
  - `STD -> std_iq0`, else spill to `std_iq1`
  - `FSU -> shared_iq1`
  - `SYS -> shared_iq1`
  - `CMD -> cmd_iq`
- If more same-cycle enqueue attempts target one IQ than it can accept, the
  older instructions in the current decode-width group win by decode-slot
  order.

#### Ready-table initialization

- `ready_table_p`, `ready_table_t`, and `ready_table_u` represent non-spec
  readiness only.
- A ready-table bit may be set only when the corresponding produced value is
  architecturally stable and will not later be withdrawn by ordinary
  cancellation or flush of a still-speculative producer.
- `S1` initializes operand readiness by querying the corresponding ready table:
  - `P` via `ready_table_p[ptag]`
  - `T` via `ready_table_t[ttag]`
  - `U` via `ready_table_u[utag]`

## Hazard and replay contract (LC-MA-HAZ-001)

- Wakeup, scoreboard, and replay control must preserve deterministic issue
  legality.
- Redirect, flush, and replay must not commit younger wrong-path state.

### IQ residency, pick, and issue rules

- Each IQ entry carries per-source `src_valid` and `src_ready` state.
- Invalid source operands are treated as ready by default.
- A valid source that is not ready leaves the entry resident in the IQ waiting
  for wakeup.
- An IQ entry becomes pick-eligible only when all of its valid source operands
  are ready and the entry is not already `inflight`.
- Pick policy is oldest-ready-first.
- Pick does not immediately remove an entry from the IQ.
- When an entry is picked, the entry remains valid and transitions to an
  `inflight` state.
- If downstream issue progress later fails, the entry is not reinserted;
  instead, `inflight` is cleared and the entry becomes eligible for a later
  retry.
- The architecture forbids a pick-then-reinsert model for ordinary issue
  cancellation or retry.
- The real IQ entry deallocation point is `I2`: only after the uop reaches
  `I2` and is confirmed non-cancellable does the IQ clear the entry's `valid`
  state.

### Ready table vs speculative ready

- `ready_table` is non-speculative readiness only.
- Speculative readiness lives in IQ entry state with an `is_spec` marker.
- Merge rule for operand readiness is:
  `src_ready = src_ready_nonspec || src_ready_spec`

### Pipeline and wakeup timing

- Pipeline stages used in the promoted issue slice are `P1 -> I1 -> I2 -> E1 ->
  W1`.
- Wakeup must not affect pick in the same cycle:
  wakeup at cycle `N` becomes visible to pick at cycle `N+1`.
- Baseline latency-to-wakeup mapping is:
  - `lat=1 -> wakeup at P1`
  - `lat=2 -> wakeup at I2`
  - `lat=3 -> wakeup at E1`
  - `lat=4 -> wakeup at W1`

### `P1`, `I1`, `I2`, `E1`, and `W1`

- `P1` selects ready, non-`inflight` IQ entries and marks the chosen entry
  `inflight`.
- `I1` is responsible for deciding which source operands require physical
  operand reads in the current issue attempt.
- `I1` performs global operand-read and RF read-port arbitration across the set
  of uops picked in the current cycle.
- If a picked uop loses required `I1` read-port arbitration, the attempt is
  cancelled for this cycle: the IQ entry remains valid, `inflight` is cleared,
  and the uop returns to normal future-pick eligibility.
- `I2` is the issue-confirmation boundary and the IQ deallocation point.
- `E1` is the first execute stage after issue confirmation.
- `W1` is the architecturally visible late resolve and wakeup stage for the
  promoted baseline slice.

### Register-file arbitration

- Read ports may contend; the default `int_rf_rports` is 3.
- `I1` performs global read-port arbitration.
- Arbitration policy is oldest-first by ROB age relative to ROB head.
- Failure to win arbitration cancels the in-flight attempt without deallocating
  the IQ entry.
- Write ports must not contend.
- Each IQ picker/issue port corresponds to a pipeline and a dedicated RF write
  port.
- `STD` has read ports but no write port.

### Load speculative wakeup, forward, and miss handling

- Loads produce speculative wakeup at `LD_E1`.
- Loads return data only at `LD_E4`.
- Consumers that become ready only via load spec-wakeup:
  - must not request RF read ports in `I1` for that source,
  - must obtain data via `E4 -> consumer-I2` forward using the bypass network.
- `ld_gen_vec` is a bitset, not onehot, representing load pipeline stages
  `E1` through `E4`.
- `ld_gen_vec` must propagate along dependency chains.
- Load pipeline movement advances `ld_gen_vec` via bit-shift.
- LSU provides `miss_pending` derived from `E4` miss detection.
- While `miss_pending == 1`, issue queues must suppress picking entries whose
  source dependency still carries `LD_E4`.
- A top-level configuration hook may later extend miss visibility to `E5`, but
  the default contract is the `E4` scheme above.

### T/U point-to-point wakeup

- `P` wakeup is global broadcast by physical tag.
- `T` and `U` wakeup are point-to-point via
  `qtag = (phys_issq_id, entry_id)`.
- `phys_issq_id` is a physical IQ enum derived via spec templates at JIT.
- `entry_id` width is derived per IQ and packed to a uniform maximum width on
  the qtag wire.

## Block and recovery contract (LC-MA-BLK-001)

- Block-structured control flow is mandatory.
- `BSTART` and `BSTOP` semantics are authoritative for architectural redirect
  and retirement behavior.
- Architectural redirect is boundary-authoritative. Execute-side `setc.cond`
  records correction metadata but does not directly rewrite the architectural
  PC.
- `BSTART` at block head opens a block.
- `BSTART` encountered in-body terminates the previous block and may restart at
  the same PC as the next block head.
- `RET`, `IND`, and `ICALL` require explicit `SETC.TGT` in the same block.
- `BSTART.CALL` does not implicitly write `ra`. Return-address updates come
  only from explicit `SETRET` or `C.SETRET`.
- `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` are valid standalone macro block
  boundaries and remain visible in committed block metadata.
- Recovery targets must resolve to legal block starts. Non-block targets raise
  `TRAP_BRU_RECOVERY_NOT_BSTART (0x0000B001)` precisely.

### Boundary-authoritative redirect

- BRU-side condition evaluation may discover a mismatch early, but
  architectural redirect remains a boundary-consumed action.
- Boundary commit is the single authority for architectural redirect selection.
- Execute-side correction metadata must not bypass ROB ordering.

### Macro boundary rules

- `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` are architectural boundary
  forms, not trace-only implementation devices.
- Template expansion must preserve architectural ordering, block visibility,
  and return-target legality.

Detailed recovery behavior remains documented in:

- `rtl/LinxCore/docs/architecture/branch_recovery_rules.md`
- `rtl/LinxCore/docs/architecture/linxisa_block_control_flow.md`

## BID and BROB contract

- BID is generated by BROB and remains 64-bit.
- Default BID encoding is `BID = (uniq << 7) | slot_id`, with
  `slot_id = BID[6:0]` for the 128-entry default.
- `cmd_tag` must equal `bid[7:0]` for PE response routing.
- Block completion is `scalar_done && (needs_engine ? engine_done : 1)`.
- `scalar_done` is triggered at both `BSTART` retire and `BSTOP` retire.
- Flush and redirect behavior is BID-based across every BID-carrying queue:
  keep `bid <= flush_bid`, kill `bid > flush_bid`.
- BROB, BISQ, and every block-carrying path must preserve full-width BID
  ordering across slot wrap.

### Architectural block-completion abstraction

- For block completion semantics, LinxCore follows the ISA-visible canonical
  block-type domain `{STD, FP, SYS, MPAR, MSEQ, VPAR, VSEQ, TMA, CUBE, TEPL}`.
- `STD`, `FP`, and `SYS` are equivalent in the two-layer completion model.
- Dynamic block instances collapse to exactly one of three architectural
  participant sets:
  - `{}` for empty/control-only scalar-family instances,
  - `{scalar}` for scalar-family instances with a real scalar body,
  - `{non-scalar}` for canonical non-scalar block types.
- Dynamic degeneration to `{}` is allowed only for scalar/control-family block
  types.
- Canonical non-scalar block types always carry a `{non-scalar}` completion
  obligation.
- The architectural `{non-scalar}` participant has single-point resolve
  semantics: `BROB` and retirement observe one `non-scalar-done` event per
  block instance.

### Block lifecycle rules

- `BSTART` carries the new BID of the new block.
- `BSTOP` retires only when the active block is no longer blocked by engine
  completion.
- Only the oldest architecturally eligible block may retire.
- Younger engine-backed work must remain cancellable under normal redirect and
  flush rules.

Detailed BROB and block-fabric behavior remains documented in:

- `rtl/LinxCore/docs/architecture/stages/BROB.md`
- `rtl/LinxCore/docs/architecture/block_fabric_contract.md`

## Privilege/trap contract (LC-MA-PRV-001)

- U->S trap entry and `SRET` return must preserve architected control and state
  transitions.
- Trap envelope and CSR-visible side effects must remain coherent with
  commit-visible behavior.
- Precise exception reporting is required under superscalar retirement.

## MMU contract (LC-MA-MMU-001)

- Translation success and failure must produce deterministic trap envelopes.
- MMU behavior must remain aligned with the `v0.56` privileged contract wording.
- MMU fault paths must preserve precise retirement and recovery ordering.

## Interrupt contract (LC-MA-IRQ-001)

- Timer interrupt delivery must remain enabled in strict-system lanes.
- Interrupt entry and return must compose with block boundaries and replay or
  flush behavior.
- Interrupt handling must preserve forward progress under sustained mixed
  workload pressure.

Interrupts must not create hidden state transitions outside commit-visible and
trap-visible architectural behavior.

## Memory-ordering contract (LC-MA-MEM-001)

- Load/store ordering, forwarding, and replay behavior must remain
  architecturally legal.
- Memory visibility at commit must remain consistent with recorded trace and
  memory metadata.
- Dispatch allocates a monotonic `load_store_id` per memory uop and LSU issue
  remains ordered by `lsid_issue_ptr`.
- Committed stores remain decoupled through the committed-store drain path;
  younger speculative memory state must still be flushable before commit.
- Ordering checks must include block and redirect interactions.

### LSU rules

- The live contract is a single-LSU-width machine.
- LSU issue remains ordered by `load_store_id`.
- Load forwarding, replay, and store-drain behavior must remain precise with
  respect to committed state.
- MMIO commit-visible behavior must remain architecturally explicit.

Detailed ordering behavior remains documented in:

- `rtl/LinxCore/docs/architecture/lsid_memory_ordering.md`

## Engine integration contract (LC-MA-ENG-001)

- Engine-backed execution must remain architecturally visible through the
  lowered block stream.
- Engine completion must compose with precise retirement and the existing
  block-engine completion model.
- Engine-local work must not create hidden global-memory side effects outside
  architecturally visible memory operations and committed block boundaries.
- Tile-oriented engines such as `TAU` must preserve the current tile-to-tile
  contract unless a future canonical architecture update changes that rule.

### Workload-engine composition

- `VEC` remains the general programmable SIMT compute engine.
- `TMA` integrates into LinxCore through the same block/BID contract as the
  rest of the machine, but its southbound memory traffic is owned by the CSU
  subsystem and targets CSU L2 alongside frontend refill traffic.
- `CUBE` and `TAU` continue to integrate through the same block/BID contract
  as peer engines.
- Engine issue, completion, exception, and flush behavior must remain visible
  to ROB, BROB, and trace machinery through the canonical interfaces.

## Forward-progress contract (LC-MA-FWD-001)

- Branch, flush, load-miss, replay, and interrupt interactions must not
  deadlock.
- Required closure gates must include explicit forward-progress evidence lanes.

## Contract evidence mapping

The gate mapping for every contract ID in this document is defined in:

- `rtl/LinxCore/docs/architecture/verification-matrix.md`
