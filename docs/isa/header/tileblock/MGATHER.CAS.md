# MGATHER.CAS

## Overview

`MGATHER.CAS` performs an element-wise atomic compare-and-swap at
`base + offset[i]`. Each lane compares memory with `expected[i]`, conditionally
stores `desired[i]`, and writes the old memory value to the destination Tile.

## Assembly syntax

```asm
MGATHER.CAS <LB0:Col, LB1:Row, DataType>, OffsetTile<.reuse>, ExpectedTile<.reuse>, DesiredTile<.reuse>, [Base], ->OldTile<Size>
```

## Descriptor roles

- The first [B.IOR](../../header/B.IOR.md) source is the scalar base address.
- The source Tile roles are, in order: offset, expected, desired.
- The destination Tile receives the old memory values.
- Retired destination-only descriptor spellings are not legal.

## Encoding

`MGATHER.CAS` expands to:

- [BSTART.MGATHER.CAS](../../instructions/bstart_mgather_cas.md) `DataType`
- [B.DIM](../../header/B.DIM.md) records for the lane shape
- [B.IOT](../../header/B.IOT.md) records binding offset, expected, desired, and old-value destination Tiles
- [B.IOR](../../header/B.IOR.md) records beginning with the scalar base address

Each active lane is one atomic operation. The returned old value is written
regardless of whether the comparison succeeds.
