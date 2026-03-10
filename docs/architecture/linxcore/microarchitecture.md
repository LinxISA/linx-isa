# LinxCore v0.4 Microarchitecture Contract

## Baseline superscalar contract

LinxCore closure target is a superscalar out-of-order core with current structural limits captured by implementation parameters.

Current baseline limits (must be treated as architectural bring-up constraints until promoted):

- fetch width: 4
- dispatch width: 4
- issue width: up to 4
- commit width: up to 4
- LSU width: 1

These constraints are the current v0.4 closure baseline. Wider issue/commit and multi-LSU scaling are follow-on expansion tracks.

## Pipeline contract (LC-MA-PIPE-001)

- Stage ownership must be explicit (frontend/decode/rename/issue/execute/commit) with no hidden pass-through stage collapse.
- Commit behavior must remain precise and ordered by architectural retirement.
- ROB bookkeeping must remain coherent across multi-commit cycles.

### Current frontend/decode/rename stage ownership (F0-D3)

The current promoted stage split from fetch through rename is:

- `F0`: PC-select only.
- `F1`: I-cache tag/data lookup control and miss/backpressure generation.
- `F2`: ECC-checked raw cache-data staging.
- `F3`: variable-length assembly/stitch, static prediction, block-boundary
  annotation, and template-stream control.
- `IB`: per-thread buffered instruction delivery.
- `D1`: decode plus ordering-id allocation.
- `D2`: rename request/translation.
- `D3`: renamed-uop latch boundary.

No hidden pass-through collapse is allowed across these boundaries in the
architectural contract.

### Frontend contract details (F0-F3 + IB)

#### F0

- `F0` is a dedicated PC-select stage.
- `F0` receives multiple candidate PCs and selects one under control logic.
- `F0->F1` is a registered pipeline boundary.
- The architecture-facing `F0->F1` interface is per-thread rather than a single
  shared port with explicit thread multiplexing.

#### F1

- `F1` owns I-cache lookup/tag-check semantics.
- `F1` determines hit/miss and applies frontend backpressure on miss.
- The architectural model reserves per-thread miss independence.
- The current physical I-cache read path is single-ported, so `F1` arbitrates
  among threads and services at most one thread lookup per cycle.
- `F1->F2` is a registered boundary.

#### F2

- `F2` receives cache-read data plus thread/PC context from `F1`.
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
- The primary boundary metadata is semantic `start_of_block` / `end_of_block`
  rather than raw `is_bstart` / `is_bstop` opcode tags.
- Template instructions (`FENTRY`, `FEXIT`, `FRET.*`) may be consumed by the
  CTU without forcing later instructions in the same fetch bundle to disappear;
  those later instructions may remain in frontend queues, but they must not
  enter `IB` before the CTU-expanded child stream for that template.
- While a CTU child stream is actively injecting instructions, `IB` write-port
  source selection is CTU-priority and ordinary IFU writes wait until the active
  child stream completes.

#### Inst Buffer (`IB`)

- `IB` is partitioned by thread; each thread owns an independent bank/FIFO.
- An `IB` entry may legally straddle a block boundary.
- Block metadata is carried per instruction, not as one summary bit per entry.
- Each stored instruction carries its own length metadata.
- PC encoding uses `entry_base_pc` plus per-instruction offset/length rather
  than a full explicit PC for every instruction.
- Each per-thread `IB` bank provides up to `decodeWidth` lane reads per cycle so
  `D1` can assemble a decode-width-aligned contiguous decode group.

### Decode and renamed-uop contract (D1-D3)

#### D1

- `D1` reads a program-order-contiguous decode group from `IB`.
- `D1` performs instruction decode and allocates `RID` / `BID` / `LSID`.
- Allocation for a decode group is all-or-nothing; if the full group cannot
  allocate successfully, the pipeline stalls and retries the whole group.
- `D1` output uops already carry decoded opcode/uop semantics, fixed operand
  slots, architectural operand tags, extended immediate values, and block/order
  metadata.

#### Canonical D2 uop shape

The architectural `D2` uop shape is:

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

Operand slots are fixed-width stage interfaces, not variable-length operand
lists. Source slots use operand classes `{P, T, U, CARG}`. Destination slots
use `{P, T, U}`; `CARG` is source-only.

#### D2 operand interpretation

- `P`: architectural scalar register operand (`R1..R23` in the current rename
  domain).
