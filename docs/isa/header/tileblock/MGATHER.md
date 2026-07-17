# MGATHER

## Overview

**Gather from Memory to Tile**

`MGATHER` gathers elements from sparse memory locations into a dense destination
Tile. The instruction uses a base address from `RegSrc` plus per-element
offsets stored in `SrcTile`.

Only the `[0, validRow) x [0, validCol)` region is read from memory. The rest
of the destination Tile is filled with `PadValue`.

## Assembly syntax

```asm
MGATHER <LB0:validCol, LB1:validRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, [RegSrc], ->DstTile<Size>
```

## Parameters

| Parameter | Description | Optional |
|-----------|-------------|----------|
| **validCol** | Number of valid columns in the offset Tile and output Tile. Written to `LB0`. | No |
| **validRow** | Number of valid rows in the offset Tile and output Tile. Written to `LB1`. | Yes, defaults to 1 |
| **Col** | Physical column count of the destination Tile, including padded columns. Written to `LB2`. | Yes, defaults to `validCol` |
| **Row** | Physical row count of the destination Tile. Hardware derives this as `Size / (Col * sizeof(DataType))`. | No |
| **DataType** | Element type loaded from memory. | No |
| **PadValue** | Fill value for elements outside the valid region. Supported values are `Null`, `Zero`, `Max`, and `Min`. | Yes, defaults to `Null` |
| **RegSrc** | Base address register. | No |
| **SrcTile** | Offset Tile. Each element is a byte offset from `RegSrc`. | No |
| **DstTile** | Output Tile that receives gathered elements. | No |
| **Size** | Destination Tile size in bytes. Must equal `Row * Col * sizeof(DataType)`. | No |

The offset width is resolved from the element width used when `SrcTile` was
written. Canonical forms allow `u16`, `u32`, or `u64` offsets.

## Encoding

`MGATHER` expands to:

- [BSTART.MGATHER](../../instructions/bstart_mgather.md) `DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` (optional)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` (`validCol`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` (`validRow`)
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` (`Col`, optional)
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

## Execution model

```c
void MGATHER(Tile dst, Scalar base, Tile src) {
  for (int i = 0; i < Row; ++i) {
    for (int j = 0; j < Col; ++j) {
      if (i < validRow && j < validCol) {
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

- `validCol <= Col` and `validRow <= Row` must hold.
- `Size` must be a whole multiple of `Col * sizeof(DataType)`.
- Elements outside the valid region do not issue memory reads.
