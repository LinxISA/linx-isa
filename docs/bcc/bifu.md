# IFU: Decoupled I-SIDE and B-SIDE Engines

The LinxCore IFU contains two independently backpressured engines:

- **I-SIDE** translates a PC, reads one L1I cacheline, performs
  boundary-only predecode, normalizes instructions to 64-bit containers, and
  writes the Instruction Buffer.
- **B-SIDE** predicts the next control-flow PC and maintains predictor
  checkpoint, training, and recovery state.

The engines communicate only through explicit request, prediction, training,
and redirect channels. Every message carries request ID, STID, PC, and epoch
where applicable. Cache and predictor responses are matched by identity, not
by same-cycle position.

## I-SIDE pipeline

I-SIDE uses I-F0 through I-F4.

| Stage | Responsibility |
|---|---|
| I-F0 | Accept/select PC; allocate fetch ID and epoch; register the request |
| I-F1 | Launch ITLB and L1I access in parallel |
| I-F2 | Join ITLB/L1I state; on ITLB miss generate an I-SIDE inner flush; on L1I miss retain refill identity |
| I-F3 | Capture one cacheline, ECC/refill result, byte cursor, and cross-line carry |
| I-F4 | Parse 2/4/6/8-byte lengths, recognize only `BSTART`/`BSTOP` boundaries, zero-extend complete instructions to 64 bits, and write the Instruction Buffer |

An ITLB-miss inner flush kills younger I-SIDE work and stale L1I responses for
the affected STID/epoch. It is not an OOO/global flush.

The Instruction Buffer is after I-F4. It stores one complete `insn64` per entry
plus PC, original length, boundary bits, request/checkpoint identity, fault,
and correlated prediction metadata.

D1 reads four contiguous 64-bit entries per cycle and performs full opcode,
operand, immediate, exception, and split/fuse decode. All instruction
interfaces after D1 remain fixed-width 64-bit.

## B-SIDE prediction engine

B-SIDE uses B-F0 through B-F4:

- B-F0: L0/NLP plus checkpoint and GHR/GHRQ snapshot;
- B-F1: uBTB and speculative RAS;
- B-F2: PBTB/BTB plus BIM;
- B-F3: short/medium TAGE plus IBTB launch;
- B-F4: long TAGE, IBTB/loop result, and final arbitration.

Provider rank is
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`; B-F4 uses exact RAS or
high-confidence IBTB targets, `loop > long-TAGE > short-TAGE > BIM`
direction, and BTB direct targets. Backend restart has higher priority as a
typed-recovery source. A later B-stage correction of an already-used
prediction inner-flushes I-SIDE and restarts I-F0.

The I- and B-side pipelines are decoupled and do not advance in lockstep.
ITLB, L1I, refill, predecode, and Instruction Buffer belong only to I-SIDE.

See [LinxCore IFU Architecture](../architecture/linxcore/ifu.md) for the
normative interface and state contract.