- `T`: transient scalar-block operand in the `t#N` namespace.
- `U`: transient scalar-block operand in the `u#N` namespace.
- `CARG`: block argument operand; there is exactly one `CARG` per block and it
  is bound to `bid`.

`D2` carries architectural/relative operand names only:

- `P` carries `atag`.
- `T` carries `t_rel`.
- `U` carries `u_rel`.
- `CARG` carries only `type=CARG`; the actual block argument is resolved via
  `bid` rather than an independent operand id.

#### D3 operand interpretation

After rename, `D3` retains the operand class plus the resolved backend tag form:

- `P` retains `atag` and adds `ptag`.
- `T` retains `t_rel` and adds resolved `ttag`.
- `U` retains `u_rel` and adds resolved `utag`.
- `CARG` is resolved at `D3` into the block-scoped `CARG` file, indexed by
  `bid`; it does not continue as an `IQ`-visible operand payload.

The architectural `D3` uop therefore preserves semantic operand identity while
also carrying the resolved backend tag form needed by later stages. `CARG` is a
special case: it is materialized into the block-scoped `CARG` file at `D3`
rather than entering the downstream `IQ` fabric as a live source operand.

#### Operand-slot field contract

| Operand slot form | D2 representation | D3+ representation | Legal |
|---|---|---|---|
| `P` src | `type=P`, `atag` | `type=P`, `atag`, `ptag` | yes |
| `P` dst | `type=P`, `atag` | `type=P`, `atag`, `ptag` | yes |
| `T` src | `type=T`, `t_rel` | `type=T`, `t_rel`, `ttag` | yes |
| `T` dst | `type=T` | `type=T`, `ttag` | yes |
| `U` src | `type=U`, `u_rel` | `type=U`, `u_rel`, `utag` | yes |
| `U` dst | `type=U` | `type=U`, `utag` | yes |
| `CARG` src | `type=CARG` | resolved into `CARG` file at `D3` via `bid` | yes (pre-`D3`) |
| `CARG` dst | illegal | illegal | no |

Interpretation rules:

- `P.atag` names the architectural scalar register in the `P` rename domain.
- `T.t_rel` and `U.u_rel` preserve the original relative scalar-block operand
  meaning (`t#N` / `u#N`) for source operands.
- `T`/`U` destination operands do not carry a relative `rel` field.
- `T.ttag` and `U.utag` are the resolved internal tags produced by rename.
- `CARG` is resolved implicitly from `bid`; no explicit `carg_id` field is
  carried in the canonical uop.
- At `D3`, `CARG` is written into the block-scoped `CARG` file and does not
  remain as an `IQ`-visible source operand.
- Operand slots are interpreted by `type`; no additional per-class `tag_valid`
  field is required in the canonical interface.

#### Rename-stage ordering inside one decode group

For one `decodeWidth`-wide contiguous decode group:

- `RID/BID/LSID` are allocated in program order at `D1`.
- `D2` and `D3` preserve decode-slot program order (`slot0 .. slotN-1`).
- Same-cycle `P` rename bookkeeping uses stable FIFO insertion order derived
  from `rid + decode_slot`.
- Same-cycle `T` and `U` allocations are performed in decode-slot order against
  `T_FIFO` and `U_FIFO` respectively.

### Rename contract (P / T / U / CARG)

#### P rename

- `P` rename is map-based.
- `CMAP` is the committed rename map.
- `SMAP` is the speculative map visible to rename.
- `MapQ` records speculative `P`-rename increments against `CMAP`.
- `MapQ` applies only to `P`-type destinations (`R1..R23`).
- Only instructions that actually perform a `P`-rename allocate a `MapQ` entry.
- Recovery is instruction-precise: `MapQ` cut points are keyed by `rid`, not
  just `bid`.
- The default flush replay boundary keeps mappings up to and including the
  flushing instruction (`<= flush_rid`) for the younger-squash redirect path.
- Same-cycle/decode-width-parallel `MapQ` updates are ordered by `rid` plus
  decode slot; the intra-`rid` local order key is the decode slot directly.

#### T/U rename

- `T` and `U` do not use `CMAP/SMAP/MapQ`.
- `T` allocates from `T_FIFO`; `U` allocates from `U_FIFO`.
- A `T`/`U` destination write advances the corresponding FIFO allocation
  pointer.
- `T`/`U` source operands are represented as relative references (`t#N`/`u#N`)
  and are resolved using the corresponding sequential pointer state.
