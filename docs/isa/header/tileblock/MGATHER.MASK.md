# MGATHER.MASK

## Overview

**Masked Gather from Memory to Tile**

`MGATHER.MASK` extends `MGATHER` with per-element predication. In addition to
the base register and offset Tile, the instruction takes a `MaskTile` whose
elements are 1-bit predicates aligned with the offset Tile.

When a mask bit is `1`, the element is gathered from memory. When a mask bit is
`0`, the gather is skipped and the destination element is filled with
`PadValue`.

## Assembly syntax

```asm
MGATHER.MASK <LB0:Col, LB1:Row, DataType, PadValue>, SrcTile<.reuse>, MaskTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## Parameters

| Parameter | Description | Optional |
|-----------|-------------|----------|
| **Col** | Column count of the offset Tile, mask Tile, and destination Tile. Written to `LB0`. | No |
| **Row** | Row count of the offset Tile, mask Tile, and destination Tile. Written to `LB1`. | Yes, defaults to 1 |
| **DataType** | Element type loaded from memory. | No |
| **PadValue** | Fill value written when the mask bit is `0`. Supported values are `Null`, `Zero`, `Max`, and `Min`. | Yes, defaults to `Null` |
| **RegSrc** | Base address register. | No |
| **SrcTile** | Offset Tile. | No |
| **MaskTile** | 1-bit predicate Tile. | No |
| **DstTile** | Output Tile. | No |
| **Size** | Destination Tile size in bytes. Must equal `Row * Col * sizeof(DataType)`. | No |

The offset width is resolved from the element width used when `SrcTile` was
written. Canonical forms allow `u16`, `u32`, or `u64` offsets.

## Encoding

`MGATHER.MASK` expands to:

- [BSTART.MGATHER.MASK](../../instructions/bstart_mgather_mask.md) `DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` (optional)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` (`Col`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` (`Row`)
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, MaskTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## Execution model

```c
void MGATHER_MASK(Tile dst, Scalar base, Tile src, Tile mask) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (mask[i][j] == 1) {
        offset_t offset = src[i][j];
        dst[i][j] = Memory[base + offset];
      } else {
        dst[i][j] = PadValue;
      }
    }
  }
}
```

## Notes

- `MaskTile` is interpreted as one predicate bit per element.
- Masked-out elements do not issue memory reads.
