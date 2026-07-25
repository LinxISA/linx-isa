# IFU Model Mapping

The architectural IFU is defined as two decoupled engines:

- I-SIDE: `I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer -> D1`;
- B-SIDE: `B-F0 -> B-F1 -> B-F2 -> B-F3 -> B-F4`.

LinxCoreModel's BFU implementation is useful as an algorithmic reference for
BTB-family lookup, GHR/GHRQ, TAGE, BIM, RAS, IBTB, loop prediction, prediction
arbitration, BRQ/checkpoint state, and recovery. Its internal stage labels do
not override the architectural I-/B-prefix names. Map model behavior to B-F0
L0/NLP+checkpoint, B-F1 uBTB/RAS, B-F2 PBTB/BTB+BIM, B-F3 short/medium
TAGE+IBTB launch, and B-F4 static+long-TAGE/IBTB/loop/final arbitration.

The B-stage provider rank is
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`. The I- and B-side
pipelines are decoupled and non-lockstep. B-F4 is the last prediction-driven
inner-flush point. Its final record follows every instruction through D1;
post-B-F4 Dispatch/BRU mismatch uses BRU flush/recover plus frontend restart.

I-SIDE independently owns parallel ITLB/L1I access at I-F1, ITLB-miss inner flush,
cacheline capture, boundary-only predecode, 64-bit normalization, and
Instruction Buffer writes. D1 reads four `insn64` entries, carries a complete
prediction record per valid lane, and performs full decode.

See [LinxCore IFU Architecture](../../architecture/linxcore/ifu.md).
