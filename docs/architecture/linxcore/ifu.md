# LinxCore IFU Architecture

## 1. Scope and terminology

The LinxCore instruction-fetch unit consists of two decoupled engines:

- **I-SIDE (Instruction Side)** owns instruction translation, L1I access,
  cacheline handling, boundary-only predecode, fixed-width normalization, and
  Instruction Buffer production.
- **B-SIDE (Branch Side)** owns control-flow prediction and predictor
  training/recovery state.

I-SIDE and B-SIDE do not share an implicit pipeline register or mutable queue.
They communicate through explicit ready/valid channels carrying request
identity. Either engine may stall without requiring the other engine to expose
its internal stages.

Both engines have five explicitly named stages:

- I-SIDE: `I-F0`, `I-F1`, `I-F2`, `I-F3`, `I-F4`;
- B-SIDE: `B-F0`, `B-F1`, `B-F2`, `B-F3`, `B-F4`.

The prefixes are mandatory because the two pipelines are decoupled and do not
advance in lockstep. The Instruction Buffer is a queue after I-F4 and before
D1.

## 2. Top-level organization

```text
                         +------------------------------+
                         | B-SIDE B-F0 .. B-F4          |
                         | L0/NLP, BTB family, history, |
                         | TAGE, BIM, RAS, IBTB, loop   |
                         +----+--------------------+----+
 prediction request ---------->                    |
 prediction response <-----------------------------+
 training/resolve --------------------------------->
 redirect/recovery <--------------------------------

 PC/redirect
     |
     v
 +----+  +----+  +----+  +----+  +----+   +--------------------+
 |I-F0|->|I-F1|->|I-F2|->|I-F3|->|I-F4|-->| Instruction Buffer |
 +----+  +----+  +----+  +----+  +----+   +----------+---------+
            |       ^                                 |
      ITLB || L1I   | inner flush                     | 4 x 64-bit
                    +---------------------------------+ v
                                                       D1 full decode
```

The fetch address is a PC. One accepted I-SIDE transaction targets the
cacheline containing that PC. Request ID, STID, PC, and epoch remain attached
until the resulting instructions are either written to the Instruction Buffer
or killed.

## 3. I-SIDE stages

### 3.1 I-F0 — PC request

I-F0:

- accepts a reset, sequential, predicted, or redirect PC;
- selects the active STID when multiple threads are runnable;
- allocates `fetch_id` and captures the current `epoch`;
- sends the correlated prediction request to B-SIDE;
- registers the I-SIDE request for I-F1.

A redirect changes the epoch before younger work for that STID can be
accepted. Responses with an old epoch are discarded.

### 3.2 I-F1 — parallel translation and L1I access

I-F1 launches the ITLB and L1I lookup in parallel for the same virtual PC and
request identity.

- The ITLB receives the virtual page and access attributes.
- L1I starts virtual index/data-array access concurrently.
- Tag comparison waits for the translated physical tag where required.

The two accesses must not be serialized as ITLB-then-L1I. Physical SRAM
banking is implementation-specific, but the architectural request behaves as
one parallel lookup.

### 3.3 I-F2 — lookup join and inner-flush decision

I-F2 joins the ITLB and L1I results.

- ITLB hit supplies the translated physical identity used to validate L1I.
- ITLB fault creates a precise fetch-fault entry.
- ITLB miss starts the page-walk/refill transaction and generates an
  **I-SIDE inner flush**.
- L1I miss starts or joins an instruction-cache refill transaction.

An inner flush cancels younger I-SIDE stages and stale L1I responses for the
affected STID/epoch. It does not flush OOO state, retire state, or another
STID, and it does not directly mutate B-SIDE predictor tables. Any B-SIDE
request cancellation is sent over the explicit redirect/cancel channel.

