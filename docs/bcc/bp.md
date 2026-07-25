# B-SIDE Branch Prediction Engine

B-SIDE is the branch-prediction half of the IFU. It is decoupled from I-SIDE
and has no direct ownership of ITLB, L1I, fetched cachelines, predecode, or the
Instruction Buffer.

## Predictor structures

- **B-F0** runs L0/NLP and allocates the GHR/GHRQ/RAS checkpoint.
- **B-F1** queries uBTB and fast RAS, then launches larger-table accesses.
- **B-F2** queries PBTB/BTB and BIM.
- **B-F3** queries short/medium TAGE and launches IBTB.
- **B-F4** collects long TAGE, final IBTB, loop, and final RAS results and
  performs unified arbitration.
- **Training/update logic** consumes resolved outcomes and updates structures
  independently of I-SIDE fetch backpressure.

Provider rank is
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`. B-F4 target selection
prefers exact RAS return or high-confidence IBTB when applicable; direction
rank is `loop > long-TAGE > short-TAGE > BIM`; BTB supplies direct targets.
Backend restart is higher priority but is a typed-recovery source rather than
a prediction provider.

## Decoupled contract

I-SIDE sends `{fetch_id, stid, epoch, pc, history_checkpoint}`. B-SIDE returns
the matching `{taken, branch_pc, target, kind, source, checkpoint_id}`. Resolution
and redirect channels restore GHR/RAS/checkpoint state and prevent stale
responses from being consumed.

The B-F0..B-F4 and I-F0..I-F4 pipelines are decoupled and non-lockstep. If a
later B-stage corrects an already-used prediction, I-SIDE inner-flushes and
restarts I-F0. Backend-resolved misprediction uses typed recovery plus the
frontend restart.

See [LinxCore IFU Architecture](../architecture/linxcore/ifu.md).
