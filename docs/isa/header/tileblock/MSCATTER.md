# MSCATTER

## Overview

**Scatter from Tile to Memory**

`MSCATTER` is the inverse of `MGATHER`. It writes dense Tile data to sparse
memory locations by combining a base address from `RegSrc` with per-element
offsets stored in `SrcTile1`.

Only the `[0, validRow) x [0, validCol)` region is written.

## Assembly syntax

```asm
MSCATTER <LB0:validCol, LB1:validRow, LB2:Col, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, [RegSrc]
```

## Parameters

| Parameter | Description | Optional |
|-----------|-------------|----------|
| **validCol** | Number of valid columns in the source data Tile and offset Tile. Written to `LB0`. | No |
| **validRow** | Number of valid rows in the source data Tile and offset Tile. Written to `LB1`. | Yes, defaults to 1 |
| **Col** | Physical column count of the source Tile, including unused columns. Written to `LB2`. | Yes, defaults to `validCol` |
| **Row** | Physical row count of the source Tile. Hardware derives this from `SrcTile0.Size / (Col * sizeof(DataType))`. | No |
| **DataType** | Element type written to memory. | No |
| **RegSrc** | Base address register. | No |
| **SrcTile0** | Source data Tile. | No |
| **SrcTile1** | Offset Tile. Each element is a byte offset from `RegSrc`. | No |

The offset width is resolved from the element width used when `SrcTile1` was
written. Canonical forms allow `u16`, `u32`, or `u64` offsets.

## Encoding

`MSCATTER` expands to:

- [BSTART.MSCATTER](../../instructions/bstart_mscatter.md) `DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` (`validCol`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` (`validRow`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` (`Col`, optional)
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## Execution model

```c
void MSCATTER(Tile src0, Scalar base, Tile src1) {
  for (int i = 0; i < validRow; ++i) {
    for (int j = 0; j < validCol; ++j) {
      offset_t offset = src1[i][j];
      Memory[base + offset] = src0[i][j];
    }
  }
}
```

## Notes

- `validCol <= Col` and `validRow <= Row` must hold.
- `SrcTile0.Size` must be a whole multiple of `Col * sizeof(DataType)`.
- If multiple active elements target the same address, the final value is
  implementation-defined.