The production Chisel line-memory bridge retains each complete accepted I-F2
miss behind a monotonic opaque tag. External 64-byte responses may return out
of order, but a response must match both the retained tag and physical line.
The bridge reconstructs every refill identity from the retained request rather
than deriving transaction, packet, STID, epoch, checkpoint, or virtual-line
state from an address. An accepted request is not cancelled independently by a
speculative flush: the miss table records it as orphaned, accepts the eventual
physical refill after the flush cycle, and suppresses stale retry. A refill may
mutate the miss row only when every retained identity field matches exactly.

### 3.4 I-F3 — cacheline response and byte-stream state

I-F3 owns the returned cacheline context:

- cacheline data and base address;
- integrity/ECC outcome;
- refill response identity;
- byte cursor from the requested PC;
- incomplete instruction carry at a cacheline boundary.

I-F3 determines the 2/4/6/8-byte encoded length, completes cross-line
assembly, and supplies complete instruction candidates to I-F4. It does not
perform full instruction decode or branch prediction.

### 3.5 I-F4 — boundary predecode and 64-bit normalization

I-F4 is the fourth I-SIDE stage. It is not the Instruction Buffer.

I-F4:

- accepts and retains the encoded length determined by I-F3;
- recognizes only `BSTART`/`BSTOP`-class block boundaries;
- zero-extends the encoded bytes into a fixed 64-bit `insn64` container;
- writes complete program-order entries into the Instruction Buffer.

I-F4 must not decode general opcodes, operands, immediates, branch kind,
prediction direction, prediction target, or template semantics. Original byte
length remains metadata for PC advancement, legality checks, and trace.

## 4. Instruction Buffer and D1

The Instruction Buffer is a per-STID queue between I-F4 and D1. Each entry
contains at least:

```text
valid
stid
fetch_id
epoch
pc
encoded_length        // 2, 4, 6, or 8
insn64                // zero-extended fixed-width container
is_bstart
is_bstop
fetch_fault
prediction_record {
  valid
  prediction_id
  branch_pc
  taken
  target
  kind
  provider
  checkpoint_id
}
```

I-F4 observes normal queue backpressure. Flush and inner-flush pruning use STID
and epoch/request identity; stale cache or prediction responses cannot revive a
killed entry.

D1 reads up to four contiguous entries from one selected STID per cycle:

```text
Instruction Buffer -> D1DecodeGroup[4] -> D2
                         4 x insn64
```

D1 performs full opcode, operand, immediate, exception, and split/fuse decode.
Every valid D1 lane carries the complete effective `prediction_record`, even
when only one instruction in the block will resolve control flow. An
implementation may share immutable backing storage, but no downstream stage may
recover prediction state from a global “current prediction” register.
After D1, all instruction-bearing interfaces use the 64-bit instruction
container. Downstream stages never reslice the original variable-length byte
stream.

## 5. B-SIDE prediction engine

B-SIDE is based on the predictor mechanisms exercised by LinxCoreModel. It has
its own five-stage pipeline, independent of I-SIDE:

| Stage | Predictor responsibility |
|---|---|
| B-F0 | L0/NLP next-line prediction; atomically allocate a prediction tag and exact history row with full request identity, immutable `ghrBefore`, and complete RAS image/pointer/count |
| B-F1 | uBTB target/type lookup, fast RAS lookup, and launch of larger-table accesses |
| B-F2 | PBTB/BTB target/type lookup and BIM base direction prediction |
| B-F3 | short- and medium-history TAGE lookup; launch IBTB indirect-target lookup |
| B-F4 | static predictor, long-history TAGE, final IBTB result, loop predictor/buffer result, final RAS check, and unified direction/type/target arbitration |

B-F0 may provide the first usable next-PC prediction. If I-F0 has already
adopted the sequential path, a differing B-F0 result is itself a correction.
B-F1 through B-F4 may confirm it or publish a better prediction for the same
`{fetch_id, stid, epoch, pc, checkpoint}`. Because B-SIDE and I-SIDE do not
advance in lockstep, every candidate and correction is correlated by identity.

The canonical provider rank is:

```text
backend restart
  > B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential
```

