<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/microarchitecture.md -->

# LinxCore v0.57 Microarchitecture Contract

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/microarchitecture.md`.


## Baseline superscalar contract

LinxCore is the canonical superscalar out-of-order core for LinxISA `v0.57`.
It retires precisely, executes out of order, and preserves a block-ordered
architectural control model across scalar and engine-backed work.

Current baseline limits:

- fetch width: 4
- dispatch width: 4
- issue width: up to 4
- commit width: up to 4
- LSU width: 1

These limits are the selected LinxCore closure baseline, not LinxISA-visible
widths. Wider issue or multi-LSU scaling is a follow-on track and must preserve
the same ordering, recovery, and observability contracts.

## Architectural state model

LinxCore must preserve the following architectural state classes:

- scalar, control, and privilege state defined by LinxISA `v0.57`,
- CSR, trap, MMU, and interrupt-visible state,
- block-visible architectural state for `BSTART`, `BSTOP`, and
  boundary-authoritative redirect,
- dynamic block identity through the `BID_W`-bit `block_bid`, with a separate
  optional `block_uid` for trace correlation,
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

## STID and SMT ownership

`STID` is the scalar frontend/BROB-ring hardware-thread namespace. A scalar
frontend field named `thread_id` maps one-to-one to STID. Engine or PE-local
`tid` and PE ID may remain separate subordinate qualifiers; they never replace
STID on shared block, memory, or recovery interfaces.

- F0 PC/redirect state, F4/IB residency, checkpoints, speculative/committed
  rename maps, local T/U managers, instruction-ROB/RID head state, BROB,
  CARG/BARG, and LSID allocation are either physically partitioned per STID or
  stored in shared structures with an explicit STID tag on every row.
- A physical-tag namespace may be globally unique, or it must carry STID at
  every ready-table, wakeup, and bypass comparison. Untagged cross-STID aliasing
  is forbidden.
- Shared IQs select oldest-ready work within each STID and then arbitrate fairly
  across eligible STIDs; they never compare per-STID ROB ages globally.
- Shared RF ports, completion collectors, command fabrics, and retire ports use
  explicit fair arbitration. A blocked or faulting head in one STID does not
  block independent progress in another except for the cycle in which a
  documented shared port is granted elsewhere.
- Flush, recovery, local cleanup, and block completion always select an STID
  first, then apply RID/BID/LSID age in that STID's ring/domain. A flush of one
  STID must not mutate another STID's state.

## Module decomposition contract

LinxCore is specified as a hierarchy of named modules. The module decomposition
is part of the architectural contract because pipeline ownership, block
ownership, and trace ownership must remain inspectable across pyCircuit, RTL
generation, trace production, and bring-up tooling.

### Stage-to-module rule

- Every architecturally visible stateful boundary must map to a named module
  owner. One pipe module may own multiple separately visible E/W or R
  coordinates; a pure timing coordinate does not require one file per cycle.
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

## Mechanism adoption policy

The live architecture contains no parallel legacy specification. Historical
OOO and LSU inputs are recoverable from the Git snapshots recorded in
`mechanism-intake.json`; that ledger maps every removed source file to one or
more reviewed mechanisms, a disposition, this contract's owning sections,
pyCircuit and Chisel owners, and required scenarios.

The intake dispositions have the following binding meaning:

- **Adopt** preserves an ISA-neutral correctness mechanism directly.
- **Adapt** preserves the mechanism after rebinding identity, ordering,
  recovery, or state to Linx block semantics.
- **Parameterize** preserves required behavior while leaving capacity,
  banking, ports, and non-visible latency configurable.
- **Reject** excludes ARM architectural state and platform-specific policy.

The promoted OOO set includes PC metadata, atomic decode admission, scalar
`SMAP`/`CMAP`/`MapQ`, block-local `T/U` rename, precise ROB/BROB
retirement, resident IQ retry ownership, speculative readiness isolation,
execution/bypass ownership, and R0-R4 recovery. The promoted LSU set includes
LSID ordering, split-store STQ/SCB ownership, LIQ and ResolveQ/LHQ replay,
byte-granular forwarding, MDB prediction, cache/TLB/refill identity,
coherence-triggered nuke requests, Linx atomics/fences/MMIO, engine memory, and
non-starving prefetch/maintenance policy.

ARM exception levels, PAC/BTI, SVE/NEON state, condition-code architecture,
ARM exclusives and AT/barrier encodings, WFx/SMT mode switching, DIDT policy,
and implementation-defined ARM registers are rejected. Similar future Linx
features require their own LinxISA contract; they cannot be restored from the
historical input as compatibility behavior.

## Pipeline contract (LC-MA-PIPE-001)

- Stage ownership must remain explicit across frontend, decode, rename, issue,
  execute, and commit; no hidden pass-through collapse is allowed.
- Each architecturally visible stateful boundary must remain inspectable in the
  pyCircuit hierarchy, either as a direct stage module or as named state inside
  a declared owner family.
- Commit behavior must remain precise and ordered by architectural retirement.
- ROB bookkeeping must remain coherent across multi-commit cycles.
- `BSTART` and `BSTOP` are ROB-visible boundary uops resolved by `D2`; they do
  not require IQ or FU issue to become architecturally visible.

### Canonical stage taxonomy

The canonical pipeline is:

```text
F0 -> F1 -> F2 -> F3 -> F4/IB -> D1 -> D2 -> D3
                                        |
                                        v
                               S1 -> S2 -> S3/IQ
                                        |
                                        v
                               [P0] -> P1 -> I1 -> I2 -> E1 -> E2 -> E3 -> ...
                                                          \---- W1/W2/W3 overlay
                     resolve/ROB -> R0 -> R1 -> R2 -> R3 -> R4
                                                  |               |
                                               CMT/FLS       restart -> F0