- `D3+` must retain both the original relative reference and the resolved tag
  (`ttag`/`utag`).

#### CARG

- `CARG` is block-scoped rather than instruction-scoped.
- There is exactly one `CARG` per block.
- `CARG` is identified implicitly by `bid` and is not independently renamed.
- `CARG` is a source-side operand class only; it is not a destination class.
- `CARG` does not enter the downstream `IQ` fabric.
- At `D3`, the resolved `CARG` value is materialized into the block-scoped
  `CARG` file, indexed by `bid`.

#### Rename pseudocode (architectural intent)

The following pseudocode is informative and captures the required architectural
behavior of `D2`/`D3`.

`D2` source translation / destination allocation request:

```text
for slot in decode_group slots in program order:
  u = d1_uop[slot]

  for each src operand s in u.src[0..2]:
    case s.type of
      P:
        s.ptag_req = SMAP[s.atag]
      T:
        s.ttag_req = ResolveTRel(T_PTR_snapshot, s.t_rel)
      U:
        s.utag_req = ResolveURel(U_PTR_snapshot, s.u_rel)
      CARG:
        s.carg_req = ResolveBlockCarg(u.bid)

  case u.dst[0].type of
    P:
      u.dst[0].ptag_alloc_req = P_FREELIST.alloc()
    T:
      u.dst[0].ttag_alloc_req = T_FIFO.alloc_next(slot_order)
    U:
      u.dst[0].utag_alloc_req = U_FIFO.alloc_next(slot_order)
    none:
      no action
```

`D3` latch / commit of rename results:

```text
for slot in decode_group slots in program order:
  u = d2_uop[slot]

  for each src operand s in u.src[0..2]:
    case s.type of
      P:    s.ptag = s.ptag_req
      T:    s.ttag = s.ttag_req
      U:    s.utag = s.utag_req
      CARG: WriteCargFile(bid=u.bid, value=s.carg_req)

  case u.dst[0].type of
    P:
      u.dst[0].ptag = u.dst[0].ptag_alloc_req.grant
      PushMapQ(rid=u.rid, decode_slot=slot, atag=u.dst[0].atag, new_ptag=u.dst[0].ptag)
    T:
      u.dst[0].ttag = u.dst[0].ttag_alloc_req.grant
    U:
      u.dst[0].utag = u.dst[0].utag_alloc_req.grant
    none:
      no action
```

#### P-map recovery pseudocode (architectural intent)

The following pseudocode is informative and captures the required architectural
recovery rule for `P` rename state on an instruction-precise flush.

```text
RecoverPMap(flush_rid):
  SMAP = Copy(CMAP)
  for e in MapQ in FIFO order:
    if e.rid <= flush_rid:
      SMAP[e.atag] = e.new_ptag
    else:
      break
```

Required properties of the above recovery rule:

- The default redirect/younger-squash boundary is inclusive: keep mappings for
  the flushing instruction itself (`<= flush_rid`).
- `MapQ` ordering is deterministic and stable across decode-width-parallel
  rename via `rid + decode_slot` FIFO insertion order.
- Only `P` destinations contribute `MapQ` entries.
- `T/U` recovery is not driven by `MapQ`; it follows the corresponding FIFO
  pointer/state recovery mechanism.

#### Non-goals of the canonical D2/D3 uop contract

- No UID/checkpoint field is carried in the canonical uop.
- No dedicated exception/replay/flushability field is carried in the canonical
  uop; those remain out-of-band or in later-stage side metadata.
- `insn_len` and `insn_raw` are retained as debug/trace residue, but
  `fetch_slot`/`decode_slot` are not carried as canonical uop fields.

### Post-rename dispatch contract (`D3 -> S1 -> S2 -> IQ`)

#### S1 stage ownership

- The pipeline stage immediately after `D3` is `S1`.
- `S1` is the first post-rename dispatch-preparation stage.
- `S1` receives renamed uops from `D3`, classifies each uop by its
  execution/issue class, selects the target physical `IQ`, and queries the
  operand ready state that will be used to initialize the eventual `IQ` entry.

#### S2 stage ownership

- `S2` is the actual `IQ` write stage.
- `S2` receives the routed/annotated uops from `S1` and performs the real
  enqueue into the selected downstream `IQ`.

#### S1/S2 routing rule

- The architectural rule is type-directed routing: the destination physical
  `IQ` is a function of the uop's decoded/renamed execution class plus the
  fixed-priority physical-queue selection policy for classes with multiple legal
  queues.
