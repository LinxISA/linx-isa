# PE IFU

The PE IFU uses the same canonical IFU contract as LinxCore:

## I-SIDE

- I-F0 accepts/selects PC and registers request identity.
- I-F1 launches ITLB and L1I in parallel.
- I-F2 joins their results; ITLB miss causes an I-SIDE inner flush.
- I-F3 captures one cacheline and cross-line byte context.
- I-F4 parses 2/4/6/8-byte lengths, recognizes only `BSTART`/`BSTOP`, expands
  each complete instruction into a 64-bit container, and writes the
  Instruction Buffer.
- D1 reads four 64-bit entries, carries the complete prediction record on each
  valid lane, and performs full decode.

## B-SIDE

B-SIDE is the independent B-F0..B-F4 predictor pipeline: B-F0 L0/NLP and
checkpoint, B-F1 uBTB/RAS, B-F2 PBTB/BTB+BIM, B-F3 short/medium TAGE and
IBTB launch, B-F4 static+long-TAGE/IBTB/loop/final arbitration. B-F4 is the
last prediction-driven inner-flush point; later validation mismatch uses BRU
flush/recover. It communicates with I-SIDE through explicit channels and does
not advance in lockstep with I-F0..I-F4.

See [LinxCore IFU Architecture](../../architecture/linxcore/ifu.md).
