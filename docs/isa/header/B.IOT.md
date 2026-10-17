# B.IOT

Sole normative source: [PTO-SPEC golden](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/block/operands/B.IOT.asl).

## Assembly forms

```asm
B.IOT SrcTile0.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>
B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, mask=PE_MASK, <last>
B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, mask=PE_MASK, <last>
B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>
```

## Encodings

| PTO form | mask | match | fields |
| --- | --- | --- | --- |
| `b_iot_32_10db6db84f5d` | `0xfc00707f` | `0x00005013` | SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_2c07e7177fad` | `0x0007f1ff` | `0x00004013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_8b8bce6bffe8` | `0x0000707f` | `0x00004013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_c11eb189dd83` | `0xfc07f1ff` | `0x00005013` | SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_efa0fe3fe49a` | `0xfff0707f` | `0x00006013` | L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_ll_src` | `0x0007f1ff` | `0x00002013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_rl_src` | `0x0007f1ff` | `0x00003013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_lr_src` | `0x0007f1ff` | `0x00007013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_ll_dst` | `0x0000707f` | `0x00002013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_rl_dst` | `0x0000707f` | `0x00003013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_lr_dst` | `0x0000707f` | `0x00007013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_last_src` | `0xfc07f1ff` | `0x04005013` | SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_last_dst` | `0xfc00707f` | `0x04005013` | SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |

## Defaults

- PEMode is a three-bit encoding expanded by the common profile decoder to the fixed four-PE semantic mask: 000 none, 001 PE0, 010 PE1, 011 PE2, 100 PE3, 101 PE0+PE1, 110 PE0+PE1+PE2, and 111 all four PEs.
- SizeCode=0 is the source-only encoding and never allocates; destination forms require SizeCode=1..10 for 128 B, 256 B, 512 B, 1 KiB, 2 KiB, 4 KiB, 8 KiB, 16 KiB, 32 KiB, and 64 KiB per participating PE.
- PEMode=000 decodes to no participating PE and is a strict no-op before placement, duplicate, schema, allocation, descriptor, memory, and downstream fault checks.
- T#1, U#1, M#1, and N#1 name the newest published generation in their hand; increasing indices select progressively older live generations. Direct model TileIndex values are resolved physical identities and are not encoded relative selectors.
- Each source suffix is independent: explicit .reuse retains the selected-PE payload; omission marks last-use. Every pre-change word decodes with .reuse. Two-source funct3 100/010/011/111 encode reuse/reuse, last/last, reuse/last, and last/reuse respectively; one-source bit 26 encodes reuse when zero and last-use when one.

## Legality

- The three-bit PEMode field accepts all eight encodings and the common profile decoder expands them exactly to the fixed four-PE semantic mask table.
- Source-only forms require SizeCode=0 and fix instruction bits 7..8 to zero; a non-zero value in those bits is reserved. Destination forms require SizeCode=1..10; codes 11..15 are reserved for Local B.IOT.
- PEMode=000 is accepted as the strict no-effect source-bearing encoding; a nonzero decoded mask is a four-PE predicate shared by every effective binding in the block.
- A participating B.IOT is legal only after BSTART and before the block body. At most four effective Local bindings are accepted in encoded order.
- The selected operation schema determines ordered Local source and destination roles and must agree with the form fields and SizeCode role.
- Every encoded Local source is resolved against the published pre-operation relative map. An unavailable relative generation raises Fault_TileLegality before source reads, allocation, or operation effects.
- Every ordinary Local source independently carries reuse. Duplicate occurrences resolving to one generation aggregate retain-dominantly per participating PE; any reuse occurrence retains payload, and only all-last-use occurrences consume it.

## State effects

- The common PE-mode decoder expands PEMode once to the semantic four-PE mask used by every effective Local binding.
- A zero decoded mask is a strict no-op. A successful last-use source consumes selected-PE payload capacity without removing its generation identity; a reuse source preserves it. A successful destination atomically updates selected payload quarters and a compatible persistent descriptor.
- The selected operation defines publication and ordering. Its first write fixes the allocation mask; later writes may update only a subset with a compatible descriptor and cannot expand the mask.
- Successful destination publication pushes a new generation at #1 of the selected T/U/M/N hand and shifts older live generations toward #16 without modifying their descriptor or payload.

## Memory effects

- none

## Ordering

- Resolve all relative sources against the published pre-operation hand order before allocating or publishing any destination. Successful destinations publish in B.IOT order; each later same-hand destination becomes the newer #1 generation.
- B.IOT bindings are consumed in encoded order. L=1 closes the sequence after the current effective binding; a later effective B.IOT raises Illegal Block Exception before effects.
- After successful non-squashed completion, last-use consumes the complete selected-PE payload backing while retaining the vtag, epoch, descriptor, hand, and relative-order entry. Fault, retry, squash, and PEMode=000 preserve payload lifetime.

## Exceptions

- Reserved instruction bits and malformed field combinations raise Fault_IllegalInstruction before architectural effects.
- A participating B.IOT outside an active header, a duplicate binding, a fifth effective binding, a role mismatch, or an unsupported SizeCode raises the applicable fault before changing the stream.
- A mismatched effective decoded PE mask, incompatible destination descriptor, mask expansion, or operation-schema mismatch raises Fault_TileLegality before tile state changes.
- PEMode=000 is a strict no-op and cannot raise a downstream schema, duplicate, allocation, descriptor, or memory fault.
- A source whose selected-PE payload was consumed raises Fault_TileLegality before source reads or effects. A Local B.ASSEMBLE ParentRef encoded as last-use raises Fault_TileLegality before modifier effects.

## Model support

New LAST/LL/LR/RL forms are not implemented by the Linx Sail subset and reject before effects. Encoding presence does not establish execution support.