- `S1` performs routing selection and ready-state query.
- `S2` performs the actual `IQ` entry write.
- `CARG` does not participate in `S1`/`S2` `IQ` routing; it has already been
  materialized into the `CARG` file at `D3`.
- `S1` and `S2` preserve program order within one decode/rename group when
  presenting multiple same-cycle enqueue attempts to downstream `IQ`s.

#### Architectural IQ domains

The externally visible issue-queue domains follow the current golden execution
classes:

- `ALU`
- `BRU`
- `AGU`
- `STD`
- `FSU`
- `SYS`
- `CMD`

Current physical implementation may merge or split some domains, and one
architectural execution class may have more than one legal physical `IQ`
target. In particular, some classes (for example `ALU`) may be dispatched to
multiple candidate physical `IQ`s, while the architectural routing class
carried by the uop remains explicit and stable.

The current physical `IQ` set is:

- `alu_iq0`
- `shared_iq1`
- `bru_iq`
- `agu_iq0`
- `agu_iq1`
- `std_iq0`
- `std_iq1`
- `cmd_iq`

Baseline physical implementation provides two enqueue/write ports per
physical `IQ`.

Baseline architectural-class to physical-`IQ` mapping:

| Architectural class | Legal physical `IQ` target(s) | Baseline routing policy |
|---|---|---|
| `ALU` | `alu_iq0`, `shared_iq1` | fixed priority: prefer `alu_iq0`, spill to `shared_iq1` |
| `BRU` | `bru_iq` | unique target |
| `AGU` | `agu_iq0`, `agu_iq1` | fixed priority: prefer `agu_iq0`, spill to `agu_iq1` |
| `STD` | `std_iq0`, `std_iq1` | fixed priority: prefer `std_iq0`, spill to `std_iq1` |
| `FSU` | `shared_iq1` | unique target |
| `SYS` | `shared_iq1` | unique target |
| `CMD` | `cmd_iq` | unique target |

`BBD` does not enter an `IQ`; block-boundary/boundary-decode handling must be
resolved before `S2` writes uops into the `IQ` fabric.

When multiple legal physical `IQ` targets exist for one architectural class,
`S1` uses a fixed-priority selection policy rather than a dynamic least-loaded
policy. The current baseline policy is to prefer the primary dedicated queue
first and spill to the secondary/shared queue only when needed (for example,
`ALU`: prefer `alu_iq0`, then spill to `shared_iq1`; `AGU`: prefer `agu_iq0`,
then spill to `agu_iq1`; `STD`: prefer `std_iq0`, then spill to `std_iq1`).

#### Dispatch invariants

- `S1` does not alter operand meaning established by `D3`; it only performs
  class/routing selection and ready-state query for the already-renamed uop.
- `S1` initializes operand readiness by querying the corresponding ready table:
  `P` via `ready_table_p[ptag]`, `T` via `ready_table_t[ttag]`, and `U` via
  `ready_table_u[utag]`.
- `ready_table_p`, `ready_table_t`, and `ready_table_u` all represent
  non-speculative readiness only: a table bit may be set only when the
  corresponding produced value is architecturally stable and will not later be
  withdrawn by ordinary cancellation/flush of a still-speculative producer.
- `CARG` does not enter `IQ`; its value has already been written to the `CARG`
  file at `D3` and is later retrieved by `bid`.
- `S2` must preserve `thread_id`, `rid`, `bid`, `lsid`, boundary metadata, and
  renamed operand payloads unchanged when writing the final `IQ` entry.
- `IQ` entries retain semantic operand identity together with backend tags for
  the live operands that enter the `IQ` fabric.
- For source operands: `P` keeps `atag+ptag`, `T` keeps `t_rel+ttag`, and `U`
  keeps `u_rel+utag`.
- For destination operands: `P` keeps `atag+ptag`, while `T` and `U` keep their
  resolved destination tags (`ttag` / `utag`) without a `rel` field.
- `S2` writes the `IQ` entry with the initial src-ready state computed by `S1`.
- `S1/S2` routing must compose with normal flush/redirect behavior; a uop is
  not considered architecturally issued merely because it has entered `S1` or
  `S2`.
- `S1/S2` dispatch for one renamed group is atomic: if any uop in the group
  cannot be accepted by its target `IQ`, the whole group stalls and no
  partial-prefix or partial-subset dispatch is allowed.