Backend restart is a recovery source, not a prediction provider. Within B-F4,
an exact RAS return target or a high-confidence IBTB indirect target wins the
corresponding target selection. Direction override order is
`loop > long-TAGE > short-TAGE > BIM > static`. The static predictor is the
final fallback and consumes identity-matched I-F4 boundary metadata; it never
runs in I-F4. BTB-family metadata supplies direct targets.

If any B-SIDE stage differs from the steering result already accepted for the
same request in `{taken, branch_pc, target, kind}`, it corrects that exact
prediction. If the replaced result has already driven I-SIDE, the correction
generates an
identity-qualified I-SIDE inner flush and marks the STID history recovery
pending without immediately changing GHR/RAS. When that proposal returns from the
redirect arbiter as the canonical prune, B-SIDE restores the exact request-owned
GHR/RAS snapshots, appends the corrected conditional direction or applies the
typed Call/Return push/pop once, preserves the producer, removes younger
checkpoints/work, and restarts the corrected PC at I-F0. Path-history state must
reuse the same canonical recovery ordering.
This prediction correction does not by itself flush backend architectural state. B-F4 is the last stage
allowed to issue a prediction-driven inner flush. A candidate selected before
any path is accepted is initial steering and does not require a flush.

After B-F4 seals the effective prediction, the record follows the instruction
bundle through the Instruction Buffer and is attached to every D1 lane.
Operand-independent direct/call checks occur at Dispatch. Conditional
`setc.*` direction and indirect/return `setc.tgt` target checks occur when BRU
E1 has the runtime operands. A type-specific mismatch after B-F4 always enters
`BRU flush + recover`, restores predictor/rename/block state according to the
recovery class, and publishes a frontend restart to I-F0; it is never reported
as another inner flush.

The Chisel `IfuBackendFeedbackBridge` implements this comparison and IFU
feedback boundary. It retains transaction ID, packet UID, fetch sequence,
request PC, prediction tag, epoch, and checkpoint independently. Correct
validation emits only actual-result training; mismatch training and the keyed
backend restart advance atomically. Dispatch/BRU event production and full-BID
ROB/BROB cleanup remain backend-composition responsibilities.

B-SIDE contains:

- BTB-family target structures: BTB, uBTB and PBTB;
- GHR and GHRQ for speculative history and recoverable checkpoints;
- TAGE plus BIM fallback for direction prediction;
- RAS for call/return prediction;
- IBTB for indirect targets;
- loop predictor and loop buffer;
- prediction arbitration, BRQ/checkpoint state, and training/update logic.

The predictor consumes PCs and resolved branch outcomes. It does not own the
ITLB, L1I, cacheline refill, predecoder, or Instruction Buffer.

## 6. Decoupled interfaces

### 6.1 I-SIDE to B-SIDE prediction request

Required fields:

```text
valid/ready
fetch_id
stid
epoch
pc
history_checkpoint
```

### 6.2 B-SIDE to I-SIDE prediction response

Required fields:

```text
valid/ready
fetch_id
stid
epoch
predicted_taken
predicted_branch_pc
predicted_target
prediction_kind
predictor_checkpoint_id
confidence/source
```

I-SIDE may accept cache data before a prediction response arrives. Matching is
by identity, never by same-cycle position.

### 6.3 Resolve/training

The branch-resolution owner sends B-SIDE the resolved PC, actual direction,
actual target, branch kind, checkpoint identity, and explicit mispredict bit.
Training uses the request-owned pre-branch history rather than live GHR. A
correct resolve releases its row; a mispredict resolve retains the row until
keyed backend recovery supplies the actual conditional delta. Stale training
may update neither learned tables nor speculative state.

### 6.4 Redirect/cancel

Redirect carries STID, new PC, new epoch, request/packet/prediction identity,
typed history action, and optional conditional delta. I-SIDE uses it to restart
I-F0 and kill stale work; B-SIDE applies history recovery only when that event
returns as canonical prune. ITLB may use an unkeyed oldest-killed snapshot
fallback; prediction and backend `RestoreTrigger` events must carry and match
an exact request-owned history key. Start explicitly resets the selected STID
history.

