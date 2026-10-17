# B.IOS

Sole normative source: [PTO-SPEC golden](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/block/operands/B.IOS.asl).

## Assembly forms

```asm
B.IOS S<SharedTileID>.reuse, mask=<PE_MASK>
B.IOS mask=<PE_MASK>, ->S<SharedTileID><SizeCode>
B.IOS S<SharedTileID>, mask=<PE_MASK>
```

## Encodings

| PTO form | mask | match | fields |
| --- | --- | --- | --- |
| `b_ios_32_4ba5ef98fdaa` | `0xfc0871ff` | `0x00001013` | SharedTileID=25:20; SizeCode=18:15; PEMode=11:9 |
| `b_ios_32_last_src` | `0xfc0ff1ff` | `0x04001013` | SharedTileID=25:20; PEMode=11:9 |

## Defaults

- S0 is an ordinary absolute Shared-register name. SizeCode=0 selects the source form; SizeCode=1..12 selects a destination capacity of 128 B, 256 B, 512 B, 1 KiB, 2 KiB, 4 KiB, 8 KiB, 16 KiB, 32 KiB, 64 KiB, 128 KiB, or 256 KiB for the complete Core-wide Shared object. Codes 13..15 are reserved.
- PEMode is a three-bit encoding expanded by the common profile decoder to the fixed four-PE semantic mask: 000 none, 001 PE0, 010 PE1, 011 PE2, 100 PE3, 101 PE0+PE1, 110 PE0+PE1+PE2, and 111 all four PEs.
- PEMode=000 decodes to no participating PE and is a strict no-op before placement, duplicate, schema, allocation, descriptor, memory, and downstream fault checks.
- Every pre-change B.IOS word has bit 26 zero and retains its source payload; canonical assembly prints .reuse for that state. An ordinary source without .reuse has bit 26 one and declares Core-wide last-use.

## Legality

- All SharedTileID codes 0..63 are assigned absolute Core-private Shared-register names S0..S63.
- SizeCode code 0 is the source role; destination codes 1..12 encode 128 B, 256 B, 512 B, 1 KiB, 2 KiB, 4 KiB, 8 KiB, 16 KiB, 32 KiB, 64 KiB, 128 KiB, and 256 KiB for the complete Core-wide Shared object. Codes 13..15 are reserved.
- The three-bit PEMode field accepts all eight encodings and the common profile decoder expands them exactly to the fixed four-PE semantic mask table. PEMode=000 is the strict no-effect source-bearing encoding.
- A participating B.IOS is legal only after BSTART and before the block body. At most four effective Shared bindings are accepted in encoded order.
- Two effective bindings in one block may not name the same Sx. The selected operation schema determines each ordered Shared operand role and must agree with SizeCode source/destination encoding.
- Bit 26 is assigned only for an ordinary source with SizeCode=0: zero retains its payload and one denotes last-use. A destination with bit 26 one is reserved; bit 27 remains reserved. A source-form B.ASSEMBLE continuation reclassified as a reused destination must encode bit 26 zero.

## State effects

- The common PE-mode decoder expands PEMode once to the semantic four-PE mask used by every effective Shared binding.
- A zero decoded mask is a strict no-op. An ordinary Shared source with .reuse leaves payload capacity intact; an ordinary last-use source consumes complete Core-wide payload capacity at successful non-squashed block completion while retaining Sx identity and descriptor.
- A successful singleton destination publishes the complete Shared parent; a multi-PE destination uses B.ASSEMBLE with explicit non-overlapping ranges and atomic LAST publication.

## Memory effects

- none

## Ordering

- Effective B.IOS bindings form one encoded-order stream of at most four operands. The selected operation consumes the stream in schema order.
- The architecture imposes no ordering between conflicting PE accesses to Shared payload offsets; software avoids conflicts or establishes separate synchronization.
- After successful non-squashed completion, an ordinary last-use source returns its complete Core-wide payload capacity while preserving Sx identity and descriptor. Fault, retry, squash, and zero participation preserve payload lifetime.

## Exceptions

- Reserved instruction bits, SizeCode 13..15, and malformed field combinations raise Fault_IllegalInstruction before architectural effects.
- A participating B.IOS outside an active header, a duplicate SharedTileID, or a fifth effective binding raises Illegal Block Exception before changing the stream.
- A mismatched effective decoded PE mask, incompatible destination descriptor, mask expansion, or operation-schema role mismatch raises Fault_TileLegality before Shared state changes.
- PEMode=000 is a strict no-op and cannot raise a downstream schema, duplicate, allocation, descriptor, or memory fault.
- A source resolving to a consumed Shared payload raises Fault_TileLegality before payload access. A B.ASSEMBLE continuation reused destination encoded as last-use raises Fault_TileLegality before effects.

## Model support

New LAST/LL/LR/RL forms are not implemented by the Linx Sail subset and reject before effects. Encoding presence does not establish execution support.