- ROB allocation is earlier than `S1`: `D1` already allocates the ROB entry and
  assigns `rid`.
- After `S1/S2`, the dispatch path has no further allocation-time relationship
  with ROB. Later completion/resolve information is reported back to ROB only
  when a uop reaches `W1` resolve.
- Baseline physical implementation provides two enqueue/write ports per
  physical `IQ`.
- If more same-cycle enqueue attempts target one `IQ` than that `IQ` can accept
  in the current cycle, contention is resolved by decode-group age/order
  priority: older instructions in the current decode-width group win the enqueue
  opportunity. In practice this is the decode-slot/program-order priority
  within the group.
- If multiple entries are written into one physical `IQ` in the same cycle, or
  across successive enqueue opportunities from the same cycle/group, the
  resulting `IQ` age/order is still defined by decode-slot order: older decode
  slots are older `IQ` entries.

#### IQ entry readiness contract

- Each `IQ` entry carries per-source `src_valid` and `src_ready` state.
- If a source slot is not valid, that source is treated as ready by default.
- If a valid source is not ready at enqueue time, the entry remains resident in
  the `IQ` and waits for wakeup.
- An `IQ` entry becomes pick-eligible only when all of its valid source
  operands are ready.
- Entries with any still-not-ready valid source operand remain in the `IQ` and
  must not be picked.

#### IQ pick / inflight contract

- Pick operates only on entries that are ready and not already `inflight`.
- Pick policy is oldest-ready-first.
- `Oldest` is defined by `IQ` enqueue/entry order rather than ROB/`rid` age.
- Pick does not immediately remove an entry from the `IQ`.
- When an entry is picked, the entry remains valid in the `IQ` and transitions
  to an `inflight`/picked state.
- If downstream issue progress later fails (for example due to RF read-port
  contention or another issue-time rejection), the entry is not reinserted;
  instead the `inflight` state is cleared and the entry becomes eligible for a
  later retry under the normal pick rules.
- The architecture therefore forbids a pick-then-reinsert model for ordinary
  issue cancellation/retry.
- The real `IQ` entry deallocation point is `I2`: only after the uop reaches
  `I2` and is considered confirmed/non-cancellable does the `IQ` clear the
  entry's `valid` state.

#### Post-pick wakeup contract (baseline)

- After `P1` picks a uop, the downstream issue/execute pipeline determines its
  eventual wakeup behavior from the produced destination tag class plus the
  operation latency.
- Wakeup routing is tag-class aware: the produced destination tag kind selects
  which dependency namespace is being woken (`P`, `T`, or `U`), and latency
  selects the cycle/stage at which the wakeup is emitted.
- Baseline latency-to-wakeup-stage mapping is: `lat=1 -> P1`, `lat=2 -> I2`,
  `lat=3 -> E1`, `lat=4 -> W1`.
- Wakeup must not affect pick in the same cycle: a wakeup emitted in cycle `N`
  becomes visible to pick only in cycle `N+1`.
- `P` wakeup is broadcast by `ptag` to all relevant physical `IQ`s that may
  hold consumers of that `P` producer.
- A non-speculative `P` wakeup also updates `ready_table_p[ptag]` to ready, in
  addition to waking already-enqueued dependent `IQ` entries.
- `T` and `U` wakeup are directed rather than globally broadcast.
- For `T/U`, the directed wakeup target is encoded as a point-to-point
  `qtag = (phys_iq_id, entry_id)` naming the destination physical `IQ` entry to
  wake.
- `T` wakeup also updates `ready_table_t[ttag]` to ready, and `U` wakeup also
  updates `ready_table_u[utag]` to ready, in addition to the directed wakeup of
  already-enqueued dependents.
- If an operation has no wakeup-producing destination, it does not generate a
  dependency wakeup event.

#### `P1 -> I1` issue-read contract

- `P1` selects ready, non-`inflight` `IQ` entries and marks the chosen entry
  `inflight`.
- `I1` is the first post-pick issue stage and is responsible for deciding which
  source operands require physical operand reads in this issue attempt.
- `I1` performs global operand-read / RF read-port arbitration across the set
  of uops picked in the current cycle.
- If a picked uop loses required `I1` read-port arbitration, the attempt is
  cancelled for this cycle: the `IQ` entry remains valid, `inflight` is
  cleared, and the uop returns to normal future-pick eligibility.