```

`F0` is canonical frontend selection/control. `F1..F4` are the four fetch
stages, and `F4` and `IB` are the same stage. `W` stages describe
producer-relative actual data-bypass/result/writeback age and overlay `E` stages; they
are not a serial tail after execute. Full ownership and implementation-alias
rules are normative in `pipeline-stage-catalog.md`.

### Frontend contract details (`F0` to `F4/IB`)

#### F0

- `F0` arbitrates runnable threads, selects reset/sequential/predicted/redirect
  PC state, and launches one registered frontend request context toward F1.
- Redirect state delivered by R4 is consumed by F0 before new sequential or
  predicted work for that thread.
- F0 is not counted among the four fetch-data stages.

#### F1

- `F1` owns iTLB/I-cache request and lookup launch for the F0-selected thread
  and PC.
- Fetch packet and checkpoint identity are assigned before leaving F1.

#### F2

- `F2` captures the I-cache response, integrity/ECC status, hit/miss state, and
  the matching thread/PC context.
- Physical port sharing is an implementation parameter and must preserve
  independent per-thread architectural state.

#### F3

- `F3` owns variable-length 16/32/48/64-bit assembly, cross-line carry state,
  and byte-stream ordering. A failed F2 integrity check produces a fetch fault
  instead of a normal instruction entry.
- F3 retains incomplete cross-line carry locally and hands only complete
  instruction records to F4/IB. It does not own final prediction or
  block-boundary predecode.

#### F4/IB

- `F4` is the fourth fetch stage and the instruction buffer. There is no
  architectural `IB -> F4` or `F4 -> IB` serial boundary.
- F4 performs final lightweight predecode, prediction, and block-boundary/
  template metadata formation before the D1 handoff. Full opcode and operand
  decode remains D1/D2 work.
- The primary boundary metadata is `start_of_block`/`end_of_block` plus branch
  kind and target context, not raw opcode residue.
- At F4 ingress, a recognized template (`FENTRY`, `FEXIT`, `FRET.*`) is marked
  as a template parent and sent through D1/D2 to D3; F4/IB holds later ordinary
  records for only that STID. F4 does not allocate BID or start child execution.
- D3 atomically allocates the template's `(STID,BID)`, checkpoint, resource
  reservation, and ordered ROB group: child rows first and one final template
  completion/trace row last. Only then does CTU emit children into their
  reserved rows through the normal rename/execute/LSU path.
- Children reuse the parent's `(STID,BID)` and do not allocate another BROB
  slot unless a child is itself an architecturally legal boundary. The final
  template row completes only after expansion and every child completes, so
  children retire before template completion/redirect becomes visible.
- Flush kills filled and unfilled reserved rows plus CTU state by STID and
  checkpoint. This is an internal F4/D3/CTU producer loop, not an architectural
  `F4 -> CTU/F5 -> IB` stage chain.
- F4/IB is partitioned by thread; each thread owns an independent bank or FIFO.
- Every stored instruction carries PC/offset, length, raw bits, boundary,
  prediction, template, and checkpoint metadata.
- F4/IB presents up to `decodeWidth` contiguous program-order instructions to
  D1. The baseline width is four, but that width does not define the F4 name.
- The D1 ingress reader may construct a continuous 64-bit view for each
  selected instruction so 48/64-bit forms decode without concatenating
  unrelated entries.
- Consumption stops at the first invalid, killed, or structurally blocked
  entry. No compaction or younger-entry skipping is allowed.

### Decode and renamed-uop contract (`D1` to `D3`)

#### D1

- `D1` reads a program-order contiguous group from F4/IB.
- `D1` performs early opcode decode, illegal-instruction and early-exception
  detection, uop split/fuse recognition, and decode-group formation.
- D1 calculates per-row shape and group demand but does not mutate ROB, BROB,
  rename, LSID, or IQ state.
- `D1` may split or fuse decoded work, but older split work must be emitted
  before younger instructions are consumed.
- With baseline `BROB_ALLOC_PER_CYCLE=1`, D1 never forms a group containing
  two new-block allocation boundaries. If a `BSTART`/template boundary is not
  the first candidate, D1 ends the current group before it. A group beginning
  with `BSTART` may include following body rows only up to the next boundary;
  a template-parent group contains only that parent.
- D1 output carries decoded opcode/uop semantics, raw instruction identity,
  length, early fault state, and the information D2 needs for operand
  extraction and resource calculation.

#### D2

- `D2` extracts architectural source/destination operands and immediates,
  resolves block-boundary metadata, and calculates the complete resource
  demand of the group.
- `D2` preserves decode-slot program order across one decode group.
- D2 marks the single boundary allocation, if present, and partitions row
  ownership so the `BSTART` row plus every following row in that group receives
  the newly allocated BID.
- `D2` prepares one coherent D3 admission request; it does not allocate
  physical tags, BID, RID, LSID, or IQ rows.
- `BSTART`, `BSTOP`, and macro boundaries are fully classified by D2 so D3 can
  reserve the correct BROB/ROB and checkpoint resources.

#### D3

- `D3` is the atomic-admission and physical-rename stage.
- D3 accepts the entire prepared group only when ROB, BROB, scalar/local
  rename, IQ write, checkpoint, and memory-order capacity are all available.
- On acceptance, the instruction ROB supplies native RID, BROB supplies the
  `BID_W`-bit BID, the memory-order owner stamps the pre-increment LSID
  snapshot and advances only for memory operations, and rename supplies
  physical tags.
- When the group begins with a new-block boundary, D3 allocates exactly one new
  `(STID,BID)` before stamping rows in decode-slot order. Adjacent BSTARTs are
  admitted in separate groups/cycles. A wider design may allocate multiple
  BIDs only by raising `BROB_ALLOC_PER_CYCLE` and preserving the same slot-order
  ownership atomically.
- D3 writes the corresponding speculative state and emits the canonical
  renamed-uop shape:

```text
{
  valid,
  stid,                // canonical hardware-thread/BROB-ring selector
  pc,
  opcode,
  uop_type,
  src[3],
  dst[1],
  imm,
  imm_type,
  imm_valid,
  rid,                 // native instruction-order identity
  block_bid,           // BID_W-bit BROB slot identity
  block_order,         // internal wrap/age sidecar where required
  model_identity,      // separate bid/gid/rid cross-check sideband
  lsid,
  mem_order_snapshot,
  checkpoint_id,
  sob,
  eob,
  boundary_type,
  boundary_target,
  pred_taken,
  insn_len,
  insn_raw
}
```

An existing scalar-frontend transport field named `thread_id` is an encoding
alias for `stid` and must map one-to-one. PE/engine-local TID, when present, is
a separate subordinate qualifier.

Native ring IDs, BROB slot BID, internal wrap/age state, optional DFX
`block_uid`, and model/cross-check identity are distinct namespaces. An
implementation must not widen BID with hidden uniqueness bits or reconstruct
order, checkpoint, or memory ownership from a currently selected queue head.

- Source slots use operand classes `{P, T, U, CARG}`.
- Destination slots use `{P, T, U}`; `CARG` is source-only.
- `P` carries architectural `atag`.
- `T` carries `t_rel`.
- `U` carries `u_rel`.
- `CARG` carries only `type=CARG`; the actual block argument is resolved via
  `(stid,bid)` rather than an independent operand id.

- D3 retains semantic operand identity while adding the resolved backend tag
  form needed by later stages.
- `P` retains `atag` and adds `ptag`.
- `T` retains `t_rel` and adds resolved `ttag`.
- `U` retains `u_rel` and adds resolved `utag`.
- `CARG` is resolved at `D3` into the block-scoped `CARG` file indexed by
  `(stid,bid)`; it does not continue as an IQ-visible operand payload.

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
- `T` and `U` do not use the scalar-`P` `CMAP`, `SMAP`, free list, or global
  remap log.
- `T` and `U` each use an independent `LocalRegMgr`/ClockHands mapping queue,
  allocation sequence, circular local physical pool, and `(STID,BID)`-qualified
  retire/commit/flush lifecycle. These local mapping queues must not be
  confused with the scalar-`P` `MapQ`.
- Same-cycle `T` and `U` allocations are performed in decode-slot order.
- There is exactly one `CARG` per block.
- `CARG` is identified implicitly by `(stid,bid)` and is not independently
  renamed.

The split exists because scalar `P` names persistent architectural state while
`T/U` name relative block-local values. Reusing one committed/speculative map
for both domains would give local values the wrong lifetime and would make
block recovery depend on unrelated scalar-map checkpoints.

### Resource admission and backpressure (LC-MA-RES-001)

An admitted decode group must have a coherent reservation for every resource
that its rows will consume. The admission check includes, as applicable:

- instruction ROB rows and native RIDs;
- a BROB slot/BID and internal ring-pointer state for a new block;
- scalar-`P` physical tags and `MapQ` rows;
- local `T/U` mapping-queue and physical-pool capacity;
- destination IQ write capacity;
- LSID/SID/LID state and split-store dispatch capacity;
- marker lifecycle and checkpoint storage;
- BISQ/BCTRL command capacity for block-fabric work.

At D3 the group either reserves all required resources in program order or
makes no state change. A reduced harness may serialize or bypass one of these resources,
but it must label that behavior as reduced and must not redefine the full-core
admission contract. Atomic admission prevents duplicate RIDs/BIDs, holes in
same-cycle rename order, and one-half allocation of a split store.

Capacity numbers from LinxCoreModel or an ARM reference implementation are
reference evidence only unless this document explicitly promotes them as a
LinxCore baseline parameter.

Detailed local-register lifetime and recovery rules are documented in
`rtl/LinxCore/docs/architecture/block_private_rf.md`.

### Post-rename dispatch contract (`S1`, `S2`, and `S3/IQ`)

#### S1

- `S1` captures admitted D3 packets into the speculative issue-buffer/write-
  port boundary. The packet already carries its execution class and selected
  physical route; S1 retains the readiness seed and cancellation state.

#### S2

- `S2` selects a free physical IQ row and writes the S1 packet plus initial
  source readiness.

#### S3/IQ

- The S2-written row becomes valid, resident, wakeable, and pick-visible at
  S3.
- S3 is the IQ residency boundary; `IQ` names the structure, not a distinct
  serial pipeline stage.

#### IQ routing and enqueue rules

- The architectural routing rule is type-directed: the destination physical IQ
  is a function of the decoded or renamed execution class plus a fixed-priority
  physical-queue selection policy for classes with multiple legal queues.
- D3 performs routing selection and prepares the ready-state seed.
- S1 captures the selected write-port packet; S2 allocates/writes; S3 exposes
  the resident entry.
- `CARG` does not participate in `S1`/`S2`/`S3` IQ routing; it has already been
  materialized into the `CARG` file at `D3`.
- `S1` and `S2` preserve program order within one D3 group when presenting
  multiple same-cycle enqueue attempts.
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
- Scalar issue capacity and physical banking are independent parameters. The
  live scalar ALU slice uses `scalarIssueBanks` equal banks and divides its
  configured total entry count evenly across them; every bank has at least two
  resident rows. This two-bank slice represents `alu_iq0` plus the scalar
  spill path into `shared_iq1`. It does not replace the complete BRU/AGU/STD/
  CMD physical layout above.
- A one-uop live dispatch selects the non-full scalar bank with the least
  occupancy; equal occupancy uses the lower physical bank index. Future
  multi-uop S1/S2 dispatch must preserve decode-slot age before applying the
  same capacity rule.

#### Ready-table initialization

- `ready_table_p`, `ready_table_t`, and `ready_table_u` represent non-spec
  readiness only.
- Scalar `P` data and `ready_table_p` are one physical GPR owner. Reset marks
  the 24 architectural identity tags ready and all additional physical tags
  not-ready. Rename allocation clears the new destination tag; committed
  writeback stores data and sets that same tag ready atomically.
- `gprPhysRegs`, `gprReadPorts`, and `gprWritePorts` are scalar-backend parameters independent
  from ROB, LIQ, STQ, LRET, and cache capacities. The physical-tag width must
  address exactly the configured GPR capacity at every connected boundary.
- A ready-table bit may be set only when the corresponding produced value is
  architecturally stable and will not later be withdrawn by ordinary
  cancellation or flush of a still-speculative producer.
- D3/S1 initializes operand readiness by querying the corresponding ready table:
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
- Pick policy is oldest-ready-first within each STID. A shared IQ forms one or
  more per-STID candidates and uses a fair/RR cross-STID grant; per-STID ROB
  ages are never compared globally.
- Each scalar bank first removes all but its oldest selectable row for every
  represented STID, then round-robins across those per-STID candidates. A
  second shared arbiter applies the same rule across bank candidates. RID
  comparison is legal only when candidate STIDs match; different STIDs are
  ordered only by the implementation fairness pointer.
- Pick does not immediately remove an entry from the IQ.
- When an entry is picked, the entry remains valid and transitions to an
  `inflight` state.
- If downstream issue progress later fails, the entry is not reinserted;
  instead, `inflight` is cleared and the entry becomes eligible for a later
  retry.
- The architecture forbids a pick-then-reinsert model for ordinary issue
  cancellation or retry.
- A non-speculative uop deallocates its IQ entry at `I2` only after the transfer
  is confirmed non-cancellable.
- A uop carrying a live `ld_gen_vec` remains valid and `inflight` in its IQ
  after I2. It deallocates only when every producer load resolves hit at E5.
  On miss/replay, recovery cancels the speculative pipe copy, clears
  `inflight`, and leaves the resident entry eligible for repick.

### Ready table vs speculative ready

- `ready_table` is non-speculative readiness only.
- Speculative readiness lives in IQ entry state with an `is_spec` marker.
- Merge rule for operand readiness is:
  `src_ready = src_ready_nonspec || src_ready_spec`

### Pipeline and wakeup timing

- The issue path is `[P0] -> P1 -> I1 -> I2`; P0 exists only when candidate
  preselection is registered.
- `E1`, `E2`, `E3`, and later E labels count absolute cycles after I2 for each
  execution pipe.
- `W1`, `W2`, and `W3` are producer-relative actual
  data-bypass/result/writeback ages. They overlay E stages and are not a serial
  continuation after E. Each pipe declares
  `{spec_wakeup, data_bypass, rf_write, resolve}` alignment; speculative
  dependency wakeup is a separate earlier E-qualified event that
  predicts a future W1 and remains cancellable.
- Wakeup must not affect pick in the same cycle:
  wakeup at cycle `N` becomes visible to pick at cycle `N+1`.
- Baseline scalar data-result alignment is:
  - 1-cycle scalar ALU: `E1/W1`, `E2/W2`, `E3/W3`;
  - 2-cycle scalar ALU: `E2/W1`, `E3/W2`, `E4/W3`;
  - 3-cycle scalar/MAC: `E3/W1`, `E4/W2`, `E5/W3`;
  - load hit: `E4/W1`, `E5/W2`, `E6/W3`.
- For all result-producing pipes, W1 is the first actual data-bypass/result
  age. In the baseline scalar pipes, W2 is the normal RF-write age and W3 is
  the RF-visible/last baseline bypass age. A special pipe may write RF at W4;
  its earlier speculative wakeup stays separately E-qualified and must be
  repaired if the predicted W1 data does not arrive.

### `P0`, `P1`, `I1`, `I2`, `E`, and `W`

- `P0`, when present, performs registered queue-local candidate reduction. A
  combinational preselect remains part of P1 and must not be traced as P0.
- `P1` selects ready, non-`inflight` IQ entries and marks the chosen entry
  `inflight`.
- `I1` is responsible for deciding which source operands require physical
  operand reads in the current issue attempt.
- `I1` performs global operand-read and RF read-port arbitration across the set
  of uops picked in the current cycle.
- If a picked uop loses required `I1` read-port arbitration, the attempt is
  cancelled for this cycle: the IQ entry remains valid, `inflight` is cleared,
  and the uop returns to normal future-pick eligibility.
- `I2` is the issue-confirmation boundary. It deallocates only
  non-speculative/non-cancellable entries; load-dependent speculative entries
  retain their resident IQ owner until the producer loads resolve at E5.
- `E1` is the first execute stage after issue confirmation.
- Result-producing pipes publish W1/W2/W3 from their real result/writeback
  state. ROB head wait, commit preparation, and trace formatting are not W
  owners.
- Control-only work remains E-qualified: for example, baseline BRU decides at
  E1, resolves at E2, and may send later LSU cleanup at E3 without inventing a
  W stage.

### Register-file arbitration

- Read ports may contend; the default `int_rf_rports` is 3.
- Chisel names this physical parameter `gprReadPorts`; it must provide at least
  three ports so one scalar uop's three source lanes receive an atomic grant.
  Additional ports are legal and remain available for wider future issue.
- `I1` performs global read-port arbitration.
- Arbitration is oldest-first by ROB age within each STID, followed by a
  fair/RR grant across STIDs for shared ports. It never compares unrelated
  per-STID ROB ages.
- Failure to win arbitration cancels the in-flight attempt without deallocating
  the IQ entry.
- A younger row may not enter I1 while an older unresolved control row in the
  same STID remains resident. BRU classification is generic backend policy;
  Linx `FRET.STK` is additionally classified because its W2 result redirects
  block flow. Its exact `(STID, BID, RID)` frontier is retained until accepted
  central recovery, not merely until IQ release.
- Stores issue oldest-first within each STID even across physical IQ banks so
  FIFO STA/STD and STQ owners observe program-order store completion. This does
  not serialize independent STIDs or prevent eligible non-store work from
  bypassing an older store.
- Read admission is whole-uop atomic. Partial source grants are forbidden: one
  bank wins all source reads needed by its I1 attempt, while every losing bank
  clears only `inflight` and retries from its unchanged resident row.
- The current C++ model services every scalar read request and therefore has no
  scalar-port denial. Finite Chisel arbitration is an ISA-neutral physical
  upgrade; its cancellation and retry path must remain architecturally
  invisible and compare against the model at commit.
- A producer may request a write port before its complete side-effect bundle
  is authorized, but data and readiness mutate only on the request's explicit
  commit/fire event. Port reservation is not writeback.
- Physical write bandwidth is parameterized. Independent tags may use
  different ports in one cycle. Same-tag requests serialize with one explicit
  priority winner; a blocked producer retains its result-stage owner and
  retries without publishing ROB resolve or wakeup.
- A one-port configuration serializes all simultaneous producers. Wider
  configurations may complete independent writes together, but must reject
  duplicate committed writes and clear/write collision on one tag.
- Each committed GPR write stores data and publishes non-speculative P-tag
  wakeup by setting `ready_table_p` in the same edge. The same committed event
  is broadcast to resident issue queues by physical P tag, updating their
  per-source next-state readiness without waiting for a second ready-mask
  sampling edge. Request/grant without commit broadcasts nothing.
- A P wakeup in cycle N may make matching valid, non-issued P sources eligible
  for pick in cycle N+1, never in cycle N. T/U sources do not match this global
  broadcast; their point-to-point qtag path remains PE/STID scoped.
- `STD` has read ports but no write port.

### Load speculative wakeup, forward, and miss handling

- Loads produce speculative wakeup at `LD_E1`.
- Loads return data only at `LD_E4`.
- Loads publish their final ROB/LSU resolve at `LD_E5` after hit/miss/fault and
  replay classification is stable.
- Baseline hit data reaches its W3/RF-visible retention age at `LD_E6`; this
  does not delay the E4/W1 bypass.
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
- `E5` resolve does not extend speculative-data availability; consumers still
  use the E4 data/forwarding rule and are repaired if E5 resolves miss/replay.

### T/U point-to-point wakeup

- `P` wakeup is global broadcast by physical tag.
- `T` and `U` wakeup are point-to-point via
  `qtag = (phys_issq_id, entry_id)`.
- `phys_issq_id` is a physical IQ enum derived via spec templates at JIT.
- `entry_id` width is derived per IQ and packed to a uniform maximum width on
  the qtag wire.

## ROB and precise retirement contract (LC-MA-ROB-001)

The instruction ROB is the precise instruction-side authority. BROB is a
separate block-lifetime and engine-completion authority; it does not replace
instruction-row retirement.

The physical retirement/recovery pipeline uses `R0..R4`:

- `R0` captures execution, LSU, block, and exception resolve/completion inputs
  into ROB-visible state.
- `R1` reads the contiguous ROB head window, selects the maximal legal commit
  prefix, and generates the precise trap, nuke, interrupt, or boundary-flush
  decision from one coherent snapshot.
- `R2` publishes ordered `CMT` rows and the coherent `FLS` flush broadcast,
  advances commit/flush state, and launches rename, local-register, LSU,
  trace, and block-last cleanup.
- `R3` consumes the registered recovery/exception classification and performs
  owner-side recovery processing and cleanup.
- `R4` publishes the legal restart PC and restored architectural/frontend
  state to F0. Deallocation may trail R4 and remains a ROB operation, not
  W-stage writeback.

ROB rows progress through distinct ownership states:

```text
Free -> Allocated -> Renamed -> Issued -> Completed -> Retired -> Free
                       \---------------------> Fault/NeedFlush
