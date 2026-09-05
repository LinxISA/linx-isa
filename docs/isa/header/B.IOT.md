# B.IOT

## Purpose

`B.IOT` binds ordered Local Tile sources and destinations. It uses only the
relative `T#1..T#16`, `U#1..U#16`, `M#1..M#16`, and `N#1..N#16` queue
namespace; Shared `S0..S63` registers are bound by `B.IOS` instead.

The machine-readable catalog is the sole encoding authority.

## Five canonical forms

```asm
B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, mask=PE_MASK, <last>
B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>
```

There is no `.reuse` suffix. `L`/`last` terminates only the effective B.IOT
binding sequence and never releases a source.

## Encoded fields

| Bits | Field | Meaning |
| --- | --- | --- |
| 31:26 | `SrcTile1` or fixed zero | Second Local source |
| 25:20 | `SrcTile0` or fixed zero | First Local source |
| 19 | `L` | End the sequence after this effective binding |
| 18:15 | `SizeCode` | 0 source-only; destination forms use 1..10 |
| 14:12 | `Func` | `100` two sources, `101` one source, `110` no source |
| 11:9 | `PEMode` | Three-bit participation mode |
| 8:7 | `DstTile` | 0 T, 1 U, 2 M, 3 N |
| 6:0 | fixed `0010011` | Minor encoding |

The assembly `PE_MASK` token is restricted to the fixed masks produced by
`PEMode`: `0000`, `1000`, `0100`, `0010`, `0001`, `1100`, `1110`, and
`1111`. `PEMode=000` is a strict no-effect path before placement, duplicate,
schema, allocation, descriptor, memory, and downstream fault checks.

## SizeCode

Source-only forms fix `SizeCode=0` and allocate no destination. Destination
forms accept codes 1..10 for 128 B, 256 B, 512 B, 1 KiB, 2 KiB, 4 KiB,
8 KiB, 16 KiB, 32 KiB, and 64 KiB per participating PE. Codes 11..15 are
reserved and illegal. Core allocation is
`popcount(decoded_mask) * per-PE capacity` and may not exceed 256 KiB.

## Ordering and faults

- Effective B.IOT bindings occur after BSTART and before the first body
  instruction; at most four are accepted.
- All effective bindings in one block use the same decoded PE mask and match
  the operation schema in encoded order.
- `L=1` closes the sequence; a later effective B.IOT traps before effects.
- Reserved bits, SizeCode values, and malformed forms trap illegal before
  architectural effects.
- Descriptor incompatibility, mask expansion, or schema mismatch traps before
  Tile state changes.

## Examples

```asm
B.IOT T#1, U#1, mask=1111, last, ->T<8>  # 16 KiB per PE
B.IOT M#1, mask=1100, last               # PE0+PE1 source
B.IOT T#1, mask=0000, last               # strict no-effect
```