- `I1` requests reads only for source operands that are both valid and need a
  read in the current attempt.
- Invalid source operands are treated as ready and never consume `I1` read
  bandwidth.
- Source operands that became ready only through speculative load wakeup must
  not consume RF read ports in `I1`; they obtain data later through the
  `LD_E4 -> consumer-I2` forward path.
- `I1` therefore establishes the per-uop operand-read plan for `I2/E1`: normal
  ready operands may come from RF read results, while load-spec-ready operands
  are carried forward as bypass-only dependencies.
- Global `I1` read-port arbitration is oldest-first by ROB age (`rid` age
  relative to ROB head), even though per-`IQ` pick order is oldest-ready-first
  by `IQ` entry order.

#### `I1 -> I2 -> E1 -> W1` issue/execute/resolve contract

- `I2` is the issue-confirmation boundary.
- A uop that reaches `I2` is considered confirmed/non-cancellable for ordinary
  `IQ` retry purposes; this is the point at which its source-acquisition plan
  has been accepted and its `IQ` entry may be deallocated.
- `I2` therefore owns the architectural `IQ`-deallocation event (`valid=0`) and
  the handoff from issue machinery into the downstream execution pipeline.
- RF-read operands granted in `I1` are consumed from the `I1 -> I2` path.
- Load-spec-ready operands are not expected from RF; their data arrives only via
  the required `LD_E4 -> consumer-I2` forward path.
- Beyond that required load-forward case, the detailed bypass topology is a
  microarchitectural implementation choice; the architectural contract fixes
  wakeup timing and legality, not a full mandatory bypass matrix.
- `E1` is the first execute stage after issue confirmation.
- Uops with `lat=3` produce their architectural wakeup event at `E1`.
- `W1` is the architecturally visible late resolve / wakeup stage.
- Uops with `lat=4` produce their architectural wakeup event at `W1`.
- Completion/resolve information becomes reportable back toward ROB when the
  uop reaches its architecturally defined resolve point; in the current
  baseline, `W1` is the generic scalar resolve stage for this purpose.
- If a uop has no destination wakeup side effect, it may still pass through the
  same stage sequence for control/exception/retire bookkeeping, but it does not
  update ready tables or awaken dependents.

## Hazard and replay contract (LC-MA-HAZ-001)

- Wakeup, scoreboard, and replay control must preserve deterministic issue legality.
- Redirect/flush/replay must not commit younger wrong-path state.
- Load-miss and replay paths must preserve correctness for dependent consumers.

## Block and recovery contract (LC-MA-BLK-001)

- Block-structured control flow is mandatory: `BSTART`/`BSTOP` semantics remain authoritative.
- Recovery targets must resolve to legal block boundaries.
- Invalid block-target recovery must be precise-trap observable.

Current LinxCore alignment details:

- architectural redirect is boundary-authoritative; execute-side `setc.cond`
  records pending correction metadata but does not directly rewrite architectural PC
- `BSTART` and `BSTOP` are ROB-visible boundary uops, and an in-body `BSTART`
  may terminate the previous block before reappearing as the next block head
- `RET`, `IND`, and `ICALL` require explicit `SETC.TGT` in the same block
- returning `BSTART.CALL` headers require adjacent `SETRET` or `C.SETRET`; there
  is no implicit `ra` rewrite on the call header itself
- `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` are valid standalone macro block
  boundaries and must be treated as fall-through macro blocks in live committed
  block metadata
- dynamic correction and recovery targets must resolve to legal block starts;
  known non-block targets raise `TRAP_BRU_RECOVERY_NOT_BSTART (0x0000B001)`
- block queues and block-engine rollback remain BID-based: keep `bid <= flush_bid`,
  kill `bid > flush_bid`

Architectural block-completion abstraction:

- For block completion semantics, LinxCore follows the ISA-visible canonical block-type domain
  `{STD, FP, SYS, MPAR, MSEQ, VPAR, VSEQ, TMA, CUBE, TEPL}`.
  Legacy compatibility spellings and selector aliases are not separate completion classes.
- `STD`, `FP`, and `SYS` are equivalent in the two-layer completion model.
- Dynamic block instances collapse to exactly one of three architectural participant sets:
  - `{}` for empty/control-only scalar-family instances,
  - `{scalar}` for scalar-family instances with a real scalar body,
  - `{non-scalar}` for canonical non-scalar block types.