```

Required behavior:

- Allocation is in program order. Completion may be out of order.
- Commit walks a contiguous prefix of completed head rows and stops at the
  first invalid, incomplete, faulting, or blocked row.
- Commit and deallocation are separate operations. A retired row remains
  resident until scalar-map release, local `T/U` relation cleanup, memory
  side effects, block-last processing, and trace publication no longer need
  its sidecars.
- A fault or nuke request may be discovered early, but the commit/recovery
  owner takes it only at the precise head point defined by the corresponding
  contract.
- Flush owns the bank mutation cycle, prunes younger rows with the request's
  declared comparison domain and scope, and rebases allocation/commit state
  without exposing a partially updated ROB. STID always qualifies a row;
  PE and thread identity qualify it when the request enables those scopes.
- Live duplicate instruction identities are illegal, including while a row is
  retired but not yet deallocated.

Each row retains the metadata needed by downstream owners rather than
reconstructing it from current queue heads:

- native ring `RID`, `BID_W`-bit `blockBid`, and any internal BROB wrap/age
  sidecar needed by the owning comparison domain;
- model/cross-check `bid/gid/rid` identity as a separate sideband;
- PC, raw instruction, length, STID/PE ownership, and checkpoint context;
- scalar and local-register destination/sequence sidecars;
- the all-row memory-order snapshot and memory/store identity where present;
- boundary, block-last, trap, and recovery metadata.

The separation between commit and deallocation is adopted from mature OOO
designs because Linx local-register and block cleanup are ordered side effects,
not bookkeeping that can be discarded when the instruction first becomes
architecturally retired.

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
- `BSTART.CALL` by itself does not implicitly write `ra`. A return label is
  materialized only by an architecturally explicit returning-call form or by
  an adjacent `SETRET`, `C.SETRET`, or `HL.SETRET` owner. A fused returning
  header is explicit materialization, not an implicit side effect of every
  call-type start marker.
- `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` are valid standalone macro block
  boundaries and remain visible in committed block metadata.
- Recovery targets must resolve to legal block starts. A bad target raises the
  precise architectural `E_BLOCK(EC_CFI)` envelope with
  `EC_CFI_KIND=CFI_BAD_TARGET`, `TRAPARG0=source PC/TPC`, and `ECSTATE.BI=0`.
  The legacy internal diagnostic `TRAP_BRU_RECOVERY_NOT_BSTART (0x0000B001)`
  must be translated before architectural trap export.

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

- BID is generated by BROB and is exactly the BROB slot index:
  `BID_W = ceil(log2(BROB_ENTRIES))`.
- `BROB_ENTRIES` is the power-of-two depth of each STID's BROB ring. The
  target default is 256 per STID, so the default BID is 8 bits.
- The cross-thread block identity is `(stid, bid)`. STID remains a separate
  field and must be carried on any shared command, response, completion,
  cleanup, or flush interface; it is not packed above BID.
- Wrap, generation, age, and DFX uniqueness are separate state. A conventional
  internal ring pointer may be `{wrap, bid}` with width `BID_W + 1`, but the
  wrap bit is not carried as part of BID.
- `block_uid`, when present, is trace/correlation metadata and must not be used
  as a wider architectural BID.
- `cmd_tag` equals BID and `cmd_stid` carries the separate ring selector. A
  fixed 8-bit command interface carries the default 8-bit BID directly;
  configurations with fewer entries zero-extend BID.
- Block completion is `scalar_done && (needs_engine ? engine_done : 1)`.
- `scalar_done` is triggered by both boundary forms, but for different dynamic
  blocks: retiring `BSTART` completes the old active `(STID,BID)` that it
  implicitly terminates, while retiring `BSTOP` completes the current active
  `(STID,BID)`. The BSTART row itself carries the new block's BID and must not
  mark that new block scalar-done.
- BID values must not be compared with unsigned `<`, `<=`, `>`, or `>=` to
  determine age across wrap.
- A canonical cleanup BID is resolved by the selected STID's BROB owner against
  its exact head/live-count window. The unique matching internal `{wrap,bid}`
  pointer defines the pivot and first-killed suffix. A migration-era wider
  transport may be compared with that result for diagnostics, but its upper
  bits are not recovery authority.
- Cleanup interfaces keep those identities structurally separate:
  `block_flush_bid` is exactly `BID_W`, while
  `block_flush_pointer_valid/block_flush_pointer` carry implementation-only
  wrap/generation context. BROB consumes the canonical BID. Rename and other
  pointer-age consumers use only the owner-resolved pointer. A global block
  cleanup without valid resolved pointer context must mutate neither owner.
- Each STID's BROB owns live block order through its head, tail, occupancy, and
  internal wrap state. On a redirect for `flush_stid` that preserves
  `flush_bid`, that ring produces the kill set for live slots from
  `successor(flush_bid)` through the pre-flush tail.
- Allocation applies only at the exact tail identity and advances only the
  tail. Retirement applies only to an exact resident completed head and
  advances only the head. Recovery truncates tail and occupancy to the first
  killed identity while preserving the head.
- Completion is persistent per-block metadata, not a retirement pulse. A
  younger completed block waits behind every older live block in its STID.
- A shared retire port selects eligible STID heads fairly and must hold its
  selected `(STID,BID)` stable under backpressure. Metadata free, head advance,
  occupancy decrement, and downstream block-commit publication are one fire.
- BROB derives a strong non-flush prefix independently for each STID from the
  exact commit head and bounded live count. The prefix stops at the first
  missing, stale, unsafe, or exception-bearing row. Its `head_bid` plus
  `prefix_count` is the ordering proof; the youngest safe BID is observability,
  not an unsigned age threshold.
- The initial promoted Chisel predicate is conservative: a row is safe only
  after full block completion and only when it has no exception. Earlier safe
  release for branch-resolved scalar non-memory blocks and authoritatively
  issued tile memory blocks requires explicit live metadata and may not be
  inferred from decode class alone.
- BID-carrying queues consume that BROB-qualified kill set, or an equivalent
  ring-age context, rather than reimplementing numeric BID ordering.
- A `(STID,BID)` slot may be reused only after its BROB row is free and no ROB
  row, engine command/response, memory side effect, or cleanup record can still
  name the prior occupant. If transport permits late/duplicate responses, it
  must carry a separate echoed transaction epoch; that epoch does not widen
  BID.

### Architectural block-completion abstraction

- For block completion semantics, LinxCore follows the ISA-visible canonical
  block-type domain
  `{STD, FP, SYS, MPAR, MSEQ, VPAR, VSEQ, TMA, CUBE, TEPL, FIXP}`.
- `STD`, `FP`, and `SYS` are equivalent in the two-layer completion model.
- Dynamic block instances collapse to exactly one of three architectural
  participant sets:
  - `{}` for empty/control-only scalar-family instances,
  - `{scalar}` for scalar-family instances with a real scalar body,
  - `{non-scalar}` for canonical non-scalar block types.
- Dynamic degeneration to `{}` is allowed only for scalar/control-family block
  types.
- Canonical non-scalar block types, including FIXP, always carry a
  `{non-scalar}` completion obligation.
- The architectural `{non-scalar}` participant has single-point resolve
  semantics: `BROB` and retirement observe one `non-scalar-done` event per
  block instance.

Normative block-type routing is:

| Block type | Completion participant / owner | Status |
|---|---|---|
| `STD`, `FP`, `SYS` | scalar path | promoted |
| `MPAR`, `MSEQ`, `VPAR`, `VSEQ` | target `VEC` | canonical route; current pyCircuit facade is reduced |
| `TMA` | TMA command/completion frontend; shared CSU/L2 transport | target split; reduced facade current |
| `CUBE` | target `CUBE` | canonical boundary; current pyCircuit facade is reduced |
| `TEPL` | target `TAU` typed tile-to-tile operation selected by `TileOpcode` | unsupported until TileOpcode/descriptor/completion behavior is promoted |
| `FIXP` | no owner | unsupported until a completion owner is promoted |
| `FENTRY`, `FEXIT`, `FRET.*` | CTU-expanded scalar child group | `{scalar}`, `needs_engine=0`; scalar done when the final template row is eligible after all children |

An unsupported type fails explicitly before issue; it must not alias scalar or
another engine and must not leave a BROB entry waiting forever.

### Block lifecycle rules

- `BSTART` carries the new `(STID,BID)` of the new block.
- An in-body BSTART same-PC head reentry reuses that allocated identity through
  an R4/F0 marker-reentry token. It does not allocate a duplicate BROB/ROB row,
  duplicate trace, or fire scalar completion again.
- `BSTOP` retires only when the active block is no longer blocked by engine
  completion.
- Block-private state is released by an `(STID,BID)`-qualified local
  block-commit event, not by opcode name alone. That event may follow an
  explicit `BSTOP`, an implicit termination by the next `BSTART`, or a
  template completion boundary.
- Local `T/U` cleanup order is: retire/relation commands, relation-map clean,
  then selected-BID/STID local block commit. Only consecutive retired local
  mapping rows at the deallocation head may be freed.
- Only the oldest architecturally eligible block within each STID may retire;
  shared retire bandwidth arbitrates fairly across eligible STID heads.
- Younger engine-backed work must remain cancellable under normal redirect and
  flush rules.

The C++ model carries `ROBID { val, wrap }` as a composite identity on some
interfaces. The narrower LinxCore hardware BID is an intentional target
contract, not a claim that the model already exposes the same wire shape. A
model adapter must map `val` to BID and retain `wrap` only as ring-order
sidecar/context. Current Chisel/pyCircuit paths that encode uniqueness above a
slot or expose a 64-bit `blockBid` are legacy, non-conforming implementations.
They remain partial evidence until migrated to `BID_W`, ring-qualified flush,
per-STID active state, and stale-response-safe reuse.

Detailed BROB and block-fabric behavior remains documented in:

- `rtl/LinxCore/docs/architecture/stages/BROB.md`
- `rtl/LinxCore/docs/architecture/block_fabric_contract.md`

## Privilege/trap contract (LC-MA-PRV-001)

- LinxCore uses the LinxISA Access Control Ring (ACR) service-request model; it
  does not implement an ARM/RISC-V-style U/S plus `SRET` contract.
- `ACRE` requests an ACR transition at block commit. `ACRC` creates a
  synchronous `SERVICE_REQUEST` immediately after execution and follows the
  ISA-defined explicit-terminator restriction.
- Trap entry saves `CSTATE` into the managing ring's `ECSTATE`, records block
  and resume PCs in `EBARG`, records `TRAPNO/TRAPARG0`, disables interrupts,
  resets `BARG`, and vectors `BPC` to the managing ring's event base.
- When `ECSTATE.BI=1`, return restores the body resume `TPC` and the
  profile-defined second-layer block snapshot, including `BSTATE`, `BARG`,
  `TQ/UQ`, and continuation state. Header-context return resumes at the saved
  block start.
- `EBREAK` is a precise architectural breakpoint trap by default. Semihosting
  is an explicit runtime opt-in and must not silently replace the trap.
- Trap-envelope and SSR-visible side effects must remain coherent with
  commit-visible behavior.
- Precise exception reporting is required under superscalar retirement.

These are ISA obligations. Full ACR/ECSTATE/EBARG/BSTATE, MMU, and interrupt
owners are not yet proven complete by the reduced RTL paths.

## MMU contract (LC-MA-MMU-001)

- Translation success and failure must produce deterministic trap envelopes.
- MMU behavior must remain aligned with the `v0.57` privileged contract wording.
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

LinxISA defines TSO and exposes BCC and MTC issue channels inside one
architectural ordering domain. The single-width, strictly LSID-ordered scalar
LSU is a conservative LinxCore design policy for the closure baseline; it is
not an additional ISA guarantee. A future speculative issue policy may replace
it only with equivalent TSO, precise recovery, and forward-progress evidence.

### Memory-order identity

- Every scalar decoded row captures the current pre-increment memory-order
  snapshot. Only load, store, atomic, and other cataloged memory operations
  consume and advance the LSID counter.
- A memory row carries its allocated LSID through ROB, LSU, replay, and flush
  ownership. A non-memory row retains the snapshot as a retire/recovery
  watermark but does not allocate a memory operation.
- The all-row watermark is an internal ROB/LSU sidecar. It must not be added to
  the architectural commit payload merely for implementation convenience.
- The strict baseline issues a scalar memory operation only when its LSID
  reaches `lsid_issue_ptr`. Flush rebases allocation, issue, and completion
  state so a squashed ID cannot deadlock the pointer.
- Flush requests declare their comparison scope. STQ/load pruning may include
  STID, PE/thread scope, block-only, group, or default STID+BID+LSID matching;
  a generic `(BID, LSID)` predicate must not replace the typed flush contract.
- LSID comparisons are wrap-qualified. An implementation either carries an
  internal LSID wrap/generation sidecar or permits counter reset/reuse only
  after that STID's memory queues and recovery records are quiescent; plain
  unsigned LSID `<` across wrap is forbidden.

### Store path: dispatch, STQ, and SCB

The canonical scalar LSU is one parameterized owner. Its queue capacities are
implementation choices and must not change architectural identity widths:

- ROB identity capacity defines the internal BID/GID/RID slot-plus-wrap width
  carried by store requests, flush requests, STQ rows, commit-queue rows, and
  SCB drain requests. LSID is not a ROB slot identifier: its canonical width is
  `lsidWidth` and it remains independent of ROB and queue capacities.
- STQ, store-commit, SCB, LIQ, ResolveQ, MDB SSIT, MDB command/output, MDB
  wait-plan, load-return queue, return-pipe, cache-line, and MapQ resources are
  independent sizing parameters.
  No implementation may infer ROB identity width from any queue capacity.
- Physical STQ row indices and masks use `stqEntries`; store-commit FIFO
  pointers use `commitQueueEntries`; issue lanes use `commitIssueWidth`; SCB
  row indices use `scbEntries`. A request crossing these owners carries its
  physical STQ index separately from its ROB-sized BID/GID/RID and full-width
  LSID ordering identity.
- The Chisel reduced live path must source these sizes from `ScalarLsuParams`.
  Compatibility defaults may make capacities equal, but unequal-size
  elaboration is a required contract test. A local compressed `ROBID` view of
  LSID is transitional implementation state and must not define ordering,
  recovery, forwarding, or the golden interface.
- R670 closes the first complete full-width transport: decode/ROB
  `lsidWidth` flows through store dispatch, split-half merge identity, STQ row
  residency, scalar early-safe commit authorization, the sorted store-commit
  FIFO, split drain requests, SCB admission, and the committed-memory overlay.
  Same-block store age uses modulo serial arithmetic with explicit half-range
  ambiguity; BID remains ROB-sized and cross-block age remains BROB-owned.
  The compressed STQ LSID projection is retained only for still-unconverted
  typed recovery and load forwarding/replay/MDB boundaries. Those consumers
  remain an implementation gap and may not be cited as full LSID closure.
- R671 promotes full-LSID-capable central recovery and scalar-redirect STQ
  pruning. `FullBidFlushReq`, retained recovery
  queues, source arbitration, class merge, `RecoveryCleanupIntent.flush`, and
  `FlushReq` carry `lsIdFullValid` plus the parameterized full LSID beside the
  transitional ring projection. Scalar redirects capture execute's all-row
  full LSID before retention. `STQFlushPrune` uses `(STID, BID, full LSID)`
  modular order for non-BID scalar cleanup and refuses to prune when full-LSID
  authority is absent or exactly half-range ambiguous. BID-only cleanup does
  not require LSID. Physical STQ size, ROB ring width, and LSID width remain
  independent through the composed decode/recovery/store path.
- Recovery arbitration continues to use typed Linx BID/RID priority; LSID does
  not replace block age, select across STIDs, or add an architectural ordering
  mode. The new full field is a payload authority for memory-row consumers.
  Recovery sources from unconverted owners leave `lsIdFullValid` clear and may
  not consume the scalar-redirect recovery claim. They never supply a
  placeholder full LSID to authoritative STQ pruning.
- R672-A promotes the canonical scalar load graph to full-LSID authority.
  `LoadInflightAlloc`, LIQ/LHQ/ResolveQ rows, MDB conflict and command queues,
  SSIT dependency offsets, wait-store metadata, retained MDB recovery, and
  scalar return queue/W1/W2 payloads preserve validity plus the parameterized
  full value. Same-BID ResolveQ cleanup/retirement and MDB conflict selection
  use modular `LSIDOrder`; same-BID group cleanup also requires full authority,
  while cross-BID age remains ROB/BROB-ring-owned. MDB wait mutation is blocked
  until the predicted store has a valid full LSID. BID/GID/RID widths do not
  change. R672-B supersedes the former reduced forwarding boundary.
- R672-B promotes the reduced replay snapshot request/token/response graph and
  reduced forwarding order.
  Live-load capture, wait-store relaunch candidates, LIQ allocation, request
  FIFO rows, the accepted-query token, response FIFO rows, and
  wait-store response state retain `CoreParams.lsidWidth` plus validity. Their
  same-BID selective cleanup uses `STQFlushPrune.matchesFlush` and refuses
  missing authority. The projection-only cleanup helper is deleted. Physical
  cluster/entry routing and ROBID-shaped compatibility fields remain distinct
  from canonical memory-order authority. Forwarding retains BID/BROB order
  across blocks; within one BID, eligibility, nearest-store choice per byte,
  and the final wait-store choice require full authority and use modular
  `LSIDOrder`. Missing or exactly half-range-ambiguous comparisons fail closed
  and are observable instead of falling back to the projection.
- The scalar LSU owns speculative STQ state and committed SCB state beneath one
  top-level boundary. A core is idle only when both retirement state and the
  LSU's speculative/response state are quiescent.
- Flush behavior is the typed Linx `FlushBus` contract, including STID,
  PE/thread scope, BID/group selection, and wrap-qualified identity. Generic
  ARM exception levels, condition flags, load/store-exclusive monitors,
  acquire/release opcode semantics, and ARM barrier encodings are not part of
  this owner and must not be imported with ISA-neutral queue mechanisms.
- The integrated Chisel owner contains the STQ-to-SCB store path, the
  LIQ-to-ResolveQ active/resolved load lifecycle, and the scalar MDB
  conflict/SSIT/fanout/wait-mutation path. `ScalarLSULoadPath` also owns final
  scalar data extraction, per-lane launch reservations, and atomic
  ResolveQ+LRET publication through the scoped load-return queue bank. It also
  owns the parameterized scoped W1/W2 return pipeline and its atomic
  resolve/writeback/wakeup rendezvous. The reduced timing path retains its
  detailed single-pipe proof surface until the live sinks consume the canonical
  outputs. The miss queue, bounded refill transport, and parameterized scalar
  L1D arrays are now canonical; memory classification remains staged. R675
  adds scalar cross-line ownership beneath the same load identity, and R676
  makes both phases use the shared L1D owner.
- R675 splits a scalar 1/2/4/8-byte request that crosses one cache-line
  boundary into two phase-local requests while retaining the original Linx
  `(PE, STID, TID, BID, GID, RID, LSID, load ID)` identity in one LIQ row. The
  first phase covers `[byte_offset, line_bytes)` and the second covers
  `[0, size - first_size)`. Each phase independently uses forwarding, miss
  coalescing, refill, and replay against its aligned line address.
- The LIQ retains the completed first line and byte-valid metadata, but the
  first phase is never an architectural hit: it emits no ResolveQ record,
  LRET, writeback, or wakeup. Only a complete second phase may assemble the
  little-endian scalar value, apply the original sign/zero extension, and
  atomically publish one ResolveQ+LRET transaction.
- The current Chisel owner launches the two phases sequentially. This is an
  architectural match and a throughput divergence from LinxCoreModel's two
  cross-half entries and `processCrossRtn` merge. A future parallel launcher
  may replace the scheduling policy only if it preserves one final result,
  per-line forwarding/miss ownership, typed recovery, and identical ordering
  identity. It must not create a second architectural load.

- A scalar store splits into address (`STA`) and data (`STD`) work with one
  shared instruction, BID, RID, SID, and LSID identity.
- Dispatch reserves the two halves atomically. After dispatch, address and data
  may execute and merge into STQ independently; a blocked address allocation
  must not prevent a complementary data half from merging into an existing
  row when the typed readiness rules allow it.
- STQ owns speculative, flushable store state. Address readiness, data
  readiness, byte mask, memory type, and row identity remain explicit.
- SCB accepts a store only after a strong non-flush decision proves that no
  branch recovery, trap, exception, or interrupt can still cancel it.
- A committed ROB store event may arrive before its block enters the strong
  non-flush prefix. The store owner retains the event with its full block BID
  and rechecks membership against the selected STID's `(head_bid,
  prefix_count)` window.
- Scalar STQ liveness has a second, model-derived proof. A ready scalar row in
  the exact commit-head `(STID, BID)` block may request `Wait -> Commit` when
  its wrap-qualified LSID is strictly older than the ROB head's LSID snapshot.
  The ROB head is the oldest instruction that can still redirect or fault, so
  an older scalar store is no longer recoverable even while the block remains
  incomplete. This proof scans resident rows directly and must not depend on a
  previously observed store-commit identity or on STA/STD merge timing.
- The strong-prefix and oldest-ROB/LSID predicates are alternative
  authorizations. Both require exact owner identity and typed recovery state;
  BID magnitude and plain unsigned LSID comparison are forbidden. The
  oldest-ROB predicate applies only to scalar IEX rows. Tile/template stores
  require their own issued/non-flush proof and cannot reuse the scalar rule.
- SCB owns committed, non-flushable, physical-cacheline coalescing. It must not
  merge new bytes into a row that has issued ownership traffic and is awaiting
  its response.
- An accepted final SCB fragment, not a standalone drain attempt, authorizes
  the matching committed STQ row to free. Request acceptance is not fence- or
  store-completion evidence; the required WriteResp or platform-equivalent
  completion must be observed where architectural completion depends on it.
- Committed stores drain in program order. Store coalescing may reduce physical
  writes but may not reorder architectural store visibility.
- Scalar LSID, load-ID, and store-ID counters are independent per STID.
  Accepted scoped recovery mutates only the selected lane; reset/restart may
  clear every lane.
- BROB separately assigns contiguous block store ranges. Its per-STID range
  cursor publishes a stable start ID for the exact resident cursor block,
  stops while that block's store count is uncertain, and advances through
  consecutive count-certain blocks without unsigned BID comparisons.
- Recovery reuses the first killed block's saved start ID when an already
  assigned suffix is removed. Store ranges do not authorize SCB admission;
  either the strong block prefix or the exact scalar oldest-ROB/LSID predicate
  must authorize STQ promotion.
- Explicit template/tile store counts use a retained, exact `(STID, full BID)`
  publication boundary. The event is admitted only inside the live BROB
  window, survives range-sink backpressure, and is canceled by the same
  accepted killed-suffix recovery as its row. Same-value duplicates are
  idempotent and conflicting duplicates are errors.
- Scalar block closure remains non-backpressurable. A different-block source
  collision publishes scalar closure first; a same-block explicit event is the
  authoritative range count. Count certainty does not imply engine completion
  or strong non-flush safety.

### Load path and forwarding

- The active-load window (`LDQInfo`/`LoadInflightQueue`, historically called
  `LIQ`) owns misses, wait-store state, replay, refill, and relaunch.
- Every active-load row carries PE, STID, TID, BID, GID, RID, and load LSID.
  Typed precise flush applies the same scope and ring-qualified comparison to
  LIQ and ResolveQ. A Boolean hard flush is reserved for reset/restart or a
  recovery event whose precise identity is unavailable.
- A precise flush prunes only matching active rows. It cancels resident E3/E4
  work and returns a surviving pipeline row to `Wait`; no survivor may remain
  stranded in `Repick` after its pipeline payload is discarded. The allocation
  cursor rebases to the first pruned slot with a changed load-ID generation so
  stale pre-flush observations cannot impersonate the replacement row.
- The resolved-load queue (`ResolveQ`/`LoadResolveQueue`, historically called
  `LHQ`) retains the address/byte metadata required to detect a later older
  store conflict. After applying an R2 commit batch, the ROB publishes one
  cumulative commit frontier per affected STID: the first uncommitted position
  as `(STID,BID,LSID)` using the all-row pre-increment LSID snapshot (or the
  equivalent tail frontier when no row remains). ResolveQ removes rows strictly
  older than that frontier by
  `(BROB_age(row_bid), row_lsid) <
  (BROB_age(frontier_bid), frontier_lsid)`. A later frontier subsumes an older
  one, so multiple commits coalesce to the most advanced frontier per STID
  without losing cleanup; no comparison crosses STIDs.
- LIQ-to-ResolveQ and LIQ-to-LRET transfer are one scalar-LSU transaction. An
  E4 hit may publish only when both ResolveQ and its selected LRET lane accept
  the same identity in the same cycle. After both sinks accept, the owner
  clears that exact LIQ slot; a parent top must not recreate either handoff
  with an independent pending bit or sideband identity.
- A load snapshots the youngest eligible store identity when allocated.
- Store-to-load forwarding is byte granular. For every requested byte, choose
  the nearest older eligible store within the same STID/PE-thread domain by
  `(BROB_age(bid), LSID)` order. BROB age is defined only in that STID's ring.
  If a
  selected byte is not data-ready, the load waits or replays; it must not fall
  through to an older value for that byte.
- Cache, SCB, refill, and store-forward data may merge only with explicit byte
  validity and matching live-row identity.
- For a scalar cross-line row, forwarding, SCB/store wakeup, miss allocation,
  and refill matching use the active phase's aligned line address and
  phase-local byte mask. The original address and size remain unchanged for
  architectural return and ResolveQ conflict overlap. A first-line refill may
  not satisfy a second-line phase, and a second-line store may not merge into
  first-line state.
- Each sequential phase is a normal LIQ launch and therefore reserves and
  releases miss and return capacity independently at E4. A first-phase E4 hit
  releases its launch reservations without allocating return-queue state. A
  second-phase miss enters the ordinary parameterized miss queue and returns
  through the retained refill transport before relaunch.
- Hard Linx recovery clears both phase state and retained first-line data.
  Typed precise recovery prunes a matching row by the existing full identity;
  a surviving row preserves completed first-line state. If its active phase
  occupied E3/E4, the payload is canceled and the same phase returns to
  `Wait`. ARM exception levels, memory types, exclusives, barriers, and
  acquire/release behavior are not introduced by this mechanism.
- `ScalarL1D` is the single scalar data-cache array owner. `l1dSets`,
  `l1dWays`, and `lineBytes` are independent parameters; none is derived from
  ROB, LIQ, STQ, SCB, miss-queue, or return-queue sizing. Each resident way
  retains an aligned physical line address, full-line data, readable validity,
  writable permission, dirty state, and replacement age.
- A scalar LIQ launch performs one combinational tag/data lookup for the active
  line phase. The L1D response, SCB return, and speculative STQ forwarding are
  merged by the registered E2-to-E3 load-forwarding boundary. A tag miss
  returns an explicit empty byte-valid mask; externally injected base-line
  data is not a canonical load source.
- Refill installation has priority over load and committed-store array access.
  The refill head remains retained in `LoadRefillTransport` while L1D cannot
  accept it. A refill first searches for the same line. A duplicate returns the
  resident data to LIQ and may add write permission, but never overwrites
  resident bytes or clears dirty state with a potentially stale lower-memory
  response.
- A new line selects the first invalid way; otherwise it selects the least
  recently used way. Any valid victim is published with line address, data,
  and dirty state and the refill remains backpressured until the eviction owner
  accepts that payload. Silent clean or dirty replacement is forbidden.
- The committed SCB path queries the same tags. A tag hit without write
  permission emits an ownership-upgrade request; a writable hit applies the
  SCB byte mask to the resident line and marks it dirty. The cache array does
  not infer permission from Linx opcodes, block boundaries, or ARM memory
  types. Lower-memory/coherence logic grants permission explicitly. When an
  accepted SCB response is decoded as an upgrade for a resident line, the L1D
  sets that line writable before the SCB retries its lookup. A write response
  for a missing line still requires the staged lower-memory refill-data path;
  permission alone must not allocate uninitialized cache data.
- L1D contents are physical, non-speculative state. Typed Linx recovery and
  hard backend restart prune LIQ, miss, refill-transport, and speculative store
  ownership as specified, but do not invalidate cache lines. Reset initializes
  every line invalid. Explicit coherence, cache-maintenance, and platform reset
  messages are separate future interfaces and must not be synthesized from a
  BID, LSID, exception level, barrier, or acquire/release operation.
- Cacheable scalar L1 misses enter a parameterized load miss queue before any
  lower-memory request is emitted. Queue depth is independent of LIQ, ROB,
  STQ, and return-queue capacity. Every accepted E2 launch reserves worst-case
  miss capacity until its E4 result is known, so an E4 miss cannot become an
  untracked one-cycle event.
- One miss entry owns one aligned cache line and one slot-plus-generation
  transaction identity. The first miss allocates the entry and an irrevocable
  FIFO request token; later same-line misses coalesce as dependent LIQ
  identities and do not emit duplicate lower-memory reads. Backpressure holds
  request valid, transaction identity, line address, and metadata stable.
- Each dependent retains LIQ slot plus generation, PE, STID, TID, BID, GID,
  RID, projected load LSID, and full-LSID validity/value. Precise recovery
  prunes dependents with the canonical Linx load flush predicate. It does not
  cancel an already issued cacheable read: an entry with no surviving
  dependents becomes an issued orphan and remains reserved until its exact
  response arrives. An unissued empty entry is discarded without traffic.
- Lower-memory responses match both miss slot generation and line address.
  A stale or malformed response is consumed without LIQ wakeup and is reported
  as a protocol diagnostic; it cannot free or otherwise mutate a live miss
  entry. A matching valid read response frees the entry and broadcasts one
  full-line refill to the LIQ,
  where only live cacheable scalar rows on that line may relaunch.
- Exact miss refills and external cache/refill packets enter one parameterized
  dual-ingress transport before LIQ wakeup. Its depth is independent of LIQ,
  miss queue, ROB, STQ, return queues, and LSID width. Both sources may be
  accepted in one cycle; miss-queue data occupies the older same-cycle FIFO
  position and external data occupies the next. A simultaneous legal ingress
  is not a collision or protocol error.
- The refill transport emits at most one stable line packet per cycle and
  backpressures both producers from post-dequeue capacity. An exact valid-read
  miss response cannot free its miss entry until its refill packet is accepted
  into this retained transport. Hard flush clears buffered packets; typed
  precise recovery holds ingress/egress for the recovery cycle but preserves
  physical line data for surviving LIQ rows.
- Hard reset/restart removes dependents and unissued work, but issued
  transactions retain orphan identity until their response is drained. This
  prevents a pre-restart response from aliasing a post-restart miss. Device,
  MMIO, tile, cache-maintenance, and other side-effecting memory classes must
  use their dedicated non-coalescing owners and are not admitted to this queue.
- Load speculation follows the `LD_E1` wakeup / `LD_E4` data contract above.
  `miss_pending` remains asserted until the affected load has been relaunched
  after refill and returns through a non-miss path.

### Load-return publication and IEX handoff

- Final scalar return publication is queue-latched. LSU data return never
  drives ROB completion, RF writeback, or issue wakeup through an unretained
  combinational pulse.
- Each return carries PE, STID, TID, BID, GID, RID, load LSID, PC, address,
  size, destination, data, speculative-wakeup state, stack state, and selected
  return-pipe identity. RID selects the resident ROB row; STID selects the
  scalar thread lane; BID/GID/LSID remain ordering and recovery identities.
  These roles are not interchangeable.
- `loadReturnQueueEntries` sizes each retained lane independently.
  `loadReturnPipeCount` and `stidCount` define a matrix of per-STID,
  per-return-pipe queues. Neither parameter changes ROB identity width.
- Every accepted scalar launch reserves one slot in its exact STID/return-pipe
  lane. Resident entries plus in-flight reservations may not exceed that
  lane's depth. E4 releases the reservation whether it hits, misses, or
  replays; a hit replaces the reservation with one resident LRET entry in the
  same transaction. Flush cancels pipeline work and its reservations together.
- Return-pipe identity is allocated with the LIQ row and carried through E4.
  The queue canonicalizes the resident payload pipe field from the accepted
  target lane; duplicate metadata may not redirect a return.
- Publication uses two readiness phases. Pre-admission credit is computed from
  the selected STID before return-pipe choice, so queue capacity cannot form a
  cycle through pipe selection. Final acceptance validates the selected pipe
  and commits the payload to exactly one queue. A published return that is not
  accepted by that queue is a protocol error.
- A full queue backpressures only its selected STID/pipe lane. Independent
  lanes retain their own credit. When several lanes target a shared IEX
  receive port, drain arbitration is round-robin so one STID cannot
  indefinitely monopolize return bandwidth.
- An empty return queue does not bypass directly into IEX. Enqueue and dequeue
  are distinct registered phases, matching the model `SimQueue` boundary and
  preventing ready/payload combinational cycles.
- IEX drains a return only when the target E4 residency slot can retain it.
  The payload then advances through registered E4, W1, and W2 stages. W2 is
  the atomic side-effect point: required ROB resolve, GPR writeback, and
  destination wakeup must all be ready before the slot clears.
- The canonical W1/W2 owner is a vector sized by `loadReturnPipeCount`. Shared
  LRET drain selects a W1 lane fairly from lanes that are empty or advancing;
  each W1 lane advances only into its paired W2 lane when W2 is empty or
  completing. W2 completion, W1 advance, and a new W1 insertion may coincide
  without dropping or duplicating a return.
- When physical resolve/writeback/wakeup bandwidth is shared, a second fair
  arbiter selects one resident W2 lane. Only that lane observes sink readiness;
  the arbiter advances after the atomic resolve fire, so a blocked lane cannot
  be skipped or duplicated and all W2 lanes eventually receive service.
- Before LRET dequeue, IEX queries the exact scoped ROB row. A missing row
  holds the queue head; a present `NeedFlush` row consumes and drops the stale
  return without entering W1. Normal admission retains the complete
  PE/STID/TID plus BID/GID/RID/load-LSID identity through W1 and W2.
- `LinxCoreTop` routes that lookup to the resident reduced ROB using the full
  slot-plus-wrap RID. External execute completion has fixed priority on the
  reduced ROB's single completion port; a colliding scalar W2 return keeps its
  slot and retries. Scalar W2 retains the full RID and the ROB revalidates slot
  plus wrap in the same cycle as completion-bit mutation; admission-time lookup
  alone is not completion authority. A free, stale, or invalid RID withholds
  resolve-ready. Legal external contention must target a different slot; a
  same-slot external/scalar candidate is rejected as duplicate producer
  ownership because the legacy external port cannot prove generation or
  idempotence. The ROB completion pulse is emitted only from the selected source,
  and completion becomes visible to retirement on the next cycle.
- `LinxCoreTop` also routes the selected W2 GPR destination and data into the
  canonical scalar GPR/ready-table sink. The sink may grant a port while W2 is
  resident, but it asserts write commit only when exact ROB resolve and every
  required wakeup side effect fire. Same-tag external writeback holds W2;
  independent tags may use separate configured ports. RF data, P-tag readiness,
  and ROB completion therefore become visible from one accepted W2 event.
- This GPR sink handles only `DestinationKind.Gpr`. Until their point-to-point
  local-link bank and qtag wakeup owner is connected, T/U destinations are not
  accepted and raise an explicit backend contract error. They must neither
  stall silently forever nor be treated as global P-tag writes.
- Typed precise recovery suppresses stage movement and side effects for that
  cycle, prunes only matching W1/W2 entries, and preserves older or independent
  lanes. Hard reset/start/restart may clear the complete pipeline.
- Non-speculative, non-stack scalar returns may publish the normal memory
  wakeup when stable data is retained. Speculative wakeup is a separate early
  prediction and must be canceled or repaired on miss/replay. T/U local-link
  wakeup remains identity-scoped and may occur at W2.
- Typed Linx recovery selectively compacts matching return entries according
  to PE/STID/TID and BID/GID/LSID scope while preserving older and independent
  entries in FIFO order. Reset, restart, or an unscoped fatal recovery may
  hard-clear every lane. Precise recovery must not be implemented as a global
  queue clear merely because it is simpler.
- The reusable mechanisms are retained queues, explicit credit, registered
  pipe residency, fair drain arbitration, precise pruning, and atomic W2
  side effects. ARM exception levels, condition flags, exclusive monitors,
  acquire/release encodings, barrier opcodes, and ARM-specific return state do
  not participate in this Linx load-return contract.

### Memory disambiguation and precise recovery

- MDB is the Memory Disambiguation Buffer/store-set predictor. It is not a
  generic miss-data buffer.
- A scalar store-arrival conflict requires the same STID/PE-thread ordering
  domain, byte/address overlap, and an older-or-equal store according to that
  STID's BROB ring age plus LSID within the block.
- An unresolved active load may be marked wait-store. A resolved load or
  ResolveQ row may be selected as a recovery candidate.
- A same-BID violation within one STID requests an inner replay/flush. A
  cross-BID violation within that same STID marks the offending load for a
  load-attributed nuke. Blocks from different STIDs have no BROB age relation
  and are not classified by this predicate.
- MDB may predict waits and learn conflicts, but it does not own architectural
  recovery. A nuke is taken only when the marked load reaches the precise ROB
  head. That row's `(STID,BID)` identifies the surviving block; the selected
  BROB ring uses its current context to flush younger live blocks.
- Scalar load allocation enqueues one PC-keyed MDB lookup before first launch.
  A hit is retained at the LU/SU fanout boundary until the named live LIQ row
  accepts its wait-store mutation; a queue-full predictor may therefore
  backpressure scalar load allocation rather than drop lookup state.
- An accepted address-bearing scalar store feeds active-LIQ and ResolveQ
  conflict detection. Store insertion is backpressured when the MDB record or
  multi-row wait-plan queues cannot retain the event. Every unresolved active
  conflict bit is retained and drained deterministically; the implementation
  must not collapse a multi-row wait mask to one pulse.
- Store-probe intent is visible before STQ acceptance so conflict-dependent
  recovery credit can participate in readiness without a combinational loop.
  Predictor, wait-plan, and recovery side effects use a separate commit pulse
  from accepted STQ insertion. A full recovery queue therefore blocks only a
  conflicting probe, not an unrelated address-bearing store.
- Reduced timing adaptation may retain accepted probes until a related
  unresolved LIQ row reaches ResolveQ, but that adapter must be a finite FIFO,
  not a replaceable latest-value register. Replay credit and canonical MDB
  transaction readiness both participate in address-bearing STQ admission;
  data-only fragments bypass the address-side gate. Every accepted probe is
  either consumed live or retained and replayed exactly once in FIFO order.
- Same-BID conflict publication emits a typed Linx `InnerFlush`; cross-BID
  conflict publication emits `NukeFlush`. The request carries the load's
  PE/STID/TID, BID/GID/RID/LSID, scalar execution-engine class, and fetch-PC
  validity. Conflict training, wait-plan capture, and recovery-report enqueue
  are one accepted store transaction. `mdbRecoveryQueueEntries` sizes the
  retained report queue; a full queue backpressures address-bearing store
  insertion rather than dropping recovery.
- `MDBConflictTransactionControl` is the admission rule inside the canonical
  scalar MDB owner. Required record,
  multi-row wait-plan, and recovery sinks must all be ready before any derived
  valid asserts; sinks not required by the current conflict decision do not
  reduce readiness. R659 applies the complete `ScalarLSUMDBPath` owner to the
  live reduced top; the former delivery-only composition has been deleted.
  Conflict detection, SSIT/fanout, multi-row waits, failed-wait decay/delete,
  and retained recovery now have one implementation.
- pyCircuit implements the same parameter-neutral admission equation and is
  checked against the Chisel generated scenario set. This parity covers atomic
  sink valids and conditional readiness only; retained report storage,
  owner-backed STID watermark selection, and exact full-BID promotion remain
  Chisel-ahead and are declared as pyCircuit gaps rather than inferred parity.
- MDB recovery reports set `immediateFlush=false`. The oldest-signal/precise
  ROB-head owner in `ScalarLSU` retains the report until wrap-qualified BID/RID
  age is eligible. The report carries the conflicting load PC as its exact
  Linx64 restart TPC whenever `fetchTpcValid` is set. Before cleanup acceptance,
  the allocator/ROB owner must
  recover the row's full implementation generation sideband through an exact
  `(BID,GID,RID,PE,STID,TID)` lookup. MDB never reconstructs that sideband from
  slot bits and never directly deletes ROB rows.
- The full-BID lookup is RID-indexed and side-effect free. The row must be
  resident, every identity and scope field must match, `blockBidValid` must be
  set, and projecting the stored full sideband back to ring ROBID must reproduce
  the request BID. Missing, stale, cross-scope, or inconsistent lookup results
  retain the report and authorize no cleanup.
- `RingFullBidRecoveryBridge` requires the lookup result to echo the current
  request before promoting the report to `FullBidFlushReq`. The central
  boundary requires every BCC, IEX, PE, and LSU producer to enter an
  independently retained source slot. R639 implements the arbiter; R640
  connects the production `ScalarLSURecoverySource` owner to it in the real-ROB
  harness and removes local LSU cleanup selection. R649 connects that same
  production owner in the live reduced top: a parameterized report queue
  selects owner-backed oldest BID/RID by report STID, requests exact resident
  full-BID lookup, and releases its head only when central recovery accepts the
  promoted source. R658 removes the duplicated STID-selection policy from that
  reduced composition. `ScalarLSURecoveryBoundary` is now the canonical,
  parameterized boundary used by both `ScalarLSU` and
  the reduced canonical-MDB composition: it selects only the report STID's watermark,
  suppresses lookup for an invalid STID, and delegates age and exact full-BID
  promotion to `ScalarLSURecoverySource`. `ScalarLsuParams.stidCount` sizes the
  canonical LSU lanes independently of queue capacities. R641 adds the class merge
  between that arbiter and cleanup: global flush, global replay, and PE-scoped
  lanes are retained per STID, same-STID `CheckOlder` cancellation and
  `mergeSignal` transformation are modeled, completed-oldest global replay is
  rejected, and the selected request is staged through an irrevocable
  downstream slot. R642 adds parameterized retained adapters for BCC miss
  prediction, IEX slow insert, IEX IQ-stall replay, and PE result mismatch.
  They publish `MissPredFlush`, immediate `NukeFlush`, configurable-threshold
  `FastReplay`, and PE-scoped `InnerFlush`, respectively. Every adapter requires
  the trigger owner to supply the exact full block BID; missing identity blocks
  publication rather than incrementing a ring BID or reinterpreting model
  `fbid`. PE inner recovery also carries the exact 64-bit restart TPC from the
  compare owner through class merge and registered cleanup. A target-valid bit
  without its target is not sufficient. R657 groups these adapters under one
  parameterized production bank and appends its four stable lanes to
  `DecodeRenameROBPath` after existing external lanes. The IQ watchdog uses a
  dedicated identity owner to select one STID's valid BROB commit cursor and
  increment the full pointer, not the canonical BID slot. Upstream live BCC,
  IEX, and PE event generation remains open; retained producer ownership and
  backend-fabric connection do not.
- R659 makes load admission and MDB lookup one transaction in the live reduced
  top. MDB command credit participates in LIQ allocation readiness, and the
  exact accepted allocation payload supplies PC, Linx identities, address,
  size, and thread scope. The implementation must not allocate a LIQ row and
  reconstruct or drop its lookup on a later pulse. Source-return and MDB row
  mutations share one arbiter. MDB-only requests use the canonical pre-launch
  `Wait` policy without SCB-return proof; source-return requests retain their
  stricter `Repick` and SCB ordering. Registered MDB store wakeup has priority
  at the LIQ wake port, while a displaced resident-store wakeup remains held.
  R645 adds the pyCircuit class owner with the same parameterized per-STID
  global-flush/global-replay slots, per-PE slots, `CheckOlder` cancellation,
  `mergeSignal` transformation, completed-oldest replay drop, invalid-scope
  rejection, fair STID selection, and irrevocable output behavior as the
  Chisel owner. The shared gate requires both generated RTL probes to declare
  and pass one named scenario set. This is class-level convergence only:
  pyCircuit source arbitration, exact producer composition, registered cleanup,
  and resident ROB/BROB consumers remain future integration boundaries.
  R646 promotes the Chisel backend boundary from probe-local wiring to a
  reusable `RecoveryBackendControl` owner. The owner routes the LSU's exact
  full-BID lookup through the resident ROB, appends the LSU report to the
  parameterized non-LSU source set, and applies `robPruneValid` only on the
  shared cleanup-intent handshake. `DecodeRenameROBPath` instantiates this
  owner around `DispatchROBAllocator` and `ROBEntryBank`, so accepted recovery
  can resolve allocator-stamped identity and prune resident rows. The full
  fetch/RF/ALU composition publishes its retained execute redirect through this
  boundary and applies backend, issue, store, LIQ, and ResolveQ mutation only
  on the same accepted intent. Immediate frontend redirection is a separate
  execute/marker control action. Reduced trace shells tie recovery off
  explicitly.
  R648 makes oldest recovery state a resident-owner contract instead of a
  top-level placeholder. `BrobMetaTracker` selects the oldest live full BID and
  completion state independently per STID. `ROBRecoveryWatermark` scans
  circular commit order for the first non-retired row in each STID and returns
  its wrap-qualified RID plus allocator-stamped full block BID. The allocator
  publishes a watermark only when the two full BIDs match exactly, then derives
  the ring BID used by recovery eligibility. Its explicit valid bit follows the
  BID through source arbitration and class merge, gating oldest-BID priority
  and completed-oldest replay rejection. This preserves Linx block/STID
  semantics, supports parameterized lane and queue sizing, and introduces no
  foreign architectural state.
  R651 promotes accepted-recovery allocation state into a complete per-STID
  live order window: independent allocation tail, commit head, and bounded
  live count. Model `MISS_PRED_FLUSH` names the first killed block; accepted
  scalar nuke/inner/fast flush preserves its authoritative target and names the
  target successor. The owner validates that identity against the resident
  window, truncates tail/count, and never moves the commit head. Metadata sees
  only the same applied suffix and classifies it by bounded modular distance
  from the commit head, including migration full-BID rollover. Exact completed
  heads arbitrate fairly across
  STIDs and cross an irrevocable retire slot, so downstream backpressure cannot
  change the selected identity. Chisel integrates this owner under
  `DispatchROBAllocator`; a generated Chisel probe proves allocation/commit
  order, exact metadata retirement, simultaneous events, valid recovery, and
  invalid identity rejection. The current Chisel owner still uses a migration
  full-BID token and one shared retire lane; canonical `BID_W` plus explicit
  wrap context, configurable multi-block retirement, non-flush/store-barrier
  frontiers, and replay-state mutation remain promotion work.
  Within one STID, arbitration applies the model `CheckOlder` type and ring-age
  rules. Different STIDs have no BID order and are serialized by fair STID
  round robin. ROB and BROB/BCTRL consumers see state-changing intent only
  after the registered cleanup handshake.
- ROB pruning applies the same Linx scope contract as conflict detection:
  request STID must match every removed row, while `baseOnPE` and
  `baseOnThread` additionally require PE and TID equality. A prune region may
  pass over an out-of-scope row without deleting it and continue to later
  in-scope younger rows.
- A raw ring-identity report cannot authorize BROB/BCTRL block cleanup.
  Successful exact lookup promotes it with the allocator-stamped full sideband,
  after which `blockFlushValid` and `bctrlFlushValid` may assert. The full
  sideband is an implementation generation token during migration to the
  canonical per-STID `BID_W` contract; it is not new Linx architectural state.
- Ordinary hard or precise recovery clears queued MDB commands, LU/SU fanout
  results, retained wait plans, and registered store wakeups. It does not erase
  SSIT prediction state; SSIT is cleared only by reset or its explicit
  confidence/weight delete policy.
- Every scalar LIQ row that waits on an MDB-predicted store owns an independent,
  saturating failed-wait age. Age is keyed by the load-slot generation and the
  predicted store `(BID, LSID, PC)`; row reuse, store-identity replacement,
  wakeup, or recovery restarts the age. Expiry is retained under backpressure.
  The owner clears wait-store state and enqueues one `delete_lu_mdb_q`
  equivalent in the same accepted cycle, so prediction confidence cannot decay
  while the load remains stranded on the failed prediction.
- `mdbFailedWaitTimeoutCycles` parameterizes the finite fallback interval. The
  Chisel owner deliberately rejects the C++ model's shared `loadPendingCyc`
  implementation because its `oldestPending` decrement enable is never set.
  Per-row deterministic ageing preserves the useful failed-prediction feedback
  mechanism without copying that dead heuristic or any ARM-specific state.
- Canonical Chisel now integrates conflict learning, SSIT lookup, atomic LU/SU
  fanout, BMDB report intent, active-row wait mutation, store-ready wakeup, and
  live failed-wait delete/decay. It also retains typed recovery reports and
  proves registered class-merged cleanup consumption against resident ROB rows.
  R652 adds the conservative per-STID strong non-flush prefix and makes the
  reduced store owner retain a committed store until its full block BID lies
  inside that exact head/count window. Early branch-resolved and tile-issued
  predicates, store-barrier allocation, and wider retirement remain open.
  Remaining IEX-local MDB training, BCC/IEX/PE trigger-owner connections, complete
  all-consumer cleanup fanout,
  pyCircuit source-arbiter/cleanup integration, and natural-workload recovery
  activation remain promotion points. The reduced `LinxCoreTop` continues to
  own `ReducedCommitROB` and is not the canonical recovery integration point.
  Before a second live source is connected beside the scalar redirect source,
  source provenance must reach accepted cleanup so scalar order/LSID sidecars
  cannot be consumed by an unrelated LSU, BCC, IEX, or PE intent.
  Marker-only backend cleanup also remains blocked until the owner can supply
  the authoritative full BID corresponding to its next-ring cleanup BID; the
  implementation must not pair an incremented ring BID with the retiring
  marker's prior full BID.
  R647 defines provenance as implementation-only metadata: a parameterized
  cause mask follows all reports contributing to one resident action, while one
  payload-owner index follows the exact request copied by model merge rules.
  Drops and cancellations resolve their cause masks without cleanup; accepted
  cleanup resolves the final cause mask and authorizes private sidecars only for
  the consumed payload owner. Provenance does not affect age, class, scope, BID,
  STID, or architectural behavior.

### Atomics, fences, Device/MMIO, and engine memory

- Linx atomics and `lr/sc` follow the ISA `.aq`, `.rl`, and `.aqrl` contract;
  they do not inherit ARM exclusive-monitor semantics.
- `FENCE.D` orders the selected Normal, Device/MMIO, and instruction-visibility
  classes. `FENCE.I` is the instruction-fetch visibility boundary.
- Device/MMIO accesses are side-effecting and non-speculative. A replay or
  retry must not duplicate an externally visible access.
- TLOAD/TSTORE and other engine memory operations remain block-fabric work
  attributable to BID and command identity. They are not hidden scalar-LSU
  traffic, but BCC and MTC still share the architectural TSO domain.

Full cache/TLB arrays, ACR/MMU fault ownership, atomics/fences, and tile-memory
integration remain implementation promotion points even though the ISA
obligations above are already normative.

Detailed ordering behavior remains documented in:

- `rtl/LinxCore/docs/architecture/lsid_memory_ordering.md`
- `rtl/LinxCore/docs/chisel/model-notes/LSU_STQ.md`

## Engine integration contract (LC-MA-ENG-001)

- Engine-backed execution must remain architecturally visible through the
  lowered block stream.
- Engine completion must compose with precise retirement and the existing
  block-engine completion model.
- Engine-local work must not create hidden global-memory side effects outside
  architecturally visible memory operations and committed block boundaries.
- `TAU` is the typed tile-to-tile template/tile-operation engine. It must keep
  memory access tile-to-tile and must not be described as a generic tensor or
  auxiliary memory engine.

### Workload-engine composition

- `VEC` remains the general programmable SIMT compute engine.
- `TMA` integrates into LinxCore through the same block/BID contract as the
  rest of the machine. TMA owns the Tile Memory Access command/completion
  frontend; its architectural southbound memory transport terminates at the
  shared CSU/L2 boundary. That target owner is not yet promoted here, and
  `src/tma/tma.py` remains a reduced compatibility facade.
- `CUBE` and `TAU` continue to integrate through the same block/BID contract
  as peer engines.
- Engine issue, completion, exception, and flush behavior must remain visible
  to ROB, BROB, and trace machinery through the canonical interfaces.

### LinxCoreModel executable-reference rules

- LinxCoreModel is the executable reference for Janus-Core-visible BFU, CUBE,
  ELF loading, direct-boot, and MMIO finisher behavior.
- Invalid BFU pipe states, missing local-pipe ownership, unsupported CUBE data
  conversions, and unsupported tile fill/element forms are model-invalid states.
  They must fail fast in debug/reference execution rather than silently
  selecting a replacement architectural behavior.
- Fallback return values that exist only to satisfy host compiler control-flow
  analysis after an assertion are not architectural defaults. LinxCore RTL or
  pyCircuit logic must not reinterpret those fallback values as legal recovery
  paths.
- Public headers and loader names must follow the current model contract
  (`ElfLoader.h` for ELF/text checkpoint loading) when LinxCore tooling shares
  model-side loaders or direct-boot setup code.

## Forward-progress contract (LC-MA-FWD-001)

- Branch, flush, load-miss, replay, and interrupt interactions must not
  deadlock.
- Required closure gates must include explicit forward-progress evidence lanes.

## Contract evidence mapping

The gate mapping for every contract ID in this document is defined in:

- `rtl/LinxCore/docs/architecture/verification-matrix.md`
