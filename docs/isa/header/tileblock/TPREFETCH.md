# TPREFETCH

## Overview

`TPREFETCH` performs the same address generation and memory-access validation
as `TLOAD`, but it has no destination Tile and produces no architectural data
result. It is a performance hint: implementations may retain, combine, or drop
the fetched data after completing the architecturally required checks.

## Assembly syntax

```asm
TPREFETCH <LB0:Col, LB1:Row, DataType>, [RegSrc]
```

## Encoding

`TPREFETCH` expands to:

- [BSTART.TPREFETCH](../../instructions/bstart_tprefetch.md) `DataType`
- [B.DIM](../../header/B.DIM.md) records for the TLOAD-equivalent shape
- [B.IOR](../../header/B.IOR.md) records for the TLOAD-equivalent base and strides

No `B.IOT` destination descriptor is legal.

## Execution model

For each address that the corresponding `TLOAD` would access, `TPREFETCH`
performs the same address calculation, translation, permission checks, and
fault behavior. It does not allocate or write a destination Tile.

## Encoding adjacency

The TLSU function assignments are `TLOAD=0`, `TSTORE=1`, `TMOV=2`, and
`TPREFETCH=3`, placing `TPREFETCH` directly beside the existing load/store
family in the v0.58 contract.
