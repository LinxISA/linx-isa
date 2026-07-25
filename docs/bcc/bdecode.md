# D1 Decode

D1 is the first full instruction-decode stage.

It reads up to four contiguous entries from the independent Instruction Buffer.
Every entry already contains one complete 64-bit `insn64`, its original
2/4/6/8-byte length, PC, `BSTART`/`BSTOP` boundary bits, fault state, and
request/checkpoint metadata.

D1 performs full opcode, operand, immediate, exception, and split/fuse decode
for all four lanes. It does not fetch a separate block header and does not
reslice a variable-length byte stream. Boundary metadata guides block-group
formation; downstream D2/D3 owners calculate demand and atomically admit
BROB/ROB, rename, IQ, and memory-order resources.
