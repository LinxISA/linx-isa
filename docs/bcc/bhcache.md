# I-SIDE L1 Instruction Cache

The fetch cache belongs to I-SIDE and is the L1I service for the I-F0..I-F4
pipeline. It is not a B-SIDE predictor structure and does not double as a BTB.

## Access contract

- I-F1 launches ITLB and L1I access in parallel for the same virtual PC and
  request identity.
- I-F2 combines the translated physical tag with the L1I lookup.
- An ITLB miss produces an I-SIDE inner flush and prevents the speculative L1I
  result from becoming an instruction.
- An L1I miss retains request ID, STID, PC, and epoch through refill.
- I-F3 captures one complete cacheline plus ECC/refill status and byte-stream
  context.

Capacity, associativity, banking, replacement, and ECC organization are
implementation parameters. They must preserve response identity, precise
fetch faults, stale-response rejection, and forward progress.

The cache supplies bytes only. I-F4 owns length parsing,
`BSTART`/`BSTOP` boundary recognition, 64-bit normalization, and Instruction
Buffer writes.
