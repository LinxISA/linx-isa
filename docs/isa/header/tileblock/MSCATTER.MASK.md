# MSCATTER.MASK

## Overview

**Masked Scatter from Tile to Memory**

`MSCATTER.MASK` extends `MSCATTER` with per-element predication. The
instruction takes a source data Tile, an offset Tile, and a 1-bit `MaskTile`.

Only elements whose mask bit is `1` are written to memory.

## Assembly syntax

```asm
MSCATTER.MASK <LB0:Col, LB1:Row, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, MaskTile<.reuse>, [RegSrc]
```

## Parameters

| Parameter | Description | Optional |
|-----------|-------------|----------|
| **Col** | Column count of the source data Tile, offset Tile, and mask Tile. Written to `LB0`. | No |
| **Row** | Row count of the source data Tile, offset Tile, and mask Tile. Written to `LB1`. | Yes, defaults to 1 |
| **DataType** | Element type written to memory. | No |
| **RegSrc** | Base address register. | No |
| **SrcTile0** | Source data Tile. | No |
| **SrcTile1** | Offset Tile. | No |
| **MaskTile** | 1-bit predicate Tile. | No |

The offset width is resolved from the element width used when `SrcTile1` was
written. Canonical forms allow `u16`, `u32`, or `u64` offsets.

## Encoding

`MSCATTER.MASK` expands to:

- [BSTART.MSCATTER.MASK](../../instructions/bstart_mscatter_mask.md) `DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` (`Col`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` (`Row`)
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, MaskTile<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## Execution model

```c
void MSCATTER_MASK(Tile src0, Scalar base, Tile src1, Tile mask) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (mask[i][j] == 1) {
        offset_t offset = src1[i][j];
        Memory[base + offset] = src0[i][j];
      }
    }
  }
}
```

## Notes

- `MaskTile` is interpreted as one predicate bit per element.
- If multiple active elements target the same address, the final value is
  implementation-defined.