## 7. superscalarNPU comparison

`superscalarNPU` `origin/main@1fae7d0` is a reference design, not a normative
dependency. It provides useful evidence for a decoupled branch/instruction
frontend: FTQ-separated B/I paths, per-thread PC/GHR/RAS state,
MBTB/TAGE/IBTB predictors, and an Instruction Buffer.

The latest reference interface exposes prediction taken/target independently
for D1 slots 0..3, carries prediction metadata to BRU, and reports
target/address mispredict at E1. Linx generalizes that per-lane contract to the
complete `PredictionRecord`, retains data-dependent validation in BRU E1, and
adds operand-independent direct/call validation in Dispatch.

The reference organization is not copied directly:

| Area | superscalarNPU reference | LinxCore target |
|---|---|---|
| Stage shape | B0–B4 plus I-F1–I-F3 | I-F0..I-F4 plus B-F0..B-F4 |
| Translation/cache | no TLB; PIPT fetch assumption | parallel ITLB/L1I at I-F1 and identity-retained miss/refill |
| Early prediction | uBTB and intra-flush removed | uBTB at B-F1; B-F4 is the final prediction-driven inner-flush point |
| Predictor grouping | B2/B3 group multiple predictor operations | staged predictor quality from L0/NLP through long TAGE/IBTB/loop arbitration |
| Fetch completion | SN I-F3 static/context work and variable-width IB payload | I-F4 boundary-only predecode, complete 64-bit entries, D1 full decode |

The reusable idea is decoupled ownership with identity-correlated prediction
and fetch queues. LinxCore stage names, translation policy, correction rules,
predecode boundary, and 4x64-bit D1 contract remain defined solely by this
specification.

## 8. Required invariants

1. I-SIDE stages are named I-F0 through I-F4; B-SIDE stages are named B-F0
   through B-F4.
2. The two engines are decoupled and never rely on lockstep stage alignment.
3. ITLB and L1I access starts in parallel at I-F1.
4. ITLB miss causes an I-SIDE inner flush, not an OOO/global flush.
5. B-F0..B-F4 may correct an already-used steering result and inner-flush I-SIDE;
   B-F4 is the final such point.
6. BHC/fetch-cache behavior belongs to I-SIDE L1I, never B-SIDE.
7. I-F3 determines instruction length and completes assembly; I-F4 predecode
   recognizes only `BSTART`/`BSTOP` boundaries.
8. Every Instruction Buffer entry contains one complete 64-bit instruction
   container.
9. D1 reads four 64-bit entries, carries the complete effective prediction
   record on every valid lane, and owns full decode.
10. Post-B-F4 Dispatch/BRU mismatch uses BRU flush/recover, never another
    prediction-driven inner flush.
11. I-SIDE and B-SIDE communicate only through explicit decoupled interfaces
   with request/STID/epoch correlation.

The production D1 implementation is `D1InstructionDecodeStage`. It consumes a
four-entry `D1InstructionGroup` directly, performs full decode without an
intermediate byte-window/slot representation, and copies the complete final
prediction record into each decoded uop. I-F3 derives a dynamic instruction
UID from fetch-packet identity plus the six-bit byte offset within the
architectural 64-byte line, preventing lane-local UID reuse across consecutive
groups from the same line.

## 9. Generated-RTL throughput gate

The canonical hot-cache supply gate is:

```bash
bash rtl/LinxCore/tools/chisel/run_chisel_ifu_throughput_gate.sh
```

It emits `LinxCoreIfu` with architectural 64-byte cachelines and requires
thirty-two consecutive full four-entry D1 groups, final B-F4 metadata on every
lane, and multiple prediction joins plus ordered line contexts in flight. This
gate proves eligible dense sequential IFU supply. It does not prove mixed
instruction lengths, prediction-recovery stress, production decode/dispatch
acceptance, or CoreMark/Dhrystone throughput.