- Dynamic degeneration to `{}` is allowed only for scalar/control-family block types (`STD`/`FP`/`SYS`).
  Canonical non-scalar block types (`MPAR`/`MSEQ`/`VPAR`/`VSEQ`/`TMA`/`CUBE`/`TEPL`) always carry
  `{non-scalar}` completion obligation.
- The architectural `{non-scalar}` participant has single-point resolve semantics: BROB/retirement observes
  one `non-scalar-done` event per block instance. Any finer engine fan-in or multi-engine join remains
  microarchitectural.

Rendering- and accelerator-facing consequence:

- engine-backed work such as TAU-oriented rendering hardening must remain
  block-visible and BID-visible,
- engine dispatch must compose with the same boundary-authoritative recovery
  model as scalar and VEC work,
- younger engine work must be cancellable under the normal flush and redirect
  rules rather than requiring a separate rollback domain.

## Privilege/trap contract (LC-MA-PRV-001)

- U->S trap entry and `SRET` return must preserve architected control/state transitions.
- Trap envelope and CSR side effects must be coherent with commit-visible behavior.
- Precise exception reporting is required under superscalar retirement.

## MMU contract (LC-MA-MMU-001)

- Translation success and failure (permission/page fault) must produce deterministic trap envelopes.
- MMU behavior must remain aligned with v0.4 privileged contract wording.
- MMU fault paths must preserve precise retirement and recovery ordering.

## Interrupt contract (LC-MA-IRQ-001)

- Timer interrupt delivery must be enabled in strict-system lanes (no silent global masking in closure runs).
- Interrupt entry/return must compose with block boundaries and replay/flush behavior.
- Interrupt handling must preserve forward progress under sustained mixed workload pressure.

## Memory-ordering contract (LC-MA-MEM-001)

- Load/store ordering, forwarding, and replay behavior must remain architecturally legal.
- Memory visibility at commit must remain consistent with recorded trace/memory metadata.
- Ordering checks must include block and redirect interactions.

## Engine integration contract (LC-MA-ENG-001)

- Engine-backed execution must remain architecturally visible through the
  lowered block stream.
- Engine completion must compose with precise retirement and the existing
  block-engine completion model.
- Engine-local work must not create hidden global-memory side effects outside
  architecturally visible memory operations and committed block boundaries.
- Tile-oriented engines such as TAU must preserve the current tile-to-tile
  contract unless a future canonical architecture update changes that rule.

## Forward-progress contract (LC-MA-FWD-001)

- Branch/flush/load-miss/replay/interrupt interactions must not deadlock.
- Required closure gates must include explicit forward-progress evidence lanes.

## Contract evidence mapping

| Contract ID | Primary gate evidence |
|---|---|
| `LC-MA-PIPE-001` | `LinxCore::stage/connectivity lint`, `Testbench::ROB bookkeeping` |
| `LC-MA-HAZ-001` | `LinxCore::trace schema and memory smoke`, `Testbench::ROB bookkeeping` |
| `LC-MA-BLK-001` | `LinxCore::runner protocol`, `Testbench::block struct pyc flow smoke` |
| `LC-MA-PRV-001` | `pyCircuit::QEMU vs pyCircuit trace diff`, `LinxCore::cosim smoke` |
| `LC-MA-MMU-001` | `pyCircuit::QEMU vs pyCircuit trace diff`, `LinxCore::cosim smoke` |
| `LC-MA-ENG-001` | `LinxCore::runner protocol`, `Testbench::block struct pyc flow smoke`, `pyCircuit::QEMU vs pyCircuit trace diff` |
| `LC-MA-IRQ-001` | `LinxCore::cosim smoke`, `LinxCore::runner protocol` |
| `LC-MA-MEM-001` | `LinxCore::trace schema and memory smoke`, `pyCircuit::QEMU vs pyCircuit trace diff` |
| `LC-MA-FWD-001` | `Testbench::ROB bookkeeping`, `LinxCore::runner protocol` |

## Reference implementation detail sources

Implementation detail sources that feed this contract:

- `rtl/LinxCore/docs/architecture/linxcore_top_design.md`
- `rtl/LinxCore/docs/architecture/pipeline_stages.md`
- `rtl/LinxCore/docs/architecture/block_fabric_contract.md`
- `rtl/LinxCore/docs/architecture/branch_recovery_rules.md`
- `rtl/LinxCore/docs/architecture/lsid_memory_ordering.md`

LinxArch remains normative when wording diverges.
